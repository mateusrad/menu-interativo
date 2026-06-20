## 📂 Arquivos do Sistema e Suas Execuções

### 1. 🏠 Porta de Entrada (`index.html`)

* **Execução**: Funciona como o hub central do convidado. Apresenta o menu completo da festa (Buffet, Doces, Bebidas Convencionais e Drinks Interativos).
* **Inteligência**: Possui um **Temporizador Progressivo em Javascript** que monitora o horário do evento. Ele exibe dinamicamente três estados:
* ⏳ *Bar Fechado*: Mostra uma contagem regressiva de horas, minutos e segundos até a abertura oficial.
* 🟢 *Bar Aberto*: Atualiza o status para alertar o tempo restante de serviço livre.
* 🔴 *Bar Encerrado*: Informa o encerramento dos pedidos do bar de coquetéis.
* *Nota*: Em ambiente de desenvolvimento, o Javascript possui uma trava comentada para permitir testes contínuos sem bloquear a navegação.



### 🍹 2. Tela de Escolha de Pedidos (`drinks.html`)

* **Execução**: Interface intuitiva onde o convidado digita seu nome e seleciona o drink desejado.
* **Validação de UX**: O botão de envio permanece bloqueado com estados visuais dinâmicos ("Escolha um Drink" ou "Digite seu Nome") e só é liberado quando o formulário estiver 100% preenchido, evitando dados vazios no banco.
* **Segurança de Dados**: Ao enviar, aciona um *overlay* de carregamento animado (*spinner*) e despacha para a nuvem o nome, o drink escolhido, o status inicial `"pendente"` e o carimbo de data/hora do servidor (`serverTimestamp`). Em seguida, redireciona o usuário de forma automática para a fila de espera.

### 📥 3. Painel Administrativo do Bartender (`painel.html`)

* **Execução**: O cérebro operacional do bar. Uma interface em **Modo Escuro (Dark Mode)** focada no trabalho sob luz baixa.
* **Contraste Dinâmico**: Caixas de pedidos com bordas brilhantes saturadas (*Glow Effect*) se separam do fundo escuro, permitindo leitura imediata pelo profissional.
* **Triagem de Segurança (🔞 Alerta de Álcool)**: O script varre o nó de pedidos em tempo real. Se o drink contiver álcool, exibe um card com alerta vermelho vivo de **`🔞 COM ÁLCOOL`** para que o bartender certifique-se da maioridade de quem está retirando. Drinks infantis/teens ganham a tag verde **`🟢 SEM ÁLCOOL`**.
* **Gestão de Fluxo**: Permite o avanço de status do pedido em apenas um clique: de `Pendente` para `Pronto` (coluna do balcão) e de `Pronto` para `Entregue` (arquivando o pedido).

### 🛎️ 4. Monitor da Fila de Espera (`fila.html`)

* **Execução**: Funciona como um painel de chamada viva (estilo telão de restaurante).
* **Atualização Instantânea**: Sem dar *F5* na página, os nomes dos convidados sobem e mudam de coluna na hora. Mostra quem está na coluna **"⏳ Preparando"** e quem deve ir ao balcão buscar o copo na coluna **"✨ Prontos para Retirada"** (que conta com uma animação pulsante para chamar a atenção visual).

### 🍽️ 5. Páginas de Apoio Estáticas (`bar.html`, `buffet.html`, `doces.html`)

* **Execução**: Cardápios elegantes que servem como consulta rápida para as opções gastronômicas do Buffet e da mesa de doces, mantendo a identidade visual idêntica (rosê/cobre) da festa da debutante.

---

## 🛠️ Detalhes Técnicos e Arquitetura

* **Sem Reload (SPA Feel)**: Toda a comunicação com o Firebase Realtime Database usa módulos oficiais (SDK v10+), escutando as alterações via `onValue` e injetando o HTML dinamicamente com manipulação de DOM nativa (`document.createElement`). Isso economiza bateria e dados móveis dos celulares na festa.
* **Responsividade Total**: O grid de CSS se adapta perfeitamente desde telas pequenas de celulares (convidados) até tablets ou monitores maiores (painel do bartender e telão da fila).
* **Glow & Contrast Effects**: Estilos aplicados especificamente para ambientes noturnos de eventos, evitando cliques errados da equipe de coquetelaria.

---

## 👨‍💻 Assinatura e Marca Pessoal

Todas as páginas contam com a assinatura profissional unificada no rodapé:

* **Componente**: Inclui a logo pessoal com bordas arredondadas e efeito de fusão de fundo (*multiply*).
* **Link Externo**: Redireciona o usuário para o portfólio oficial em uma nova aba (`target="_blank"`), servindo como uma ferramenta ativa de captação de novos clientes durante o evento.

---

*Desenvolvido por **Mateus Rosa**.*

