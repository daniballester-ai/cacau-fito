# ADR-0001: Transfer learning com EfficientNet-B0 (backbone congelado) para o classificador de folhas

**Status:** Aceita
**Data:** 2026-08-28

## Contexto

Precisávamos treinar um classificador de imagem para 3 classes (sadia, CSSVD, antracnose) a partir do Amini Cocoa Contamination Dataset — 5.529 imagens rotuladas, um volume médio para treinar uma rede convolucional do zero, e sem GPU local disponível (só GPU gratuita do Kaggle, com cota de tempo limitada).

## Decisão

Usamos **EfficientNet-B0 pré-treinada em ImageNet**, com o backbone convolucional **congelado** e apenas a camada final (`Linear(1280 → 3)`) treinada. Hiperparâmetros (`learning rate`, `weight_decay`) posteriormente ajustados por busca sistemática com Optuna (ver notebook de treino), em vez de fixados manualmente desde o início.

## Alternativas consideradas

- **Treinar uma CNN do zero**: rejeitada — 5.529 imagens é pouco para aprender características visuais úteis do zero; exigiria muito mais dados ou muito mais tempo de GPU do que tínhamos disponível.
- **Fine-tuning completo do backbone** (não só a última camada): rejeitada nesta primeira iteração — mais parâmetros treináveis aumentam o risco de overfitting com um dataset deste porte, e o backbone congelado já usa características genéricas de baixo/médio nível aprendidas do ImageNet que se aplicam bem a fotos de folha. Documentado como próximo passo em `docs/limitations_and_next_steps.md`.
- **Arquiteturas maiores (EfficientNet-B3+, ResNet50)**: rejeitadas para esta iteração — mais parâmetros e mais tempo de treino, sem garantia de ganho proporcional dado o tamanho do dataset; EfficientNet-B0 é o ponto de partida mais barato e mais rápido de validar.

## Consequências

- Treino rápido (~55 min para 15 épocas na GPU gratuita do Kaggle), permitindo iterar (incluindo a busca de hiperparâmetros com Optuna) dentro do tempo disponível.
- Acurácia de teste de 77,8% (78,1% após Optuna) — um sinal real de viabilidade, mas não um resultado de produção; documentado explicitamente como limitação em `docs/limitations_and_next_steps.md`.
- Caminho claro para melhoria futura (fine-tuning completo, mais dados, arquitetura maior) sem precisar refazer o pipeline — só trocar a etapa de treino.
