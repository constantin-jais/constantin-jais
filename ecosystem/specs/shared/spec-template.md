# Product Spec Template — `<product-name>`

## 00. Product Charter

### Mission

### Target Users

### Jobs To Be Done

### Product Promise

### Non-Goals

### Product Boundaries

### Success Metrics

### MVP Scope

### Post-MVP Scope

### Dependencies on Bolt/Wrench/Gear

### Risks

---

## 01. Personas and Roles

For each role:

```md
## Role: <name>

### Goal
### Motivations
### Permissions
### Visible Data
### Editable Data
### Allowed Actions
### Forbidden Actions
### Edge Cases
### Trust / Security Expectations
```

---

## 02. User Journeys

For each journey:

```md
## Journey: <name>

### Trigger
### Actor
### Preconditions
### Happy Path
### Alternate Paths
### Failure Paths
### Recovery Path
### Data Created or Updated
### Events Emitted
### Audit Requirements
### Acceptance Criteria
```

---

## 03. Information Architecture

- Navigation model
- Primary spaces
- Object hierarchy
- Search/browse model
- Settings model
- Empty state strategy

---

## 04. Screens and Actions

For each screen:

```md
## Screen: <name>

### Purpose
### Route / Entry Point
### Allowed Roles
### Displayed Data
### Actions by Role
### Empty State
### Loading State
### Error State
### Offline State
### Permission Denied State
### Accessibility Notes
### Telemetry / Events
### Service Calls
### Acceptance Criteria
```

For each action:

```md
## Action: <name>

### Actor
### Intent
### Input
### Preconditions
### Business Rules
### Validation Rules
### Side Effects
### Events Emitted
### Audit Log
### Permission Check
### Idempotency
### Rollback / Retry
### Errors
### Acceptance Criteria
```

---

## 05. Domain Model

For each entity/value object:

- definition;
- owner;
- fields;
- lifecycle states;
- relationships;
- invariants;
- state transitions;
- deletion/archive rules;
- emitted events;
- shared capability candidates.

---

## 06. Data Model

For each table/collection:

- columns and types;
- primary key;
- foreign keys;
- indexes;
- constraints;
- RLS/auth rules;
- audit fields;
- retention policy;
- PII classification;
- local-first/sync behavior;
- migration notes.

---

## 07. Services and APIs

For each service/API:

- owner layer;
- input;
- output;
- auth;
- idempotency;
- failure modes;
- observability;
- tests.

Separate:

- Rumble app services;
- domain services;
- Bolt calls;
- Wrench calls;
- Gear calls;
- external integrations.

---

## 08. Events and Workflows

For each event:

- name;
- producer;
- consumers;
- payload;
- persistence;
- replay behavior;
- audit relevance.

For each workflow:

- trigger;
- steps;
- gates;
- rollback;
- retry;
- evidence.

---

## 09. Permissions, Security, RGPD

- roles;
- permission matrix;
- sensitive data;
- data retention;
- export;
- deletion;
- audit;
- consent;
- data residency;
- threat model notes.

---

## 10. Non-Functional Requirements

- offline behavior;
- sync/conflict handling;
- performance;
- accessibility;
- observability;
- portability/self-hosting;
- backup/restore;
- disaster recovery;
- cost constraints.

---

## 11. Acceptance Tests

- Given/When/Then scenarios;
- role-based permission tests;
- screen smoke tests;
- domain invariant tests;
- API contract tests;
- migration tests;
- security/RLS tests;
- offline/sync tests.

---

## 12. Open Questions

| Question | Impact | Owner | Status |
| --- | --- | --- | --- |
