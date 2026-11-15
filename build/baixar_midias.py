"""Baixa TODAS as fotos dos imóveis do site atual da Aldeia, no arquivo original, e geocodifica.

Uso: python3 -I build/baixar_midias.py <pasta_html_bruto> <imoveis-bruto.json>

Para cada foto do anúncio (na ordem do site):
  public/assets/imoveis/<COD>/<n>.webp    original, lado maior limitado a 1400 px, proporção preservada
  public/assets/imoveis/<COD>/<n>m.webp   miniatura de 360 px de largura
  public/assets/imoveis/<COD>/c.webp      capa do card: recorte central 3:2 em 720x480
dados/midias.json guarda, por código: fotos [{arq, w, h}], lat, lng, precisao.
Idempotente: pula o que já existe.
"""
import json, os, re, subprocess, sys, time, urllib.parse, urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRUTO, LISTA = sys.argv[1], sys.argv[2]
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
LADO = 1400
MINIMO = 120  # original menor que isso é miniatura corrompida no servidor (43x58): não entra
SAIDA = os.path.join(RAIZ, "dados", "midias.json")


def baixar(url, tentativas=3):
    for i in range(tentativas):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read()
        except Exception:
            time.sleep(1.5 * (i + 1))
    return b""


def dimensoes(caminho):
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", caminho], capture_output=True, text=True).stdout
    w = re.search(r"pixelWidth:\s*(\d+)", out)
    h = re.search(r"pixelHeight:\s*(\d+)", out)
    return (int(w.group(1)), int(h.group(1))) if w and h else (0, 0)


def geocodificar(consulta):
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": consulta, "format": "json", "limit": 1, "countrycodes": "br"})
    req = urllib.request.Request(url, headers={"User-Agent": "site-imobiliaria-build/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read())
            if d:
                return float(d[0]["lat"]), float(d[0]["lon"])
    except Exception:
        pass
    return None


midias = json.load(open(SAIDA)) if os.path.exists(SAIDA) else {}
itens = json.load(open(LISTA))
falhas = []
for it in itens:
    cod = it["cod"]
    reg = midias.setdefault(cod, {"fotos": [], "lat": None, "lng": None, "precisao": None})
    html = open(os.path.join(BRUTO, "imovel_%s.html" % it["arquivo"]), errors="replace").read()
    principal = html.split("veis parecidos")[0]
    hashes = []
    for h in re.findall(r'href="https://www\.aldeia\.com\.br/site/thumb/([0-9a-f]{32})"\s+rel="lightbox"', principal):
        if h not in hashes:
            hashes.append(h)
    pasta = os.path.join(RAIZ, "public", "assets", "imoveis", cod)
    os.makedirs(pasta, exist_ok=True)
    marca = os.path.join(pasta, ".original2")  # marca que a pasta já está no formato novo
    if not os.path.exists(marca):
        for velho in os.listdir(pasta):
            os.remove(os.path.join(pasta, velho))
        open(marca, "w").write("fotos originais, sem corte\n")
    fotos, pequenas, n = [], reg.get("pequenas", []), 0
    ja = {f.get("hash"): f for f in reg.get("fotos", []) if f.get("hash")}
    for h in hashes:
        if h in pequenas:
            continue
        n += 1
        destino = os.path.join(pasta, "%d.webp" % n)
        mini = os.path.join(pasta, "%dm.webp" % n)
        tmp = os.path.join(pasta, "_tmp.jpg")
        if not (os.path.exists(destino) and os.path.exists(mini) and h in ja):
            dado = baixar("https://www.aldeia.com.br/site/thumb/%s" % h)
            if len(dado) < 300:
                falhas.append((cod, n, h))
                n -= 1
                continue
            open(tmp, "wb").write(dado)
            ow, oh = dimensoes(tmp)
            if max(ow, oh) < MINIMO:
                pequenas.append(h)
                os.remove(tmp)
                n -= 1
                continue
            if max(ow, oh) > LADO:
                subprocess.run(["sips", "-s", "format", "jpeg", "-Z", str(LADO), tmp, "--out", tmp], capture_output=True)
            else:
                subprocess.run(["sips", "-s", "format", "jpeg", tmp, "--out", tmp], capture_output=True)
            subprocess.run(["cwebp", "-quiet", "-q", "72", tmp, "-o", destino], check=False)
            subprocess.run(["cwebp", "-quiet", "-q", "62", "-resize", "360", "0", tmp, "-o", mini], check=False)
            if n == 1:
                w, hh = dimensoes(tmp)
                # recorte central 3:2 para a capa do card
                if w and hh:
                    if w / hh > 1.5:
                        cw, ch = int(hh * 1.5), hh
                    else:
                        cw, ch = w, int(w / 1.5)
                    x, y = (w - cw) // 2, (hh - ch) // 2
                    subprocess.run(["cwebp", "-quiet", "-q", "72", "-crop", str(x), str(y), str(cw), str(ch),
                                    "-resize", "720", "480", tmp, "-o", os.path.join(pasta, "c.webp")], check=False)
            os.remove(tmp)
            time.sleep(0.15)
        if os.path.exists(destino):
            dw = subprocess.run(["webpinfo", "-summary", destino], capture_output=True, text=True).stdout
            m = re.search(r"Width:\s*(\d+)\s*Height:\s*(\d+)", dw.replace("\n", " "))
            w, hh = (int(m.group(1)), int(m.group(2))) if m else (0, 0)
            fotos.append({"arq": "%d.webp" % n, "w": w, "h": hh, "hash": h})
    reg["fotos"] = fotos
    reg["pequenas"] = pequenas
    reg["total_no_site"] = len(hashes)
    if reg["lat"] is None:
        end = (it.get("endereco") or "").strip()
        rua = end.split(",")[0].strip()
        num = (re.search(r",\s*(\d+)", end) or [None, ""])[1]
        cidade = (it.get("cidade") or "").title()
        tentativas = []
        if rua and num:
            tentativas.append(("rua", "%s %s, %s, SP, Brasil" % (rua, num, cidade)))
        if rua:
            tentativas.append(("rua", "%s, %s, SP, Brasil" % (rua, cidade)))
        bairro = re.sub(r"^Condom[íi]nio em ", "", it.get("bairro") or "")
        tentativas.append(("bairro", "%s, %s, SP, Brasil" % (bairro, cidade)))
        tentativas.append(("cidade", "%s, SP, Brasil" % cidade))
        for prec, q in tentativas:
            p = geocodificar(q)
            time.sleep(1.1)
            if p:
                reg["lat"], reg["lng"], reg["precisao"] = p[0], p[1], prec
                break
    json.dump(midias, open(SAIDA, "w"), ensure_ascii=False, indent=1)
    print(cod, "%d de %d fotos, %d corrompidas no servidor" % (len(fotos), len(hashes), len(pequenas)), flush=True)
print("FIM", len(midias), "imoveis;", sum(len(v["fotos"]) for v in midias.values()), "fotos;", len(falhas), "falhas", falhas[:10])
