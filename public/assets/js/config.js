/* Configuração do site. É o único arquivo que precisa mudar para ligar medição e WhatsApp.
   Deixe o campo vazio ('') para manter desligado. Nenhum script de terceiro carrega sem ID. */
window.ALDEIA = {
  // Medição. Só carrega depois que o visitante aceita os cookies.
  metaPixelId: '',        // ex.: '1234567890123456'  (Gerenciador de Eventos da Meta)
  ga4Id: '',              // ex.: 'G-XXXXXXXXXX'      (Google Analytics 4)
  gtmId: '',              // ex.: 'GTM-XXXXXXX'       (Google Tag Manager; se usar GTM, deixe ga4Id vazio)
  googleAdsId: '',        // ex.: 'AW-123456789'

  // WhatsApp de atendimento: só números, com 55 e DDD. ex.: '5519999999999'
  // Formulários, barra do celular e botões já montam a mensagem pronta e abrem este número.
  // Vazio = o WhatsApp abre com a mensagem pronta e o visitante escolhe o contato (serve só para demonstração).
  // Em 15/11/2026 os fixos (19) 3241-6444 e (19) 2121-6444 não tinham conta no WhatsApp.
  whatsapp: '',
  emailContato: 'aldeia@aldeia.com.br',

  // Endpoint próprio que recebe uma cópia de cada lead (CRM, imo7 ou API de Conversões). Vazio = desligado.
  endpointLead: ''
};
