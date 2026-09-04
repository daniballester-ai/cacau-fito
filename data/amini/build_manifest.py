"""Builds an image-level manifest from the Amini Cocoa Contamination Dataset's
box-level Train.csv, and splits it into train/val/test with no overlap.

Source: https://www.kaggle.com/datasets/ohagwucollinspatrick/amini-cocoa-contamination-dataset
License: CC BY 4.0
"""
import pandas as pd
from sklearn.model_selection import train_test_split

SEED = 42
VAL_FRAC = 0.15
TEST_FRAC = 0.15

df = pd.read_csv("Train.csv")

# Collapse per-box annotations into a single whole-image label.
# Only 6/5529 images contain more than one distinct class; for those,
# take the majority class (ties broken by first-seen class).
def majority_class(s):
    return s.value_counts().idxmax()

manifest = (
    df.groupby("Image_ID")
    .agg(label=("class", majority_class), ImagePath=("ImagePath", "first"), num_boxes=("class", "size"))
    .reset_index()
)
manifest["source"] = "amini-cocoa-contamination-dataset"
manifest["license"] = "CC BY 4.0"

print("Total images:", len(manifest))
print(manifest["label"].value_counts())

mixed = df.groupby("Image_ID")["class"].nunique()
mixed_ids = mixed[mixed > 1].index.tolist()
print(f"Mixed-class images collapsed to majority label ({len(mixed_ids)}):", mixed_ids)

# Stratified split: train/val/test, disjoint by construction (each image assigned to exactly one split).
train_val, test = train_test_split(
    manifest, test_size=TEST_FRAC, stratify=manifest["label"], random_state=SEED
)
train, val = train_test_split(
    train_val, test_size=VAL_FRAC / (1 - TEST_FRAC), stratify=train_val["label"], random_state=SEED
)

train["split"] = "train"
val["split"] = "val"
test["split"] = "test"

full = pd.concat([train, val, test], ignore_index=True)

# Verify disjointness
assert len(set(train["Image_ID"]) & set(val["Image_ID"])) == 0
assert len(set(train["Image_ID"]) & set(test["Image_ID"])) == 0
assert len(set(val["Image_ID"]) & set(test["Image_ID"])) == 0
assert len(full) == len(manifest)

full.to_csv("manifest.csv", index=False)

print("\nPer-split, per-class counts:")
print(full.groupby(["split", "label"]).size().unstack(fill_value=0))
print("\nSaved manifest.csv with", len(full), "rows")
