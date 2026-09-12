# Tema da apresentação

Apresentação para o Projeto Final da disciplina "Desenvolvimento de Software com IA" (PPGTI/UFRN) — projeto CacauFito, classificador de folhas de cacau por visão computacional, desenvolvido com Spec-Driven Development e agente de IA (Claude Code).

A apresentação deve cobrir, em slides bem visuais com elementos animados, gráficos, fluxos e diagramas:

1. Contexto e motivação do problema (cacauicultores sem forma acessível de identificar pragas/doenças foliares)
2. Processo de especificação SDD (OpenSpec e GitHub Spec Kit, comparação das duas ferramentas)
3. Harness e controle de agentes (nível de autonomia, guardrail real configurado com evidência de bloqueio, checkpoint humano antes de expor endpoint)
4. Decisões de arquitetura (ADRs: EfficientNet-B0 com transfer learning, SQLite para histórico) + diagrama de arquitetura (C4 container, pipeline de dados, sequência de uma predição)
5. Modelos, estratégias e ferramentas de IA usadas (Claude Sonnet 5, Claude Code, OpenSpec, Spec Kit, pytest, Playwright, Kaggle+Optuna)
6. Demonstração funcional: upload de folha, diagnóstico, resultado incerto sinalizado, histórico de predições, estatísticas
7. Resultados do modelo (77,8% para 78,1% de acurácia com Optuna, gráfico de métricas antes/depois)
8. Aprendizados e dificuldades reais (bug de especificidade CSS no atributo hidden, só encontrado testando em navegador real)
9. Próximos passos (6 requisitos funcionais adicionais já especificados: feedback do usuário, exportação CSV, autenticação multi-usuário, dashboard de estatísticas, deploy Docker, docs de API interativa)

Toda a documentação-fonte já existe no repositório em C:\Fitec\CacauFito\docs\ (ADRs, architecture-diagram.md, guardrail_evidence.md, ferramentas_ia.md, comparacao_sdd_tools.md, relatorio_final.md, ml_canvas.md) e README.md — a apresentação deve se basear nesse conteúdo real, não inventar dados.
