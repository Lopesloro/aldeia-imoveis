"""Constantes, formatação, layout e componentes compartilhados."""
import html, json, re, unicodedata
from collections import Counter

# Enquanto for demonstração, nada é indexado. Trocar para True só com o domínio do cliente.
PUBLICADO = False
SITE_URL = "https://aldeia-imoveis.onrender.com"
VERSAO = "6"

EMPRESA = {
    "nome": "Aldeia Imóveis",
    "razao": "Aldeia Consultoria, Vendas e Administração de Imóveis Ltda.",
    "creci": "3716-J",
    "rua": "Av. Dr. Alberto Sarmento, 684",
    "bairro": "Castelo",
    "cidade": "Campinas",
    "uf": "SP",
    "cep": "13070-711",
    "referencia": "próximo ao Balão do Castelo",
    "tel1": "(19) 3241-6444", "tel1_link": "+551932416444",
    "tel2": "(19) 2121-6444", "tel2_link": "+551921216444",
    "email": "aldeia@aldeia.com.br",
    "horario": "Segunda a sexta, das 9h às 12h e das 13h30 às 17h",
    "boleto": "https://gerenciador.imo7.com.br/boletos/aldeia",
    "lat": -22.8942445, "lng": -47.0786245,
    "anos": 42,
}

MENU = [("Comprar", "/comprar/"), ("Alugar", "/alugar/"), ("Anunciar imóvel", "/anunciar/"),
        ("Administração", "/administracao/"), ("Financiamento", "/financiamento/"),
        ("A Aldeia", "/a-aldeia/"), ("Contato", "/contato/")]


def e(s):
    return html.escape(str(s), quote=True)


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def milhar(v):
    return ("%d" % round(v)).replace(",", ".") if v < 1000 else "{:,.0f}".format(v).replace(",", ".")


def reais(v, centavos=False):
    if not v:
        return ""
    if centavos or abs(v - round(v)) > 0.004:
        return "R$ " + "{:,.2f}".format(v).replace(",", "X").replace(".", ",").replace("X", ".")
    return "R$ " + milhar(v)


def area(v):
    if not v:
        return ""
    if abs(v - round(v)) > 0.004:
        return ("%.2f" % v).replace(".", ",") + " m²"
    return milhar(v) + " m²"


def plural(n, um, varios):
    return "%d %s" % (n, um if n == 1 else varios)


def specs(it, curto=False):
    out = []
    if it["quartos"]:
        out.append(plural(it["quartos"], "dormitório", "dormitórios"))
    if it["suites"] and not curto:
        out.append(plural(it["suites"], "suíte", "suítes"))
    if it["banheiros"] and not curto:
        out.append(plural(it["banheiros"], "banheiro", "banheiros"))
    if it["vagas"]:
        out.append(plural(it["vagas"], "vaga", "vagas"))
    if it["area"]:
        out.append(area(it["area"]))
    return out


def selo(it):
    return {"v": "Venda", "l": "Locação", "vl": "Venda e locação"}[it["modo"]]


def preco_card(it, modo=""):
    partes = []
    if it["venda"] and modo != "l":
        partes.append('<span class="preco-v">%s</span>' % reais(it["venda"]))
    if it["locacao"] and modo != "v":
        partes.append('<span class="preco-l">%s <small>por mês</small></span>' % reais(it["locacao"]))
    return "".join(partes)


def foto(it, n=0, capa=False):
    if not it["fotos"]:
        return ""
    return "/assets/imoveis/%s/%s" % (it["codigo"], "c.webp" if capa else it["fotos"][n])


def card(it, modo="", h="h3"):
    alt = "%s, %s" % (it["titulo"], it["cidade"])
    if it["fotos"]:
        img = '<img src="%s" alt="%s" width="640" height="427" loading="lazy" decoding="async">' % (foto(it, capa=True), e(alt))
    else:
        img = '<div class="sem-foto"><span>Fotos sob consulta</span></div>'
    titulo = it["tipo"] + (" de " + plural(it["quartos"], "dormitório", "dormitórios") if it["quartos"] else "")
    lis = "".join("<li>%s</li>" % s for s in specs(it, curto=True))
    return (
        '<article class="card" data-card data-modo="{modo}" data-tipo="{tipo}" data-cidade="{cid}" '
        'data-bairro="{bai}" data-q="{q}" data-pv="{pv}" data-pl="{pl}" data-area="{ar}" data-num="{num}" '
        'data-lat="{lat}" data-lng="{lng}" data-titulo="{tit}">'
        '<a class="card-link" href="{url}">'
        '<div class="card-foto">{img}<span class="selo">{selo}</span></div>'
        '<div class="card-corpo"><p class="card-local">{bairro}, {cidade}</p>'
        '<{h} class="card-titulo">{titulo}</{h}><ul class="specs">{lis}</ul>'
        '<p class="card-preco">{preco}</p><p class="card-cod">Cód. {cod}</p></div></a></article>'
    ).format(modo=it["modo"], tipo=slug(it["tipo"]), cid=slug(it["cidade"]), bai=slug(it["bairro"]),
             q=it["quartos"], pv=int(it["venda"] or 0), pl=int(it["locacao"] or 0), ar=int(it["area"] or 0),
             num=it["num"], lat=it["lat"] or "", lng=it["lng"] or "", tit=e(it["titulo"]), url=it["url"],
             img=img, selo=selo(it), bairro=e(it["bairro"]), cidade=e(it["cidade"]), h=h, titulo=e(titulo),
             lis=lis, preco=preco_card(it, modo), cod=it["codigo"])


class Contexto:
    def __init__(self, itens):
        self.itens = itens
        self.venda = [i for i in itens if i["venda"]]
        self.locacao = [i for i in itens if i["locacao"]]
        self.por_cod = {i["codigo"]: i for i in itens}
        self.bairros = Counter((i["bairro"], i["cidade"]) for i in itens)
        self.tipos = Counter(i["tipo"] for i in itens)
        self.cidades = Counter(i["cidade"] for i in itens)
        self.financiaveis = [i for i in itens if i["financiavel"] and i["venda"]]


def titulo_seo(it):
    t = it["titulo"]
    if len(t) > 61:
        t = it["tipo"] + (" de " + plural(it["quartos"], "dormitório", "dormitórios") if it["quartos"] else "")
        t += " %s %s" % ("na" if re.match(r"(Vila|Cidade|Estância)\b", it["bairro"]) else "no", it["bairro"])
    t = t if len(t) > 61 else t + " | Aldeia"
    return t[:70]


def regua():
    return '<span class="regua" aria-hidden="true"></span>'


def cabecalho_secao(eyebrow, titulo, link=None, tag="h2"):
    acao = '<a class="ver-tudo" href="%s">%s</a>' % link if link else ""
    olho = '<p class="eyebrow">%s</p>' % e(eyebrow) if eyebrow else ""
    return '<div class="sec-cab reveal"><div>%s<%s class="sec-titulo">%s</%s>%s</div>%s</div>' % (
        olho, tag, titulo, tag, regua(), acao)


def formulario(assunto, mensagem="", titulo="Fale com a Aldeia", extra="", botao="Enviar mensagem", cod=""):
    return (
        '<form class="form" data-form data-assunto="{assunto}" data-cod="{cod}" novalidate>'
        '<h2 class="form-titulo">{titulo}</h2>'
        '<label>Nome<input type="text" name="nome" autocomplete="name" required></label>'
        '<label>Telefone<input type="tel" name="telefone" autocomplete="tel" inputmode="tel" required></label>'
        '<label>E-mail <span class="opc">opcional</span><input type="email" name="email" autocomplete="email"></label>'
        '{extra}'
        '<label>Mensagem<textarea name="mensagem" rows="4">{mensagem}</textarea></label>'
        '<button class="btn btn-cheio" type="submit" data-evento="Lead">{botao}</button>'
        '<p class="form-nota">Ao enviar, você concorda com a <a href="/privacidade/">política de privacidade</a>. '
        'A Aldeia responde no horário de atendimento: {horario_min}.</p>'
        '<p class="form-ok" data-form-ok hidden role="status"></p>'
        '</form>'
    ).format(assunto=e(assunto), cod=e(cod), titulo=e(titulo), extra=extra, mensagem=e(mensagem), botao=e(botao),
             horario_min="segunda a sexta, 9h às 12h e 13h30 às 17h")


def jsonld(obj):
    return '<script type="application/ld+json">%s</script>' % json.dumps(obj, ensure_ascii=False)


def ld_empresa():
    E = EMPRESA
    return {
        "@context": "https://schema.org", "@type": "RealEstateAgent", "@id": SITE_URL + "/#aldeia",
        "name": E["nome"], "legalName": E["razao"], "url": SITE_URL + "/",
        "image": SITE_URL + "/assets/marca/og.png",
        "logo": SITE_URL + "/assets/marca/aldeia-verde.png",
        "telephone": [E["tel1_link"], E["tel2_link"]], "email": E["email"],
        "identifier": {"@type": "PropertyValue", "name": "CRECI-SP", "value": E["creci"]},
        "address": {"@type": "PostalAddress", "streetAddress": E["rua"], "addressLocality": E["cidade"],
                    "addressRegion": E["uf"], "postalCode": E["cep"], "addressCountry": "BR"},
        "geo": {"@type": "GeoCoordinates", "latitude": E["lat"], "longitude": E["lng"]},
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
             "opens": "09:00", "closes": "12:00"},
            {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
             "opens": "13:30", "closes": "17:00"}],
        "areaServed": [{"@type": "City", "name": "Campinas"}],
        "knowsAbout": ["venda de imóveis", "locação de imóveis", "administração de imóveis"],
    }


def ld_migalhas(trilha):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": n, "name": nome, "item": SITE_URL + url}
                                for n, (nome, url) in enumerate(trilha, 1)]}


def migalhas(trilha):
    partes = []
    for nome, url in trilha[:-1]:
        partes.append('<a href="%s">%s</a>' % (url, e(nome)))
    partes.append('<span aria-current="page">%s</span>' % e(trilha[-1][0]))
    return '<nav class="migalhas" aria-label="Você está em">%s</nav>' % '<span class="sep" aria-hidden="true">/</span>'.join(partes)


def pagina(titulo, descricao, caminho, corpo, hero=False, pagina_id="", ld=None, attrs="", imagem=None,
           mapa=False, barra=None, indexavel=True):
    E = EMPRESA
    lds = [ld_empresa()] + (ld or [])
    robots = "index, follow" if (PUBLICADO and indexavel) else "noindex, nofollow"
    og_img = SITE_URL + (imagem or "/assets/marca/og.png")
    nav = "".join('<li><a href="%s"%s>%s</a></li>' % (u, ' aria-current="page"' if caminho.startswith(u) else "", e(n))
                  for n, u in MENU)
    leaflet_css = ('<link rel="stylesheet" href="/assets/vendor/leaflet.min.css">'
                   if mapa else "")
    leaflet_js = ('<script src="/assets/vendor/leaflet.min.js" defer></script>'
                  if mapa else "")
    if barra is None:
        barra = ('<a href="tel:{t}" data-evento="Contact" data-canal="telefone">Ligar</a>'
                 '<a href="/contato/" data-wa-troca data-evento="Contact" data-canal="mensagem">Mensagem</a>'
                 '<a href="/comprar/">Buscar imóvel</a>').format(t=E["tel1_link"])
    return """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
<meta name="description" content="{descricao}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="{nome}">
<meta property="og:title" content="{titulo}">
<meta property="og:description" content="{descricao}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og_img}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#2d5047">
<link rel="icon" href="/assets/marca/favicon.png" type="image/png">
<link rel="preload" href="/assets/fontes/playfair-display-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fontes/inter-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
{leaflet_css}
<link rel="stylesheet" href="/assets/css/site.css?v={v}">
<script>document.documentElement.className='js'</script>
{lds}
</head>
<body class="{classe}" data-pagina="{pid}"{attrs}>
<a class="pular" href="#conteudo">Pular para o conteúdo</a>
<div class="util">
  <div class="cont util-linha">
    <p class="util-end">{rua}, {bairro}, {cidade}</p>
    <p class="util-dir"><span>{horario}</span><a href="{boleto}" target="_blank" rel="noopener" data-evento="Boleto">2ª via de boleto</a></p>
  </div>
</div>
<header class="topo" data-topo>
  <div class="cont topo-linha">
    <a class="marca" href="/" aria-label="Aldeia Imóveis, página inicial"><img src="/assets/marca/aldeia-branco.png" alt="Aldeia Consultoria, Vendas e Administração de Imóveis, CRECI 3716-J" width="1020" height="366"></a>
    <nav class="menu" id="menu" aria-label="Principal"><ul>{nav}</ul>
      <div class="menu-extra"><a href="tel:{tel1_link}">{tel1}</a><a href="{boleto}" target="_blank" rel="noopener">2ª via de boleto</a></div>
    </nav>
    <a class="topo-tel" href="tel:{tel1_link}" data-evento="Contact" data-canal="telefone">{tel1}</a>
    <button class="menu-btn" type="button" aria-controls="menu" aria-expanded="false" data-menu-btn><span class="sr">Abrir menu</span><i></i><i></i><i></i></button>
  </div>
</header>
<main id="conteudo">
{corpo}
</main>
<footer class="rodape">
  <div class="cont rodape-grade">
    <div class="rodape-marca">
      <img src="/assets/marca/aldeia-branco.png" alt="Aldeia Imóveis" width="1020" height="366" loading="lazy">
      <p>{razao}</p>
      <p>CRECI {creci}</p>
    </div>
    <div>
      <p class="rodape-tit">Navegar</p>
      <ul><li><a href="/comprar/">Imóveis à venda</a></li><li><a href="/alugar/">Imóveis para alugar</a></li><li><a href="/imoveis/">Todos os imóveis no mapa</a></li><li><a href="/anunciar/">Anunciar imóvel</a></li><li><a href="/administracao/">Administração de imóveis</a></li><li><a href="/financiamento/">Financiamento</a></li><li><a href="/a-aldeia/">A Aldeia</a></li></ul>
    </div>
    <div>
      <p class="rodape-tit">Contato</p>
      <ul><li><a href="tel:{tel1_link}" data-evento="Contact" data-canal="telefone">{tel1}</a></li><li><a href="tel:{tel2_link}" data-evento="Contact" data-canal="telefone">{tel2}</a></li><li><a href="mailto:{email}" data-evento="Contact" data-canal="email">{email}</a></li><li><a href="{boleto}" target="_blank" rel="noopener">2ª via de boleto</a></li><li><a href="/contato/">Fale conosco</a></li></ul>
    </div>
    <div>
      <p class="rodape-tit">Onde estamos</p>
      <address>{rua}<br>{bairro}, {cidade}/{uf}<br>CEP {cep}<br>{referencia_cap}</address>
      <p class="rodape-hor">{horario}</p>
    </div>
  </div>
  <div class="cont rodape-fim">
    <p>© {ano} {razao} <a href="/privacidade/">Privacidade</a> <button type="button" class="link-btn" data-consent-abrir>Preferências de cookies</button></p>
    <a class="credito" href="https://blueshieldpro.com.br/" target="_blank" rel="noopener" aria-label="Site desenvolvido por BlueShieldPro, abre em nova aba"><span>Desenvolvido por</span><img src="/assets/marca/blueshieldpro.svg" alt="BlueShieldPro" width="236" height="56" loading="lazy"></a>
  </div>
</footer>
<nav class="barra-acao" aria-label="Contato rápido">{barra}</nav>
<div class="consent" data-consent hidden>
  <p>Usamos cookies de medição para saber quais imóveis são mais vistos. <a href="/privacidade/">Saiba mais</a></p>
  <div><button type="button" class="btn btn-linha btn-p" data-consent-nao>Recusar</button><button type="button" class="btn btn-cheio btn-p" data-consent-sim>Aceitar</button></div>
</div>
<script src="/assets/js/config.js?v={v}"></script>
<script src="/assets/js/medicao.js?v={v}" defer></script>
{leaflet_js}
<script src="/assets/js/site.js?v={v}" defer></script>
</body>
</html>
""".format(titulo=e(titulo), descricao=e(descricao), robots=robots, url=SITE_URL + caminho, nome=E["nome"],
           og_img=og_img, leaflet_css=leaflet_css, leaflet_js=leaflet_js, v=VERSAO,
           lds="\n".join(jsonld(x) for x in lds), classe="tem-hero" if hero else "sem-hero", pid=pagina_id,
           attrs=attrs, rua=E["rua"], bairro=E["bairro"], cidade=E["cidade"], uf=E["uf"], cep=E["cep"],
           horario=E["horario"], boleto=E["boleto"], nav=nav, tel1=E["tel1"], tel1_link=E["tel1_link"],
           tel2=E["tel2"], tel2_link=E["tel2_link"], email=E["email"], razao=E["razao"], creci=E["creci"],
           referencia_cap=E["referencia"].capitalize(), ano=2026, corpo=corpo, barra=barra)


def robots(producao=False):
    if not (producao or PUBLICADO):
        return ("# Demonstração. Nada aqui deve ser indexado.\n"
                "# A versão de produção está em /robots.producao.txt e entra quando o domínio do cliente for apontado.\n"
                "User-agent: *\nDisallow: /\n")
    bots = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User",
            "PerplexityBot", "Perplexity-User", "Google-Extended", "Applebot-Extended", "CCBot", "Bingbot"]
    linhas = ["# Aldeia Imóveis. Buscadores e assistentes de IA podem ler o site inteiro.", "User-agent: *", "Allow: /",
              "Disallow: /apresentacao/", ""]
    for b in bots:
        linhas += ["User-agent: " + b, "Allow: /", "Disallow: /apresentacao/", ""]
    linhas += ["Sitemap: %s/sitemap.xml" % SITE_URL, ""]
    return "\n".join(linhas)


def llms(ctx, completo=False):
    E = EMPRESA
    L = ["# Aldeia Imóveis", "",
         "> Imobiliária de Campinas/SP com %d anos de mercado. Vende, aluga e administra imóveis. "
         "Sede própria na %s, %s. CRECI %s." % (E["anos"], E["rua"], E["bairro"], E["creci"]), "",
         "## Fatos", "",
         "- Razão social: " + E["razao"],
         "- Endereço: %s, %s, %s/%s, CEP %s (%s)" % (E["rua"], E["bairro"], E["cidade"], E["uf"], E["cep"], E["referencia"]),
         "- Telefones: %s e %s" % (E["tel1"], E["tel2"]),
         "- E-mail: " + E["email"],
         "- Atendimento: " + E["horario"],
         "- Carteira publicada: %d imóveis (%d à venda, %d para alugar)" % (len(ctx.itens), len(ctx.venda), len(ctx.locacao)),
         "- Cidades com imóveis: " + ", ".join("%s (%d)" % c for c in ctx.cidades.most_common()),
         "- Bairros com mais imóveis: " + ", ".join("%s (%d)" % (b[0], n) for b, n in ctx.bairros.most_common(6)),
         "", "## Páginas", "",
         "- [Imóveis à venda](%s/comprar/): lista com filtro por tipo, bairro, dormitórios e preço" % SITE_URL,
         "- [Imóveis para alugar](%s/alugar/): lista de locação com valor mensal" % SITE_URL,
         "- [Todos os imóveis no mapa](%s/imoveis/)" % SITE_URL,
         "- [Anunciar imóvel](%s/anunciar/): para proprietários que querem vender ou alugar" % SITE_URL,
         "- [Administração de imóveis](%s/administracao/): locação, 2ª via de boleto e atendimento" % SITE_URL,
         "- [Financiamento](%s/financiamento/): simulador de parcelas SAC e Price" % SITE_URL,
         "- [A Aldeia](%s/a-aldeia/): quem é a imobiliária" % SITE_URL,
         "- [Contato](%s/contato/)" % SITE_URL,
         "- [Carteira em JSON](%s/imoveis.json): todos os imóveis com preço, área e descrição" % SITE_URL, ""]
    if completo:
        L += ["## Imóveis", ""]
        for it in ctx.itens:
            precos = []
            if it["venda"]:
                precos.append("venda " + reais(it["venda"]))
            if it["locacao"]:
                precos.append("locação %s por mês" % reais(it["locacao"]))
            L += ["### %s (cód. %s)" % (it["titulo"], it["codigo"]), "",
                  "- " + "; ".join(precos),
                  "- " + ", ".join(specs(it)) if specs(it) else "- " + it["tipo"],
                  "- Local: %s, %s%s" % (it["bairro"], it["cidade"], (" (" + it["rua"] + ")") if it["rua"] else ""),
                  "- Página: %s%s" % (SITE_URL, it["url"]), "", it["texto"]]
            if it["obs"]:
                L += ["", "Observação: " + it["obs"]]
            L += [""]
    else:
        L += ["## Mais", "", "- [Versão completa, com todos os imóveis](%s/llms-full.txt)" % SITE_URL, ""]
    return "\n".join(L)
