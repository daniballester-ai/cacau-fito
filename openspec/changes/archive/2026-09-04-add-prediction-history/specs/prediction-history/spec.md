## Purpose

Persists a record of each prediction the inference service makes and exposes it for later browsing, so a person can see what was diagnosed over time instead of every prediction disappearing after the response is sent.

## ADDED Requirements

### Requirement: Prediction recording
The system SHALL record a history entry for every prediction the inference service successfully returns, including a timestamp, the predicted label, the confidence score, the per-class probabilities, and a reference to the submitted image.

#### Scenario: Successful prediction is recorded
- **WHEN** the inference service returns a successful prediction
- **THEN** a history entry is persisted containing the timestamp, predicted label, confidence, per-class probabilities, and a reference to the image

#### Scenario: Recording failure does not break the prediction response
- **WHEN** persisting the history entry fails for any reason (e.g., storage unavailable)
- **THEN** the prediction response is still returned to the client successfully, and the failure is logged rather than surfaced as a prediction error

#### Scenario: Rejected uploads are not recorded
- **WHEN** an uploaded file is rejected as unsupported or invalid (per the inference service's existing validation)
- **THEN** no history entry is created for that request

### Requirement: History listing
The system SHALL provide a way to list past prediction history entries, ordered most recent first, with pagination.

#### Scenario: Listing returns entries newest-first
- **WHEN** a client requests the prediction history with more than one entry recorded
- **THEN** the entries are returned ordered from most recent to oldest

#### Scenario: Listing is paginated
- **WHEN** a client requests a page of history with a page size smaller than the total number of entries
- **THEN** only that page's worth of entries is returned, along with enough information to request the next page

#### Scenario: Empty history
- **WHEN** a client requests the prediction history before any prediction has been recorded
- **THEN** the system returns an empty list rather than an error

### Requirement: Bounded retention
The system SHALL enforce a bounded retention policy on history entries so storage does not grow without limit.

#### Scenario: Oldest entries are evicted beyond the retention limit
- **WHEN** recording a new history entry would exceed the documented maximum number of retained entries
- **THEN** the oldest entry (or entries) beyond that limit are removed so the total stays within the documented bound

### Requirement: History browsing page
The system SHALL provide a minimal page where a person can browse recorded prediction history without calling the API directly.

#### Scenario: Person views recent predictions
- **WHEN** a person opens the history page
- **THEN** the page displays the most recent predictions (label, confidence, and timestamp) without requiring login

#### Scenario: Person views history with nothing recorded yet
- **WHEN** a person opens the history page before any prediction has been made
- **THEN** the page displays a clear empty-state message instead of an error or blank screen
