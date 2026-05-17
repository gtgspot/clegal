# PRD: South African Employment Law Overlay

**Date:** 2026-05-17
**Status:** Ready for implementation
**Phase:** 1 of 3 (Employment → Commercial → Privacy/POPIA)

---

## Problem Statement

The claude-for-legal plugin system provides 12 practice-area plugins with 157 skills, but all legal content — statutory references, procedural checklists, high-risk flag tables, classification tests, and practice profile templates — is US-centric. A South African in-house employment lawyer or labour consultant using the employment-legal plugin today would receive actively wrong guidance: at-will dismissal assumptions where the LRA requires substantive and procedural fairness, FMLA leave frameworks where BCEA statutory leave applies, FLSA classification tests where BCEA s213 and common law control tests govern, and escalation paths referencing EEOC/NLRB instead of CCMA/bargaining councils.

The fork exists to adapt this system for South African legal workflows. The highest-risk practice area is employment law, where US defaults would produce guidance that exposes users to CCMA referrals, Labour Court claims, and statutory penalties.

## Solution

Build an additive jurisdiction overlay system that layers South African employment law content on top of the existing plugin infrastructure without modifying upstream skill files. The overlay uses structured YAML statute files for thresholds and citations that change via Government Gazette, markdown topic files for procedural and workflow guidance, a router file that maps skills to their relevant overlays, and a separate ZA practice profile template that the cold-start interview populates for SA users.

The only upstream file modification is a single fork point in the cold-start interview skill, which detects SA jurisdiction after Part 0 and branches into SA-specific onboarding questions. All other changes are additive files in the `jurisdictions/za/` directory tree.

## User Stories

1. As an SA in-house employment lawyer, I want the cold-start interview to ask me about BCEA earnings thresholds, bargaining council coverage, and CCMA dispute posture, so that my practice profile reflects my actual statutory environment instead of US defaults.

2. As an SA in-house employment lawyer, I want the termination-review skill to flag procedural unfairness (no hearing held) and automatically unfair grounds (LRA s187), so that I catch dismissals likely to be referred to the CCMA before the decision is finalised.

3. As an SA in-house employment lawyer, I want the termination-review skill to distinguish between small-scale and large-scale retrenchments (s189 vs s189A), so that I know when the more onerous consultation and facilitation requirements apply.

4. As an SA in-house employment lawyer, I want the hiring-review skill to apply SA restraint-of-trade doctrine and BCEA probation requirements (LRA Schedule 8 Item 8), so that offer letters and employment contracts are reviewed against the correct legal framework.

5. As an SA in-house employment lawyer, I want the worker-classification skill to apply BCEA s213 and the common law control test instead of the US ABC test, so that classification opinions are legally sound for SA engagements.

6. As an SA in-house employment lawyer, I want the wage-hour-qa skill to reference BCEA working-time rules (s9-s16), overtime provisions, and the earnings threshold for protected employees, so that answers about hours, overtime, and rest breaks are correct for SA.

7. As an SA in-house employment lawyer, I want the leave-tracker skill to track BCEA statutory leave (annual s20, sick s22, family responsibility s27, maternity s25), so that leave deadlines and entitlements reflect SA law rather than FMLA/state-specific US rules.

8. As an SA in-house employment lawyer, I want the policy-drafting skill to produce policies structured around SA legal requirements (disciplinary codes aligned to Schedule 8, grievance procedures, sexual harassment policy per the Code of Good Practice), so that drafted policies are compliant with SA labour law.

9. As an SA in-house employment lawyer, I want the work-product header to reflect SA legal professional privilege doctrine rather than asserting US "attorney work product" protection (FRCP 26(b)(3)) that does not exist in SA law, so that privilege markings are legally honest.

10. As an SA in-house employment lawyer, I want the work-product header to warn me when I am in-house counsel acting in a commercial capacity (where privilege may not attach), so that I do not rely on privilege markings that would not survive a challenge.

11. As an SA in-house employment lawyer, I want the system to reference a single source of truth for statutory thresholds (BCEA earnings threshold, minimum wages, notice periods) that includes effective dates, so that I know which threshold applied at any given point in time for dispute purposes.

12. As an SA in-house employment lawyer, I want the system to detect jurisdiction = ZA from my practice profile and automatically load the correct SA overlays without me having to specify jurisdiction on every skill invocation.

13. As an SA in-house employment lawyer, I want to override the company-level jurisdiction at the matter level, so that I can handle a specific matter under a different jurisdiction when needed.

14. As an SA in-house employment lawyer, I want the cold-start interview to ask for my disciplinary code and standard employment contract template as seed documents, so that the plugin learns my company's actual disciplinary framework and employment terms.

15. As an SA in-house employment lawyer, I want the cold-start interview to optionally accept CCMA outcomes and my Employment Equity Plan, so that the plugin can learn my dispute posture and EE compliance status when I have those documents available.

16. As an SA in-house employment lawyer, I want the cold-start interview to capture my designated employer status, BEE posture, and whether I have recognised unions, so that downstream skills correctly handle EEA obligations and dispute routing.

17. As an SA in-house employment lawyer, I want a discrete discrimination/EEA-ground flag in the termination-review high-risk table, so that dismissals connected to race, gender, disability, HIV status, or other EEA-protected characteristics are flagged as potentially automatically unfair.

18. As an SA in-house employment lawyer, I want the termination-review to flag employees earning below the BCEA earnings threshold as higher-risk, because these employees enjoy full working-time and overtime protections and changes to their conditions are more likely to be scrutinised.

19. As an SA in-house employment lawyer, I want statute YAML files to carry `source_url` fields pointing to the authoritative source (labour.gov.za), so that I can verify thresholds against the primary source.

20. As an SA in-house employment lawyer, I want the system to not reference US concepts (FMLA, FLSA, at-will employment, EEOC, state-specific rules) when my jurisdiction is ZA, so that outputs are clean and jurisdiction-appropriate.

21. As a contributor to this fork, I want a structural validation suite that checks YAML schema validity, cross-references between router/topic/statute files, and template completeness, so that broken references are caught before merge.

22. As a contributor to this fork, I want golden-path scenario evaluation cases for each SA-adapted skill, so that I can verify skills fire the correct flags and reference the correct statutes for known SA fact patterns.

23. As a contributor to this fork, I want an ARCHITECTURE.md in `jurisdictions/za/` that documents the overlay pattern, so that I can extend the system to commercial-legal and privacy-legal without re-deriving the architecture.

24. As a contributor to this fork, I want documented MCP connector requirements for SA legal data sources (SAFLII, DoEL, CCMA, LexisNexis SA), so that future integration work has clear specifications.

25. As a future maintainer, I want statute thresholds to carry `effective_from` and `effective_until` fields from day one, so that temporal reasoning ("what applied on date X?") works without schema migration.

26. As a future maintainer, I want a jurisdiction-expansion skill that codifies the overlay architecture and can guide adaptation to new practice areas (commercial-legal, privacy-legal) or new jurisdictions, so that expansion is repeatable and disciplined.

## Implementation Decisions

### Directory layout

All SA-specific content lives under `jurisdictions/za/`:

- `jurisdictions/za/statutes/` — shared YAML statute files (BCEA, LRA, EEA, sectoral determinations), used by all SA-adapted practice areas
- `jurisdictions/za/employment-legal/` — practice-area-specific overlays
- `jurisdictions/za/employment-legal/topics/` — 6 shared markdown topic overlays (dismissal, hiring, classification, leave-and-conditions, policy-and-handbook, investigation-privilege)
- `jurisdictions/za/employment-legal/router.md` — maps each skill to its relevant topic files and statute files
- `jurisdictions/za/employment-legal/practice-profile-template.md` — ZA variant of the employment-legal CLAUDE.md template

Planning documents live in `project/`:
- `project/decisions/` — ADR capturing architecture rationale
- `project/mcp-requirements-za.md` — deferred MCP connector requirements

### Statute YAML schema

Each statute file follows this schema:

```yaml
statute: "<full Act name and number>"
authority: "<governing department or body>"
last_confirmed: "YYYY-MM-DD"
source_url: "<authoritative URL>"
sections:
  <section_key>:
    ref: "<Act section reference, Gazette notice if applicable>"
    value: <numeric or string value>
    currency: "ZAR"          # if monetary
    unit: "<per_annum | hours_per_week | days | etc.>"
    effective_from: "YYYY-MM-DD"   # null = original statute
    effective_until: null          # null = still current
    effect: "<plain-English description>"
    gazette_date: "YYYY-MM-DD"    # if threshold set by Gazette
    note: "<optional clarification>"
```

Temporal fields are present from day one. Old values are preserved (not overwritten) when thresholds change — a new entry is added with the new `effective_from` and the old entry gets an `effective_until`.

### Skill wiring mechanism

Skills are not modified (except cold-start-interview). The wiring works through three layers:

1. **ZA practice profile template** — includes an instruction: "After loading context, read `jurisdictions/za/employment-legal/router.md` and load the listed overlays for the active skill."
2. **Router file** — YAML mapping of skill name → list of topic overlay files + statute files to load.
3. **Topic overlays** — markdown files with SA-specific procedural guidance, checklists, and flag tables that the skill follows instead of its US-default sections.

### Cold-start interview fork

The single upstream modification: after Part 0 (role, practice setting, integrations), check jurisdiction from the company profile. If primary jurisdiction is South Africa:

- Part 1 asks SA-specific footprint questions (provinces, sectoral determinations, bargaining councils, BEE/EEA posture, dispute resolution posture, leave above/at minimums, s189A threshold)
- Part 2 asks for SA seed documents (disciplinary code + employment contract as must-haves; CCMA outcomes + EE Plan as nice-to-haves)
- Output writes to the ZA practice profile template instead of the US template

Multi-jurisdiction (SA + US) is out of scope.

### Work-product header (SA)

Role-differentiated with SA-specific privilege caveat:

- **Admitted attorney/advocate:** `PRIVILEGED & CONFIDENTIAL — PREPARED BY/AT THE DIRECTION OF LEGAL COUNSEL FOR THE PURPOSE OF PROVIDING LEGAL ADVICE`
- **Non-lawyer:** `CONFIDENTIAL — NOT LEGAL ADVICE — CONSULT AN ADMITTED ATTORNEY OR ADVOCATE BEFORE ACTING`
- **Caveat:** SA legal professional privilege is narrower than US work product. It protects communications for the purpose of legal advice, not all internal legal analysis. Documents prepared by in-house counsel acting in a commercial capacity may not be protected.

### SA high-risk termination flags

11 flags in the dismissal topic overlay:

1. No hearing held (Schedule 8 procedural fairness)
2. Automatically unfair ground (LRA s187)
3. Discrimination / EEA-protected ground (LRA s187(1)(f) + EEA)
4. Protected disclosure (Protected Disclosures Act)
5. Recent CCMA/union activity (LRA s187(1)(d))
6. Operational requirements without s189 process (with s189A large-scale sub-check)
7. Probation without Code compliance (LRA Schedule 8 Item 8)
8. Fixed-term contract — reasonable expectation of renewal (LRA s186(1)(b))
9. Earnings below BCEA threshold (broadened: full BCEA protections, higher scrutiny for adverse changes)
10. Thin documentation (jurisdiction-neutral)
11. Comparator problem / inconsistent discipline (jurisdiction-neutral)

### Upstream merge strategy

Only `employment-legal/skills/cold-start-interview/SKILL.md` is modified. The fork point is a single conditional block after Part 0. All other SA content is additive in `jurisdictions/za/` which upstream does not have. Merge conflicts are localised to one file.

### Update model

Manual updates for v1. When the Government Gazette publishes new thresholds:
1. Contributor reads the Gazette
2. Adds new entry with `effective_from` set to the new effective date
3. Sets `effective_until` on the previous entry
4. Updates `last_confirmed` on the statute file
5. Submits PR

Automated monitoring via the reg-monitor managed-agent cookbook (watching DoEL/Gazette feeds) is a phase-2 enhancement.

## Testing Decisions

Tests should verify external behaviour — that the overlay system produces correct jurisdiction-specific outputs for known inputs — not implementation details like file-loading order or internal routing logic.

### Module 1: Statute data layer
- Schema validation: every YAML file in `jurisdictions/za/statutes/` parses and conforms to the statute schema
- Temporal integrity: `effective_from` dates are valid, `effective_until` is null or later than `effective_from`, no overlapping validity periods for the same section
- Cross-reference: every `ref` field contains a recognisable SA statute/Gazette reference pattern
- Fixture-based: valid and intentionally-invalid YAML fixtures test both pass and fail paths

### Module 2: Topic overlays
- Every topic file in `jurisdictions/za/employment-legal/topics/` is valid markdown with no broken internal links
- Every statute reference in a topic file (e.g., "BCEA s9(1)") has a corresponding entry in the relevant statute YAML
- No US-specific legal concepts appear (FMLA, FLSA, at-will, EEOC, NLRB, state-specific references)

### Module 3: Skill router
- Every skill name in the router maps to an existing skill directory under `employment-legal/skills/`
- Every topic file referenced in the router exists in `jurisdictions/za/employment-legal/topics/`
- Every statute file referenced in the router exists in `jurisdictions/za/statutes/`
- No orphaned topic files (every topic file is referenced by at least one skill in the router)

### Module 4: ZA practice profile template
- Template contains all required sections (jurisdictional footprint, termination review, hiring review, escalation, etc.)
- No `[PLACEHOLDER]` markers in structural sections (only in user-populated fields)
- SA-specific sections are present (CCMA posture, BEE/EEA status, bargaining council, sectoral determinations)
- No US-specific sections (state supplements, FMLA, FLSA exemption)
- Work-product header matches the agreed SA formulation

### Module 5: Cold-start interview fork
- Scenario eval: given a company profile with jurisdiction = ZA, the interview asks SA-specific questions (BCEA threshold, bargaining councils, designated employer status) and does not ask US-specific questions (which states, FMLA administrator)
- Scenario eval: the interview requests the correct seed documents (disciplinary code, employment contract as must-have)
- Scenario eval: the interview writes to the ZA practice profile template, not the US template

### Module 6: Structural validation scripts
- Validation script catches intentionally-broken YAML (missing required fields, invalid dates, duplicate section keys)
- Validation script catches broken router references (skill pointing to non-existent topic file)
- Validation script passes on the valid production files

### Module 7: Scenario evaluation suite
- 3-5 golden-path test cases per skill (7 skills × 3-5 = 21-35 cases)
- Each case specifies: input fact pattern, expected flag triggers, expected statute references, concepts that must NOT appear
- Cases cover: straightforward SA dismissal, edge cases (probation, fixed-term, below-threshold employee, large-scale retrenchment), classification disputes, leave entitlement questions, policy drafting scenarios
- Prior art: the existing `scripts/test-cookbooks.sh` pattern (input → validate output structure → check expected content)

## Out of Scope

- **Multi-jurisdiction support** — SA + US companies needing both sets of questions in a single cold-start. SA-only for v1.
- **MCP connectors** — no live connections to SAFLII, DoEL, CCMA, or LexisNexis SA. Requirements are documented for future implementation.
- **Automated statute monitoring** — reg-monitor adaptation for Government Gazette feeds. Manual updates for v1.
- **Commercial-legal adaptation** (phase 2) — Consumer Protection Act, SA contract conventions.
- **Privacy-legal / POPIA adaptation** (phase 3) — POPIA compliance, Information Regulator processes.
- **SaaS integration** — convergence with existing SA practice management product is future work.
- **Managed-agent cookbook adaptation** — no SA-specific managed agents in v1.
- **New marketplace plugin** — no `employment-legal-za` plugin; the overlay system extends the existing plugin.

## Further Notes

### Phase 2-3 expansion

A jurisdiction-expansion skill will be built after phase 1 ships. This skill will codify the overlay architecture (directory layout, file schemas, wiring pattern) and run a structured grilling interview to adapt additional practice areas. It loads `jurisdictions/za/ARCHITECTURE.md` as its primary context.

### Expert review gate

Before release, the SA overlay content (statute YAML values, topic overlay procedures, high-risk flag table, practice profile template) must be reviewed by an SA employment law practitioner. This is a process gate, not an automated test. The scenario evaluation suite provides a structured review surface.

### Statute currency

SA statutory thresholds change via Government Gazette, typically annually for monetary thresholds (BCEA earnings threshold, minimum wages) and periodically for structural changes (EEA designated employer criteria). The `last_confirmed` field on each statute file signals when values were last verified. Contributors should check `source_url` before relying on values for user-facing guidance.

### Upstream relationship

This fork tracks `anthropics/claude-for-legal` as `upstream` remote. The overlay architecture is designed so that `git merge upstream/main` produces conflicts only in `employment-legal/skills/cold-start-interview/SKILL.md` (the one modified file). All other SA content is additive and merge-clean.
