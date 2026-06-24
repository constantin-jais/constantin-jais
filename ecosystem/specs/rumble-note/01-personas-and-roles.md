# Personas and Roles — rumble-note

Status: Drafting.

## Product Stance

`rumble-note` serves people who need a private local thinking surface before asking agents or ecosystem tools to act. The primary value is not storage alone; it is controlled transformation from rough notes to explicit context.

## Role: Local Knowledge Owner

### Goal

Maintain a private, local-first workspace of personal notes and decide what can be reused elsewhere.

### Motivations

- Keep sensitive work-in-progress thoughts under local control.
- Avoid losing decisions, references, and rationale across sessions.
- Reuse context without manually reconstructing it each time.

### Permissions

- Full control over local workspace content.
- Create, edit, archive, delete, export, and hand off blocks.
- Configure privacy/export policies.

### Visible Data

- All local notebooks, documents, blocks, links, labels, source references, and handoff history in the workspace.

### Editable Data

- Workspace settings.
- Documents and blocks.
- Block metadata, labels, references, and handoff state.
- Export/handoff package contents before submission.

### Allowed Actions

- Create notebooks and documents.
- Capture quick blocks.
- Link blocks to other blocks, documents, and sources.
- Qualify blocks as question, decision, source reference, task candidate, spec candidate, learning-session candidate, or context fragment.
- Search and filter notes.
- Build and approve handoff packages.
- Export or delete local data.

### Forbidden Actions

- Trigger agent execution directly from note content.
- Silently publish private blocks to remote systems.
- Bypass explicit confirmation before handoff.

### Edge Cases

- User works offline for long periods.
- User accidentally includes sensitive blocks in a handoff package.
- User deletes a block referenced by prior handoffs.
- User imports content that has partial or missing provenance.

### Trust / Security Expectations

- Local data remains local unless explicitly exported or handed off.
- Handoff preview clearly shows included blocks and metadata.
- Deletion and export behavior is understandable and reversible where feasible.

## Role: Spec / Product Author

### Goal

Turn scattered notes into structured spec, product, task, or decision context.

### Motivations

- Move from discovery notes to implementable artifacts.
- Preserve traceability from observations to decisions.
- Feed `rumble-canvas` or the harness with curated context rather than raw dumps.

### Permissions

- Create and edit product-oriented notes.
- Mark blocks as spec candidates, decision candidates, risks, assumptions, or open questions.
- Create handoff packages for spec drafting or planning.

### Visible Data

- Notes, linked sources, prior handoffs, block relationships, and candidate artifacts in accessible workspaces.

### Editable Data

- Block content and structure.
- Candidate status and labels.
- Handoff grouping and summaries.

### Allowed Actions

- Create a note-to-spec handoff.
- Link a block to a source or product decision.
- Group related blocks into a draft artifact context.
- Export context for `rumble-canvas`.

### Forbidden Actions

- Mark unreviewed notes as accepted specs without a downstream validation flow.
- Override provenance or source metadata from imported content.

### Edge Cases

- Same block contributes to multiple specs.
- A note contradicts an earlier decision.
- A source is later deemed unreliable.

### Trust / Security Expectations

- Traceability from spec candidate to note/source remains inspectable.
- Contradictions and stale links are visible rather than hidden.

## Role: Learning Session Preparer

### Goal

Prepare source-grounded notes that can become learning-session context.

### Motivations

- Turn readings and reflections into teachable/session-ready material.
- Keep citations and source references close to claims.
- Avoid hallucinated or ungrounded learning flows.

### Permissions

- Create learning-session candidate blocks.
- Link notes to sources and questions.
- Export selected blocks as session context.

### Visible Data

- Notes, source references, questions, summaries, and learning-session candidates.

### Editable Data

- Learning labels, block summaries, questions, and handoff package descriptions.

### Allowed Actions

- Mark blocks as learning objectives, questions, examples, or source-grounded claims.
- Build a note-to-learning-session handoff.
- Preserve citations in exports.

### Forbidden Actions

- Claim source grounding where no source reference exists.
- Send private notes as participant-visible material without review.

### Edge Cases

- A source has multiple interpretations.
- A block is useful for facilitator context but not participant display.
- The user wants to export only citations, not private commentary.

### Trust / Security Expectations

- Handoff distinguishes private facilitator context from shareable learning material.
- Source references survive export.

## Role: Harness Consumer

This is a system-facing role, not a human operator inside the editor.

### Goal

Receive deterministic, bounded context packages prepared by a human.

### Motivations

- Avoid ambiguous prompts and raw note dumps.
- Receive block IDs, source links, labels, and intended use.
- Preserve auditability of what context was supplied.

### Permissions

- Read only the handoff package explicitly produced by the user.
- Return status, plan, refusal, or generated artifact metadata depending on the downstream system.

### Visible Data

- Included blocks and declared metadata only.
- Package purpose, provenance, and constraints.

### Editable Data

- None inside `rumble-note`; any returned artifact or status is appended through explicit import/recording.

### Allowed Actions

- Consume package content.
- Reference block IDs in responses.
- Produce a plan, task candidate, spec draft, learning-session outline, or refusal in downstream systems.

### Forbidden Actions

- Read the full workspace without explicit permission.
- Mutate notes directly.
- Treat candidate blocks as accepted durable memory without user approval.

### Edge Cases

- Package references a deleted or archived block.
- Package contains insufficient source context.
- Consumer refuses execution due to missing provenance or policy constraints.

### Trust / Security Expectations

- Least-context principle: only selected blocks are exposed.
- Returned outputs are auditable and linked to the originating handoff.

## Role: Imported Source Provider

This is a system-facing role for content produced by `wrench-loader` or another importer.

### Goal

Provide normalized source material that the user can reference from notes.

### Motivations

- Keep extraction/parsing outside `rumble-note`.
- Preserve provenance and extraction evidence.
- Let the user decide which parts become note context.

### Permissions

- Create source references or imported source blocks through an explicit import flow.
- Attach provenance metadata.

### Visible Data

- Import target workspace or document selected by the user.
- Relevant source metadata.

### Editable Data

- Imported source objects only during import; user owns subsequent note annotations.

### Allowed Actions

- Provide canonical content, source IDs, citations, checksums, and extraction status.
- Refresh source metadata if user approves.

### Forbidden Actions

- Run broad ingestion without user-selected scope.
- Rewrite user-authored notes.
- Mark imported content as trusted without provenance.

### Edge Cases

- Partial extraction.
- Duplicate source import.
- Source content changes upstream.

### Trust / Security Expectations

- Imported content is distinguishable from user-authored notes.
- Provenance is preserved during references and handoffs.
