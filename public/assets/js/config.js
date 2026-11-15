/* Configuração do site. É o único arquivo que precisa mudar para ligar medição e WhatsApp.
   Deixe o campo vazio ('') para manter desligado. Nenhum script de terceiro carrega sem ID. */
window.ALDEIA = {
  // Medição. Só carrega depois que o visitante aceita os cookies.
  metaPixelId: '',        // ex.: '1234567890123456'  (Gerenciador de Eventos da Meta)
  ga4Id: '',              // ex.: 'G-XXXXXXXXXX'      (Google Analytics 4)
  gtmId: '',              // ex.: 'GTM-XXXXXXX'       (Google Tag Manager; se usar GTM, deixe ga4Id vazio)
  googleAdsId: '',        // ex.: 'AW-123456789'

  // Contato. Com o WhatsApp preenchido, formulários e a barra do celular passam a abrir a conversa.
  whatsapp: '',           // só números, com 55 e DDD. ex.: '5519999999999'
  emailContato: 'aldeia@aldeia.com.br',

  // Endpoint próprio para receber os formulários (CRM, imo7 ou API de Conversões). Vazio = e-mail/WhatsApp.
  endpointLead: ''
};
