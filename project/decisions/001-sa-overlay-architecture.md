# ADR-001: South African Jurisdiction Overlay Architecture

**Date:** 2026-05-17
**Status:** Accepted
**Deciders:** Rakheen Dama

## Context

This fork adapts `anthropics/claude-for-legal` for South African legal workflows, starting with the employment-legal plugin (20 skills). The upstream system is US-centric — statutory references, procedural checklists, classification tests, and practice profile templates assume US law. Applying US defaults to SA matters would produce actively wrong guidance (e.g., at-will dismissal assumptions where the LRA requires fairness, FLSA tests where BCEA s213 governs).

The adaptation must:
- Preserve upstream merge compatibility (the fork tracks `anthropics/claude-for-legal` as upstream)
- Support phased rollout across practice areas (employment → commercial → privacy)
- Handle annually-changing statutory thresholds (via Government Gazette)
- Produce correct SA-specific legal output for 7 priority skills

## Decisions

### D1: Additive overlays, not separate plugins or in-place rewrites

**Decision:** SA content lives in `jurisdictions/za/` as overlay files that the existing plugin infrastructure routes to when jurisdiction = ZA.

**Alternatives considered:**
- **(B) Separate `employment-legal-za` plugin:** Clean separation but fragments the marketplace, duplicates jurisdiction-neutral logic (matter workspaces, output formatting, guardrails), and doubles maintenance.
- **(C) In-place modification of existing skills:** Direct but makes upstream merges painful — every skill change upstream creates conflicts.

**Why A:** The existing plugin already has a "jurisdiction recognition" guardrail that says "detect → assess → route." Overlays follow this pattern naturally. Only one upstream file needs modification (cold-start-interview). The marketplace entry count stays clean. A contributor adding a new practice area follows the same pattern.

### D2: Company profile default + matter-level jurisdiction override

**Decision:** Jurisdiction is a structured field in the company profile (set at cold-start) with per-matter overrides via the existing matter-workspace system.

**Alternatives considered:**
- **(A) Company profile only:** Simple but breaks for companies with matters in different jurisdictions.
- **(C) Fully dynamic detection:** No structured field; every skill infers jurisdiction from document content. Flexible but fragile, inconsistent, and wasteful (re-infers every invocation).

**Why B:** The matter-workspace skill already isolates per-matter state. Adding a jurisdiction field is a small schema addition. Deterministic routing without per-skill re-inference. Multi-jurisdiction companies are out of scope for v1 but the architecture supports them naturally.

### D3: Hybrid file format — YAML for thresholds, markdown for workflows

**Decision:** Structured YAML files for statutory thresholds and citations (`jurisdictions/za/statutes/`), markdown files for procedural and workflow guidance (`jurisdictions/za/employment-legal/topics/`).

**Alternatives considered:**
- **(A) All YAML:** Machine-readable and consistent but poor for narrative procedural guidance (CCMA hearing steps, dismissal procedures).
- **(B) All markdown:** Easy to author but duplicates thresholds across skills and makes annual updates error-prone.

**Why C:** Thresholds like the BCEA earnings threshold change annually via Gazette — a single YAML file updated in one place beats finding and updating the same number across 8 markdown files. But dismissal procedure guidance is narrative and skill-specific — markdown is the right format. The split maps to the update frequency: YAML for things that change by Gazette, markdown for things that change by statute amendment or practice evolution.

### D4: Temporal fields from day one

**Decision:** Every statute entry carries `effective_from` and `effective_until` fields, even in v1 with manual updates.

**Why:** Employment disputes frequently involve "what was the threshold when this employee was dismissed 8 months ago?" Adding temporal reasoning to the schema later is a painful migration. The cost of including unused fields now is near zero; the cost of retrofitting them later is high.

### D5: Shared topic overlays, not per-skill overlays

**Decision:** Topic overlay files are organized by legal topic (dismissal, hiring, classification, etc.) and shared across skills, not one overlay per skill.

**Alternatives considered:**
- **(A) Per-skill overlays:** Simple wiring (one skill, one file) but duplicates content — SA dismissal law is referenced by termination-review, policy-drafting, hiring-review, and handbook-updates.

**Why B:** 6 topic files serve 7 skills without duplication. When the LRA is amended, you update `dismissal.md` once and every skill that references it gets the update. The router file maps which topics each skill needs.

### D6: Router file for skill wiring

**Decision:** A router file (`jurisdictions/za/employment-legal/router.md`) maps each skill to its relevant topic and statute files. The ZA practice profile template includes one instruction to check the router. No upstream SKILL.md files are modified.

**Alternatives considered:**
- **(A) Modify each SKILL.md:** Direct but touches 7 upstream files, creating merge conflicts on every upstream update.
- **(C) Practice profile embeds everything:** No routing needed but makes the practice profile very long and mixes config with workflow guidance.

**Why B:** Zero upstream SKILL.md changes. The ZA practice profile template (which we fully own) is the only file that references the router. Adding a new skill to SA coverage means adding one line to the router — no other files change.

### D7: Separate ZA practice profile template

**Decision:** A dedicated ZA practice profile template at `jurisdictions/za/employment-legal/practice-profile-template.md` with SA-native sections, replacing the US template for SA users.

**Alternatives considered:**
- **(A) Single template with conditional branches:** Keeps one file but pushes it past 600 lines and mixes US and SA sections.

**Why B:** SA practitioners see SA-native sections from first run (bargaining council coverage, CCMA posture, BEE/EEA status) instead of US sections (state supplements, FMLA, FLSA). Each template is focused and maintainable. The cold-start interview picks the right template based on jurisdiction.

### D8: Modify only cold-start-interview upstream

**Decision:** The cold-start interview SKILL.md is the single upstream file modification. A jurisdiction fork after Part 0 routes into SA-specific onboarding.

**Alternatives considered:**
- **(B) Separate `/cold-start-interview-za` skill:** No upstream conflict but fragments the user experience and duplicates Part 0.
- **(C) Hook-based injection:** No file modification but hooks don't support this level of flow control.

**Why A:** The fork point is small and well-defined (one conditional after Part 0). Cold-start is the entry point that determines everything downstream — it's the one file where modification is justified. Merge conflicts are localised and the interview structure is stable.

### D9: Manual statute updates for v1, automated monitoring for v2

**Decision:** Contributors manually update statute YAML files when the Government Gazette publishes new thresholds. Automated monitoring via the reg-monitor managed-agent cookbook is phase 2.

**Why:** Building a Gazette feed monitor blocks v1 on external integration work. The statute schema already supports versioning (temporal fields, `gazette_date`). The manual process is: read Gazette → add new entry → set `effective_until` on old entry → PR. Automated monitoring follows the existing reg-monitor cookbook pattern once SA feeds are wired.

### D10: MCP connectors deferred, requirements documented

**Decision:** No live MCP connections to SA legal data sources in v1. Requirements for SAFLII, DoEL, CCMA, and LexisNexis SA are documented in `project/mcp-requirements-za.md`.

**Why:** SAFLII and DoEL don't have MCP endpoints. Building scrapers or API wrappers is a separate engineering project. The statute YAML files handle threshold data, document uploads handle case-specific materials, and `source_url` fields give users pointers for manual verification.

### D11: SA work-product header — role-differentiated with honest privilege caveat

**Decision:** Headers match the existing template's role-differentiation pattern but use SA-appropriate privilege formulations, with an explicit caveat about in-house counsel acting in commercial vs. legal capacity.

**Why:** SA legal professional privilege is narrower than US attorney-client privilege + work product combined. Asserting "ATTORNEY WORK PRODUCT" (a US FRCP 26(b)(3) doctrine) on an SA document creates false confidence. The in-house commercial-vs-legal capacity distinction is the exact issue SA lawyers get wrong — flagging it in the template prevents documents being disclosed because privilege was incorrectly assumed.

### D12: Multi-jurisdiction out of scope for v1

**Decision:** The cold-start interview and practice profile serve SA-only companies. Companies with employees in both SA and US are not supported in v1.

**Why:** Multi-jurisdiction support adds complexity (dual practice profiles, per-matter jurisdiction switching, mixed flag tables) that delays shipping. The architecture supports it (matter-level jurisdiction override exists) but the cold-start interview only runs one jurisdiction path.

### D13: Jurisdiction-expansion skill for phases 2-3

**Decision:** After phase 1 ships, build a skill that codifies the overlay architecture and runs a structured interview to adapt new practice areas or jurisdictions. It loads `jurisdictions/za/ARCHITECTURE.md` as its primary context.

**Why:** The architecture decisions made here are repeatable. A skill that understands the pattern (directory layout, file schemas, wiring mechanism, testing model) can guide a contributor through adapting commercial-legal or privacy-legal without re-deriving the architecture from scratch.

## Consequences

**Positive:**
- Upstream merges are clean except for one file (cold-start-interview)
- SA content is portable — a future SaaS layer can read the same files
- Adding a new practice area follows the same pattern (statute YAMLs + topic overlays + router + practice profile template)
- Temporal statute schema supports historical queries from day one
- No marketplace fragmentation — same 12 plugins, jurisdiction-aware

**Negative:**
- Cold-start-interview merges require manual conflict resolution when upstream changes the interview flow
- Router-based wiring adds an indirection layer that contributors must understand
- Topic overlays are a new concept not present in upstream — contributors need onboarding

**Risks:**
- SA legal content accuracy depends on expert review (not automatable)
- Statute YAML files can go stale between Gazette publications without automated monitoring
- The "thin profile" cold-start approach may miss configuration that proves important for specific skills
