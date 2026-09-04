## Context

This is a proof-of-concept for two academic purposes at once: the Aprendizado Profundo course (train a real model) and Tópicos Avançados em Engenharia de Software 2 (use OpenSpec/SDD to structure delivery). No cacau leaf pest/disease dataset exists yet; it must be built from public sources, primarily iNaturalist.org observations. See proposal.md for motivation and specs/ for the behavior contracts. Scope is intentionally small: one model, one prediction endpoint, one minimal upload page — this is not the CacauClima production system (see the LLM/RAG macro-requirements doc for that larger scope).

## Goals / Non-Goals

**Goals:**
- Prove or disprove, within the time available, that a useful signal for cacau leaf condition (pest/disease/dehydration vs. healthy) can be learned from a small, community-sourced image dataset.
- Produce a trained model, a minimal inference API, and a minimal upload UI end-to-end.
- Keep the pipeline reproducible enough to document in the course deliverables (dataset notes, training script, metrics).

**Non-Goals:**
- Production-grade accuracy, scalability, or uptime guarantees.
- Multi-class fine-grained diagnosis beyond what the available data supports (may collapse to healthy vs. affected if per-disease data is too sparse).
- Integration with the broader CacauClima platform (remote sensing, climate data, RAG/LLM advisory) — that is a separate, much larger initiative.
- User accounts, persistence of uploaded images, or analytics.

## Decisions

**Dataset sourcing: the Amini Cocoa Contamination Dataset is the primary and sufficient source; iNaturalist is an optional stretch supplement, not a requirement.**
Verified on 2026-08-27 by downloading and inspecting the dataset directly (not just its listing): **Amini Cocoa Contamination Dataset** (Kaggle: https://www.kaggle.com/datasets/ohagwucollinspatrick/amini-cocoa-contamination-dataset, license CC BY 4.0). `Train.csv` contains 5,529 unique labeled cacao leaf photos (field images, not studio/lab shots) across 3 classes with bounding-box annotations: `healthy` (4,280 boxes), `cssvd` — cocoa swollen shoot virus disease (3,241 boxes), `anthracnose` (2,271 boxes). Only 6 of 5,529 images contain more than one distinct class, so the bounding boxes can be safely collapsed into a **single whole-image label per photo** (majority/only class present), avoiding object-detection complexity entirely for this PoC. The dataset's own `Test.csv` (1,626 images) has no ground truth — it is a competition (Zindi/Amini) submission set — so this project must carve its own held-out test split from the labeled `Train.csv` images (see Requirement: Train/validation/test split).

This single source is large enough (well above the PoC per-class floor) that the originally-planned iNaturalist collection and manual labeling step is now a stretch goal for additional diversity/robustness, not a requirement to reach a working model — it de-risks the project by removing dependence on unlabeled, manually-curated data. If pursued, iNaturalist (`api.inaturalist.org`, taxon `Theobroma cacao`, `photos=true`, ~10,500 photos available, no condition annotations, mixed per-photo licenses, ~1 req/sec pacing) remains available exactly as previously scoped.

Other candidates evaluated and deprioritized during the same survey: CocoaMoniliaDataSet (Zenodo, 1,953 images, 4 classes, high-quality COCO/YOLO/segmentation annotations) and other Kaggle/GitHub cacao datasets are pod-level, not leaf-level — kept only as a fallback auxiliary/pretraining source, now unlikely to be needed. PlantVillage (54,306 images, 14 crops, no cacao) remains available only as a generic pretraining base, also now unlikely to be needed. GBIF, Pl@ntNet, and EOL have the same structural limitation as iNaturalist (species-ID only, no condition labels). No dedicated public image dataset was found for cacao's named diseases/pests individually beyond what Amini already covers (witches' broom/*Moniliophthora perniciosa*, black pod/*Phytophthora* spp., frosty pod rot/*Moniliophthora roreri*, mirid/capsid damage, mealybug are not separately represented in Amini and remain out of reach for this PoC).

**Labeling scheme: 3-class classification (healthy / cssvd / anthracnose), matching the Amini dataset's native labels.**
With per-class counts confirmed (4,280 / 3,241 / 2,271), all three classes clear the PoC floor comfortably, so there is no need to collapse to binary healthy-vs-affected — the original binary-first fallback is no longer necessary given real data in hand. Binary (healthy vs. affected) remains a documented fallback only if training reveals one class performs poorly enough to warrant merging (e.g., if cssvd and anthracnose prove visually indistinguishable to the model).

**Model architecture: transfer learning on EfficientNet-B0 (PyTorch/torchvision), trained via a Kaggle Notebook rather than locally.**
With a small dataset, training from scratch is infeasible; transfer learning is the standard approach for small-data image classification and is explicitly a course topic (Aprendizado Profundo). The local development machine has no GPU, so the training pipeline is a self-contained notebook: it downloads the Amini dataset via the Kaggle API, rebuilds the manifest/split, trains with a frozen EfficientNet-B0 backbone plus a fine-tuned classifier head, evaluates, and packages the resulting artifacts (model weights, label mapping, eval report) as a zip in `/kaggle/working/`. Originally scoped as a Google Colab notebook; switched to **Kaggle Notebooks** in practice (`notebooks/train_kaggle.ipynb`) since Kaggle Secrets makes Kaggle-API auth simpler when the dataset itself is already hosted on Kaggle, and Kaggle's free GPU quota was sufficient. This trades local reproducibility for practical training speed; the notebook is deterministic (fixed seed) so results should be reproducible run-to-run, provided the kernel session is not interrupted mid-run (an interruption between training and artifact-saving loses the in-memory model and requires a full re-run).

**Actual training run (2026-08-28, Kaggle, GPU, 15 epochs, ~55 min, "Save & Run All"):** held-out test set (830 images, disjoint from train/val) — overall accuracy **77.83%** (646/830), precision/recall/F1 per class: healthy 0.732/0.803/0.766, cssvd 0.781/0.786/0.783, anthracnose 0.837/0.740/0.786. All three test classes have 200+ samples (well above the 50-sample PoC floor), so no low-confidence caveats were triggered. Artifacts (`models/cacao_leaf_classifier.pt`, `label_mapping.json`, `eval_report.json`) were reloaded independently on CPU via `models/verify_reload.py` and reproduced the exact same test accuracy (0.7783, diff 0.0000), confirming the artifact is self-consistent and portable. This confirms the PoC's central feasibility question: a useful signal for cacao leaf condition **can** be learned from this dataset with a standard transfer-learning setup — good enough for a course demo, not for production-grade diagnosis.

**Inference service: a minimal HTTP API (single prediction endpoint) separate from the frontend.**
Keeping inference behind a small API (rather than embedding the model directly in the frontend) matches the spec's separation of `leaf-inference-service` and `leaf-upload-frontend`, and makes it possible to test the model independently of the UI.

**Frontend: a single-page minimal upload form, no framework requirement.**
The spec only requires upload + result display + error display; a minimal static page or lightweight framework app is sufficient and keeps implementation time low.

## Risks / Trade-offs

- [Dataset too small or too imbalanced to learn anything meaningful] → Mitigate by collapsing to binary classification, documenting the shortfall per the dataset spec's "Insufficient data discovered" scenario, and reporting evaluation caveats per the classifier spec's "Feasibility disclosure" requirement rather than overstating results.
- [iNaturalist labels are inconsistent or the "affected" condition is ambiguous (pest vs. disease vs. dehydration vs. normal leaf aging)] → Document labeling criteria used during curation; when in doubt, exclude ambiguous images rather than mislabel them.
- [Licensing of iNaturalist photos, and of the Amini/CocoaMonilia datasets, varies by observation/source] → Record license per image (dataset spec's provenance requirement) and only use images whose license permits this academic/research use; verify Kaggle/Zenodo dataset license terms explicitly before use, not just per-photo iNaturalist licenses.
- [Leaf-level labeled data (Amini + manually labeled iNaturalist) turns out too small even for binary classification] → Fall back to using PlantVillage-pretrained features (generic lesion/necrosis) and/or the pod-level CocoaMoniliaDataSet as auxiliary pretraining, documenting that the model is trained partly on non-leaf or non-cacao-specific imagery.
- [Model overfits given small data] → Use standard mitigations (data augmentation, transfer learning with frozen base layers, early stopping on validation loss); accept that results are a feasibility signal, not a production benchmark.
- [Time constraint: canvas due next day, full pipeline due later] → The ML canvas deliverable can be completed from the proposal/design content already captured here; dataset collection and training are the longer-lead tasks tracked in tasks.md.

## Open Questions

- Choice of deep learning framework (PyTorch vs. TensorFlow/Keras) is left to whoever implements the training pipeline; does not affect the spec-level behavior.
