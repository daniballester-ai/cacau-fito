## MODIFIED Requirements

### Requirement: History listing
The system SHALL provide a way to list the logged-in user's own past prediction history entries, ordered most recent first, with pagination.

#### Scenario: Listing returns entries newest-first
- **WHEN** a logged-in client requests the prediction history with more than one entry recorded for that user
- **THEN** the entries are returned ordered from most recent to oldest

#### Scenario: Listing is paginated
- **WHEN** a client requests a page of history with a page size smaller than the total number of entries for that user
- **THEN** only that page's worth of entries is returned, along with enough information to request the next page

#### Scenario: Empty history
- **WHEN** a client requests the prediction history before any prediction has been recorded for that user
- **THEN** the system returns an empty list rather than an error

#### Scenario: Users only see their own history
- **WHEN** a logged-in user requests the prediction history
- **THEN** only predictions made by that user are returned, never another user's predictions

### Requirement: History browsing page
The system SHALL provide a minimal page where a logged-in person can browse their own recorded prediction history without calling the API directly.

#### Scenario: Person views recent predictions
- **WHEN** a logged-in person opens the history page
- **THEN** the page displays that person's most recent predictions (label, confidence, and timestamp)

#### Scenario: Person views history with nothing recorded yet
- **WHEN** a logged-in person opens the history page before any prediction has been made under their account
- **THEN** the page displays a clear empty-state message instead of an error or blank screen
