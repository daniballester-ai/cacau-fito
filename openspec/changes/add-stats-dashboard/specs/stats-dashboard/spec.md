## Purpose

Gives a person a visual dashboard of diagnosis trends over time, built on the time-bucketed prediction breakdown, without needing to read raw JSON from the API.

## ADDED Requirements

### Requirement: Dashboard visualization
The system SHALL provide a page that visualizes prediction counts over time as a chart, broken down by class, alongside the existing lifetime per-class totals.

#### Scenario: Dashboard shows trend chart with data present
- **WHEN** a person opens the dashboard after predictions have been recorded across multiple days
- **THEN** the page displays a chart showing prediction counts per class over time, plus the lifetime totals

#### Scenario: Dashboard handles no data gracefully
- **WHEN** a person opens the dashboard before any prediction has been recorded
- **THEN** the page displays a clear empty-state message instead of a broken or blank chart
