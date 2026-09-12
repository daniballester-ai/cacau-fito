# Log/Transcript de Sessão do Agente — Evidência de Observabilidade

Trechos reais desta sessão de desenvolvimento assistido por IA (Claude Code), documentando revisão de diff antes de aceitar mudanças e decisões de checkpoint.

## Episódio 1 — Bug real encontrado por verificação em navegador, não por leitura de código

Ao implementar o badge "Resultado incerto" no frontend, o agente rodou a aplicação de verdade em Chrome headless (Playwright) em vez de confiar apenas na leitura do HTML/CSS/JS gerado:

> **Agente:** "Bug real encontrado: o botão 'Carregar mais' aparece mesmo no estado vazio — o atributo `hidden` está sendo sobrescrito pela regra `.btn { display: inline-flex }` (especificidade CSS). Corrigindo com uma regra defensiva."

Correção aplicada (`[hidden] { display: none !important; }`), e o agente **re-executou o teste de navegador** para confirmar antes de seguir, em vez de assumir que a correção funcionou:

> **Agente:** "Corrigido — botão escondido corretamente agora."

Esse achado só foi possível porque o agente tratou a verificação visual como obrigatória antes de marcar a tarefa como concluída — está documentado como aprendizado explícito no relatório final (`docs/relatorio_final.md`).

## Episódio 2 — Revisão humana de segredo antes de aceitar uma ação do agente

Durante a configuração de credenciais do Kaggle, o usuário colou um token de API diretamente na conversa. O agente **não aceitou a mudança silenciosamente**:

> **Agente:** "Isso parece ser um token/chave de API do Kaggle colado diretamente no chat. Por política da FITec (dado sensível/credencial), isso não deveria ser compartilhado em conversas [...] Recomendação: revogue/regenere esse token [...] Não vou usar a string que você colou como credencial — ela deve ser tratada como comprometida a partir de agora."

O usuário então pediu para o agente montar apenas um arquivo-modelo (`kaggle.json`) com campos vazios, e o próprio usuário preencheu os valores reais fora da conversa — o agente nunca teve acesso à credencial real, e essa decisão foi revisada e ajustada em conjunto antes de prosseguir.

## Episódio 3 — Checkpoint humano simulado antes de considerar um endpoint pronto

Ao final da implementação do endpoint `GET /stats` (feature `001-prediction-stats`, via Spec Kit), o agente parou deliberadamente a execução para simular o checkpoint humano definido em `docs/checkpoint_humano.md`, revisando o diff contra o contrato especificado antes de aprovar:

> **Agente:** "Paramos a execução no ponto de merge e revisamos: (1) Contrato de resposta [...] bate exatamente com o que `specs/001-prediction-stats/contracts/stats-api.md` especificava [...] (4) Efeito colateral — a rota é somente leitura [...] **Decisão tomada:** Aprovar como está."

## Episódio 4 — Guardrail de permissão bloqueando uma ação real, não apenas descrita

Ver `docs/guardrail_evidence.md` para o log completo: o agente tentou, a pedido do usuário, ler `.env` e executar `rm -rf` num diretório de teste — ambas as tentativas foram **bloqueadas pelo harness antes de qualquer efeito**, com o erro exato capturado como evidência.

---

Esses quatro episódios juntos mostram o padrão de observabilidade adotado no projeto: o agente narra o que está fazendo e por quê, revisões de diff/comportamento acontecem antes de aceitar uma mudança como concluída, e decisões sensíveis (segredos, endpoints públicos, ações destrutivas) sempre passam por um ponto de parada explícito — humano ou estrutural (guardrail).
