# cacao-leaf-dataset Specification

## Purpose

Provides a labeled collection of cacau leaf images (healthy vs. affected by pest/disease/dehydration) suitable for training and evaluating an image classifier, since no such dataset currently exists.

## Requirements

### Requirement: Dataset composition
The dataset SHALL contain cacau leaf images labeled with condition (healthy, cssvd, or anthracnose), built primarily from the Amini Cocoa Contamination Dataset (CC BY 4.0), with each image assigned a single whole-image label derived from its annotations, and optionally extended with additional cacau (Theobroma cacao) leaf photos sourced from iNaturalist.org and manually labeled by the team.

#### Scenario: Minimum viable dataset assembled
- **WHEN** the dataset collection step completes
- **THEN** there are at least enough labeled images per class to run a train/validation/test split (target: a minimum per-class count documented in the dataset notes, e.g. at least 50 images per class as a PoC floor)

#### Scenario: Insufficient data discovered
- **WHEN** fewer images than the documented minimum are found for a class after searching iNaturalist and other public sources
- **THEN** the dataset documentation SHALL record the shortfall and the classifier capability SHALL treat that class as out of scope or merge it into a coarser category rather than silently training on too few examples

### Requirement: Data provenance and licensing
Each image included in the dataset SHALL retain a record of its source (URL or observation ID) and license/usage terms, so the dataset can be defended as legitimately usable for a course/research PoC.

#### Scenario: Image traceable to source
- **WHEN** an image is added to the dataset
- **THEN** a corresponding metadata entry records its origin (source platform, observation ID or URL, and license) alongside the assigned label

### Requirement: Train/validation/test split
The dataset SHALL be partitioned into training, validation, and test subsets with no image appearing in more than one subset.

#### Scenario: Split is disjoint
- **WHEN** the dataset is partitioned for training
- **THEN** the training, validation, and test subsets contain no overlapping images
