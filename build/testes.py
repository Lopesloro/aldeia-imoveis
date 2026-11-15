"""Testes do site gerado. Rodar depois de build/gerar.py.

    python3 build/testes.py

Sai com código 1 se qualquer verificação falhar.
"""
import json, os, re, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(RAIZ, "public")
falhas, ok = [], 0


def checar(cond, msg):
    global ok
    if cond:
        ok += 1
    else:
        falhas.append(msg)


def paginas():
    for base, _, arquivos in os.walk(PUB):
        for a in arquivos:
            if a.endswith(".html"):
                yield os.path.join(base, a)


def ler(caminho):
    return open(caminho, encoding="utf-8").read()


todas = list(paginas())
rel = lambda p: os.path.relpath(p, PUB)

# 1. Páginas obrigatórias
for p in ["index.html", "comprar/index.html", "alugar/index.html", "imoveis/index.html",
          "anunciar/index.html", "administracao/index.html", "financiamento/index.html",
          "a-aldeia/index.html", "contato/index.html", "privacidade/index.html",
          "apresentacao/index.html", "404.html", "sitemap.xml", "robots.txt", "llms.txt",
          "llms-full.txt", "imoveis.json", "assets/css/site.css", "assets/js/site.js",
          "assets/js/medicao.js", "assets/js/config.js"]:
    checar(os.path.exists(os.path.join(PUB, p)), "falta o arquivo public/" + p)

# 2. Carteira: 55 imóveis (57 do site atual, menos o de teste e o duplicado)
fichas = [p for p in todas if os.sep + "imovel" + os.sep in p]
checar(len(fichas) == 55, "esperava 55 fichas de imóvel, achei %d" % len(fichas))
if os.path.exists(os.path.join(PUB, "imoveis.json")):
    feed = json.load(open(os.path.join(PUB, "imoveis.json"), encoding="utf-8"))
    checar(len(feed["imoveis"]) == 55, "imoveis.json deveria ter 55 itens")
    cods = [i["codigo"] for i in feed["imoveis"]]
    checar("APA00340" not in cods, "o imóvel de teste APA00340 foi publicado")
    checar("SAL0044" not in cods, "a sala duplicada SAL0044 foi publicada")

# 3. Regras por página
for p in todas:
    h = ler(p)
    n = rel(p)
    checar(len(re.findall(r"<h1[\s>]", h)) == 1, n + ": precisa de exatamente um <h1>")
    checar(re.search(r"<title>[^<]{10,70}</title>", h) is not None, n + ": <title> ausente ou fora de 10–70 caracteres")
    checar('name="robots" content="noindex' in h, n + ": demonstração sem noindex")
    checar('name="viewport"' in h, n + ": sem meta viewport")
    checar("blueshieldpro.svg" in h, n + ": sem o logo da BlueShieldPro no rodapé")
    checar("aldeia-branco.png" in h, n + ": sem o logo da Aldeia")
    checar("3716-J" in h, n + ": sem o CRECI")
    checar(re.search(r"R\$\s?0(,00)?(?![\d.])", h) is None, n + ": preço zerado na tela")
    checar(re.search(r"(?<![\d.,])0 m²", h) is None, n + ": área zerada na tela")
    checar("None" not in re.sub(r"<script.*?</script>", "", h, flags=re.S), n + ": 'None' vazou para o HTML")
    checar("lorem" not in h.lower(), n + ": lorem ipsum")
    checar(re.search(r'<link[^>]+stylesheet[^>]+href="https?://', h) is None, n + ": folha de estilo externa bloqueia a página se o terceiro cair")
    checar(re.search(r'<script[^>]+src="https?://', h) is None, n + ": script externo no HTML (terceiros só entram pelo medicao.js, com consentimento)")
    checar("—" not in re.sub(r"<script.*?</script>", "", h, flags=re.S), n + ": travessão no texto")
    checar(re.search(r'<img(?![^>]*\balt=)[^>]*>', h) is None, n + ": imagem sem alt")
    for bloco in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, flags=re.S):
        try:
            json.loads(bloco)
            checar(True, "")
        except ValueError as e:
            checar(False, n + ": JSON-LD inválido (%s)" % e)
    # links internos
    for href in re.findall(r'(?:href|src)="(/[^"#?]*)', h):
        alvo = os.path.join(PUB, href.lstrip("/"))
        if href.endswith("/"):
            alvo = os.path.join(alvo, "index.html")
        checar(os.path.exists(alvo), n + ": link interno quebrado -> " + href)

# 4. Fichas: dados estruturados e contato
for p in fichas:
    h = ler(p)
    n = rel(p)
    checar('"RealEstateListing"' in h, n + ": sem JSON-LD RealEstateListing")
    checar("data-form" in h, n + ": sem formulário de contato")
    checar("data-galeria" in h, n + ": sem galeria")

# 4b. Todas as fotos do site atual foram trazidas, e cada ficha mostra todas
midias = json.load(open(os.path.join(RAIZ, "dados", "midias.json"), encoding="utf-8"))
total_site = total_novo = 0
for cod, m in midias.items():
    if cod in ("APA00340", "SAL0044"):
        continue
    total_site += m.get("total_no_site", 0)
    total_novo += len(m["fotos"])
    # foto cujo original no servidor tem menos de 120 px é miniatura corrompida: fica fora, mas é contada
    checar(len(m["fotos"]) + len(m.get("pequenas", [])) == m.get("total_no_site", 0),
           "%s: %d fotos no site atual, %d no novo e %d corrompidas" % (cod, m.get("total_no_site", 0), len(m["fotos"]), len(m.get("pequenas", []))))
    for f in m["fotos"]:
        base_f = os.path.join(PUB, "assets", "imoveis", cod, f["arq"])
        checar(os.path.exists(base_f) and os.path.exists(base_f.replace(".webp", "m.webp")), "%s: arquivo de foto ausente %s" % (cod, f["arq"]))
        checar(max(f["w"], f["h"]) >= 120, "%s: foto %s pequena demais (%dx%d)" % (cod, f["arq"], f["w"], f["h"]))
for p in fichas:
    h = ler(p)
    cod = re.search(r'data-imovel="([^"]+)"', h).group(1)
    n = len(midias[cod]["fotos"])
    checar(len(re.findall(r"data-gal-ir=", h)) == n, rel(p) + ": galeria deveria ter %d miniaturas" % n)
    checar("object-fit" not in h, rel(p) + ": estilo inline na galeria")

# 4c. Contato de compra, aluguel e anúncio sai pelo WhatsApp, com mensagem pronta
for p in todas:
    h = ler(p)
    n = rel(p)
    for form in re.findall(r"<form[^>]*data-form.*?</form>", h, flags=re.S):
        checar("Enviar pelo WhatsApp" in form, n + ": formulário sem botão de WhatsApp")
        checar('name="text"' in form and re.search(r"<textarea[^>]*>\s*\S", form) is not None, n + ": formulário sem mensagem pronta")
        checar('type="email"' not in form, n + ": formulário ainda pede e-mail")
    for a in re.findall(r"<a[^>]*data-wa[^>]*>", h):
        checar("https://wa.me/" in a and "text=" in a, n + ": link de WhatsApp sem mensagem pronta")
for p in fichas:
    h = ler(p)
    cod = re.search(r'data-imovel="([^"]+)"', h).group(1)
    checar(re.search(r"<textarea[^>]*>[^<]*" + cod, h) is not None, rel(p) + ": mensagem pronta sem o código do imóvel")

# 5. Demonstração fechada para buscadores
if os.path.exists(os.path.join(PUB, "robots.txt")):
    checar("Disallow: /" in ler(os.path.join(PUB, "robots.txt")), "robots.txt da demonstração deveria bloquear tudo")

# 6. Medição só com ID
if os.path.exists(os.path.join(PUB, "assets/js/config.js")):
    cfg = ler(os.path.join(PUB, "assets/js/config.js"))
    checar(re.search(r"metaPixelId:\s*''", cfg) is not None, "config.js não pode sair com ID de pixel preenchido")

print("%d verificações ok, %d falhas" % (ok, len(falhas)))
for f in falhas[:40]:
    print("FALHA:", f)
if len(falhas) > 40:
    print("... e mais", len(falhas) - 40)
sys.exit(1 if falhas else 0)
