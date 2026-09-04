# Checkpoint Humano (Etapa 4)

## Checkpoint definido

**Antes de expor um novo endpoint HTTP publicamente** (ou seja, antes de fazer merge de uma rota nova para a branch `main`), um humano do grupo deve revisar o diff gerado pelo agente e decidir explicitamente: **aprovar como está / editar / rejeitar e voltar à especificação**. Nenhum endpoint novo entra em produção só porque os testes automatizados passaram — a aprovação humana é obrigatória e separada da execução da IA.

**Por que este checkpoint**: endpoints HTTP são a superfície de contrato mais visível do projeto — uma vez expostos, qualquer cliente (o frontend, ou futuramente o CacauClima) passa a depender do formato exato da resposta. Reverter um endpoint já publicado é mais caro do que revisar antes de publicar.

## Simulação do checkpoint

Aplicamos o checkpoint retroativamente ao endpoint `GET /stats` (gerado via Spec Kit, feature `001-prediction-stats`), tratando o momento do merge como se ainda estivesse pendente de aprovação.

**Paramos a execução no ponto de merge e revisamos:**

1. **Contrato de resposta** — o formato implementado em `src/inference_service/main.py` (`{"total": ..., "by_class": {...}}`, 200 em sucesso / 503 em falha) bate exatamente com o que `specs/001-prediction-stats/contracts/stats-api.md` especificava, sem desvio.
2. **Ausência de autenticação** — decisão consciente e já registrada em `spec.md` (seção Assumptions), consistente com o restante do PoC, não uma omissão acidental.
3. **Cobertura de teste** — os 3 cenários do contrato (sucesso com dados, sucesso vazio, falha de storage) têm teste automatizado correspondente em `tests/test_stats_api.py`, e o quickstart (`quickstart.md`) foi executado manualmente contra o servidor real.
4. **Efeito colateral** — a rota é somente leitura (`GET`), não altera nenhum schema existente nem o comportamento de `/predict`.

## Decisão tomada

**Aprovar como está.**

**Justificativa**: o endpoint é somente leitura, não introduz estado novo (reaproveita a tabela `predictions` já existente), está integralmente coberto por teste automatizado e verificação manual, e sua resposta já é exatamente o que o contrato descrito na especificação previa — não há divergência entre o que foi especificado e o que foi implementado que justificasse pedir edição, nem risco (segurança, dado sensível, mudança de schema) que justificasse rejeitar e voltar à especificação.

## Papel humano assumido

O grupo assumiu o papel de **revisor técnico**: validar que a implementação gerada pelo agente de IA cumpre o contrato especificado, antes de ela ser considerada pronta para expor publicamente — a IA implementa e testa, mas não tem autoridade para aprovar sua própria mudança como pronta para produção/merge. Essa separação é exatamente o ponto do checkpoint: mesmo com testes verdes, a decisão de "isso pode ir para `main`" continua sendo humana.
