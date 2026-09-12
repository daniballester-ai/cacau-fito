# Relatório Final — De Spec a Código (CacauFito)

**Grupo:**
Danielle Magalhães Ballester (danielleballester@gmail.com)
Jales Anderson de Assis Monteiro (jalesmonteiro@hotmail.com)

## Funcionalidades escolhidas e por que eram bons casos para SDD

Escolhemos duas funcionalidades novas no CacauFito: **histórico de predições** (registro persistente + API paginada + página de navegação) e **sinalização de resultado incerto** (flag na resposta de `/predict` quando a confiança do modelo é baixa ou há disputa acirrada entre classes). Uma terceira, **estatísticas agregadas** (`GET /stats`), foi usada para repetir o processo com outra ferramenta. Todas têm regras de negócio reais e não triviais (o que gravar, quando não gravar, limite de retenção; os dois critérios independentes do limiar de incerteza e sua ordem de precedência; contagem zerada por classe mesmo sem dados), pelo menos dois cenários de uso cada, e tocam mais de um arquivo (storage, API, frontend), tornando a especificação prévia genuinamente útil em vez de burocrática.

## Abordagens de especificação usadas

Usamos **OpenSpec** para as duas primeiras funcionalidades e para o próprio modelo de visão computacional (proposal → specs delta → design → tasks), e o **GitHub Spec Kit** para a terceira (spec com user stories priorizadas P1/P2 → plan/research/data-model/contracts → tasks). Na prática, o OpenSpec se mostrou mais natural para mudanças que alteram capabilities já existentes — o conceito de spec "delta" (ADDED/MODIFIED/REMOVED) deixou explícito exatamente o que a sinalização de incerteza mudava em requisitos que já estavam publicados, e o passo de sincronização no archive impede specs principais desatualizadas. O Spec Kit, por sua vez, brilhou numa feature nova e isolada: a priorização por user story com "Independent Test" tornou natural pensar no MVP (só a distribuição geral) antes do caso de borda (histórico vazio) antes do polimento (falha de storage) — e o checklist de qualidade da especificação, gerado e autovalidado antes de seguir para o plano, é um gate que o OpenSpec não tem nativamente. Comparação completa em `docs/comparacao_sdd_tools.md`.

## Uma dificuldade real enfrentada

A mais concreta foi técnica: ao adicionar o badge de "resultado incerto" no frontend, ele simplesmente não aparecia — nem no caso incerto nem, mais grave, o botão "Carregar mais" da página de histórico ficava visível mesmo em estado vazio. A causa era sutil: o atributo HTML `hidden` estava sendo sobrescrito pela regra CSS `.btn { display: inline-flex }`, porque uma classe de autor com `display` explícito tem precedência sobre o `display: none` que o navegador aplica por padrão a `[hidden]`. Só descobrimos isso testando de verdade em um navegador headless (Playwright) em vez de confiar na leitura do código — a lição prática foi que, para qualquer mudança de frontend, a verificação visual real (não só a leitura do JSX/HTML) é o que efetivamente pega esse tipo de bug de especificidade CSS, que passaria despercebido numa revisão só de código.

## O que faríamos diferente

Duas coisas. Primeiro, deixaríamos os guardrails de permissão (`permissions.deny` no harness) configurados desde o primeiro commit, não só depois de já termos vários requisitos implementados — a proteção contra comandos destrutivos e leitura de segredos deveria ter sido parte do setup inicial do projeto, não um item adicionado à parte perto do fim. Segundo, teríamos planejado os 10 requisitos funcionais do início, em vez de começar por 4 e ir especificando o restante conforme percebíamos a necessidade — isso deixou a implementação dos últimos 6 requisitos comprimida no fim do prazo, quando um planejamento inicial mais completo teria distribuído esse trabalho de forma mais uniforme ao longo do projeto.
