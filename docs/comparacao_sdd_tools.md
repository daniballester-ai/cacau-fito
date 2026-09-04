# Comparação: OpenSpec vs. Spec Kit (Etapa 5)

Comparação entre as duas ferramentas de SDD usadas neste projeto: **OpenSpec** (usado nas Etapas 1-4, para `add-prediction-history` e `add-uncertain-diagnosis-flag`) e **GitHub Spec Kit** (usado nesta etapa, para `001-prediction-stats`).

## Artefatos gerados

| | OpenSpec | Spec Kit |
|---|---|---|
| Localização | `openspec/changes/<nome>/` (temporário) → `openspec/specs/<capability>/` (permanente, após archive) | `specs/<NNN-nome>/` (permanente desde o início) |
| Motivação (why) | `proposal.md` | Seção "User Scenarios & Testing" implícita no `spec.md` (não há um "why" isolado) |
| Requisitos comportamentais | `specs/<capability>/spec.md` (delta: ADDED/MODIFIED/REMOVED Requirements + cenários WHEN/THEN) | `spec.md` (Functional Requirements FR-XXX + User Stories priorizadas P1/P2/P3 + Acceptance Scenarios Given/When/Then) |
| Design técnico | `design.md` (Decisions, Risks/Trade-offs, Migration Plan) | `plan.md` (Technical Context, Constitution Check, Project Structure) + `research.md` (Decisions com alternativas) + `data-model.md` + `contracts/` |
| Plano de tarefas | `tasks.md` (checklist numerado por seção) | `tasks.md` (checklist por *user story*, com IDs `TXXX`, marcadores `[P]` de paralelismo e `[USx]` de rastreabilidade à história) |
| Guia de validação | Não existe artefato dedicado — a verificação fica implícita nas tarefas | `quickstart.md` (cenários de validação manual, prontos para copiar/colar) |
| Checklist de qualidade da spec | Não existe — a qualidade é garantida pela revisão humana ao ler o `proposal.md`/`spec.md` | `checklists/requirements.md`, gerado e autoavaliado automaticamente antes de prosseguir para o plano |
| Arquivamento | Comando explícito (`/opsx:archive`) move a change para `archive/` e sincroniza specs "delta" nas specs principais | Não há um passo de arquivamento — a spec já nasce no lugar final; não existe o conceito de "delta spec" separado da spec principal |

## Abordagem e processo

**OpenSpec** é centrado no conceito de *delta*: cada change declara o que muda (ADDED/MODIFIED/REMOVED) em relação a specs principais já existentes, e um passo de sincronização explícito aplica essa mudança. Isso força uma pergunta constante — "isso é uma capability nova ou estou alterando uma que já existe?" — o que deixa muito claro o efeito colateral de uma mudança sobre requisitos anteriores (ficou evidente ao especificar `add-uncertain-diagnosis-flag`, que precisou copiar e ajustar requisitos inteiros de duas capabilities já publicadas).

**Spec Kit** é centrado no conceito de *user story priorizada*: cada spec organiza o trabalho em fatias verticais e independentemente entregáveis (P1, P2, P3...), e o `tasks.md` resultante já vem agrupado por história, com uma "Implementation Strategy" que sugere explicitamente qual é o MVP (só a P1) e como as demais entram depois. Isso tornou muito natural planejar `001-prediction-stats` como "história 1 = valor central, história 2 = caso de borda do histórico vazio, polish = tratamento de falha" — uma divisão que no OpenSpec eu teria feito por seção de tarefas, mas sem o conceito explícito de "isso sozinho já é um MVP entregável".

Outra diferença notável: o Spec Kit tem uma etapa de **research.md** dedicada só a registrar decisões técnicas com alternativas rejeitadas, separada do plano — no OpenSpec essa informação fica dentro do próprio `design.md`, na seção "Decisions". Resultado prático parecido, mas o Spec Kit obriga a separar "o que pesquisei" de "o que decidi construir" (`plan.md`), enquanto o OpenSpec deixa isso mais fluido em um único documento.

## Pontos positivos e negativos

**OpenSpec — positivos:**
- O conceito de spec "principal" vs. "delta" dá rastreabilidade real: dá para ver exatamente o que uma mudança alterou em um requisito já existente, sem reescrevê-lo do zero.
- O passo de sincronização (`/opsx:sync` embutido no archive) evita specs principais desatualizadas — é impossível arquivar sem que a spec principal reflita a mudança.
- Fluxo mais enxuto para mudanças pequenas e cirúrgicas (como `add-uncertain-diagnosis-flag`, que só mexeu em 2 requisitos existentes).

**OpenSpec — negativos:**
- Não tem uma etapa de "plano de tarefas por prioridade/MVP" nativa — cabe a quem escreve o `tasks.md` decidir como fatiar o trabalho.
- Não gera um checklist de qualidade da especificação automaticamente; a validação de completude é manual.

**Spec Kit — positivos:**
- A priorização por user story (P1/P2/P3) com "Independent Test" obriga a pensar em fatias de valor entregáveis desde o começo — encaixou muito bem no pedido da atividade de ter cenários de uso claros.
- O checklist de qualidade da spec (`checklists/requirements.md`) é gerado e autovalidado antes de seguir para o plano — um gate de qualidade automático que o OpenSpec não tem.
- `research.md` + `data-model.md` + `contracts/` separados deixam a documentação mais granular e fácil de referenciar isoladamente (por exemplo, o contrato de API pode ser lido sem precisar abrir o plano inteiro).

**Spec Kit — negativos:**
- Não tem o conceito de "delta spec" — toda spec já nasce como documento final, então não há um mecanismo nativo para expressar "isso modifica um requisito que já existia em outra feature" (tive que tratar `001-prediction-stats` como uma feature nova e independente, mesmo reaproveitando módulos já existentes de `add-prediction-history`).
- Mais arquivos por feature (spec, plan, research, data-model, contracts, quickstart, tasks — 7 arquivos, contra 4 do OpenSpec) — mais verboso para uma mudança pequena como esta.
- Setup inicial mais pesado (`specify init` instala scripts, templates, skills, uma "constitution" ainda vazia) — overhead desnecessário para quem já está no meio de um projeto com convenções estabelecidas.

## Comparação do código gerado

A funcionalidade `001-prediction-stats` (Spec Kit) e as duas funcionalidades feitas com OpenSpec seguem exatamente o mesmo padrão arquitetural no código: uma função pura em `history.py` (camada de storage) + uma rota fina em `main.py` (camada HTTP) + testes em `tests/`. Isso não é coincidência da ferramenta — é porque em ambos os casos usei o mesmo agente (eu) seguindo as convenções já estabelecidas no projeto; a ferramenta de SDD influenciou o *processo de planejamento*, não a *arquitetura do código resultante*.

A única diferença de código atribuível diretamente à ferramenta: a spec do Spec Kit, por trazer um `contracts/stats-api.md` explícito com o formato exato de sucesso (200) e falha (503), tornou a tarefa de implementar o tratamento de erro (FR-006) mais direta — o formato da resposta de erro já estava decidido antes de escrever qualquer código. No fluxo OpenSpec das duas features anteriores, esse tipo de detalhe (formato exato de erro) ficou mais faseado dentro do `design.md`/`tasks.md`, sem um contrato de API isolado.

Todas as 3 funcionalidades atendem integralmente aos requisitos especificados, com testes automatizados cobrindo os cenários principais e de borda — validado com `pytest` (20/20 testes passando) e, quando aplicável, verificação manual em navegador real.

## O que foi aprendido

Nenhuma das duas ferramentas resolve escrever a spec por você — em ambos os casos o trabalho real de pensar em regras de negócio, casos de borda e critérios de aceite continua sendo humano. A diferença está em **como cada uma estrutura esse pensamento**: OpenSpec puxa para "o que muda em relação ao que já existe", Spec Kit puxa para "quais fatias de valor entrego, em que ordem". Para features que modificam capabilities já especificadas (como `add-uncertain-diagnosis-flag`), OpenSpec pareceu mais natural. Para uma feature nova e isolada (como `001-prediction-stats`), Spec Kit deu uma estrutura de priorização (MVP primeiro) que o OpenSpec não força.
