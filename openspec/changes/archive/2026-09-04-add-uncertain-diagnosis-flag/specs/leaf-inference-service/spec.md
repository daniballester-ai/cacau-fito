## MODIFIED Requirements

### Requirement: Image prediction endpoint
The service SHALL accept a single leaf image upload and return the predicted condition label along with a confidence score, plus an uncertainty flag computed from a documented confidence rule.

#### Scenario: Valid image submitted
- **WHEN** a client submits a supported image file (JPEG or PNG) to the prediction endpoint
- **THEN** the service returns the predicted condition label and a confidence score for that prediction

#### Scenario: Unsupported input rejected
- **WHEN** a client submits a file that is not a supported image format, or no file at all
- **THEN** the service returns an error response explaining the input is invalid, without crashing

#### Scenario: Low-confidence prediction flagged as uncertain
- **WHEN** the top predicted class's confidence is below the documented confidence threshold
- **THEN** the response includes `is_uncertain: true` and `uncertainty_reason: "low_confidence"`, alongside the existing label, confidence, and probabilities

#### Scenario: Close call between top classes flagged as uncertain
- **WHEN** the difference between the top two classes' probabilities is below the documented close-call margin, even if the top confidence itself is above the low-confidence threshold
- **THEN** the response includes `is_uncertain: true` and `uncertainty_reason: "close_call"`

#### Scenario: Confident prediction is not flagged
- **WHEN** the top predicted class's confidence is at or above the confidence threshold and it is not a close call with the runner-up
- **THEN** the response includes `is_uncertain: false` and no `uncertainty_reason`
