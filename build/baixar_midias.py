"""Baixa as fotos dos imóveis do site atual da Aldeia e geocodifica os endereços.

Uso: python3 -I build/baixar_midias.py <pasta_html_bruto> <imoveis-bruto.json>
Saída: public/assets/imoveis/<COD>/<n>.webp, public/assets/imoveis/<COD>/c.webp
       dados/midias.json  (fotos por código + lat/lng)
Idempotente: pula o que já existe.
"""
import json, os, re, subprocess, sys, time, urllib.parse, urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRUTO, LISTA = sys.argv[1], sys.argv[2]
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
MAX_FOTOS = 8
SAIDA = os.path.join(RAIZ, "dados", "midias.json")


def baixar(url, tentativas=3):
    for i in range(tentativas):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
                return r.read()
        except Exception:
            time.sleep(1.5 * (i + 1))
    return b""


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
for it in itens:
    cod = it["cod"]
    reg = midias.setdefault(cod, {"fotos": [], "lat": None, "lng": None, "precisao": None})
    html = open(os.path.join(BRUTO, "imovel_%s.html" % it["arquivo"]), errors="replace").read()
    principal = html.split("veis parecidos")[0]
    hashes = []
    for h in re.findall(r"thumb/([0-9a-f]{32})/195/235", principal):
        if h not in hashes:
            hashes.append(h)
    pasta = os.path.join(RAIZ, "public", "assets", "imoveis", cod)
    os.makedirs(pasta, exist_ok=True)
    fotos = []
    for n, h in enumerate(hashes[:MAX_FOTOS], 1):
        destino = os.path.join(pasta, "%d.webp" % n)
        if not os.path.exists(destino):
            dado = baixar("https://www.aldeia.com.br/site/thumb/%s/1200/800/crop/" % h)
            if len(dado) < 2000:
                continue
            tmp = destino[:-5] + ".jpg"
            open(tmp, "wb").write(dado)
            subprocess.run(["cwebp", "-quiet", "-q", "72", tmp, "-o", destino], check=False)
            os.remove(tmp)
            time.sleep(0.2)
        if os.path.exists(destino):
            fotos.append("%d.webp" % n)
    capa = os.path.join(pasta, "c.webp")
    if fotos and not os.path.exists(capa):
        subprocess.run(["cwebp", "-quiet", "-q", "70", "-resize", "640", "0",
                        os.path.join(pasta, fotos[0]), "-o", capa], check=False)
    reg["fotos"] = fotos
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
    print(cod, len(fotos), "fotos", reg["precisao"], flush=True)
print("FIM", len(midias))
