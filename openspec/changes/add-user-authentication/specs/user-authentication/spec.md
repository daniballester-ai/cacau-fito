## Purpose

Gives CacauFito a notion of user identity — registration and login — so predictions, history, and stats can belong to a specific person instead of being shared anonymously across everyone.

## ADDED Requirements

### Requirement: Account registration
The system SHALL let a person register a new account with a unique identifier (e.g., email or username) and a password.

#### Scenario: Successful registration
- **WHEN** a person registers with an identifier not already in use and a valid password
- **THEN** an account is created and the person can subsequently log in with those credentials

#### Scenario: Duplicate registration rejected
- **WHEN** a person tries to register with an identifier already in use by an existing account
- **THEN** the registration is rejected with a clear error, and no second account is created

### Requirement: Login and session
The system SHALL let a registered person log in with their credentials and receive a session that identifies them on subsequent requests.

#### Scenario: Successful login
- **WHEN** a person logs in with correct credentials
- **THEN** the system establishes a session identifying that user for subsequent requests

#### Scenario: Invalid credentials rejected
- **WHEN** a person logs in with an incorrect password or an unregistered identifier
- **THEN** the login is rejected with a clear error, and no session is established

### Requirement: Logout
The system SHALL let a logged-in person end their session.

#### Scenario: Logout ends the session
- **WHEN** a logged-in person logs out
- **THEN** their session is no longer valid for subsequent requests to protected endpoints
