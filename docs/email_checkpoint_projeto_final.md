**Para:** jean.lima@imd.ufrn.br
**Assunto:** [Desenvolvimento de Software com IA] Checkpoint 05/09 — Projeto Final (Dupla)

Prezado Prof. Jean Mário,

Segue o checkpoint obrigatório de 05/09 referente ao Projeto Final da disciplina Desenvolvimento de Software com IA.

**Membros do grupo**

- Danielle Magalhães Ballester — Matrícula 20261022137
- Jales Anderson de Assis Monteiro — Matrícula 20261012284

**Ideia do projeto**

Vamos dar continuidade ao **CacauFito**, projeto de visão computacional que já iniciamos na disciplina, que classifica a condição fitossanitária de folhas de cacau (sadia, CSSVD ou antracnose) a partir de uma foto, com um serviço de inferência e um frontend de upload. Para o Projeto Final, vamos ampliar o sistema até um mínimo de 10 requisitos funcionais completos e demonstráveis, mantendo o foco em Spec-Driven Development e no harness de controle de agentes de IA como já vínhamos praticando.

**Requisitos funcionais a serem implementados**

Já implementados (base herdada da atividade anterior):
1. Upload de imagem de folha de cacau e classificação automática (sadia / CSSVD / antracnose) via modelo de visão computacional (EfficientNet-B0).
2. Sinalização de resultado incerto quando a confiança do modelo é baixa ou há disputa acirrada entre as classes mais prováveis.
3. Histórico paginado de predições (imagem, rótulo previsto, confiança, data).
4. Estatísticas agregadas de predições por classe.

Novos, a construir até a apresentação:
5. Feedback do usuário sobre o diagnóstico (confirmar ou corrigir o rótulo previsto), alimentando uma base para retreino futuro do modelo.
6. Exportação do histórico de predições em CSV.
7. Autenticação simples (cadastro/login), permitindo múltiplos usuários com histórico individual.
8. Painel de acompanhamento com gráfico da evolução dos diagnósticos ao longo do tempo.
9. Empacotamento e deploy containerizado (Docker/docker-compose) de toda a aplicação.
10. Documentação de API interativa (OpenAPI/Swagger) com exemplos de uso dos endpoints.

**Frameworks e tecnologias**

- **Backend**: Python 3.12, FastAPI
- **Modelo de IA**: PyTorch/torchvision (EfficientNet-B0, transfer learning), treinado em GPU gratuita do Kaggle
- **Persistência**: SQLite
- **Frontend**: HTML/CSS/JavaScript (com biblioteca de gráficos a definir para o painel, ex.: Chart.js)
- **Autenticação**: a definir na fase de design (ex.: FastAPI + sessão/JWT simples)
- **Empacotamento**: Docker / docker-compose
- **Especificação (SDD)**: OpenSpec e GitHub Spec Kit (já usados e comparados na atividade anterior)
- **Agente de IA / harness**: Claude Code

Ficamos à disposição para qualquer ajuste de escopo.

Atenciosamente,
Danielle Ballester e Jales Monteiro
