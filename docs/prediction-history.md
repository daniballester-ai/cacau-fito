# Histórico de predições

Feature especificada em `openspec/changes/add-prediction-history/` (ver `specs/prediction-history/spec.md` para o contrato completo).

## Armazenamento

- **Local:** SQLite em `history/history.db` (raiz do projeto), criado automaticamente na primeira execução.
- **Imagens:** salvas em `history/images/`, referenciadas por caminho no banco.
- **Retenção:** limitada às **200 entradas mais recentes**. Ao inserir uma nova entrada que excederia esse limite, a mais antiga (linha + arquivo de imagem) é removida automaticamente.

## API

- `GET /history?limit=&offset=` — lista paginada, mais recente primeiro. `limit` padrão 20, máximo 100. Resposta: `{items, total, next_offset}` (`next_offset: null` quando não há mais páginas).
- Registro é automático a cada chamada bem-sucedida de `POST /predict` — não há endpoint separado para registrar manualmente.

## Página

`GET /history.html` — página mínima que lista rótulo, confiança e data/hora de cada predição, com paginação "Carregar mais" e mensagem de estado vazio. Sem login, como o restante do PoC.

## Limitação conhecida

O histórico é armazenado em disco local (arquivo SQLite + imagens). Se o serviço rodar em um ambiente efêmero (ex.: container sem volume persistente), o histórico é perdido a cada reinício. Aceitável para este PoC; não resolvido nesta iteração.
