# ADR 0027 — Content-Site Method Exception and Planned Rebuild

Status: Accepted
Date: 2026-07-02
Decision owner: Rumble COS product
Related decision: D6 (decision-log)

## Context

`rumble-cos` (the public content site) is currently built with Astro, an exception to the Rust+Dioxus/Leptos doctrine for interactive Rumbles. Astro was chosen for rapid content iteration and static-first performance. However, maintaining two UI frameworks (Astro + Rust) creates toolchain friction and risks fragmentation.

A rebuild of `rumble-cos` using the elected web shell (Leptos, per ADR 0030) is planned but not immediate. The current Astro site must remain live during the transition; content and redirects are migration assets, not throwaway work.

This ADR formalizes the exception, the rebuild path, and the transition sequencing.

## Decision

1. **Exception status**: `rumble-cos` continues to use Astro until a Leptos replacement (web-shell election settled in ADR 0030) passes all quality gates (E2E tests, performance, accessibility, SEO).

2. **Rebuild scope** (after web-shell election):
   - Port content model (structured data, frontmatter) to new framework without loss.
   - Preserve URLs and implement `_redirects` or equivalent to maintain SEO and external links.
   - Run both sites in parallel briefly to verify crawlability and user experience.
   - Archive Astro build artifacts for reference.

3. **Current site stability**: No new Astro framework dependencies or major architectural changes. Bug fixes and content updates only. Framework upgrade/refactors are out of scope until rebuild is live.

4. **Rebuild gates**:
   - E2E spike complete, web-shell winner decided (Dioxus or Leptos).
   - Replacement site passes performance benchmarks (LCP, CLS, FID) ≥ current Astro baseline.
   - Redirect chain verified (no broken links to external sites).
   - Content parity: all pages rendered, search indexes migrated.
   - Accessibility: WCAG 2.1 AA compliance verified.
   - SEO: sitemap, canonical URLs, OG metadata present.

5. **Sequencing**: Rebuild happens after high-urgency governance/product work (maturity.json, Biscuit, Canvas handoff) is completed and gates are passing. Estimated: Q3 2026 earliest.

## Architecture objectives satisfied

| Objective            | ADR consequence                                                           |
| -------------------- | ------------------------------------------------------------------------- |
| Framework coherence  | Astro exception is bounded and will be resolved after web-shell decision. |
| User-facing quality  | Current site remains stable and performant during transition.             |
| Audit trail          | Content is not lost; migration is traced via git history and redirects.   |
| Release independence | COS rebuild does not block other Rumble products.                         |

## Consequences

### Positive

- Current Astro site remains operational and low-risk.
- Content and metadata are portable to any web framework via structured export.
- Web-shell election is not blocked by COS rebuild; decisions are independent.
- Rebuild can be treated as a separate project with its own scope and timeline.

### Negative / Costs

- Dual-framework maintenance (brief, but real overhead).
- Astro dependencies must be kept current while rebuild is pending.
- Content migration has non-trivial complexity (templating, metadata, image asset handling).
- Redirect/SEO verification requires careful testing.

## Alternatives considered

### Rebuild immediately with best-guess framework

Rejected. Web-shell decision (Dioxus/Leptos) should drive the choice, not COS schedule.

### Abandon Astro site and start from scratch

Rejected. Content has business and historical value; loss would harm SEO and user discovery.

### Keep Astro forever

Rejected. Creates permanent framework inconsistency and prevents framework-level improvements.

## Required follow-up

- Web-shell election settled: Leptos (ADR 0030). Spikes complete.
- Structure COS content model for export (Markdown + YAML frontmatter or JSON).
- Plan COS rebuild as separate Github issue/epic with gates and milestones.
- Document current Astro performance baseline (Lighthouse, Core Web Vitals).
- Add `_redirects` strategy to COS rebuild checklist.
- Reserve rebuild budget after prioritized governance and product work is complete.

## Acceptance criteria

- Astro site is stable and receives only bug fixes and content updates.
- Web-shell winner is documented in decision-log.
- Content export from Astro includes all metadata (titles, descriptions, images, frontmatter).
- Rebuild plan includes gate checklist (performance, accessibility, SEO, redirects).
- No new Astro-specific dependencies are added to COS until rebuild is live.
