"""Loads the trained cacao leaf classifier artifact and exposes a predict() function.

Reads the model architecture, image size, and class order from label_mapping.json
so the served labels always match what the training pipeline produced (see
specs/leaf-inference-service/spec.md — Requirement: Model version consistency).
"""
import io
import json
import os

import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image, UnidentifiedImageError
from torchvision import transforms
from torchvision.models import efficientnet_b0

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models")

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

SUPPORTED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/jpg",
    "image/webp",
    "image/pjpeg",
    "image/jfif",
    "application/octet-stream",
}


class InvalidImageError(Exception):
    """Raised when the uploaded file is missing or not a supported, decodable image."""


LOW_CONFIDENCE_THRESHOLD = 0.6
CLOSE_CALL_MARGIN = 0.1


def compute_uncertainty(probabilities: dict):
    """Returns (is_uncertain, uncertainty_reason) from a class -> probability mapping.

    Checks low confidence before close-call, so a result that is both is reported
    as "low_confidence" (see design.md — Decisions).
    """
    sorted_probs = sorted(probabilities.values(), reverse=True)
    top_prob = sorted_probs[0]
    second_prob = sorted_probs[1] if len(sorted_probs) > 1 else 0.0

    if top_prob < LOW_CONFIDENCE_THRESHOLD:
        return True, "low_confidence"
    if (top_prob - second_prob) < CLOSE_CALL_MARGIN:
        return True, "close_call"
    return False, None


class LeafClassifier:
    def __init__(self, models_dir=MODELS_DIR):
        with open(os.path.join(models_dir, "label_mapping.json")) as f:
            mapping = json.load(f)

        if mapping["architecture"] != "efficientnet_b0":
            raise ValueError(f"Unsupported architecture in label_mapping.json: {mapping['architecture']}")

        self.classes = mapping["classes"]
        self.image_size = mapping["image_size"]

        self.transform = transforms.Compose([
            transforms.Resize((self.image_size, self.image_size)),
            transforms.ToTensor(),
            transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
        ])

        model = efficientnet_b0(weights=None)
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, len(self.classes))
        state_dict = torch.load(os.path.join(models_dir, "cacao_leaf_classifier.pt"), map_location="cpu")
        model.load_state_dict(state_dict)
        model.eval()
        self.model = model

    def predict(self, image_bytes: bytes):
        if not image_bytes:
            raise InvalidImageError("No file was uploaded.")
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except UnidentifiedImageError as exc:
            raise InvalidImageError("File is not a valid, decodable image.") from exc

        tensor = self.transform(image).unsqueeze(0)
        with torch.no_grad():
            logits = self.model(tensor)
            probs = F.softmax(logits, dim=1).squeeze(0)

        top_idx = int(torch.argmax(probs).item())
        return {
            "label": self.classes[top_idx],
            "confidence": float(probs[top_idx]),
            "probabilities": {cls: float(probs[i]) for i, cls in enumerate(self.classes)},
        }
