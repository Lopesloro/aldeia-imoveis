"""Construtores de página. Cada função devolve o HTML completo."""
import json
from base import (EMPRESA as E, SITE_URL, e, slug, reais, area, plural, specs, selo, foto, card, regua,
                  cabecalho_secao, formulario, pagina, migalhas, ld_migalhas, titulo_seo)


def _opcoes(pares, vazio):
    return '<option value="">%s</option>' % vazio + "".join('<option value="%s">%s</option>' % (v, e(n)) for v, n in pares)


def _op_tipos(itens):
    tipos = sorted({i["tipo"] for i in itens})
    return _opcoes([(slug(t), t) for t in tipos], "Todos os tipos")


def _op_bairros(itens):
    cidades = {}
    for i in itens:
        cidades.setdefault(i["cidade"], set()).add(i["bairro"])
    out = '<option value="">Todos os bairros</option>'
    for cid in sorted(cidades, key=lambda c: (c != "Campinas", c)):
        out += '<optgroup label="%s">' % e(cid)
        out += "".join('<option value="%s">%s</option>' % (slug(b), e(b)) for b in sorted(cidades[cid]))
        out += "</optgroup>"
    return out


OP_QUARTOS = _opcoes([("1", "1 ou mais"), ("2", "2 ou mais"), ("3", "3 ou mais"), ("4", "4 ou mais")], "Dormitórios")


# ---------------------------------------------------------------- home
def pg_home(ctx):
    nv, nl, nt = len(ctx.venda), len(ctx.locacao), len(ctx.itens)
    destaque_v = [i for i in ctx.venda if i["fotos"]][:9]
    destaque_l = sorted((i for i in ctx.locacao if i["fotos"]), key=lambda i: (i["comercial"], -i["locacao"]))[:6]
    top = ctx.bairros.most_common(5)

    def painel(rotulo, numero, linha, img):
        return ('<div class="prova-painel" style="background-image:url(%s)"><div><p class="eyebrow">%s</p>'
                '<p class="prova-num">%s</p><p class="prova-linha">%s</p></div></div>') % (img, rotulo, numero, linha)

    mosaico = ""
    for n, ((bairro, cidade), qtd) in enumerate(top):
        cands = sorted((i for i in ctx.itens if i["bairro"] == bairro and i["fotos"]), key=lambda i: (i["comercial"], -(i["venda"] or 0)))
        ex = cands[0] if cands else None
        mosaico += ('<a class="mos mos-%d" href="/imoveis/?bairro=%s"><img src="%s" alt="Imóvel no bairro %s, %s" loading="lazy" '
                    'width="1200" height="800"><span class="mos-txt"><strong>%s</strong><em>%s</em></span></a>') % (
            n + 1, slug(bairro), foto(ex) if ex else "", e(bairro), e(cidade),
            e(bairro), plural(qtd, "imóvel disponível", "imóveis disponíveis"))

    def servico(titulo, linha, url, cod):
        it = ctx.por_cod.get(cod)
        return ('<a class="serv" href="%s"><img src="%s" alt="%s" loading="lazy" width="1200" height="800">'
                '<span class="serv-txt"><strong>%s</strong><em>%s</em></span></a>') % (
            url, foto(it) if it else "", e(it["titulo"]) if it else "", titulo, linha)

    corpo = """
<section class="hero" aria-label="Busca de imóveis">
  <video class="hero-midia" autoplay muted loop playsinline preload="metadata" poster="/assets/video/hero.webp" aria-hidden="true">
    <source src="/assets/video/hero-m.mp4" type="video/mp4" media="(max-width: 860px)">
    <source src="/assets/video/hero.mp4" type="video/mp4">
  </video>
  <div class="hero-veu"></div>
  <div class="cont hero-txt">
    <h1 class="hero-h1">Imóveis em Campinas,<br>há {anos} anos</h1>
    <p class="hero-sub">A Aldeia vende, aluga e administra imóveis a partir da sede própria no Castelo.</p>
    <form class="busca" action="/comprar/" method="get" data-busca>
      <div class="busca-abas" role="tablist" aria-label="O que você procura">
        <button type="button" role="tab" aria-selected="true" data-aba="/comprar/">Comprar</button>
        <button type="button" role="tab" aria-selected="false" data-aba="/alugar/">Alugar</button>
      </div>
      <div class="busca-campos">
        <label><span class="sr">Tipo de imóvel</span><select name="tipo">{op_tipos}</select></label>
        <label><span class="sr">Bairro</span><select name="bairro">{op_bairros}</select></label>
        <label><span class="sr">Dormitórios</span><select name="quartos">{op_quartos}</select></label>
        <button class="btn btn-cheio" type="submit">Buscar</button>
      </div>
    </form>
  </div>
  <a class="hero-seta" href="#prova" aria-label="Ver mais"><i></i></a>
</section>

<section class="prova" id="prova" aria-label="A Aldeia em números">
  {p1}{p2}{p3}
</section>

<section class="sec">
  <div class="cont">
    {cab_v}
  </div>
  <div class="trilho" data-trilho>
    <div class="trilho-faixa" data-trilho-faixa>{cards_v}</div>
    <div class="cont trilho-nav"><button type="button" class="seta-btn" data-trilho-ant aria-label="Imóveis anteriores"><i class="seta seta-e"></i></button><button type="button" class="seta-btn" data-trilho-prox aria-label="Próximos imóveis"><i class="seta seta-d"></i></button></div>
  </div>
</section>

<section class="sec sec-alt">
  <div class="cont duas">
    <figure class="duas-foto"><img src="{foto_qs}" alt="Casa de tijolo à vista no Jardim Chapadão com a placa de aluga-se da Aldeia no portão" width="1200" height="800" loading="lazy"></figure>
    <div class="duas-txt reveal">
      <p class="eyebrow">Quem somos</p>
      <h2 class="sec-titulo">{anos} anos no mesmo bairro</h2>
      {regua}
      <p>A Aldeia atende em sede própria na Av. Dr. Alberto Sarmento, 684, perto do Balão do Castelo. É dali que saem as visitas, os contratos e a administração dos imóveis alugados.</p>
      <p>A maior parte da carteira fica a poucos minutos da sede: {b1} e {b2} somam {nb} dos {nt} imóveis publicados hoje.</p>
      <p>A empresa também trabalha com lançamento de edifícios residenciais e comerciais. O registro no CRECI é o {creci}.</p>
      <a class="btn btn-linha" href="/a-aldeia/">Conhecer a Aldeia</a>
    </div>
  </div>
</section>

<section class="sec">
  <div class="cont">
    {cab_s}
    <div class="servs">{s1}{s2}{s3}</div>
  </div>
</section>

<section class="citacao">
  <div class="cont">
    <p class="eyebrow">Caminhos e destinos</p>
    <blockquote>Fazemos nossos caminhos e lhes chamamos destino.</blockquote>
  </div>
</section>

<section class="sec sec-alt">
  <div class="cont">
    {cab_l}
    <div class="grade">{cards_l}</div>
  </div>
</section>

<section class="sec">
  <div class="cont">
    {cab_b}
    <div class="mosaico">{mosaico}</div>
  </div>
</section>

<section class="objecao">
  <video class="objecao-midia" autoplay muted loop playsinline preload="none" poster="/assets/video/predio.webp" aria-hidden="true"><source src="/assets/video/predio.mp4" type="video/mp4"></video>
  <div class="hero-veu"></div>
  <div class="cont objecao-txt">
    <h2>Não achou o que procurava?</h2>
    <p>Nem todo imóvel está no site. Diga o bairro, o tipo e o valor que cabe no seu orçamento, e um corretor da Aldeia procura para você.</p>
    <a class="btn btn-claro" href="/contato/?assunto=procuro">Pedir uma busca</a>
  </div>
</section>

<section class="sec">
  <div class="cont dono">
    <div class="reveal">
      <p class="eyebrow">Para proprietários</p>
      <h2 class="sec-titulo">Tem imóvel para vender ou alugar em Campinas?</h2>
      {regua}
      <p>A Aldeia anuncia, agenda e acompanha as visitas e cuida do contrato. Na locação, administra o imóvel e emite os boletos do aluguel.</p>
    </div>
    <div class="dono-acoes"><a class="btn btn-cheio" href="/anunciar/">Anunciar meu imóvel</a><a class="btn btn-linha" href="/administracao/">Como funciona a administração</a></div>
  </div>
</section>
""".format(
        anos=E["anos"], foto_qs=foto(ctx.por_cod["CAS00229"]), op_tipos=_op_tipos(ctx.itens), op_bairros=_op_bairros(ctx.itens), op_quartos=OP_QUARTOS,
        p1=painel("Tempo de mercado", "%d anos" % E["anos"], "de mercado imobiliário em Campinas", foto(ctx.por_cod["APA00227"])),
        p2=painel("Carteira de hoje", plural(nt, "imóvel", "imóveis"), "%d à venda e %d para alugar" % (nv, nl), foto(ctx.por_cod["APA00282"])),
        p3=painel("Registro profissional", "CRECI " + E["creci"], "sede própria no Castelo", foto(ctx.por_cod["BAR00321"])),
        cab_v=cabecalho_secao("À venda", "Imóveis à venda em Campinas e região", ("/comprar/", "Ver os %d imóveis" % nv)),
        cards_v="".join(card(i, "v") for i in destaque_v),
        regua=regua(), b1=top[0][0][0], b2=top[1][0][0], nb=top[0][1] + top[1][1], nt=nt, creci=E["creci"],
        cab_s=cabecalho_secao("O que a Aldeia faz", "Três formas de começar"),
        s1=servico("Comprar", "%d imóveis à venda" % nv, "/comprar/", "APA00282"),
        s2=servico("Alugar", "%d imóveis para locação" % nl, "/alugar/", "CAS00229"),
        s3=servico("Anunciar", "Venda ou alugue com a Aldeia", "/anunciar/", "BAR00321"),
        cab_l=cabecalho_secao("Para alugar", "Locação com administração da Aldeia", ("/alugar/", "Ver os %d imóveis" % nl)),
        cards_l="".join(card(i, "l") for i in destaque_l),
        cab_b=cabecalho_secao("Por bairro", "Onde a Aldeia tem mais imóveis", ("/imoveis/", "Ver todos no mapa")),
        mosaico=mosaico)
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": E["nome"], "url": SITE_URL + "/", "inLanguage": "pt-BR",
           "potentialAction": {"@type": "SearchAction", "target": SITE_URL + "/imoveis/?codigo={search_term_string}",
                               "query-input": "required name=search_term_string"}}]
    return pagina("Aldeia Imóveis | Venda, locação e administração em Campinas",
                  "Imobiliária em Campinas há %d anos, com sede própria no Castelo. %d imóveis à venda e %d para alugar. CRECI %s." % (E["anos"], nv, nl, E["creci"]),
                  "/", corpo, hero=True, pagina_id="home", ld=ld)


# ---------------------------------------------------------------- listagem
def pg_listagem(ctx, modo):
    if modo == "v":
        itens, caminho, h1 = ctx.venda, "/comprar/", "Imóveis à venda"
        desc = "%d imóveis à venda em Campinas e região com a Aldeia: apartamentos, casas, salas e terrenos. Filtre por bairro, tipo e preço." % len(itens)
        titulo = "Imóveis à venda em Campinas | Aldeia Imóveis"
    elif modo == "l":
        itens, caminho, h1 = ctx.locacao, "/alugar/", "Imóveis para alugar"
        desc = "%d imóveis para alugar em Campinas com administração da Aldeia. Veja valor do aluguel, condomínio e IPTU de cada um." % len(itens)
        titulo = "Imóveis para alugar em Campinas | Aldeia Imóveis"
    else:
        itens, caminho, h1 = ctx.itens, "/imoveis/", "Todos os imóveis"
        desc = "Os %d imóveis da Aldeia no mapa de Campinas e região, à venda e para alugar." % len(itens)
        titulo = "Todos os imóveis no mapa | Aldeia Imóveis"
    faixas_v = [("200000", "até R$ 200 mil"), ("300000", "até R$ 300 mil"), ("500000", "até R$ 500 mil"),
                ("800000", "até R$ 800 mil"), ("1000000", "até R$ 1 milhão"), ("1500000", "até R$ 1,5 milhão")]
    faixas_l = [("1500", "até R$ 1.500"), ("2500", "até R$ 2.500"), ("5000", "até R$ 5.000"), ("12000", "até R$ 12.000")]
    transacao = ""
    if not modo:
        transacao = '<label><span>Negócio</span><select name="modo"><option value="">Venda e locação</option><option value="v">Venda</option><option value="l">Locação</option></select></label>'
        preco = ""
    else:
        preco = '<label><span>Valor</span><select name="preco">%s</select></label>' % _opcoes(faixas_v if modo == "v" else faixas_l, "Qualquer valor")
    ordem = [("recente", "Mais recentes"), ("menor", "Menor valor"), ("maior", "Maior valor"), ("area", "Maior área")]
    mapa = ""
    if not modo:
        mapa = ('<div class="mapa-bloco"><div id="mapa" class="mapa" data-mapa-lista role="region" aria-label="Mapa com os imóveis"></div>'
                '<p class="nota">Imóvel sem endereço publicado aparece no centro do bairro.</p></div>')
    abas = "".join('<a href="%s"%s>%s</a>' % (u, ' aria-current="page"' if u == caminho else "", n)
                   for n, u in (("Comprar", "/comprar/"), ("Alugar", "/alugar/"), ("Todos no mapa", "/imoveis/")))
    corpo = """
<section class="lista-topo">
  <div class="cont">
    {migalhas}
    <div class="lista-cab">
      <h1 class="pg-titulo">{h1} <span class="contagem" data-contagem>{n}</span></h1>
      <nav class="abas" aria-label="Tipo de negócio">{abas}</nav>
    </div>
    <form class="filtros" data-filtros data-modo="{modo}" aria-label="Filtros">
      {transacao}
      <label><span>Tipo</span><select name="tipo">{op_tipos}</select></label>
      <label><span>Bairro</span><select name="bairro">{op_bairros}</select></label>
      <label><span>Dormitórios</span><select name="quartos">{op_quartos}</select></label>
      {preco}
      <label><span>Código</span><input type="search" name="codigo" placeholder="Ex.: APA00345" autocomplete="off"></label>
      <label><span>Ordenar</span><select name="ordem">{ordem}</select></label>
      <button type="reset" class="link-btn" data-limpar>Limpar filtros</button>
    </form>
  </div>
</section>
<section class="sec sec-lista">
  <div class="cont">
    {mapa}
    <div class="grade" data-grade>{cards}</div>
    <div class="vazio" data-vazio hidden>
      <h2>Nenhum imóvel com esses filtros</h2>
      <p>A carteira muda toda semana e nem tudo está publicado. Diga o que procura e um corretor da Aldeia retorna no horário de atendimento.</p>
      <a class="btn btn-cheio" href="/contato/?assunto=procuro">Pedir uma busca</a>
    </div>
    <aside class="legit">
      <p><strong>{razao}</strong> CRECI {creci}</p>
      <p>{rua}, {bairro}, {cidade}/{uf}. {horario}.</p>
    </aside>
  </div>
</section>
""".format(migalhas=migalhas([("Início", "/"), (h1, caminho)]), h1=h1, n=len(itens), abas=abas, modo=modo,
           transacao=transacao, op_tipos=_op_tipos(itens), op_bairros=_op_bairros(itens), op_quartos=OP_QUARTOS.replace("Dormitórios", "Qualquer"),
           preco=preco, ordem="".join('<option value="%s">%s</option>' % o for o in ordem), mapa=mapa,
           cards="".join(card(i, modo, h="h2") for i in itens), razao=E["razao"], creci=E["creci"], rua=E["rua"],
           bairro=E["bairro"], cidade=E["cidade"], uf=E["uf"], horario=E["horario"])
    ld = [ld_migalhas([("Início", "/"), (h1, caminho)]),
          {"@context": "https://schema.org", "@type": "ItemList", "name": h1, "numberOfItems": len(itens),
           "itemListElement": [{"@type": "ListItem", "position": n, "url": SITE_URL + i["url"], "name": i["titulo"]}
                               for n, i in enumerate(itens, 1)]}]
    return pagina(titulo, desc, caminho, corpo, pagina_id="lista", ld=ld, mapa=not modo)


# ---------------------------------------------------------------- ficha
def pg_ficha(ctx, it):
    negocio = {"v": "à venda", "l": "para alugar", "vl": "à venda ou para alugar"}[it["modo"]]
    h1 = "%s, %s" % (it["titulo"], negocio) if it["cidade"] != "Campinas" else "%s, Campinas, %s" % (it["titulo"], negocio)
    lista = ("Imóveis à venda", "/comprar/") if it["venda"] else ("Imóveis para alugar", "/alugar/")
    trilha = [("Início", "/"), lista, ("%s %s" % (it["tipo"], it["codigo"]), it["url"])]
    alt_base = "%s, %s, %s" % (it["tipo"], it["bairro"], it["cidade"])
    if it["fotos"]:
        principal = '<button type="button" class="gal-principal" data-gal-abrir="0"><img src="%s" alt="%s, foto 1 de %d" width="1200" height="800" fetchpriority="high" data-gal-img></button>' % (
            foto(it, 0), e(alt_base), len(it["fotos"]))
        minis = "".join('<button type="button" class="gal-mini" data-gal-ir="%d"%s><img src="%s" alt="%s, foto %d" width="1200" height="800" loading="lazy"></button>' % (
            n, ' aria-current="true"' if n == 0 else "", foto(it, n), e(alt_base), n + 1) for n in range(len(it["fotos"])))
        galeria = '<div class="gal" data-galeria data-fotos=\'%s\'>%s<div class="gal-minis">%s</div></div>' % (
            json.dumps([foto(it, n) for n in range(len(it["fotos"]))]), principal, minis)
    else:
        galeria = '<div class="gal" data-galeria data-fotos="[]"><div class="sem-foto sem-foto-g"><span>As fotos deste imóvel ainda não foram publicadas. Peça pelo formulário ao lado.</span></div></div>'

    valores = ""
    if it["venda"]:
        valores += '<div class="valor valor-p"><dt>Venda</dt><dd>%s</dd></div>' % reais(it["venda"])
    if it["locacao"]:
        valores += '<div class="valor valor-p"><dt>Aluguel</dt><dd>%s <small>por mês</small></dd></div>' % reais(it["locacao"])
    if it["condominio"]:
        valores += '<div class="valor"><dt>Condomínio</dt><dd>%s</dd></div>' % reais(it["condominio"], True)
    if it["iptu"]:
        valores += '<div class="valor"><dt>IPTU informado</dt><dd>%s</dd></div>' % reais(it["iptu"], True)
    ficha = "".join("<li>%s</li>" % s for s in specs(it))
    obs = '<div class="obs"><p class="eyebrow">Importante</p><p>%s</p></div>' % e(it["obs"]) if it["obs"] else ""
    local = "%s, %s, %s" % (it["rua"], it["bairro"], it["cidade"]) if it["rua"] else "%s, %s" % (it["bairro"], it["cidade"])
    nota_mapa = {"rua": "Posição pelo endereço do anúncio.", "bairro": "Posição aproximada: centro do bairro. Peça o endereço à Aldeia.",
                 "cidade": "Posição aproximada: a cidade. Peça o endereço à Aldeia."}.get(it["precisao"], "")
    mapa = ""
    if it["lat"]:
        mapa = '<div id="mapa" class="mapa mapa-ficha" data-mapa-ponto data-lat="%s" data-lng="%s" data-zoom="%d" data-rotulo="%s"></div><p class="nota">%s</p>' % (
            it["lat"], it["lng"], 16 if it["precisao"] == "rua" else 14 if it["precisao"] == "bairro" else 12, e(it["titulo"]), nota_mapa)
    simular = ""
    if it["venda"]:
        simular = '<a class="btn btn-linha" href="/financiamento/?valor=%d">Simular financiamento</a>' % it["venda"]
    chave = "venda" if it["venda"] else "locacao"
    parecidos = [i for i in ctx.itens if i["codigo"] != it["codigo"] and i["fotos"] and i[chave]]
    parecidos.sort(key=lambda i: (i["tipo"] != it["tipo"], i["bairro"] != it["bairro"], abs(i[chave] - it[chave])))
    msg = "Olá. Quero saber mais sobre o imóvel código %s (%s). Podem me retornar?" % (it["codigo"], it["titulo"])
    corpo = """
<article class="ficha">
  <div class="cont">
    {migalhas}
    {galeria}
    <div class="ficha-grade">
      <div class="ficha-main">
        <p class="eyebrow">{selo} <span class="cod">Cód. {cod}</span></p>
        <h1 class="pg-titulo">{h1}</h1>
        {regua}
        <p class="ficha-local">{local}</p>
        <dl class="valores">{valores}</dl>
        <ul class="specs specs-g">{ficha}</ul>
        <h2 class="sub">Sobre o imóvel</h2>
        <p class="ficha-texto">{texto}</p>
        {obs}
        <div class="ficha-acoes">{simular}<a class="btn btn-linha" href="tel:{tel}" data-evento="Contact" data-canal="telefone">Ligar {tel_txt}</a></div>
        <h2 class="sub">Localização</h2>
        <p class="ficha-local">{local}</p>
        {mapa}
      </div>
      <aside class="ficha-lado" id="interesse">
        {form}
        <div class="lado-info"><p><strong>Visitas com agendamento.</strong> {horario}.</p><p>CRECI {creci}</p></div>
      </aside>
    </div>
  </div>
</article>
<section class="sec sec-alt">
  <div class="cont">
    {cab}
    <div class="grade">{parecidos}</div>
  </div>
</section>
""".format(migalhas=migalhas(trilha), galeria=galeria, selo=selo(it), cod=it["codigo"], h1=e(h1), regua=regua(),
           local=e(local), valores=valores, ficha=ficha, texto=e(it["texto"]), obs=obs, simular=simular,
           tel=E["tel1_link"], tel_txt=E["tel1"], mapa=mapa,
           form=formulario("Interesse no imóvel " + it["codigo"], msg, titulo="Quero visitar este imóvel", botao="Tenho interesse", cod=it["codigo"]),
           horario=E["horario"], creci=E["creci"],
           cab=cabecalho_secao("Parecidos", "Outros imóveis para comparar", (lista[1], "Ver a lista completa")),
           parecidos="".join(card(i, "v" if it["venda"] else "l") for i in parecidos[:3]))
    ofertas = []
    if it["venda"]:
        ofertas.append({"@type": "Offer", "price": it["venda"], "priceCurrency": "BRL", "availability": "https://schema.org/InStock",
                        "businessFunction": "http://purl.org/goodrelations/v1#Sell", "seller": {"@id": SITE_URL + "/#aldeia"}})
    if it["locacao"]:
        ofertas.append({"@type": "Offer", "price": it["locacao"], "priceCurrency": "BRL", "availability": "https://schema.org/InStock",
                        "businessFunction": "http://purl.org/goodrelations/v1#LeaseOut", "seller": {"@id": SITE_URL + "/#aldeia"},
                        "priceSpecification": {"@type": "UnitPriceSpecification", "price": it["locacao"], "priceCurrency": "BRL", "unitText": "MON"}})
    sobre = {"@type": "Apartment" if it["tipo"] in ("Apartamento", "Kitnet") else "House" if it["tipo"].startswith(("Casa", "Sobrado", "Chácara")) and not it["comercial"] else "Place",
             "name": it["titulo"],
             "address": {"@type": "PostalAddress", "streetAddress": it["rua"] or None, "addressLocality": it["cidade"], "addressRegion": "SP", "addressCountry": "BR"}}
    sobre["address"] = {k: v for k, v in sobre["address"].items() if v}
    if it["area"]:
        sobre["floorSize"] = {"@type": "QuantitativeValue", "value": it["area"], "unitCode": "MTK"}
    if it["quartos"]:
        sobre["numberOfBedrooms"] = it["quartos"]
    if it["banheiros"]:
        sobre["numberOfBathroomsTotal"] = it["banheiros"]
    if it["lat"] and it["precisao"] == "rua":
        sobre["geo"] = {"@type": "GeoCoordinates", "latitude": it["lat"], "longitude": it["lng"]}
    ld = [ld_migalhas(trilha),
          {"@context": "https://schema.org", "@type": "RealEstateListing", "name": h1, "url": SITE_URL + it["url"],
           "description": it["texto"], "identifier": it["codigo"],
           "image": [SITE_URL + foto(it, n) for n in range(len(it["fotos"]))] or None,
           "offers": ofertas, "about": sobre, "provider": {"@id": SITE_URL + "/#aldeia"}}]
    ld[1] = {k: v for k, v in ld[1].items() if v}
    desc = "%s. %s" % (h1, it["texto"])
    desc = desc if len(desc) <= 158 else desc[:155].rsplit(" ", 1)[0] + "..."
    attrs = ' data-imovel="%s" data-valor="%d" data-tipo-imovel="%s"' % (it["codigo"], it["venda"] or it["locacao"] or 0, e(it["tipo"]))
    barra = ('<a href="tel:%s" data-evento="Contact" data-canal="telefone">Ligar</a><a href="#interesse" class="barra-forte">Tenho interesse</a>' % E["tel1_link"])
    return pagina(titulo_seo(it), desc, it["url"], corpo, pagina_id="ficha", ld=ld, attrs=attrs,
                  imagem=foto(it, 0) or None, mapa=bool(it["lat"]), barra=barra)


# ---------------------------------------------------------------- páginas de serviço
def _hero_pg(eyebrow, h1, sub, img=None, video=None, alt=""):
    if video:
        midia = '<video class="hero-midia" autoplay muted loop playsinline preload="metadata" poster="/assets/video/%s.webp" aria-hidden="true"><source src="/assets/video/%s.mp4" type="video/mp4"></video>' % (video, video)
    else:
        midia = '<img class="hero-midia" src="%s" alt="%s" width="1200" height="800" fetchpriority="high">' % (img, e(alt))
    return ('<section class="hero hero-pg">%s<div class="hero-veu"></div><div class="cont hero-txt"><p class="eyebrow">%s</p>'
            '<h1 class="hero-h1">%s</h1><p class="hero-sub">%s</p></div></section>') % (midia, eyebrow, h1, sub)


def _faq(pares):
    itens = "".join('<details class="faq-item"><summary>%s</summary><p>%s</p></details>' % (e(p), r) for p, r in pares)
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": p, "acceptedAnswer": {"@type": "Answer", "text": _sem_tags(r)}} for p, r in pares]}
    return '<div class="faq">%s</div>' % itens, ld


def _sem_tags(s):
    import re
    return re.sub(r"<[^>]+>", "", s)


def pg_anunciar(ctx):
    it = ctx.por_cod["BAR00321"]
    extra = ('<label>O que você quer fazer<select name="finalidade"><option>Vender</option><option>Alugar</option><option>Vender ou alugar</option></select></label>'
             '<label>Tipo do imóvel<input type="text" name="tipo" placeholder="Apartamento, casa, sala, terreno"></label>'
             '<label>Bairro e cidade<input type="text" name="bairro"></label>')
    faq, ld_faq = _faq([
        ("Em quais cidades a Aldeia anuncia?", "A maior parte da carteira fica em Campinas. Hoje o site também tem imóveis em %s." % ", ".join(c for c in ctx.cidades if c != "Campinas")),
        ("Quem acompanha as visitas?", "As visitas são agendadas e acompanhadas pela Aldeia, de segunda a sexta, no horário de atendimento."),
        ("Posso anunciar para venda e para locação ao mesmo tempo?", "Pode. Hoje a carteira tem %d imóveis anunciados nas duas modalidades." % len([i for i in ctx.itens if i["modo"] == "vl"])),
        ("Meu imóvel está alugado. Dá para vender assim?", "Dá. O anúncio informa que o imóvel está locado, e a visita é combinada com o inquilino."),
    ])
    corpo = _hero_pg("Para proprietários", "Venda ou alugue seu imóvel com a Aldeia",
                     "Você conta sobre o imóvel. A Aldeia anuncia, agenda as visitas e cuida do contrato.", img=foto(it),
                     alt="Barracão no Jardim do Trevo com a placa da Aldeia na fachada") + """
<section class="sec">
  <div class="cont duas duas-form">
    <div class="duas-txt">
      <p class="eyebrow">Como funciona</p>
      <h2 class="sec-titulo">Do primeiro contato ao contrato</h2>
      {regua}
      <ol class="passos">
        <li><strong>Você descreve o imóvel.</strong> Pelo formulário, por telefone ou na sede, no Castelo.</li>
        <li><strong>A Aldeia publica o anúncio.</strong> Com fotos, metragem, valor de condomínio e IPTU, e a situação da documentação.</li>
        <li><strong>As visitas são agendadas.</strong> Um corretor acompanha cada interessado, de segunda a sexta.</li>
        <li><strong>A proposta chega até você.</strong> Venda, permuta ou locação: a decisão é sua.</li>
        <li><strong>O contrato sai pela Aldeia.</strong> Na locação, o imóvel passa a ser administrado pela imobiliária.</li>
      </ol>
      <h2 class="sub">O que ajuda a vender mais rápido</h2>
      <p>Os anúncios da carteira que informam documentação pronta para financiamento e FGTS são {nfin} hoje. Quem compra financiado filtra por isso. Se a sua escritura e o seu IPTU estão em ordem, diga no formulário.</p>
      <h2 class="sub">Perguntas de quem anuncia</h2>
      {faq}
    </div>
    <aside class="ficha-lado">{form}</aside>
  </div>
</section>
""".format(regua=regua(), nfin=len(ctx.financiaveis), faq=faq,
           form=formulario("Quero anunciar meu imóvel", "", titulo="Conte sobre o seu imóvel", extra=extra, botao="Enviar para avaliação"))
    return pagina("Anunciar imóvel em Campinas | Aldeia Imóveis",
                  "Venda ou alugue seu imóvel em Campinas com a Aldeia, imobiliária com %d anos de mercado e sede própria no Castelo. CRECI %s." % (E["anos"], E["creci"]),
                  "/anunciar/", corpo, hero=True, pagina_id="anunciar", ld=[ld_faq, ld_migalhas([("Início", "/"), ("Anunciar imóvel", "/anunciar/")])])


def pg_administracao(ctx):
    faq, ld_faq = _faq([
        ("Como emito a 2ª via do boleto do aluguel?", 'Pelo sistema de boletos da Aldeia: <a href="%s" target="_blank" rel="noopener">abrir a 2ª via de boleto</a>. Se o boleto não aparecer, ligue para %s.' % (E["boleto"], E["tel1"])),
        ("Qual é o horário de atendimento da locação?", "%s. Não há expediente aos sábados, domingos e feriados." % E["horario"]),
        ("Que garantia é pedida para alugar?", "Depende do imóvel. Nos anúncios que informam a garantia, o pedido é fiador pessoa física com imóvel quitado e registrado em Campinas ou na Região Metropolitana de Campinas. Confirme a do imóvel que você escolheu."),
        ("Onde entrego documentos e assino o contrato?", "Na sede da Aldeia: %s, %s, %s." % (E["rua"], E["bairro"], E["referencia"])),
    ])
    corpo = _hero_pg("Administração de imóveis", "Seu imóvel alugado, administrado no Castelo",
                     "A Aldeia cuida da locação a partir da sede própria, com boleto do aluguel emitido pelo sistema da imobiliária.", video="predio") + """
<section class="sec">
  <div class="cont duas">
    <div class="duas-txt reveal">
      <p class="eyebrow">Para quem é dono</p>
      <h2 class="sec-titulo">Você entrega a chave, a Aldeia cuida do resto</h2>
      {regua}
      <p>A administração começa no anúncio e segue depois do contrato assinado. A Aldeia divulga o imóvel, agenda e acompanha as visitas, confere a garantia do inquilino e emite a cobrança mensal.</p>
      <p>Hoje são {nl} imóveis para locação na carteira, entre apartamentos, casas, salas comerciais e um barracão.</p>
      <a class="btn btn-cheio" href="/anunciar/">Colocar meu imóvel para alugar</a>
    </div>
    <div class="duas-txt bloco-escuro">
      <p class="eyebrow">Para quem aluga</p>
      <h2 class="sec-titulo">Boleto, visita e contrato</h2>
      {regua}
      <p>A 2ª via do boleto fica disponível online, a qualquer hora. Visitas e assinatura de contrato acontecem de segunda a sexta.</p>
      <a class="btn btn-claro" href="{boleto}" target="_blank" rel="noopener" data-evento="Boleto">Emitir 2ª via de boleto</a>
      <a class="btn btn-linha-clara" href="/alugar/">Ver imóveis para alugar</a>
    </div>
  </div>
</section>
<section class="sec sec-alt">
  <div class="cont estreito">
    {cab}
    {faq}
  </div>
</section>
""".format(regua=regua(), nl=len(ctx.locacao), boleto=E["boleto"], cab=cabecalho_secao("Dúvidas", "Perguntas sobre locação"), faq=faq)
    return pagina("Administração de imóveis em Campinas | Aldeia Imóveis",
                  "Administração de locação em Campinas com a Aldeia: anúncio, visitas, contrato e boleto do aluguel. 2ª via de boleto online. CRECI %s." % E["creci"],
                  "/administracao/", corpo, hero=True, pagina_id="administracao", ld=[ld_faq, ld_migalhas([("Início", "/"), ("Administração", "/administracao/")])])


def pg_financiamento(ctx):
    bancos = [("Caixa Econômica Federal", "https://www.caixa.gov.br/voce/habitacao/simulador/Paginas/default.aspx"),
              ("Banco do Brasil", "https://www.bb.com.br/site/pra-voce/financiamentos/financiamento-imobiliario/"),
              ("Bradesco", "https://banco.bradesco/html/classic/produtos-servicos/emprestimo-e-financiamento/imoveis/index.shtm")]
    lista = "".join('<li><a href="%s" target="_blank" rel="noopener" data-evento="Simulador" data-canal="%s">%s</a></li>' % (u, e(n), e(n)) for n, u in bancos)
    faq, ld_faq = _faq([
        ("Qual a diferença entre SAC e Price?", "No SAC a amortização é fixa e a parcela cai todo mês. Na Price a parcela é igual do começo ao fim, mas o total de juros pago é maior."),
        ("O simulador inclui seguros e taxas?", "Não. O cálculo considera só amortização e juros. Seguro, taxa de administração e correção monetária mudam de banco para banco e entram na proposta oficial."),
        ("Todo imóvel pode ser financiado?", "Não. Depende da documentação. Na carteira da Aldeia, %d imóveis à venda informam documentação pronta para financiamento, e os que não podem ser financiados trazem o aviso no anúncio." % len(ctx.financiaveis)),
    ])
    corpo = """
<section class="lista-topo">
  <div class="cont">
    {migalhas}
    <h1 class="pg-titulo">Simulador de financiamento</h1>
    <p class="lead">Veja quanto fica a parcela antes de visitar. O cálculo é uma estimativa: a proposta oficial é do banco.</p>
  </div>
</section>
<section class="sec sec-lista">
  <div class="cont duas duas-form">
    <form class="form sim" data-sim novalidate>
      <h2 class="form-titulo">Dados do financiamento</h2>
      <label>Valor do imóvel (R$)<input type="text" name="valor" inputmode="numeric" value="500.000"></label>
      <label>Entrada (R$)<input type="text" name="entrada" inputmode="numeric" value="100.000"></label>
      <label>Prazo (anos)<input type="number" name="prazo" min="1" max="35" value="30"></label>
      <label>Juros ao ano (%)<input type="text" name="juros" inputmode="decimal" value="10,5"></label>
      <button class="btn btn-cheio" type="submit" data-evento="Simulacao">Calcular parcelas</button>
      <p class="form-nota">A taxa de 10,5% ao ano é só um ponto de partida. Troque pela taxa que o seu banco informar.</p>
    </form>
    <div class="sim-res" data-sim-res aria-live="polite">
      <h2 class="form-titulo">Resultado</h2>
      <div class="sim-grade">
        <div><p class="eyebrow">Tabela SAC</p><p class="sim-num" data-sac-1></p><p class="nota">primeira parcela</p><p class="sim-num sim-num-p" data-sac-n></p><p class="nota">última parcela</p><p class="nota" data-sac-t></p></div>
        <div><p class="eyebrow">Tabela Price</p><p class="sim-num" data-price-1></p><p class="nota">parcela fixa</p><p class="nota" data-price-t></p></div>
      </div>
      <p class="nota" data-sim-fin></p>
      <a class="btn btn-linha" href="/comprar/" data-sim-link>Ver imóveis nesse valor</a>
    </div>
  </div>
</section>
<section class="sec sec-alt">
  <div class="cont duas">
    <div class="duas-txt">
      <p class="eyebrow">Simuladores oficiais</p>
      <h2 class="sec-titulo">Confirme no banco</h2>
      {regua}
      <p>Cada banco tem taxa, prazo e regra de entrada próprios. Estes são os simuladores oficiais:</p>
      <ul class="links">{lista}</ul>
    </div>
    <div class="duas-txt">
      <p class="eyebrow">Na carteira</p>
      <h2 class="sec-titulo">{nfin} imóveis com documentação pronta</h2>
      {regua}
      <p>São os anúncios em que a Aldeia já informa documentação em ordem para financiamento, e em vários casos também para uso do FGTS.</p>
      <a class="btn btn-cheio" href="/comprar/">Ver imóveis à venda</a>
    </div>
  </div>
</section>
<section class="sec">
  <div class="cont estreito">
    {cab}
    {faq}
  </div>
</section>
""".format(migalhas=migalhas([("Início", "/"), ("Financiamento", "/financiamento/")]), regua=regua(), lista=lista,
           nfin=len(ctx.financiaveis), cab=cabecalho_secao("Dúvidas", "Antes de financiar"), faq=faq)
    return pagina("Simulador de financiamento imobiliário | Aldeia Imóveis",
                  "Simule parcelas nas tabelas SAC e Price e veja os imóveis da Aldeia com documentação pronta para financiamento em Campinas.",
                  "/financiamento/", corpo, pagina_id="financiamento", ld=[ld_faq, ld_migalhas([("Início", "/"), ("Financiamento", "/financiamento/")])])


def pg_sobre(ctx):
    top = ctx.bairros.most_common(2)
    corpo = _hero_pg("A Aldeia", "%d anos de mercado imobiliário em Campinas" % E["anos"],
                     "Consultoria, vendas e administração de imóveis, com sede própria no Castelo.",
                     video="hero") + """
<section class="sec">
  <div class="cont duas">
    <div class="duas-txt reveal">
      <p class="eyebrow">Quem somos</p>
      <h2 class="sec-titulo">Uma imobiliária de bairro, no sentido bom</h2>
      {regua}
      <p>A {razao} está no mercado imobiliário há {anos} anos. O endereço é a {rua}, {referencia}, em imóvel próprio.</p>
      <p>Estar no mesmo lugar há tanto tempo aparece na carteira: {b1} e {b2}, os dois bairros vizinhos da sede, somam {nb} dos {nt} imóveis publicados.</p>
      <p>O registro no Conselho Regional de Corretores de Imóveis é o CRECI {creci}, de pessoa jurídica.</p>
    </div>
    <div class="duas-txt bloco-alt">
      <p class="eyebrow">O que a Aldeia faz</p>
      <ul class="lista-fatos">
        <li><strong>Venda de imóveis</strong>Apartamentos, casas, salas, terrenos e chácaras. {nv} anúncios hoje.</li>
        <li><strong>Locação e administração</strong>{nl} imóveis para alugar, com boleto emitido pela imobiliária.</li>
        <li><strong>Lançamentos</strong>Edifícios de apartamentos residenciais e comerciais.</li>
        <li><strong>Sede própria</strong>Atendimento presencial no Castelo, de segunda a sexta.</li>
      </ul>
    </div>
  </div>
</section>
<section class="citacao">
  <div class="cont">
    <p class="eyebrow">Caminhos e destinos</p>
    <blockquote>Fazemos nossos caminhos e lhes chamamos destino.</blockquote>
  </div>
</section>
<section class="sec sec-alt">
  <div class="cont duas">
    <div class="duas-txt">
      <p class="eyebrow">Onde estamos</p>
      <h2 class="sec-titulo">{rua}</h2>
      {regua}
      <p>{bairro}, {cidade}/{uf}, CEP {cep}. Fica {referencia}.</p>
      <p>{horario}.</p>
      <p><a href="tel:{t1l}">{t1}</a> e <a href="tel:{t2l}">{t2}</a></p>
      <a class="btn btn-cheio" href="/contato/">Falar com a Aldeia</a>
    </div>
    <div id="mapa" class="mapa" data-mapa-ponto data-lat="{lat}" data-lng="{lng}" data-zoom="16" data-rotulo="Aldeia Imóveis"></div>
  </div>
</section>
""".format(regua=regua(), razao=E["razao"], anos=E["anos"], rua=E["rua"], referencia=E["referencia"], b1=top[0][0][0],
           b2=top[1][0][0], nb=top[0][1] + top[1][1], nt=len(ctx.itens), creci=E["creci"], nv=len(ctx.venda),
           nl=len(ctx.locacao), bairro=E["bairro"], cidade=E["cidade"], uf=E["uf"], cep=E["cep"], horario=E["horario"],
           t1=E["tel1"], t1l=E["tel1_link"], t2=E["tel2"], t2l=E["tel2_link"], lat=E["lat"], lng=E["lng"])
    ld = [ld_migalhas([("Início", "/"), ("A Aldeia", "/a-aldeia/")]),
          {"@context": "https://schema.org", "@type": "AboutPage", "name": "A Aldeia", "url": SITE_URL + "/a-aldeia/", "about": {"@id": SITE_URL + "/#aldeia"}}]
    return pagina("A Aldeia: imobiliária em Campinas há %d anos" % E["anos"],
                  "Conheça a Aldeia: %d anos de mercado imobiliário em Campinas, sede própria no Castelo, venda, locação e administração de imóveis. CRECI %s." % (E["anos"], E["creci"]),
                  "/a-aldeia/", corpo, hero=True, pagina_id="sobre", ld=ld, mapa=True)


def pg_contato(ctx):
    extra = ('<label>Assunto<select name="assunto_sel" data-assunto-sel><option value="duvida">Dúvida sobre um imóvel</option>'
             '<option value="procuro">Procuro um imóvel que não está no site</option><option value="anunciar">Quero anunciar meu imóvel</option>'
             '<option value="locacao">Sou inquilino ou proprietário da Aldeia</option></select></label>')
    corpo = """
<section class="lista-topo">
  <div class="cont">
    {migalhas}
    <h1 class="pg-titulo">Fale com a Aldeia</h1>
    <p class="lead">Atendimento de segunda a sexta, das 9h às 12h e das 13h30 às 17h, por telefone, e-mail ou na sede.</p>
  </div>
</section>
<section class="sec sec-lista">
  <div class="cont duas duas-form">
    <div class="duas-txt">
      <ul class="lista-fatos">
        <li><strong>Telefone</strong><a href="tel:{t1l}" data-evento="Contact" data-canal="telefone">{t1}</a> e <a href="tel:{t2l}" data-evento="Contact" data-canal="telefone">{t2}</a></li>
        <li><strong>E-mail</strong><a href="mailto:{email}" data-evento="Contact" data-canal="email">{email}</a></li>
        <li><strong>Endereço</strong>{rua}, {bairro}, {cidade}/{uf}, CEP {cep}. Fica {referencia}.</li>
        <li><strong>Boleto do aluguel</strong><a href="{boleto}" target="_blank" rel="noopener" data-evento="Boleto">Emitir 2ª via</a></li>
      </ul>
      <div id="mapa" class="mapa" data-mapa-ponto data-lat="{lat}" data-lng="{lng}" data-zoom="16" data-rotulo="Aldeia Imóveis"></div>
      <a class="btn btn-linha" href="https://www.google.com/maps/dir/?api=1&amp;destination={lat},{lng}" target="_blank" rel="noopener" data-evento="Rota">Traçar rota até a sede</a>
    </div>
    <aside class="ficha-lado">{form}</aside>
  </div>
</section>
""".format(migalhas=migalhas([("Início", "/"), ("Contato", "/contato/")]), t1=E["tel1"], t1l=E["tel1_link"], t2=E["tel2"],
           t2l=E["tel2_link"], email=E["email"], rua=E["rua"], bairro=E["bairro"], cidade=E["cidade"], uf=E["uf"],
           cep=E["cep"], referencia=E["referencia"], boleto=E["boleto"], lat=E["lat"], lng=E["lng"],
           form=formulario("Contato pelo site", "", titulo="Envie uma mensagem", extra=extra))
    ld = [ld_migalhas([("Início", "/"), ("Contato", "/contato/")]),
          {"@context": "https://schema.org", "@type": "ContactPage", "name": "Contato", "url": SITE_URL + "/contato/", "about": {"@id": SITE_URL + "/#aldeia"}}]
    return pagina("Contato | Aldeia Imóveis, Castelo, Campinas",
                  "Telefones, e-mail, endereço e horário da Aldeia Imóveis em Campinas: %s, %s. %s." % (E["rua"], E["bairro"], E["tel1"]),
                  "/contato/", corpo, pagina_id="contato", ld=ld, mapa=True)


def pg_privacidade(ctx):
    corpo = """
<section class="lista-topo">
  <div class="cont estreito">
    {migalhas}
    <h1 class="pg-titulo">Política de privacidade</h1>
    <p class="lead">O que este site coleta, para quê e como pedir a exclusão.</p>
  </div>
</section>
<section class="sec sec-lista">
  <div class="cont estreito prosa">
    <h2 class="sub">Quem responde pelos dados</h2>
    <p>{razao}, CRECI {creci}, com sede na {rua}, {bairro}, {cidade}/{uf}. Contato: <a href="mailto:{email}">{email}</a> ou {t1}.</p>
    <h2 class="sub">O que é coletado</h2>
    <p>Nos formulários: nome, telefone, e-mail (se você informar) e a mensagem. Esses dados servem para a Aldeia responder ao seu pedido e não são vendidos nem repassados a terceiros.</p>
    <p>Na navegação: se você aceitar os cookies de medição, o site registra páginas vistas, buscas feitas e cliques em telefone e formulário. Se recusar, nada disso é registrado e o site funciona do mesmo jeito.</p>
    <h2 class="sub">Ferramentas de medição</h2>
    <p>Quando ativadas pela Aldeia, as ferramentas usadas são o Google Analytics, o Google Tag Manager e o Pixel da Meta. Elas só carregam depois do seu aceite. Você pode mudar a escolha a qualquer momento no link "Preferências de cookies", no rodapé.</p>
    <h2 class="sub">Seus direitos</h2>
    <p>Pela Lei Geral de Proteção de Dados (Lei 13.709/2018), você pode pedir acesso, correção ou exclusão dos seus dados. Escreva para <a href="mailto:{email}">{email}</a>.</p>
    <h2 class="sub">Mapas</h2>
    <p>Os mapas usam dados do OpenStreetMap. Ao abrir uma página com mapa, seu navegador baixa as imagens do mapa direto dos servidores do OpenStreetMap.</p>
  </div>
</section>
""".format(migalhas=migalhas([("Início", "/"), ("Privacidade", "/privacidade/")]), razao=E["razao"], creci=E["creci"],
           rua=E["rua"], bairro=E["bairro"], cidade=E["cidade"], uf=E["uf"], email=E["email"], t1=E["tel1"])
    return pagina("Política de privacidade | Aldeia Imóveis",
                  "Como o site da Aldeia Imóveis trata os dados enviados nos formulários e os cookies de medição, conforme a LGPD.",
                  "/privacidade/", corpo, pagina_id="privacidade")


def pg_404(ctx):
    corpo = """
<section class="lista-topo erro">
  <div class="cont estreito">
    <p class="eyebrow">Erro 404</p>
    <h1 class="pg-titulo">Esta página não existe mais</h1>
    <p class="lead">O imóvel pode ter sido vendido ou alugado. A carteira atual está nas listas abaixo.</p>
    <div class="dono-acoes"><a class="btn btn-cheio" href="/comprar/">Imóveis à venda</a><a class="btn btn-linha" href="/alugar/">Imóveis para alugar</a></div>
  </div>
</section>
"""
    return pagina("Página não encontrada | Aldeia Imóveis", "Página não encontrada no site da Aldeia Imóveis.", "/404.html", corpo, pagina_id="404", indexavel=False)


# ---------------------------------------------------------------- apresentação (reunião)
def pg_apresentacao(ctx):
    from apresentacao import corpo_apresentacao
    return pagina("Antes e depois | Site da Aldeia Imóveis",
                  "Comparação entre o site atual da Aldeia e a nova versão, com o que foi mantido, o que foi corrigido e o que falta.",
                  "/apresentacao/", corpo_apresentacao(ctx), pagina_id="apresentacao", indexavel=False)
