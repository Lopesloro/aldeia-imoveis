/* Medição da Aldeia: consentimento (LGPD), Pixel da Meta, GA4, GTM e Google Ads.
   Regras:
   1. Nada de terceiro carrega sem ID em config.js E sem o aceite do visitante.
   2. Todo evento leva um event_id. O mesmo id deve ser enviado pela API de Conversões
      quando ela existir, para a Meta deduplicar navegador e servidor.
   3. Eventos: PageView, ViewContent (ficha), Search (filtro), Lead (formulário),
      Contact (telefone, e-mail, WhatsApp) e eventos personalizados (Boleto, Simulacao, Rota). */
(function () {
  'use strict';
  var C = window.ALDEIA || {};
  var CHAVE = 'aldeia_consent';
  var fila = [];
  var ligado = false;
  window.dataLayer = window.dataLayer || [];

  function ler(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function gravar(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  function temId() { return !!(C.metaPixelId || C.ga4Id || C.gtmId || C.googleAdsId); }
  function novoId() { return Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 10); }

  // Origem da visita: guarda UTM e fbclid/gclid para anexar ao lead.
  function origem() {
    var salvo = {};
    try { salvo = JSON.parse(sessionStorage.getItem('aldeia_origem') || '{}'); } catch (e) {}
    var q = new URLSearchParams(location.search), mudou = false;
    ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'fbclid', 'gclid'].forEach(function (k) {
      if (q.get(k)) { salvo[k] = q.get(k); mudou = true; }
    });
    if (!salvo.entrada) { salvo.entrada = location.pathname; salvo.referencia = document.referrer || ''; mudou = true; }
    if (mudou) { try { sessionStorage.setItem('aldeia_origem', JSON.stringify(salvo)); } catch (e) {} }
    return salvo;
  }
  var ORIGEM = origem();

  function carregarScript(src) {
    var s = document.createElement('script'); s.async = true; s.src = src; document.head.appendChild(s);
  }

  function ligar() {
    if (ligado) return; ligado = true;
    if (C.gtmId) {
      window.dataLayer.push({ 'gtm.start': Date.now(), event: 'gtm.js' });
      carregarScript('https://www.googletagmanager.com/gtm.js?id=' + encodeURIComponent(C.gtmId));
    }
    if (C.ga4Id || C.googleAdsId) {
      window.gtag = function () { window.dataLayer.push(arguments); };
      window.gtag('js', new Date());
      if (C.ga4Id) window.gtag('config', C.ga4Id);
      if (C.googleAdsId) window.gtag('config', C.googleAdsId);
      carregarScript('https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(C.ga4Id || C.googleAdsId));
    }
    if (C.metaPixelId) {
      var f = window, n;
      if (!f.fbq) {
        n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); };
        if (!f._fbq) f._fbq = n; n.push = n; n.loaded = true; n.version = '2.0'; n.queue = [];
        carregarScript('https://connect.facebook.net/en_US/fbevents.js');
      }
      window.fbq('init', C.metaPixelId);
    }
    fila.splice(0).forEach(function (ev) { despachar(ev[0], ev[1], ev[2]); });
  }

  var PADRAO_META = { PageView: 1, ViewContent: 1, Search: 1, Lead: 1, Contact: 1 };
  var NOME_GA = { PageView: 'page_view', ViewContent: 'view_item', Search: 'search', Lead: 'generate_lead', Contact: 'contact' };

  function despachar(nome, dados, id) {
    window.dataLayer.push({ event: 'aldeia_' + nome, aldeia: dados, event_id: id });
    if (window.fbq && C.metaPixelId) {
      window.fbq(PADRAO_META[nome] ? 'track' : 'trackCustom', nome, dados, { eventID: id });
    }
    if (window.gtag && (C.ga4Id || C.googleAdsId) && nome !== 'PageView') {
      window.gtag('event', NOME_GA[nome] || nome.toLowerCase(), dados);
    }
  }

  // API pública: window.aldeiaEvento('Lead', {content_ids:['APA00345']})
  window.aldeiaEvento = function (nome, dados) {
    var id = novoId();
    dados = dados || {};
    if (ler(CHAVE) === 'sim' && temId()) { ligar(); despachar(nome, dados, id); }
    else if (temId() && ler(CHAVE) !== 'nao') { fila.push([nome, dados, id]); }
    return id;
  };
  window.aldeiaOrigem = function () { return ORIGEM; };

  // Consentimento
  function caixa() { return document.querySelector('[data-consent]'); }
  function mostrar(sim) { var c = caixa(); if (c) c.hidden = !sim; }
  function decidir(v) { gravar(CHAVE, v); mostrar(false); if (v === 'sim') ligar(); else fila.length = 0; }

  document.addEventListener('DOMContentLoaded', function () {
    var escolha = ler(CHAVE);
    // Sem nenhum ID configurado não há o que consentir: a faixa nem aparece.
    if (temId()) { if (escolha === 'sim') ligar(); else if (!escolha) mostrar(true); }
    document.addEventListener('click', function (ev) {
      var t = ev.target.closest('[data-consent-sim],[data-consent-nao],[data-consent-abrir],[data-evento]');
      if (!t) return;
      if (t.hasAttribute('data-consent-sim')) return decidir('sim');
      if (t.hasAttribute('data-consent-nao')) return decidir('nao');
      if (t.hasAttribute('data-consent-abrir')) return mostrar(true);
      var nome = t.getAttribute('data-evento');
      if (nome === 'Lead' || nome === 'Simulacao') return; // disparados pelo site.js depois da validação
      var b = document.body;
      window.aldeiaEvento(nome, { canal: t.getAttribute('data-canal') || '', pagina: b.getAttribute('data-pagina') || '',
        content_ids: b.getAttribute('data-imovel') ? [b.getAttribute('data-imovel')] : [] });
    });

    window.aldeiaEvento('PageView', {});
    var b = document.body;
    if (b.getAttribute('data-imovel')) {
      window.aldeiaEvento('ViewContent', {
        content_ids: [b.getAttribute('data-imovel')], content_type: 'home_listing',
        content_category: b.getAttribute('data-tipo-imovel') || '',
        value: Number(b.getAttribute('data-valor')) || 0, currency: 'BRL'
      });
    }
  });
})();
