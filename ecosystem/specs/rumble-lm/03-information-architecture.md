# Information Architecture — rumble-lm

Status: Draft.

## Primary Product Spaces

```text
Workspace
  Sessions
    Session
      Setup
      Sources
      Activities
      Citation Review
      Live
      Results
      Summary
      Exports
      Audit / History

Participant Entry
  Join
  Current Activity
  Published Results
  Published Recap
```

## Object Hierarchy

```text
Workspace
  └── Session
      ├── SessionSettings
      ├── SourceSet
      │   └── Source references / Source chunks
      ├── Activity[]
      │   ├── ActivityOption[]
      │   ├── Citation[]
      │   └── ActivityRun[]
      ├── Participant[]
      │   └── Response[]
      ├── Summary[]
      │   └── Citation[]
      └── Export[]
```

## Main Navigation

### Facilitator Navigation

1. **Sessions** — find/create/resume sessions.
2. **Setup** — objective, audience, lifecycle readiness.
3. **Sources** — import and review grounding material.
4. **Activities** — build and order interactive agenda.
5. **Citations** — validate source support.
6. **Live** — run the session.
7. **Results** — inspect responses and learning signals.
8. **Summary** — produce and validate synthesis.
9. **Export** — generate artifacts and archive.

### Participant Navigation

Participant navigation is intentionally minimal:

1. **Join** — identify or enter as guest according to policy.
2. **Current Activity** — respond to the active prompt.
3. **Results/Recap** — view only what facilitator publishes.

### Admin Navigation

1. **Workspace sessions** — metadata and governance.
2. **Roles and access** — assignments and invitations.
3. **Policy** — retention, source types, export rules.
4. **Audit** — lifecycle, export, deletion/anonymization events.

## Search and Browse Model

MVP search:

- search sessions by title/objective;
- filter sessions by status, owner, date;
- filter activities by type/status;
- filter citations by unresolved/rejected/validated;
- filter exports by audience/format/date.

Post-MVP search:

- semantic search across sources and summaries;
- cross-session source reuse;
- workspace-level learning signals.

## Settings Model

### Workspace Settings

- allowed source types;
- participant access modes;
- role assignment policy;
- retention defaults;
- export formats/audiences;
- generation provider policy;
- audit retention.

### Session Settings

- default response visibility;
- guest access enabled/disabled;
- activity result visibility;
- summary audience defaults;
- export data classes;
- retention override if allowed.

### Activity Settings

- response mode;
- response visibility;
- allow edit before close;
- show aggregate results;
- duration/timer;
- grounding mode.

## Empty State Strategy

- **No sessions:** explain the core loop and offer session creation.
- **No sources:** prompt import and explain source-grounded value.
- **No activities:** offer manual creation or source-grounded generation.
- **No citations:** state whether no citations are needed or generation has not happened.
- **No participants:** show join options and preview link/state.
- **No responses:** distinguish not started, open with no responses, and closed with no responses.
- **No summary:** offer generation only after session close.
- **No exports:** offer export when policy and lifecycle allow.

## State Visibility Rules

- Facilitators see readiness blockers and unpublished objects.
- Participants see only current/published objects.
- Admins see metadata and governance surfaces; content access depends on policy.
- Archived sessions are read-only except authorized restore/follow-up.

## Boundary Notes

`rumble-lm` owns navigation and user-facing workflow. It does not own global identity, canonical source extraction, generic artifact storage, or orchestration runtime; those remain shared capability candidates.
