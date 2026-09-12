## Purpose

Packages the CacauFito inference service and frontend as a runnable container image, so the system can be started reliably on any machine with a container runtime, without manually installing Python/PyTorch dependencies on the host.

## ADDED Requirements

### Requirement: Single-command startup
The system SHALL be startable with a single documented command on any machine with a compatible container runtime, without manual installation of Python dependencies on the host.

#### Scenario: Fresh machine can start the system
- **WHEN** the documented startup command is run on a machine that only has the container runtime installed (no Python/PyTorch preinstalled)
- **THEN** the inference service and frontend become reachable, serving the same endpoints and pages as running it directly with Python

### Requirement: Persistent data survives container restarts
Prediction history data and model artifacts SHALL be stored outside the container's writable layer, so they are not lost when the container is stopped, rebuilt, or restarted.

#### Scenario: History survives a restart
- **WHEN** the container is stopped and started again (without removing its mounted volumes)
- **THEN** prediction history recorded before the restart is still present afterward

### Requirement: Fail fast on missing model artifacts
The system SHALL fail at startup with a clear error if required model artifacts are not present, rather than starting successfully and only failing on the first prediction request.

#### Scenario: Missing model artifact is caught at startup
- **WHEN** the container starts without the expected model artifact mounted or present
- **THEN** startup fails immediately with a clear error message identifying the missing artifact, instead of accepting requests that would then fail
