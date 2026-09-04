# Escopo — Atividade Prática Assíncrona (De Spec a Código)

**Projeto:** CacauFito — classificador de folhas de cacau por visão computacional (dataset Amini, EfficientNet-B0, API FastAPI + frontend de upload). Repositório existente, com duas funcionalidades novas especificadas abaixo.

## Funcionalidade 1 — Histórico de predições

**O que é:** cada predição feita pelo serviço de inferência passa a ser registrada (rótulo, confiança, probabilidades por classe, timestamp e referência da imagem), com uma API paginada (`GET /history`) e uma página mínima para navegar pelo histórico, sob uma política de retenção limitada (200 entradas).

**Cenários de uso:**
1. Uma predição bem-sucedida é registrada automaticamente, sem afetar a resposta ao cliente mesmo se o registro falhar.
2. Um cliente lista o histórico paginado, mais recente primeiro; com histórico vazio, a listagem retorna vazia em vez de erro.

**Por que é um bom caso para SDD:** A funcionalidade tem regras de negócio reais — o que gravar, quando não gravar, e um limite de retenção para não crescer sem parar. Ela também tem casos de borda concretos: upload rejeitado não deve gerar entrada, falha de storage não deve derrubar a predição, e histórico vazio precisa de tratamento próprio. Além disso, mexe em múltiplos arquivos e camadas ao mesmo tempo — um novo módulo de storage, a integração no handler de `/predict`, um novo endpoint e uma nova página de frontend. Por isso não é uma mudança trivial de um único arquivo, e se beneficia de ter os requisitos e critérios de aceite escritos antes de começar a codificar.

## Funcionalidade 2 — Sinalização de resultado incerto (limiar de confiança)

**O que é:** a resposta de `/predict` passa a incluir `is_uncertain` e `uncertainty_reason`, calculados a partir de uma regra com dois critérios (confiança baixa OU disputa acirrada entre as duas classes mais prováveis), e o frontend passa a exibir um indicador visual quando o resultado é incerto, em vez de apresentar toda predição com a mesma aparência de certeza.

**Cenários de uso:**
1. Uma predição com confiança abaixo do limiar é sinalizada como incerta (`uncertainty_reason: "low_confidence"`).
2. Uma predição com confiança aceitável, mas com as duas classes top muito próximas, também é sinalizada como incerta (`uncertainty_reason: "close_call"`) — o caso de borda que motiva a funcionalidade.
3. Uma predição confiante continua sendo exibida exatamente como antes, sem nenhum indicador.

**Por que é um bom caso para SDD:** A regra de negócio não é trivial — são dois critérios independentes (confiança baixa e disputa acirrada), com uma ordem de precedência definida entre eles quando os dois ocorrem juntos. Existe um caso de borda central que motiva a própria funcionalidade: a disputa acirrada entre classes, que um limiar simples de confiança sozinho não capturaria. A mudança também é aditiva sobre contrato já existente em duas capabilities já implementadas (`leaf-inference-service` e `leaf-upload-frontend`), então precisa preservar o comportamento anterior sem quebrá-lo. Cada uma dessas regras vira um cenário Given/When/Then testável objetivamente, o que torna a especificação prévia diretamente verificável no código.

## Artefatos

Especificação completa de ambas as funcionalidades via **OpenSpec** (`openspec/changes/add-prediction-history/` e `openspec/changes/add-uncertain-diagnosis-flag/`), cada uma com `proposal.md`, `specs/<capability>/spec.md`, `design.md` e `tasks.md`.
