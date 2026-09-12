# ADR-0002: SQLite como storage do histórico de predições

**Status:** Aceita
**Data:** 2026-09-04

## Contexto

O serviço de inferência (`src/inference_service/`) precisava passar a persistir cada predição (histórico paginado, estatísticas agregadas) — o primeiro estado do lado servidor no projeto, que até então era completamente stateless por requisição.

## Decisão

Usamos **SQLite via o módulo `sqlite3` do Python** (`src/inference_service/history.py`), um arquivo local (`history/history.db`) com uma tabela `predictions`, mais imagens salvas em `history/images/`.

## Alternativas consideradas

- **Arquivo JSON simples**: rejeitada — paginação e ordenação exigiriam carregar e reordenar o arquivo inteiro a cada requisição, e escritas concorrentes de múltiplas requisições não são seguras de forma atômica.
- **Banco gerenciado (Postgres) com ORM completo**: rejeitada — peso desnecessário para um PoC com uma tabela pequena e um único processo; adicionaria uma dependência de infraestrutura externa (serviço de banco rodando) que o projeto não precisa nesta fase.

## Consequências

- Sem dependência nova (SQLite vem embutido no Python), consultas reais (`ORDER BY`/`LIMIT`/`OFFSET`/`GROUP BY`) em vez de reimplementar paginação e agregação em Python.
- Escritas concorrentes seguras o suficiente para a escala do PoC, mas não projetadas para alta concorrência — documentado como limitação conhecida em `docs/prediction-history.md`.
- Histórico é perdido se o storage for efêmero (ex.: container sem volume persistente) — resolvido pela decisão de montar `history/` como volume externo no Docker (`add-docker-deployment`).
