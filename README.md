# Aldeia Imóveis — site novo (demonstração)

Site estático multipágina da Aldeia Consultoria, Vendas e Administração de Imóveis (Campinas/SP, CRECI 3716-J).
Feito pela BlueShieldPro como versão nova do site atual, https://www.aldeia.com.br/site/.

## Como funciona

- `dados/` guarda a carteira copiada do site atual em 15/11/2026: dados brutos, descrições reescritas e fotos/coordenadas.
- `build/gerar.py` lê os dados e escreve o site em `public/`. Só usa a biblioteca padrão do Python.
- `build/testes.py` confere o que foi gerado.
- `public/` é o que o Render serve. Não há build no servidor.

```bash
python3 build/gerar.py && python3 build/testes.py
python3 -m http.server 8755 --directory public
```

## Ligar medição e WhatsApp

Tudo fica em `public/assets/js/config.js`: Pixel da Meta, GA4, Tag Manager, Google Ads, número do WhatsApp
e um endpoint próprio para os formulários. Campo vazio fica desligado. Nenhum script de terceiro carrega sem ID
e sem o aceite de cookies do visitante.

## Antes de apontar o domínio

1. Em `build/base.py`, trocar `SITE_URL` pelo domínio final e `PUBLICADO` para `True`.
2. Rodar o gerador. O `robots.txt` passa a liberar buscadores e assistentes de IA, e o `noindex` sai das páginas.
3. Conferir as pendências do cliente em `/apresentacao/`.

## Atualizar a carteira

`build/baixar_midias.py` baixa fotos e coordenadas a partir das páginas salvas do site atual. É idempotente.
O caminho definitivo é receber a exportação do imo7 e gerar `dados/` a partir dela.
