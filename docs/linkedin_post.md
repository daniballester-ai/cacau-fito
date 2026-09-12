# Post LinkedIn — Método STAR

*(texto pronto para publicar; ajustar handles/menções conforme preferência)*

---

Nas últimas semanas, encarei um desafio da disciplina de Desenvolvimento de Software com IA, do doutorado profissional em Tecnologia da Informação (PPGTI) que faço no IMD/UFRN, do jeito que faria em qualquer projeto real: especificando antes de codificar, e comparando ferramentas na prática em vez de escolher uma de ouvido.

**A situação**

Todo projeto de IA tem o mesmo risco: um agente que "já sai codificando" produz algo que funciona no primeiro teste e quebra no segundo caso de borda que ninguém pensou em escrever. Queríamos evitar exatamente isso, num protótipo de classificação de imagem (visão computacional aplicada a diagnóstico em uma área agrícola), construído inteiramente com um agente de IA como par de desenvolvimento.

**A tarefa**

Em vez de escolher uma ferramenta de Spec-Driven Development e seguir em frente, decidimos comparar duas abordagens de verdade, na mesma base de código: o OpenSpec, que documenta cada mudança como um "delta" sobre requisitos já existentes (ADDED / MODIFIED / REMOVED), e o GitHub Spec Kit, que organiza tudo em torno de user stories priorizadas (P1, P2, P3) com um MVP explícito desde o planejamento.

**A ação**

Usamos o OpenSpec nas mudanças que alteravam comportamento já publicado, onde a rastreabilidade "o que exatamente mudou nesse requisito" importava mais. Usamos o Spec Kit numa funcionalidade nova e isolada, onde a pergunta era "qual fatia eu entrego primeiro". Cada especificação virou requisitos testáveis, critérios de aceite no formato Given/When/Then (com casos de borda reais, não hipotéticos) e um plano de tarefas revisado antes de qualquer linha de código.

Isso não ficou só no papel: configuramos guardrails reais no harness do agente (bloqueio de comandos destrutivos e de leitura de segredos), testados ao vivo durante o desenvolvimento, e um checkpoint humano obrigatório antes de qualquer endpoint novo ir para produção. Um bug real de CSS só apareceu quando testamos de verdade num navegador (não bastou ler o código gerado), o que reforçou por que "IA que implementa" e "humano que aprova" precisam continuar sendo papéis separados.

**O resultado**

Um sistema funcional, testado, com o histórico de decisões documentado do início ao fim, e uma comparação concreta (não teórica) de quando cada ferramenta de SDD compensa mais. Principal aprendizado: nenhuma ferramenta substitui pensar em requisitos e casos de borda antes de codificar; elas só mudam *como* essa disciplina fica estruturada. Para quem trabalha com agentes de IA no desenvolvimento: especificar antes não é burocracia, é o que separa "funcionou no meu teste" de "funciona de verdade".

#DesenvolvimentoDeSoftware #InteligenciaArtificial #SpecDrivenDevelopment #EngenhariaDeSoftware #PPGTI #UFRN

---

**Danielle Ballester** e **Jales Monteiro**
