# Feature Specification: Prediction Stats

**Feature Branch**: `001-prediction-stats`

**Created**: 2026-09-04

**Status**: Draft

**Input**: User description: "Add a GET /stats endpoint to the CacauFito inference service that returns the total number of predictions made and a breakdown of how many predictions fall into each class (healthy, cssvd, anthracnose), computed from the existing prediction history storage. This lets someone quickly see the overall distribution of diagnoses made by the service so far, without paging through the full history. At least 2 usage scenarios: (1) viewing stats after several predictions have been made, seeing accurate counts per class and a total; (2) viewing stats before any prediction has been made, seeing all-zero counts instead of an error."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View overall diagnosis distribution (Priority: P1)

Someone reviewing how the CacauFito model is being used wants a quick summary of what it has diagnosed so far, without scrolling through a long, paginated list of individual predictions.

**Why this priority**: This is the entire value of the feature — a fast, at-a-glance summary. Without it, there is no reason for the feature to exist.

**Independent Test**: Can be fully tested by making several predictions of different classes and then requesting the stats, and delivers value by showing accurate aggregate counts in one response.

**Acceptance Scenarios**:

1. **Given** several predictions have been made across the three classes (healthy, cssvd, anthracnose), **When** a client requests the stats, **Then** the response shows the correct count for each class and a total that equals the sum of all class counts.
2. **Given** predictions have been made but skewed toward one class (e.g., mostly healthy), **When** a client requests the stats, **Then** the per-class counts reflect that skew accurately, not an even/default split.

---

### User Story 2 - View stats with no predictions yet (Priority: P2)

Someone opens the stats view on a freshly deployed or just-reset instance, before anyone has used the classifier yet.

**Why this priority**: A real edge case that, if unhandled, would present as a bug (an error page or a crash) on the very first use of the feature — lower priority than the core happy path, but essential for the feature to be considered complete.

**Independent Test**: Can be fully tested by requesting stats on an instance with an empty prediction history and delivers value by confirming the feature degrades gracefully instead of failing.

**Acceptance Scenarios**:

1. **Given** no predictions have ever been recorded, **When** a client requests the stats, **Then** the response shows a total of zero and zero for every class, rather than an error.

---

### Edge Cases

- What happens when a class defined by the classifier has never appeared in any recorded prediction? It must still appear in the per-class breakdown with a count of zero, not be silently omitted.
- What happens if the underlying prediction history storage is temporarily unavailable when stats are requested? The response must clearly indicate the stats could not be computed, rather than returning misleading zero/partial counts as if they were accurate.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a way to retrieve the total number of predictions recorded so far.
- **FR-002**: System MUST provide a way to retrieve, alongside the total, a count of recorded predictions broken down by each of the three known classes (healthy, cssvd, anthracnose).
- **FR-003**: System MUST include every known class in the breakdown even if its count is zero (no class silently omitted for lack of data).
- **FR-004**: System MUST return a valid, zero-filled stats response (total = 0, every class count = 0) when no predictions have been recorded yet, rather than an error.
- **FR-005**: System MUST reflect only successfully recorded predictions in the stats (consistent with what the existing prediction history already records — rejected/invalid uploads are not counted).
- **FR-006**: System MUST clearly signal a failure (rather than a misleading zero or partial result) if the stats cannot be computed due to an underlying storage problem.

### Key Entities

- **Prediction Stats Summary**: An aggregate view over existing recorded predictions — a total count and a per-class count breakdown. It is derived data, not a new record of its own; it always reflects the current state of recorded prediction history at the moment it is requested.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A person can determine the total number of diagnoses made and their distribution across all classes by making a single request, without paging through individual history records.
- **SC-002**: The reported counts exactly match the number of successfully recorded predictions per class, verified by comparing against the full prediction history at the same point in time.
- **SC-003**: Requesting stats before any prediction exists succeeds (does not error) and clearly communicates that nothing has been recorded yet.

## Assumptions

- The set of possible classes (healthy, cssvd, anthracnose) is fixed and already known from the existing classifier/history capability; this feature does not need to discover classes dynamically.
- Stats are computed on demand from existing prediction history at request time; no separate long-term storage or caching of the aggregate is required for this feature's scope.
- This feature reuses the same no-authentication, single-instance PoC posture as the rest of CacauFito — no access control or multi-tenant breakdown is in scope.
