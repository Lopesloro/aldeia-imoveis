/* Comportamento do site da Aldeia. Sem dependências, exceto Leaflet nas páginas com mapa. */
(function () {
  'use strict';
  var C = window.ALDEIA || {};
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var evento = function (n, d) { if (window.aldeiaEvento) window.aldeiaEvento(n, d); };
  var brl = function (v) { return 'R$ ' + Math.round(v).toLocaleString('pt-BR'); };

  /* topo: transparente sobre o hero, sólido depois de 80px */
  var topo = $('[data-topo]');
  if (topo) {
    var aoRolar = function () { topo.classList.toggle('solido', window.scrollY > 80); };
    aoRolar(); window.addEventListener('scroll', aoRolar, { passive: true });
  }

  /* menu do celular */
  var btn = $('[data-menu-btn]'), menu = $('#menu');
  if (btn && menu) {
    var alternar = function (abrir) {
      menu.classList.toggle('aberto', abrir);
      btn.setAttribute('aria-expanded', String(abrir));
      btn.querySelector('.sr').textContent = abrir ? 'Fechar menu' : 'Abrir menu';
      document.documentElement.style.overflow = abrir ? 'hidden' : '';
    };
    btn.addEventListener('click', function () { alternar(!menu.classList.contains('aberto')); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') alternar(false); });
    menu.addEventListener('click', function (e) { if (e.target.closest('a')) alternar(false); });
  }

  /* entrada das seções */
  var alvos = $$('.reveal');
  if ('IntersectionObserver' in window && alvos.length) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { threshold: 0.18 });
    alvos.forEach(function (a) { io.observe(a); });
  } else { alvos.forEach(function (a) { a.classList.add('in'); }); }

  /* WhatsApp: só aparece se houver número em config.js */
  function linkWa(texto) { return 'https://wa.me/' + C.whatsapp + '?text=' + encodeURIComponent(texto); }
  if (C.whatsapp) {
    $$('[data-wa-troca]').forEach(function (a) {
      a.textContent = 'WhatsApp'; a.href = linkWa('Olá. Vim pelo site da Aldeia.'); a.target = '_blank'; a.rel = 'noopener';
      a.setAttribute('data-canal', 'whatsapp');
    });
  }

  /* busca do hero */
  var busca = $('[data-busca]');
  if (busca) {
    $$('[data-aba]', busca).forEach(function (b) {
      b.addEventListener('click', function () {
        $$('[data-aba]', busca).forEach(function (o) { o.setAttribute('aria-selected', String(o === b)); });
        busca.action = b.getAttribute('data-aba');
      });
    });
    busca.addEventListener('submit', function () {
      $$('select', busca).forEach(function (s) { s.disabled = !s.value; }); // não polui a URL com campos vazios
      setTimeout(function () { $$('select', busca).forEach(function (s) { s.disabled = false; }); }, 400);
    });
  }

  /* trilho horizontal */
  $$('[data-trilho]').forEach(function (t) {
    var faixa = $('[data-trilho-faixa]', t);
    var passo = function (dir) { faixa.scrollBy({ left: dir * (faixa.clientWidth * 0.8), behavior: 'smooth' }); };
    var a = $('[data-trilho-ant]', t), p = $('[data-trilho-prox]', t);
    if (a) a.addEventListener('click', function () { passo(-1); });
    if (p) p.addEventListener('click', function () { passo(1); });
  });

  /* mapa (Leaflet) */
  var mapaLista = null, camada = null;
  function criarMapa(el, lat, lng, zoom) {
    if (!window.L) return null;
    var m = L.map(el, { scrollWheelZoom: false }).setView([lat, lng], zoom);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(m);
    return m;
  }
  function pino(lat, lng) {
    return L.circleMarker([lat, lng], { radius: 9, color: '#fff', weight: 2, fillColor: '#2d5047', fillOpacity: 1 });
  }
  function iniciarMapas() {
    $$('[data-mapa-ponto]').forEach(function (el) {
      var lat = Number(el.dataset.lat), lng = Number(el.dataset.lng);
      var m = criarMapa(el, lat, lng, Number(el.dataset.zoom) || 15);
      if (m) pino(lat, lng).addTo(m).bindPopup(el.dataset.rotulo || '');
    });
    var el = $('[data-mapa-lista]');
    if (el) {
      mapaLista = criarMapa(el, -22.9, -47.06, 12);
      if (mapaLista) { camada = L.layerGroup().addTo(mapaLista); desenharPinos(); }
    }
  }
  function desenharPinos() {
    if (!mapaLista || !camada) return;
    camada.clearLayers();
    var pts = [], vistos = {};
    $$('[data-card]').forEach(function (c) {
      if (c.hidden || !c.dataset.lat) return;
      var lat = Number(c.dataset.lat), lng = Number(c.dataset.lng), k = lat + ',' + lng;
      // imóveis no mesmo ponto (centro do bairro) são afastados alguns metros para não se esconderem
      vistos[k] = (vistos[k] || 0) + 1;
      if (vistos[k] > 1) { var ang = vistos[k] * 1.3; lat += 0.0012 * Math.sin(ang) * Math.sqrt(vistos[k]); lng += 0.0012 * Math.cos(ang) * Math.sqrt(vistos[k]); }
      var a = c.querySelector('a');
      var preco = c.querySelector('.card-preco');
      pino(lat, lng).addTo(camada).bindPopup('<div class="pino-txt"><a href="' + a.getAttribute('href') + '">' +
        c.dataset.titulo + '</a><br>' + (preco ? preco.textContent : '') + '</div>');
      pts.push([lat, lng]);
    });
    if (pts.length) mapaLista.fitBounds(pts, { padding: [36, 36], maxZoom: 15 });
  }
  if (document.readyState === 'complete') iniciarMapas(); else window.addEventListener('load', iniciarMapas);

  /* filtros da listagem */
  var form = $('[data-filtros]'), grade = $('[data-grade]');
  if (form && grade) {
    var cards = $$('[data-card]', grade), fixo = form.dataset.modo, vazio = $('[data-vazio]'), cont = $('[data-contagem]');
    var campo = function (n) { return form.elements[n]; };
    var q = new URLSearchParams(location.search);
    ['modo', 'tipo', 'bairro', 'quartos', 'preco', 'codigo', 'ordem'].forEach(function (n) {
      if (campo(n) && q.get(n)) campo(n).value = q.get(n);
    });
    var primeira = true;
    var aplicar = function () {
      var modo = fixo || (campo('modo') ? campo('modo').value : '');
      var f = { tipo: campo('tipo').value, bairro: campo('bairro').value, quartos: Number(campo('quartos').value) || 0,
        preco: campo('preco') ? Number(campo('preco').value) || 0 : 0,
        codigo: (campo('codigo').value || '').trim().toLowerCase().replace(/[^a-z0-9]/g, ''), ordem: campo('ordem').value };
      var valor = function (c) { return Number(modo === 'l' ? c.dataset.pl : c.dataset.pv) || Number(c.dataset.pv) || Number(c.dataset.pl); };
      var n = 0;
      cards.forEach(function (c) {
        var ok = (!modo || c.dataset.modo.indexOf(modo) > -1) && (!f.tipo || c.dataset.tipo === f.tipo) &&
          (!f.bairro || c.dataset.bairro === f.bairro) && (!f.quartos || Number(c.dataset.q) >= f.quartos) &&
          (!f.preco || (valor(c) && valor(c) <= f.preco)) &&
          (!f.codigo || ('' + c.dataset.num).indexOf(f.codigo.replace(/\D/g, '') || 'x') > -1 || c.querySelector('.card-cod').textContent.toLowerCase().replace(/[^a-z0-9]/g, '').indexOf(f.codigo) > -1);
        c.hidden = !ok; if (ok) n++;
      });
      var ordenar = { recente: function (a, b) { return b.dataset.num - a.dataset.num; },
        menor: function (a, b) { return valor(a) - valor(b); }, maior: function (a, b) { return valor(b) - valor(a); },
        area: function (a, b) { return b.dataset.area - a.dataset.area; } }[f.ordem] || null;
      if (ordenar) cards.slice().sort(ordenar).forEach(function (c) { grade.appendChild(c); });
      if (cont) cont.textContent = n;
      if (vazio) vazio.hidden = n > 0;
      grade.hidden = n === 0;
      var p = new URLSearchParams();
      Object.keys(f).forEach(function (k) { if (f[k] && !(k === 'ordem' && f[k] === 'recente')) p.set(k, k === 'codigo' ? campo('codigo').value.trim() : f[k]); });
      if (!fixo && modo) p.set('modo', modo);
      history.replaceState(null, '', location.pathname + (p.toString() ? '?' + p : ''));
      desenharPinos();
      if (!primeira || p.toString()) evento('Search', { search_string: p.toString(), resultados: n, content_category: modo === 'l' ? 'locacao' : modo === 'v' ? 'venda' : 'todos' });
      primeira = false;
    };
    form.addEventListener('change', aplicar);
    form.addEventListener('input', function (e) { if (e.target.name === 'codigo') aplicar(); });
    form.addEventListener('submit', function (e) { e.preventDefault(); aplicar(); });
    form.addEventListener('reset', function () { setTimeout(aplicar, 0); });
    aplicar();
  }

  /* galeria da ficha */
  var gal = $('[data-galeria]');
  if (gal) {
    var fotos = []; try { fotos = JSON.parse(gal.dataset.fotos || '[]'); } catch (e) {}
    var img = $('[data-gal-img]', gal), atual = 0, luz = null;
    var ir = function (n) {
      if (!fotos.length) return;
      atual = (n + fotos.length) % fotos.length;
      if (img) { img.src = fotos[atual]; img.alt = img.alt.replace(/foto \d+/, 'foto ' + (atual + 1)); }
      $$('[data-gal-ir]', gal).forEach(function (m, i) { if (i === atual) m.setAttribute('aria-current', 'true'); else m.removeAttribute('aria-current'); });
      if (luz) { $('img', luz).src = fotos[atual]; $('[data-luz-n]', luz).textContent = (atual + 1) + ' de ' + fotos.length; }
    };
    var fechar = function () { if (luz) { luz.remove(); luz = null; document.documentElement.style.overflow = ''; var b = $('[data-gal-abrir]', gal); if (b) b.focus(); } };
    var abrir = function () {
      if (!fotos.length || luz) return;
      luz = document.createElement('div'); luz.className = 'luz'; luz.setAttribute('role', 'dialog'); luz.setAttribute('aria-modal', 'true'); luz.setAttribute('aria-label', 'Fotos do imóvel');
      luz.innerHTML = '<div class="luz-topo"><span data-luz-n></span><button type="button" data-luz-x>Fechar</button></div>' +
        '<div class="luz-palco"><img alt="Foto ampliada do imóvel"></div>' +
        '<div class="luz-base"><button type="button" data-luz-a>Anterior</button><button type="button" data-luz-p>Próxima</button></div>';
      document.body.appendChild(luz); document.documentElement.style.overflow = 'hidden';
      $('[data-luz-x]', luz).addEventListener('click', fechar);
      $('[data-luz-a]', luz).addEventListener('click', function () { ir(atual - 1); });
      $('[data-luz-p]', luz).addEventListener('click', function () { ir(atual + 1); });
      var x0 = null;
      luz.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
      luz.addEventListener('touchend', function (e) { if (x0 === null) return; var d = e.changedTouches[0].clientX - x0; if (Math.abs(d) > 48) ir(atual + (d < 0 ? 1 : -1)); x0 = null; });
      ir(atual); $('[data-luz-x]', luz).focus();
    };
    gal.addEventListener('click', function (e) {
      var m = e.target.closest('[data-gal-ir]'); if (m) return ir(Number(m.dataset.galIr));
      if (e.target.closest('[data-gal-abrir]')) abrir();
    });
    document.addEventListener('keydown', function (e) {
      if (!luz) return;
      if (e.key === 'Escape') fechar(); else if (e.key === 'ArrowRight') ir(atual + 1); else if (e.key === 'ArrowLeft') ir(atual - 1);
    });
  }

  /* formulários: validam, registram o Lead e abrem WhatsApp, endpoint próprio ou e-mail */
  var qs = new URLSearchParams(location.search);
  $$('[data-form]').forEach(function (f) {
    var sel = $('[data-assunto-sel]', f);
    if (sel && qs.get('assunto')) sel.value = qs.get('assunto');
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var ok = true, saida = $('[data-form-ok]', f);
      $$('[required]', f).forEach(function (c) {
        var bom = c.value.trim().length >= (c.name === 'telefone' ? 8 : 2);
        c.setAttribute('aria-invalid', String(!bom)); if (!bom && ok) { c.focus(); } ok = ok && bom;
      });
      if (!ok) { saida.hidden = false; saida.textContent = 'Preencha nome e telefone para a Aldeia conseguir retornar.'; return; }
      var d = {}; $$('input,select,textarea', f).forEach(function (c) { if (c.name && c.value.trim()) d[c.name] = c.value.trim(); });
      var assunto = f.dataset.assunto + (sel ? ': ' + sel.options[sel.selectedIndex].text : '');
      var linhas = [assunto, '', 'Nome: ' + d.nome, 'Telefone: ' + d.telefone];
      if (d.email) linhas.push('E-mail: ' + d.email);
      ['finalidade', 'tipo', 'bairro'].forEach(function (k) { if (d[k]) linhas.push(k.charAt(0).toUpperCase() + k.slice(1) + ': ' + d[k]); });
      if (d.mensagem) linhas.push('', d.mensagem);
      linhas.push('', 'Página: ' + location.href);
      var o = window.aldeiaOrigem ? window.aldeiaOrigem() : {};
      if (o.utm_source) linhas.push('Origem: ' + o.utm_source + ' / ' + (o.utm_medium || '') + ' / ' + (o.utm_campaign || ''));
      var texto = linhas.join('\n');
      var id = window.aldeiaEvento ? window.aldeiaEvento('Lead', { content_name: assunto, content_ids: f.dataset.cod ? [f.dataset.cod] : [] }) : '';
      saida.hidden = false;
      if (C.endpointLead) {
        fetch(C.endpointLead, { method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ assunto: assunto, dados: d, origem: o, pagina: location.href, event_id: id }) })
          .then(function (r) { saida.textContent = r.ok ? 'Mensagem enviada. A Aldeia retorna no horário de atendimento.' : 'Não foi possível enviar agora. Ligue para (19) 3241-6444.'; if (r.ok) f.reset(); })
          .catch(function () { saida.textContent = 'Não foi possível enviar agora. Ligue para (19) 3241-6444.'; });
      } else if (C.whatsapp) {
        window.open(linkWa(texto), '_blank', 'noopener');
        saida.textContent = 'Abrimos o WhatsApp com a sua mensagem pronta. É só enviar.';
      } else {
        location.href = 'mailto:' + (C.emailContato || 'aldeia@aldeia.com.br') + '?subject=' + encodeURIComponent(assunto) + '&body=' + encodeURIComponent(texto);
        saida.textContent = 'Abrimos o seu programa de e-mail com a mensagem pronta. Se nada abriu, ligue para (19) 3241-6444.';
      }
    });
  });

  /* simulador de financiamento: SAC e Price, só amortização e juros */
  var sim = $('[data-sim]');
  if (sim) {
    var num = function (s) { return Number(String(s).replace(/\./g, '').replace(',', '.').replace(/[^\d.]/g, '')) || 0; };
    var mil = function (c) { c.addEventListener('blur', function () { var v = num(c.value); if (v) c.value = Math.round(v).toLocaleString('pt-BR'); }); };
    mil(sim.elements.valor); mil(sim.elements.entrada);
    if (qs.get('valor')) {
      var v0 = Number(qs.get('valor')) || 0;
      if (v0 > 0) { sim.elements.valor.value = v0.toLocaleString('pt-BR'); sim.elements.entrada.value = Math.round(v0 * 0.2).toLocaleString('pt-BR'); }
    }
    var set = function (s, t) { var el = $(s); if (el) el.textContent = t; };
    var calcular = function (registrar) {
      var valor = num(sim.elements.valor.value), entrada = num(sim.elements.entrada.value);
      var meses = Math.min(35, Math.max(1, Number(sim.elements.prazo.value) || 30)) * 12;
      var aa = num(sim.elements.juros.value) / 100, pv = valor - entrada;
      if (pv <= 0 || !valor) { set('[data-sim-fin]', 'Informe um valor de imóvel maior que a entrada.'); ['[data-sac-1]', '[data-sac-n]', '[data-price-1]', '[data-sac-t]', '[data-price-t]'].forEach(function (s) { set(s, ''); }); return; }
      var i = Math.pow(1 + aa, 1 / 12) - 1, am = pv / meses;
      var sac1 = am + pv * i, sacN = am + am * i, sacTotal = pv + i * pv * (meses + 1) / 2;
      var price = i ? pv * i / (1 - Math.pow(1 + i, -meses)) : pv / meses;
      set('[data-sac-1]', brl(sac1)); set('[data-sac-n]', brl(sacN)); set('[data-price-1]', brl(price));
      set('[data-sac-t]', 'Total pago ao banco: ' + brl(sacTotal)); set('[data-price-t]', 'Total pago ao banco: ' + brl(price * meses));
      set('[data-sim-fin]', 'Valor financiado: ' + brl(pv) + ' em ' + meses + ' meses, com entrada de ' + Math.round(entrada / valor * 100) + '%. Sem seguros, taxas e correção.');
      var link = $('[data-sim-link]'); if (link) link.href = '/comprar/?preco=' + [200000, 300000, 500000, 800000, 1000000, 1500000].filter(function (f) { return f >= valor; }).concat([''])[0];
      if (registrar) evento('Simulacao', { value: valor, currency: 'BRL', prazo_meses: meses });
    };
    sim.addEventListener('submit', function (e) { e.preventDefault(); calcular(true); });
    calcular(false);
  }
})();
