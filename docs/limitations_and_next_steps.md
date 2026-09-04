# Limitações, ressalvas de avaliação e próximos passos — CacauFito

## Limitações do dataset

- O dataset primário (Amini Cocoa Contamination Dataset) cobre apenas 3 condições (sadia, CSSVD, antracnose) das várias pragas/doenças relevantes para o cacaueiro no Sul da Bahia (ex.: vassoura-de-bruxa/*Moniliophthora perniciosa*, podridão parda/*Phytophthora* spp., ataque de percevejo/mirídeo, cochonilha). Nenhuma dessas foi encontrada em dataset público pronto para uso — ficam fora do escopo deste PoC.
- As imagens foram coletadas fora do Brasil (contexto do desafio Zindi/Amini), não especificamente na região cacaueira baiana — variação de variedade de cacau, iluminação, ângulo de câmera e estágio da doença pode diferir do que se encontraria em campo no Sul da Bahia.
- As anotações originais são por *bounding box* (múltiplas por imagem); foram colapsadas em um rótulo único por imagem (classe majoritária), o que descarta a localização da lesão — aceitável para este PoC de classificação, mas não para uma futura tarefa de detecção/localização.
- O split de treino/validação/teste foi construído localmente (70/15/15, estratificado, seed fixa) a partir do `Train.csv`, já que o `Test.csv` oficial da competição não tem gabarito.

## Ressalvas sobre a avaliação do modelo

- Acurácia de teste: **77,8%** (646/830), com precisão/recall por classe: sadia 0,73/0,80, CSSVD 0,78/0,79, antracnose 0,84/0,74. Todas as classes têm 200+ amostras de teste (acima do piso de 50 definido no `design.md`), então nenhuma classe foi sinalizada como estatisticamente pouco confiável.
- A principal confusão do modelo é entre **sadia e CSSVD** (ver matriz de confusão no notebook de treino) — plausível, já que sintomas iniciais de CSSVD podem ser sutis visualmente.
- O resultado foi obtido com um backbone congelado (EfficientNet-B0 pré-treinada, apenas a camada classificadora foi ajustada) — não foi feito fine-tuning completo nem busca de hiperparâmetros; há margem de melhoria não explorada por restrição de tempo/escopo do PoC.
- Este resultado é um **sinal de viabilidade para fins de curso e demonstração**, não uma validação clínica/agronômica — não deve ser usado como base para decisão de manejo agrícola real sem validação adicional por especialista fitossanitário.

## Próximos passos (se o projeto avançar para o CacauClima)

1. Coletar e rotular imagens de campo do Sul da Bahia (com apoio de agrônomos/CEPLAC), cobrindo as doenças/pragas prioritárias da região (vassoura-de-bruxa, podridão parda) — hoje ausentes do dataset usado.
2. Avaliar fine-tuning completo do backbone (não só a camada classificadora) e comparar outras arquiteturas (ex.: EfficientNet-B3, ConvNeXt-Tiny) já que há folga de tempo de treino na GPU gratuita usada.
3. Investigar se a confusão sadia/CSSVD melhora com mais dados ou com uma segunda etapa de verificação (ex.: modelo de detecção de lesão antes da classificação).
4. Se integrado ao CacauClima, conectar esta capacidade de classificação de imagem ao pipeline de ciência cidadã e ao assistente conversacional (RAG/LLM) já mapeado no documento de macrorrequisitos do CacauClima, permitindo que um produtor envie uma foto e receba tanto o diagnóstico visual quanto uma recomendação textual.
5. Formalizar processo de coleta de consentimento/licença para imagens enviadas por produtores reais, dado que o dataset atual (terceiros, CC BY 4.0) não cobre esse cenário de uso.
