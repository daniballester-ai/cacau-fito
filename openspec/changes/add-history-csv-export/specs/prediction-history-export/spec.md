## Purpose

Exposes the full prediction history as a downloadable CSV file, so it can be analyzed outside the application (spreadsheet, external tooling, or future retraining work) instead of only being browsable a page at a time.

## ADDED Requirements

### Requirement: CSV export of full history
The system SHALL let a client download the complete prediction history as a CSV file, with one row per recorded prediction.

#### Scenario: Export includes all recorded fields
- **WHEN** a client requests the CSV export
- **THEN** the response is a valid CSV with a header row and one data row per recorded prediction, including timestamp, predicted label, confidence, and per-class probabilities

#### Scenario: Export reflects the current history, not a stale snapshot
- **WHEN** new predictions have been recorded since the last export
- **THEN** a fresh export request includes those new predictions

### Requirement: Empty history exports as a valid empty CSV
The system SHALL return a valid CSV (header row only) when no predictions have been recorded, rather than an error.

#### Scenario: Export with no predictions recorded
- **WHEN** a client requests the CSV export before any prediction has been made
- **THEN** the response is a valid CSV containing only the header row
