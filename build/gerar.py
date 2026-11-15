"""Gera o site estático da Aldeia Imóveis em public/.

    python3 build/gerar.py

Entrada: dados/imoveis-bruto.json, dados/descricoes.json, dados/midias.json
Sem dependências fora da biblioteca padrão.
"""
import html, json, os, re, shutil, unicodedata
from datetime import date

from paginas import (pg_home, pg_listagem, pg_ficha, pg_anunciar, pg_administracao,
                     pg_financiamento, pg_sobre, pg_contato, pg_privacidade,
                     pg_apresentacao, pg_404)
import base

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(RAIZ, "public")

FORA = {"APA00340": "anúncio de teste", "SAL0044": "duplicado de SAL0074"}
COMERCIAIS = {"Sala Comercial", "Barracão", "Casa Comercial", "Prédio Comercial", "Loja", "Comercial"}
SEM_COMODOS = COMERCIAIS | {"Terreno", "Terreno Residencial"}

NOMES = {
    "AURELIA": "Jardim Aurélia", "CAMBUI": "Cambuí", "JARDIM PAULICEIA": "Jardim Paulicéia",
    "ESTANCIA DAS ÁGUAS": "Estância das Águas", "SANTO ANTONIO": "Santo Antônio",
    "JAGUARIUNA": "Jaguariúna", "JARDIM IV CENTENÁRIO": "Jardim IV Centenário",
    "TAUBATÉ": "Taubaté", "SUMARÉ": "Sumaré",
}
MINUSCULAS = {"de", "da", "do", "das", "dos", "e", "em"}


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def nome_proprio(s):
    s = " ".join(s.split())
    if s.upper() in NOMES:
        return NOMES[s.upper()]
    out = []
    for i, p in enumerate(s.lower().split(" ")):
        if p in ("iv", "ii", "iii"):
            out.append(p.upper())
        elif i and p in MINUSCULAS:
            out.append(p)
        else:
            out.append(p[:1].upper() + p[1:])
    return " ".join(out)


def dinheiro(s):
    m = re.search(r"R\$\s*([\d.]+),(\d\d)", s or "")
    if not m:
        return None
    v = float(m.group(1).replace(".", "") + "." + m.group(2))
    return v if v > 0 else None


def numero(lista, padrao):
    for c in lista:
        m = re.search(padrao, c, re.I)
        if m:
            return float(m.group(1).replace(".", "").replace(",", "."))
    return 0


def artigo(bairro):
    return "na" if re.match(r"(Vila|Cidade|Estância)\b", bairro) else "no"


def rua_de(endereco, bairro_bruto):
    if not endereco:
        return ""
    e = endereco.strip()
    corte = e.upper().rfind(", " + bairro_bruto.upper())
    if corte > 0:
        e = e[:corte]
    else:
        e = e.rsplit(" - ", 1)[0]
    e = re.sub(r"\s*APT[º°.]*\s*\d+", "", e, flags=re.I)
    e = re.sub(r"\s+N\s+(\d)", r", \1", e)
    e = re.sub(r"\s+(\d[\d.]*)$", r", \1", e) if "," not in e else e
    e = nome_proprio(e.strip(" ,"))
    return re.sub(r"\b(Dr|Av|Com)\.", lambda m: m.group(0), e)


def normalizar():
    bruto = json.load(open(os.path.join(RAIZ, "dados", "imoveis-bruto.json"), encoding="utf-8"))
    desc = json.load(open(os.path.join(RAIZ, "dados", "descricoes.json"), encoding="utf-8"))
    midias = json.load(open(os.path.join(RAIZ, "dados", "midias.json"), encoding="utf-8"))
    itens = []
    for b in bruto:
        cod = b["cod"]
        if cod in FORA:
            continue
        car = b["caracteristicas"]
        tipo = car[0] if car else b["tipo"]
        bairro_bruto = re.sub(r"^Condom[íi]nio em ", "", b["bairro"]).strip()
        bairro = nome_proprio(bairro_bruto)
        cidade = nome_proprio(b["cidade"])
        venda, locacao = dinheiro(b["venda"]), dinheiro(b["locacao"])
        trans = (b["transacao"] or "").lower()
        tem_v = "venda" in trans and venda
        tem_l = ("loca" in trans and locacao)
        if cod == "SAL0074":  # fundido com SAL0044, que era a mesma sala
            tem_l, locacao = True, locacao or 600.0
        if cod == "APA00279":  # anunciado só para venda; o aluguel citado é do contrato atual
            tem_l = False
        m = midias.get(cod, {})
        d = desc.get(cod, {})
        it = {
            "codigo": cod, "tipo": tipo, "bairro": bairro, "cidade": cidade,
            "venda": venda if tem_v else None, "locacao": locacao if tem_l else None,
            "quartos": int(numero(car, r"(\d+)\s*dormit")), "suites": int(numero(car, r"(\d+)\s*su[íi]te")),
            "vagas": int(numero(car, r"(\d+)\s*vaga")), "banheiros": int(numero(car, r"(\d+)\s*banheiro")),
            "area": numero(car, r"([\d.,]+)\s*M²"),
            "condominio": dinheiro(b["condominio"]), "iptu": dinheiro(b["iptu"]),
            "rua": rua_de(b["endereco"], bairro_bruto),
            "texto": d.get("texto", ""), "obs": d.get("obs", ""),
            "fotos": m.get("fotos", []), "lat": m.get("lat"), "lng": m.get("lng"),
            "precisao": m.get("precisao"),
        }
        if tipo in SEM_COMODOS:
            it["quartos"] = it["suites"] = 0
        if tipo.startswith("Terreno"):
            it["vagas"] = it["banheiros"] = 0
        it["comercial"] = tipo in COMERCIAIS
        it["num"] = int(re.sub(r"\D", "", cod) or 0)
        it["slug"] = "%s-%s-%s" % (cod.lower(), slug(tipo), slug(bairro))
        it["url"] = "/imovel/%s/" % it["slug"]
        it["modo"] = ("v" if it["venda"] else "") + ("l" if it["locacao"] else "")
        it["financiavel"] = bool(re.search(r"pronta para financiamento|aceita financiamento|pode ser financiado de novo", it["obs"], re.I))
        partes = [tipo]
        if it["quartos"]:
            partes.append("de %d dormitório%s" % (it["quartos"], "s" if it["quartos"] > 1 else ""))
        if it["area"]:
            partes.append(("e " if it["quartos"] else "de ") + base.area(it["area"]))
        it["titulo"] = "%s %s %s" % (" ".join(partes), artigo(bairro), bairro)
        if cidade != "Campinas":
            it["titulo"] += ", " + cidade
        itens.append(it)
    itens.sort(key=lambda i: -i["num"])
    return itens


def escrever(caminho, conteudo):
    destino = os.path.join(PUB, caminho)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    open(destino, "w", encoding="utf-8").write(conteudo)


def main():
    itens = normalizar()
    ctx = base.Contexto(itens)
    # limpa só o que este script gera
    for pasta in ["imovel", "comprar", "alugar", "imoveis", "anunciar", "administracao",
                  "financiamento", "a-aldeia", "contato", "privacidade", "apresentacao"]:
        shutil.rmtree(os.path.join(PUB, pasta), ignore_errors=True)

    paginas = []  # (caminho, prioridade)
    escrever("index.html", pg_home(ctx)); paginas.append(("/", "1.0"))
    for modo, caminho in (("v", "comprar"), ("l", "alugar"), ("", "imoveis")):
        escrever(caminho + "/index.html", pg_listagem(ctx, modo)); paginas.append(("/%s/" % caminho, "0.9"))
    for it in itens:
        escrever(it["url"].strip("/") + "/index.html", pg_ficha(ctx, it)); paginas.append((it["url"], "0.8"))
    for caminho, fn in (("anunciar", pg_anunciar), ("administracao", pg_administracao),
                        ("financiamento", pg_financiamento), ("a-aldeia", pg_sobre),
                        ("contato", pg_contato), ("privacidade", pg_privacidade)):
        escrever(caminho + "/index.html", fn(ctx)); paginas.append(("/%s/" % caminho, "0.6"))
    escrever("apresentacao/index.html", pg_apresentacao(ctx))
    escrever("404.html", pg_404(ctx))

    hoje = date.today().isoformat()
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for caminho, pri in paginas:
        sm.append("<url><loc>%s%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>" % (base.SITE_URL, caminho, hoje, pri))
    sm.append("</urlset>")
    escrever("sitemap.xml", "\n".join(sm) + "\n")
    escrever("robots.txt", base.robots())
    escrever("robots.producao.txt", base.robots(producao=True))
    escrever("llms.txt", base.llms(ctx))
    escrever("llms-full.txt", base.llms(ctx, completo=True))
    feed = {"imobiliaria": base.EMPRESA["nome"], "creci": base.EMPRESA["creci"], "atualizado": hoje,
            "fonte": "https://www.aldeia.com.br/site/",
            "imoveis": [{k: it[k] for k in ("codigo", "tipo", "titulo", "bairro", "cidade", "venda", "locacao",
                                            "quartos", "suites", "vagas", "banheiros", "area", "condominio",
                                            "iptu", "texto", "obs")} | {"url": base.SITE_URL + it["url"]}
                        for it in itens]}
    escrever("imoveis.json", json.dumps(feed, ensure_ascii=False, indent=1))
    print("gerado: %d imóveis, %d páginas no sitemap" % (len(itens), len(paginas)))


if __name__ == "__main__":
    main()
