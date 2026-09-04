## MODIFIED Requirements

### Requirement: Image upload and result display
The frontend SHALL let a user select or upload a single leaf image and display the predicted condition and confidence score returned by the inference service, visually distinguishing an uncertain result from a confident one.

#### Scenario: Successful prediction displayed
- **WHEN** a user uploads a valid leaf image and submits it
- **THEN** the page displays the predicted condition label and confidence score returned by the inference service

#### Scenario: Prediction error surfaced to the user
- **WHEN** the inference service returns an error (e.g., unsupported file type or service failure)
- **THEN** the page displays a clear message to the user instead of failing silently or showing a blank result

#### Scenario: Uncertain result is visually distinguished
- **WHEN** the inference service returns a prediction with `is_uncertain: true`
- **THEN** the page displays a visible "resultado incerto" indicator alongside the label and confidence, instead of presenting the result exactly like a confident one

#### Scenario: Confident result displayed as before
- **WHEN** the inference service returns a prediction with `is_uncertain: false`
- **THEN** the page displays the result the same way it did before this change, with no uncertainty indicator
