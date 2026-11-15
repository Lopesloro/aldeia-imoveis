"""Página interna da reunião: antes e depois, o que a Aldeia tem, o que falha, o que falta."""
from base import EMPRESA as E, e, regua, cabecalho_secao

FALHAS = [
    ("No celular a página estoura a largura", "Em tela de 390 px o card corta a foto e o preço. Quem chega pelo telefone não consegue ler o anúncio."),
    ("Há um imóvel de teste publicado", "O código APA00340, em Caraguatatuba, tem a descrição \"teste\", metragem zerada e nenhum preço."),
    ("Um aluguel de R$ 7.000 está sem descrição", "No APA00326, no Guanabara, o campo de apresentação é \"NNMMKKOO\" e não há fotos."),
    ("Um anúncio promete entrega em novembro de 2019", "O CAS00160 ainda fala em obra e chaves com sete anos de atraso em relação ao texto."),
    ("A mesma sala aparece duas vezes", "SAL0044 e SAL0074 são a sala da Rua José de Alencar, 293, com valores de condomínio diferentes."),
    ("O texto institucional está cortado", "A lista de serviços termina em \"Advocacia pr\", no meio da palavra."),
    ("A página de financiamento está vazia", "Só existe o título \"Simuladores de Financiamento\". Nenhum link, nenhum simulador."),
    ("O Google não recebe mapa do site", "robots.txt e sitemap.xml respondem erro 404. O título das páginas começa com um hífen solto."),
    ("Nenhuma medição instalada", "Sem Pixel da Meta, sem Google Analytics, sem Tag Manager. Não dá para saber qual imóvel é mais visto nem de onde vem o contato."),
    ("Não há WhatsApp", "Os canais são telefone fixo, e-mail e um chat próprio. Nenhum botão leva para o WhatsApp."),
    ("As descrições estão em caixa alta", "55 dos 57 anúncios, com valores de IPTU de 2020 a 2024 misturados ao texto."),
    ("35 imóveis não têm endereço", "O campo de localização está vazio. No mapa, eles não aparecem no lugar certo."),
    ("Campos preenchidos errado", "Sala comercial com \"1 dormitório\", terreno com \"2 vagas\", casa comercial com \"10 dormitórios\"."),
    ("A paginação não tem fim", "O endereço /index/page/778/ responde como se existisse. Para o Google, é conteúdo duplicado sem limite."),
    ("Bibliotecas de 2012", "O site roda jQuery 1.8.3 e chama scripts por http://, sem correção de segurança há mais de dez anos."),
    ("A Aldeia não aparece fora do próprio site", "Busca pelo nome, endereço e CRECI não devolve nenhuma página da imobiliária em portais ou diretórios."),
]

MANTIDO = [
    "O logo, o verde da marca e o CRECI 3716-J em toda página.",
    "As frases da casa: \"Caminhos e destinos\" e \"Fazemos nossos caminhos e lhes chamamos destino\".",
    "A busca por negócio, tipo, cidade, bairro, dormitórios, preço e código do imóvel.",
    "Os imóveis no mapa.",
    "A 2ª via de boleto, no mesmo sistema (imo7), sem mudar nada para o inquilino.",
    "Telefones, e-mail, endereço e horário de atendimento.",
]

NOVO = [
    "Funciona no celular: menu, busca, fotos e formulário em tela de 390 px.",
    "55 descrições reescritas, uma a uma, só com o que já estava no anúncio.",
    "Página para o proprietário que quer vender ou alugar, que hoje não existe.",
    "Página de administração de locação, com o boleto a um toque.",
    "Simulador de financiamento SAC e Price, com link para os bancos.",
    "Formulário em toda ficha de imóvel, já com o código preenchido.",
    "Espaço pronto para Pixel da Meta, Google Analytics e Tag Manager, com aviso de cookies conforme a LGPD.",
    "Dados estruturados para Google e assistentes de IA: imobiliária, cada imóvel, perguntas frequentes.",
    "sitemap.xml, robots.txt, llms.txt e a carteira em JSON.",
]

PENDENTE = [
    ("Número de WhatsApp de atendimento", "O botão já existe no código. Entra no ar assim que o número for informado."),
    ("Texto completo do institucional", "O que vem depois de \"Advocacia pr\"."),
    ("Ano de fundação", "O site diz 42 anos. Precisamos do ano para não envelhecer o texto."),
    ("Logo em arquivo vetorial", "O logo usado foi recortado de uma imagem de 163 px de altura. Em tela grande ele perde nitidez."),
    ("Regras da administração", "Garantias aceitas, repasse e o que está incluído. A página nova só afirma o que os anúncios já dizem."),
    ("Fotos da fachada e da equipe", "Para substituir o vídeo de abertura por imagens da própria Aldeia."),
    ("Foto de Campinas do cabeçalho, em alta", "A vista da cidade ao entardecer que abre o site atual tem 163 px de altura. Com o arquivo original ela volta para a página inicial."),
    ("Decisão sobre quatro anúncios", "APA00340 (teste), APA00326 (sem descrição), CAS00160 (obra de 2019) e a sala duplicada."),
    ("Acesso à exportação do imo7", "Para a carteira atualizar sozinha, sem digitar duas vezes."),
]


def _par(rotulo, antes, depois, alt):
    return ('<div class="ad"><p class="eyebrow">%s</p><div class="ad-grade">'
            '<figure><img src="/assets/apresentacao/%s" alt="Antes: %s" loading="lazy" width="1440" height="900"><figcaption>Antes</figcaption></figure>'
            '<figure><img src="/assets/apresentacao/%s" alt="Depois: %s" loading="lazy" width="1440" height="900"><figcaption>Depois</figcaption></figure>'
            '</div></div>') % (rotulo, antes, alt, depois, alt)


def corpo_apresentacao(ctx):
    falhas = "".join("<tr><th scope=\"row\">%d</th><td><strong>%s</strong><span>%s</span></td></tr>" % (n, e(t), e(d))
                     for n, (t, d) in enumerate(FALHAS, 1))
    pend = "".join("<li><strong>%s</strong>%s</li>" % (e(t), e(d)) for t, d in PENDENTE)
    return """
<section class="lista-topo">
  <div class="cont">
    <p class="eyebrow">Documento da reunião, não aparece no menu nem no Google</p>
    <h1 class="pg-titulo">O site da Aldeia, antes e depois</h1>
    <p class="lead">O site atual foi lido página por página em 15 de novembro de 2026: {n_bruto} imóveis, quatro páginas institucionais, mapa e busca. Abaixo está o que ele tem, o que falha e o que a versão nova resolve.</p>
  </div>
</section>
<section class="sec sec-lista">
  <div class="cont">
    {p1}{p2}{p3}
  </div>
</section>
<section class="sec sec-alt">
  <div class="cont duas">
    <div class="duas-txt">
      <p class="eyebrow">Da Aldeia</p>
      <h2 class="sec-titulo">O que já existia e continua</h2>
      {regua}
      <ul class="check">{mantido}</ul>
    </div>
    <div class="duas-txt">
      <p class="eyebrow">Da versão nova</p>
      <h2 class="sec-titulo">O que entrou</h2>
      {regua}
      <ul class="check">{novo}</ul>
    </div>
  </div>
</section>
<section class="sec">
  <div class="cont estreito">
    {cab_f}
    <table class="tabela"><caption class="sr">Falhas do site atual</caption><tbody>{falhas}</tbody></table>
  </div>
</section>
<section class="sec sec-alt">
  <div class="cont duas">
    <div class="duas-txt">
      <p class="eyebrow">A dúvida que ficou</p>
      <h2 class="sec-titulo">E a hospedagem que está com outra pessoa?</h2>
      {regua}
      <p>Nada no site atual foi tocado. A versão nova roda em outro endereço, em paralelo, e o site de hoje segue no ar do jeito que está.</p>
      <p>A troca só acontece quando a Aldeia aprovar. Nesse dia, o domínio aldeia.com.br passa a apontar para o site novo. É uma mudança de DNS, feita por quem tem acesso ao registro do domínio, e pode ser desfeita.</p>
      <p>O boleto continua no imo7, no mesmo link. O inquilino não percebe diferença.</p>
    </div>
    <div class="duas-txt">
      <p class="eyebrow">Para fechar</p>
      <h2 class="sec-titulo">O que só a Aldeia pode informar</h2>
      {regua}
      <ul class="lista-fatos">{pend}</ul>
    </div>
  </div>
</section>
<section class="sec">
  <div class="cont estreito">
    {cab_c}
    <p>Os imóveis desta versão foram copiados do site atual em 15 de novembro de 2026. Imóvel vendido ou alugado depois dessa data ainda aparece aqui.</p>
    <p>Dois anúncios ficaram de fora: o de teste (APA00340) e a sala repetida (SAL0044). Os outros {n} estão publicados com as fotos da própria Aldeia, até oito por imóvel.</p>
    <p>O site está fechado para o Google enquanto for demonstração. A abertura para buscadores e assistentes de IA já está escrita e entra junto com o domínio.</p>
  </div>
</section>
""".format(n_bruto=len(ctx.itens) + 2, n=len(ctx.itens), regua=regua(),
           p1=_par("Página inicial no computador", "antes-home.webp", "depois-home.webp", "página inicial"),
           p2=_par("Página inicial no celular", "antes-celular.webp", "depois-celular.webp", "página inicial no celular"),
           p3=_par("Ficha de imóvel", "antes-imovel.webp", "depois-imovel.webp", "ficha do apartamento APA00345"),
           mantido="".join("<li>%s</li>" % e(x) for x in MANTIDO), novo="".join("<li>%s</li>" % e(x) for x in NOVO),
           cab_f=cabecalho_secao("Diagnóstico", "%d falhas do site atual" % len(FALHAS)), falhas=falhas, pend=pend,
           cab_c=cabecalho_secao("Limites", "O que esta demonstração ainda não é"))
