"""Verifies the saved model artifact reloads and reproduces the reported test accuracy
using the same manifest/split (data/amini/manifest.csv, built with the same seed=42).
Run locally on CPU — slower than the Kaggle GPU run but only needs to confirm consistency,
not match wall-clock speed.
"""
import json
import os

import pandas as pd
import torch
import torch.nn as nn
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from torchvision.models import efficientnet_b0

HERE = os.path.dirname(__file__)
DATA_ROOT = os.path.join(HERE, "..", "data", "amini")

with open(os.path.join(HERE, "label_mapping.json")) as f:
    label_mapping = json.load(f)

CLASSES = label_mapping["classes"]
IMAGE_SIZE = label_mapping["image_size"]

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

eval_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
])


class CacaoLeafDataset(Dataset):
    def __init__(self, split, transform=None):
        manifest = pd.read_csv(os.path.join(DATA_ROOT, "manifest.csv"))
        self.rows = manifest[manifest["split"] == split].reset_index(drop=True)
        self.transform = transform
        self.class_to_idx = {c: i for i, c in enumerate(CLASSES)}

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, idx):
        row = self.rows.iloc[idx]
        image = Image.open(os.path.join(DATA_ROOT, row["ImagePath"])).convert("RGB")
        if self.transform:
            image = self.transform(image)
        return image, self.class_to_idx[row["label"]]


test_ds = CacaoLeafDataset("test", transform=eval_transform)
test_loader = DataLoader(test_ds, batch_size=32, shuffle=False)
print("Reloaded test split size:", len(test_ds))

model = efficientnet_b0(weights=None)
model.classifier[1] = nn.Linear(model.classifier[1].in_features, len(CLASSES))
state_dict = torch.load(os.path.join(HERE, "cacao_leaf_classifier.pt"), map_location="cpu")
model.load_state_dict(state_dict)
model.eval()
print("Weights loaded successfully; architecture matches label_mapping.json.")

correct, seen = 0, 0
with torch.no_grad():
    for imgs, labels in test_loader:
        outputs = model(imgs)
        preds = outputs.argmax(1)
        correct += (preds == labels).sum().item()
        seen += labels.size(0)

acc = correct / seen
print(f"Reloaded-model test accuracy: {acc:.4f} ({correct}/{seen})")

with open(os.path.join(HERE, "eval_report.json")) as f:
    reported_acc = json.load(f)["accuracy"]
print(f"Reported (Kaggle-run) test accuracy: {reported_acc:.4f}")
print(f"Difference: {abs(acc - reported_acc):.4f}")
