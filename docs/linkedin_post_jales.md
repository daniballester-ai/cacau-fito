# Post LinkedIn (Jales) — Método STAR

*(texto pronto para publicar; ajustar handles/menções conforme preferência)*

---

Fiz uma pergunta simples pro meu agente de IA no meio do desenvolvimento: "apaga essa pasta de teste aí". A resposta veio na hora: bloqueado. E foi exatamente isso que eu queria testar.

**A situação**

Na disciplina de Desenvolvimento de Software com IA, do doutorado profissional em Tecnologia da Informação (PPGTI) que faço no IMD/UFRN, o desafio não era só entregar um sistema funcionando: era entregar um sistema construído com um agente de IA como par de desenvolvimento, sem perder o controle sobre o que ele podia ou não fazer sozinho. Trabalhamos num protótipo de classificação de imagem (diagnóstico visual aplicado a uma área agrícola), mas o produto final foi só o pretexto: o que a gente avaliou de verdade foi o processo.

**A tarefa**

Definir, na prática (não só na teoria), até onde a autonomia do agente ia. Ele podia planejar, especificar, implementar e testar de ponta a ponta sem pedir aprovação a cada passo. Mas duas coisas nunca podiam passar batido: qualquer endpoint novo exposto publicamente, e qualquer ação irreversível.

**A ação**

Configuramos guardrails de verdade no harness do agente, não só como recomendação escrita: regras que bloqueiam comandos destrutivos (`rm -rf`, reset forçado no git) e leitura de arquivos com credenciais. Testamos ao vivo, durante o próprio desenvolvimento, pedindo exatamente essas ações proibidas, e o bloqueio aconteceu de verdade, antes de qualquer efeito no sistema de arquivos.

Junto com isso, um checkpoint humano obrigatório antes de qualquer endpoint ir para produção: o agente implementa e testa, mas a decisão final de "isso pode ir pro ar" continua sendo nossa. Toda funcionalidade nasceu de uma especificação (comparamos duas ferramentas de SDD diferentes na prática) antes de qualquer código ser escrito, com critérios de aceite testáveis e casos de borda reais, não hipotéticos.

**O resultado**

Um sistema funcional e testado, mas o que mais me marcou foi um bug bobo de CSS que só apareceu quando testamos de verdade num navegador: nenhuma leitura do código gerado teria pego aquilo. Ficou a lição prática: usar IA pra desenvolver não é abrir mão de controle, é decidir com clareza onde a autonomia compensa e onde a revisão humana (ou um bloqueio estrutural) precisa continuar existindo.

#DesenvolvimentoDeSoftware #InteligenciaArtificial #EngenhariaDeSoftware #PPGTI #UFRN

---

**Jales Monteiro** e **Danielle Ballester**
