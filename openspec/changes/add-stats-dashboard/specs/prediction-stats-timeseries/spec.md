## Purpose

Provides a time-bucketed breakdown of recorded predictions per class, so trends over time (not just a lifetime total) can be observed and visualized.

## ADDED Requirements

### Requirement: Time-bucketed prediction breakdown
The system SHALL provide a way to retrieve prediction counts grouped by day and by class, covering the full recorded history.

#### Scenario: Breakdown reflects predictions across multiple days
- **WHEN** predictions have been recorded across more than one calendar day
- **THEN** the breakdown returns one entry per day that had at least one prediction, with the count for each class on that day

#### Scenario: Empty history returns an empty series
- **WHEN** no predictions have been recorded yet
- **THEN** the breakdown returns an empty series rather than an error

#### Scenario: A day with no predictions for a given class is not misreported
- **WHEN** a day has predictions for some classes but not others
- **THEN** that day's entry only reports counts for classes that actually occurred that day (not a fabricated zero misrepresented as a real data point) — the dashboard consuming this data is responsible for filling gaps for display, not this capability
