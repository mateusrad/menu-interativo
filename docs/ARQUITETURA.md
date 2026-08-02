# Arquitetura do projeto — Menu Interativo (15 Anos Bárbara)

Este documento explica **como o projeto funciona hoje e por que foi desenhado assim** — não é um changelog nem uma linha do tempo do desenvolvimento. A ideia é que qualquer pessoa (mesmo sem ler o código) consiga entender o sistema, saber onde mexer, e conversar sobre as decisões já tomadas.

## 1. Visão geral

Um site estático (sem servidor próprio) feito sob medida para um evento único: os 15 anos da Bárbara, no dia 06/09/2026. Os convidados usam o celular para consultar o cardápio (buffet, doces, bebidas) e pedir drinks personalizados direto de um bar interativo; o pedido aparece em tempo real num painel operado pelo bartender e numa tela de fila pública, e o próprio convidado recebe um aviso no celular quando seu drink fica pronto. Não existe versão para múltiplos eventos — o projeto foi construído inteiramente em função desta festa específica.

## 2. Stack tecnológico

| Peça | O que é | Por que essa escolha |
|---|---|---|
| HTML/CSS/JavaScript puro | Sem framework (React, Vue, etc.), sem build step | Evento de um dia só: não há necessidade de manter/escalar um app complexo, e qualquer editor de texto já é suficiente para dar manutenção |
| Firebase Realtime Database | Banco de dados na nuvem, com sincronização automática em tempo real (`onValue`) | Entrega "tempo real" (fila e painel do bartender atualizando sozinhos) sem escrever um servidor/WebSocket próprio; plano gratuito cobre com folga o volume de uma festa |
| GitHub Pages | Hospedagem estática gratuita, publicada direto do repositório Git | Zero custo, zero servidor para manter, deploy é literalmente um `git push` |
| Google Fonts (Montserrat, Cormorant Garamond, Lora) | Fontes carregadas via CDN do Google | Identidade visual consistente sem precisar hospedar arquivos de fonte |
| Python (`qrcode` + `Pillow`) | Script rodado localmente, fora do site | Só serve para gerar as imagens dos QR codes impressos (mesa 1 a 10) — não faz parte do que é publicado nem roda em produção |

## 3. Como o projeto roda / é publicado

- **Sem etapa de build**: os arquivos `.html` já são o produto final, servidos como estão.
- **Deploy**: um `git push` para o branch `main` do repositório (`github.com/mateusrad/menu-interativo`) é suficiente — o GitHub Pages publica automaticamente em `https://mateusrad.github.io/menu-interativo/`.
- **Sem ambiente de teste separado**: rodar localmente (ex: `python -m http.server`) abre as mesmas páginas, mas elas se conectam ao **mesmo Firebase real** usado na festa — não existe um banco de dados de "teste". Por isso, qualquer pedido de teste feito localmente aparece de verdade no painel do bartender e precisa ser marcado como "Entregue" (ou removido manualmente pelo console do Firebase) para não sujar os dados do evento.

## 4. Autenticação / acesso

Não existe login de usuário nem conta de convidado — qualquer pessoa com o link acessa. Existem duas travas *client-side* independentes, pensadas só para evitar acesso casual (por exemplo, alguém da gráfica testando o QR impresso antes da festa), não como segurança real — a senha fica em texto simples no código-fonte de cada página:

- **`index.html`**: pede uma senha até a data/hora configurada (06/09/2026, 00h00), a partir da qual libera automaticamente para todo mundo, sem exigir nada dos convidados na festa.
- **`barman.html`**: pede uma senha fixa, sem liberação automática por data — o bartender precisa dela sempre que abrir o painel (guardada em `sessionStorage`, então só pede uma vez por sessão do navegador).

## 5. Modelo de dados

Existe um único nó no Firebase Realtime Database: `/pedidos/{idGeradoPeloFirebase}`. Cada pedido é um objeto simples:

```json
{
  "convidado": "Ricardo",
  "drink": "Piña Colada (Com Álcool)",
  "status": "pendente",
  "dataHora": 1757200000000,
  "mesa": "5"
}
```

- `convidado` e `drink`: texto livre (drink vem de uma lista fixa de botões, convidado é digitado pelo usuário).
- `status`: um de quatro valores fixos — `pendente` → `fazendo` → `pronto` → `entregue`.
- `dataHora`: carimbo de tempo do servidor do Firebase (`serverTimestamp()`), usado para ordenar a fila.
- `mesa`: opcional — só existe quando o convidado chegou via QR code de uma mesa específica.

Não há coleção de usuários, cardápio, ou configuração — os itens do cardápio (drinks, buffet, doces) estão fixos no HTML de cada página, não no banco de dados.

## 6. Modelo de segurança / acesso a dados

As regras de acesso do Firebase Realtime Database são configuradas direto no console do Firebase (não existe um arquivo de regras versionado neste repositório). O desenho atual:

- **Leitura**: pública — qualquer um com o link enxerga todos os pedidos (necessário para a fila pública e o painel do bartender funcionarem).
- **Escrita**: permite criar um pedido novo livremente, mas em um pedido já existente só permite alterar o campo `status` (para um dos quatro valores válidos) — `convidado`, `drink` e `dataHora` não podem ser alterados depois de criados.
- **Sem diferenciação de usuário**: como não há login, o banco não sabe distinguir "convidado" de "bartender" — a senha do `barman.html` é só uma cortina na interface, não uma permissão real de banco de dados. Qualquer pessoa com acesso às ferramentas de desenvolvedor do navegador tecnicamente consegue avançar o status de um pedido de outra pessoa.
- O nome do convidado é escapado antes de ser inserido na tela (`fila.html` e `barman.html`) para impedir que alguém injete HTML/script através do campo de nome.

## 7. Funcionalidades — como cada uma funciona por trás dos panos

**Pedido de drink (`drinks.html`)**
O convidado escolhe um drink pré-definido e digita o nome; o pedido é enviado com `push()` para `/pedidos`. Duas proteções client-side entram em ação: (1) um cooldown de 2 minutos guardado no `localStorage` do aparelho, que só *avisa* (pede confirmação) se o **mesmo nome** tentar pedir de novo rápido demais — nome diferente no mesmo aparelho passa direto, para cobrir quem pede por outra pessoa da mesa; (2) o próprio ID do pedido gerado pelo Firebase é guardado no `localStorage`, para o mecanismo de aviso descrito abaixo.

**Fila em tempo real (`fila.html`)**
Escuta o nó `/pedidos` inteiro via `onValue` e redesenha duas colunas (Preparando / Prontos) sempre que qualquer pedido muda — sem dar F5, sem paginação ou filtro do lado do servidor (o navegador sempre recebe a lista completa de pedidos do evento).

**Painel do bartender (`barman.html`)**
Três colunas de status (Para Fazer → Fazendo → No Balcão → arquivado como Entregue), pensadas para dois bartenders trabalharem ao mesmo tempo sem risco de pegar o mesmo pedido: assim que alguém clica "Iniciar", o pedido sai da coluna "Para Fazer" para todo mundo que estiver com a tela aberta. Interface em modo escuro, pensada para o ambiente de baixa luz de uma festa à noite.

**Mesa via QR code**
Cada mesa tem um QR impresso apontando para `index.html?mesa=N`. O JavaScript lê esse parâmetro da URL, mostra um selo "Mesa N" na tela, e repassa o número automaticamente para o link do bar de drinks (`drinks.html?mesa=N`). Se o pedido tiver mesa, ela é gravada junto no Firebase e exibida tanto no painel do bartender quanto na fila pública — permitindo que um garçom, se a família decidir usar um, saiba para onde levar o drink.

**Aviso de "drink pronto" sem notificação push**
Em vez de push de verdade (Firebase Cloud Messaging), o aviso funciona enquanto a aba do navegador do convidado estiver aberta em algum momento (mesmo minimizada): o mesmo `onValue` que alimenta a fila/pedido também compara os IDs salvos no `localStorage` daquele aparelho específico contra o snapshot do Firebase; quando um deles vira `"pronto"`, dispara vibração do celular, um beep curto (gerado por código, sem arquivo de áudio), o título da aba piscando, e um banner na tela. Como a lista de IDs monitorados é local a cada aparelho, um convidado só é avisado dos pedidos que ele mesmo criou.

**Cronômetro do bar (`index.html`)**
Duas janelas de horário fixas (19h20–20h20 e 21h30–00h30 do dia 06/09/2026), escritas diretamente no código. O relógio usado é o do próprio aparelho do convidado — não há ajuste de fuso horário no servidor.

**Cardápios estáticos (`bar.html`, `buffet.html`, `doces.html`)**
Páginas de consulta, sem conexão com o Firebase — os itens do cardápio estão escritos direto no HTML. `buffet.html` também mostra o horário em que cada etapa (Entrada, Finger Food) fica disponível.

## 8. Segredos e scripts administrativos

- A configuração do Firebase (`apiKey`, `projectId`, etc.) aparece em texto plano no código-fonte de `drinks.html`, `fila.html` e `barman.html`. Isso é esperado e normal para um app client-side do Firebase — essa chave não é um segredo por natureza; a proteção de verdade são as regras de acesso do banco (seção 6), não o sigilo dessa chave.
- `scripts/gerar_qrcodes.py`: script Python rodado manualmente pelo desenvolvedor (não faz parte do site publicado) para gerar os 10 cartões de QR code (um por mesa), salvos em `qrcodes/`.
- `IDEIAS-FUTURO.md`: fica de fora do controle de versão (listado no `.gitignore`) — são notas de planejamento para uma eventual versão multi-evento do projeto, sem relação com o funcionamento da festa atual.

## 9. Decisões técnicas e por quê

| Decisão | Alternativa considerada | Motivo da escolha |
|---|---|---|
| HTML/CSS/JS estático, sem framework | React/Vue/Next.js | Evento de um dia, sem necessidade de escalar; menor barreira para o próprio dono do projeto dar manutenção depois |
| Firebase Realtime Database | Backend próprio (Node/Django + Postgres) ou Firestore | Sincronização em tempo real "de fábrica" via `onValue`, sem escrever infraestrutura própria; plano gratuito é suficiente para o volume de uma festa |
| GitHub Pages | Hospedagem paga (Vercel/Netlify em plano pago, VPS) | Gratuito, deploy automático via `git push`, adequado para um site 100% estático |
| Aviso local (vibração/som/título piscando) em vez de push de verdade (FCM) | Firebase Cloud Messaging + Cloud Function | Cobre a mesma necessidade prática sem exigir o plano pago Blaze (necessário para Cloud Functions) nem esbarrar na limitação do iPhone, que só recebe push de verdade se o site for instalado na tela de início |
| Três status no painel do bartender (Para Fazer / Fazendo / No Balcão) | Dois status (Pendente / Pronto) | Evita que dois bartenders trabalhando ao mesmo tempo peçam o mesmo drink duas vezes — o pedido sai da fila assim que alguém "inicia" |
| Senha simples em JavaScript (não Firebase Auth) | Login de verdade com Firebase Authentication | Suficiente para o nível de ameaça real (evitar acesso casual antes da festa), sem o custo de implementar cadastro/login para um evento de um dia |
| Mesa via parâmetro de URL (`?mesa=N`) | Perguntar o número da mesa no formulário de pedido | Zero digitação para o convidado — o QR já identifica a mesa sozinho |

## 10. Custos e limites

O projeto inteiro roda no plano gratuito de cada serviço:

- **Firebase Realtime Database (plano gratuito "Spark")**: limite de 1 GB armazenado e 10 GB de download por mês. Um pedido é um objeto de texto pequeno (poucas dezenas de bytes); mesmo com centenas de pedidos e todos os convidados atualizando a fila em tempo real durante a festa toda, o consumo fica muito abaixo desses limites — não há risco realista de custo para um evento único.
- **GitHub Pages**: gratuito para repositórios públicos, sem limite de tráfego relevante para o uso aqui (uma festa, algumas dezenas de convidados).
- **O que mudaria essa conta**: se o projeto virasse uma base multi-evento (vários eventos simultâneos usando o mesmo banco, ou anos de dados acumulados sem limpeza), o volume de leitura/escrita poderia se aproximar dos limites gratuitos do Firebase. Também, se um dia decidirem implementar notificação push de verdade (FCM disparado por Cloud Function), isso exigiria migrar o Firebase do plano gratuito para o plano Blaze (pay-as-you-go) — o uso provavelmente continuaria dentro da faixa gratuita do Blaze, mas exigiria cadastrar um cartão de cobrança no projeto.

## 11. Limitações conhecidas

- **Sem autenticação real**: qualquer pessoa com o link pode enviar pedidos ou, usando as ferramentas de desenvolvedor do navegador, alterar o status de um pedido de outra pessoa — as regras do banco impedem mudar nome/drink/hora, mas não impedem alguém de "confirmar" um pedido alheio como pronto.
- **Travas de acesso são só deterrentes visuais**: as senhas de `index.html` e `barman.html` ficam em texto plano no código-fonte; servem para evitar cliques casuais, não para proteger dados sensíveis.
- **Sem paginação**: `fila.html` e `barman.html` sempre carregam a lista completa de pedidos do evento inteiro — adequado para o volume de uma festa, mas não escalaria para uso contínuo ao longo de vários eventos.
- **Aviso de "drink pronto" depende da aba estar aberta**: funciona mesmo com a aba minimizada ou em segundo plano, mas não funciona se o navegador estiver totalmente fechado no momento em que o pedido fica pronto.
- **Duas imagens órfãs**: `img/comartilhar.jpg` e `img/google_fotos.jpg` não são mais referenciadas por nenhuma página (sobraram de um botão de compartilhamento de fotos que foi removido do `index.html`).
- **`README.md` desatualizado em alguns pontos**: por exemplo, ainda cita o arquivo `painel.html`, que hoje se chama `barman.html`, e não reflete a mesa via QR nem o aviso de "drink pronto".

## 12. Mapa do código

```
index.html              Hub principal — menu de navegação, cronômetro do bar,
                         trava de acesso por senha/data, captura da mesa via QR
drinks.html              Pedido de drinks — formulário, cooldown anti-spam,
                         aviso de "drink pronto"
fila.html                Painel de fila em tempo real para os convidados
barman.html              Painel operacional do bartender (3 colunas de status),
                         protegido por senha fixa
bar.html                 Cardápio estático de bebidas convencionais
buffet.html              Cardápio estático do buffet, com horários de disponibilidade
doces.html               Cardápio estático da mesa de doces

img/
  favicon.svg            Ícone do medalhão "15", usado em todas as páginas
  logo_mateus.png         Logo da assinatura do desenvolvedor no rodapé
  comartilhar.jpg         Órfã (não referenciada em nenhuma página)
  google_fotos.jpg        Órfã (não referenciada em nenhuma página)

qrcodes/
  mesa-01.png … mesa-10.png   Cartões de QR code por mesa, prontos para impressão

scripts/
  gerar_qrcodes.py        Gera os arquivos em qrcodes/ — roda localmente, fora do site

docs/
  sessions/               Resumos de sessões de trabalho anteriores
  ARQUITETURA.md          Este documento

README.md                Descrição funcional das páginas (parcialmente desatualizada)
IDEIAS-FUTURO.md          Notas de roadmap futuro — fora do controle de versão (.gitignore)
```

---
*Documento gerado em 02/08/2026, com base no commit `28ee949` (branch `main`, working tree limpo). Se o código mudou desde então, algumas seções podem estar desatualizadas.*
