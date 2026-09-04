## Why

Cacau growers in the CacauClima region lack an accessible way to identify pests, diseases, or dehydration stress from a leaf photo. This project is a proof-of-concept computer vision model to test whether pest/phytosanitary conditions can be identified from cacao leaf images, serving both as the ML deliverable for the Aprendizado Profundo course and as an early technical exploration for the broader CacauClima initiative (see the LLM/RAG macro-requirements doc, which covers a much larger scope not addressed here). No labeled dataset currently exists for this task; it must be assembled, most likely by curating community-contributed observations from iNaturalist.org.

## What Changes

- Assemble a labeled image dataset of cacau leaves showing pest damage, disease symptoms, and/or dehydration, sourced primarily from iNaturalist.org (and other public sources if needed), organized into a healthy vs. affected (and, if data allows, per-condition) classification scheme.
- Train an image classification model (transfer learning on a standard CNN backbone) to predict leaf condition from an uploaded photo, evaluated for accuracy/feasibility given the small, informally-collected dataset.
- Build a minimal inference service that loads the trained model and returns a prediction for a submitted image.
- Build a simple web frontend where a user uploads a leaf photo and views the predicted condition.
- Produce a completed ML/Data Project Canvas documenting problem, data sources, target, features, and pitch framing for the course deliverable.

## Capabilities

### New Capabilities
- `cacao-leaf-dataset`: acquisition, labeling, and organization of the cacau leaf image dataset (from iNaturalist and other sources) used for training and evaluation.
- `leaf-disease-classifier`: training pipeline that fits and evaluates the image classification model on the curated dataset, producing a saved model artifact.
- `leaf-inference-service`: a service that loads the trained model artifact and exposes a prediction endpoint for a submitted leaf image.
- `leaf-upload-frontend`: a simple web UI for uploading a leaf image and displaying the predicted condition returned by the inference service.

## Impact

- New repository structure for dataset scripts/notes, training code, a small inference API, and a frontend app.
- No existing code or specs are modified (greenfield project).
- Dependency on external data availability/quality from iNaturalist.org; dataset size and label reliability are the primary feasibility risks and will shape what the trained model can realistically demonstrate.
