# South African Jurisdiction Overlay — Architecture Guide

This document is the operating manual for the SA overlay system. It describes the directory layout, file schemas, wiring mechanism, and how to extend the system to new practice areas.

For the rationale behind these decisions, see `project/decisions/001-sa-overlay-architecture.md`.

---

## Directory Layout

```
jurisdictions/za/
├── ARCHITECTURE.md                        # This file
├── statutes/                              # Shared YAML statute files (all practice areas)
│   ├── bcea.yaml                          # Basic Conditions of Employment Act 75 of 1997
│   ├── lra.yaml                           # Labour Relations Act 66 of 1995
│   ├── eea.yaml                           # Employment Equity Act 55 of 1998
│   └── sectoral-determinations.yaml       # Per-sector overrides (domestic, hospitality, farm, etc.)
│
├── employment-legal/                      # Practice-area overlay
│   ├── practice-profile-template.md       # ZA variant of employment-legal/CLAUDE.md template
│   ├── router.md                          # Maps skills → topic files + statute files
│   └── topics/                            # Shared markdown overlays (by legal topic)
│       ├── dismissal.md                   # LRA s188/s189, CCMA, Schedule 8, high-risk flags
│       ├── hiring.md                      # Restraint of trade, probation, EEA at hire
│       ├── classification.md              # BCEA s213, common law control test, deemed employees
│       ├── leave-and-conditions.md        # BCEA leave (s20-28), above-minimum handling
│       ├── policy-and-handbook.md         # Disciplinary codes, grievance procedures, SA conventions
│       └── investigation-privilege.md     # SA legal professional privilege, Protected Disclosures Act, POPIA
│
├── commercial-legal/                      # Phase 2 (empty until then)
│
└── privacy-legal/                         # Phase 3 — POPIA (empty until then)
```

Planning documents live outside this tree:
- `project/decisions/001-sa-overlay-architecture.md` — ADR with rationale
- `project/mcp-requirements-za.md` — deferred MCP connector requirements
- `project/prd-sa-employment-overlay.md` — PRD for phase 1

## How It Works

### 1. Jurisdiction detection

Jurisdiction is determined from two sources, checked in order:

1. **Matter-level override** — if a matter workspace is active and has a `jurisdiction` field, use it.
2. **Company profile default** — the `jurisdiction` field in `~/.claude/plugins/config/claude-for-legal/company-profile.md`, set during cold-start.

If jurisdiction = `ZA`, the overlay system activates.

### 2. Overlay loading sequence

When a skill runs and jurisdiction = ZA:

1. Skill loads the practice profile as usual: `~/.claude/plugins/config/claude-for-legal/employment-legal/CLAUDE.md`
2. The ZA practice profile (written from `practice-profile-template.md`) contains an instruction: **"After loading context, read `jurisdictions/za/employment-legal/router.md` and load the listed overlays for this skill."**
3. The router maps the skill name to its relevant topic files and statute files.
4. The skill loads the listed topic overlays (markdown) and statute files (YAML).
5. The skill follows the SA overlay guidance instead of its US-default sections.

### 3. Router format

The router is a YAML mapping:

```yaml
termination-review:
  topics: [dismissal]
  statutes: [lra, bcea]

hiring-review:
  topics: [hiring]
  statutes: [bcea, eea]

worker-classification:
  topics: [classification]
  statutes: [bcea]

wage-hour-qa:
  topics: [leave-and-conditions]
  statutes: [bcea]

leave-tracker:
  topics: [leave-and-conditions]
  statutes: [bcea]

policy-drafting:
  topics: [policy-and-handbook, dismissal]
  statutes: [bcea, lra, eea]

cold-start-interview:
  topics: []
  statutes: [bcea, lra, eea]
```

Topic names resolve to `jurisdictions/za/employment-legal/topics/{name}.md`.
Statute names resolve to `jurisdictions/za/statutes/{name}.yaml`.

## File Schemas

### Statute YAML

```yaml
statute: "Basic Conditions of Employment Act 75 of 1997"  # Full Act name and number
authority: "Department of Employment and Labour"            # Governing body
last_confirmed: "2025-03-01"                                # When values were last verified
source_url: "https://www.labour.gov.za/..."                 # Authoritative source for verification

sections:
  earnings_threshold:                      # Machine-readable key
    ref: "BCEA s6(3), GN R2316 GG 48928"  # Statute section + Gazette reference
    value: 254371.67                       # The threshold/limit/amount
    currency: "ZAR"                        # Currency (if monetary)
    unit: "per_annum"                      # Unit of measurement
    effective_from: "2024-03-01"           # When this value took effect (null = original statute)
    effective_until: null                  # When superseded (null = still current)
    effect: "Employees earning above threshold excluded from ss9-16, 17(2), 18(3)"
    gazette_date: "2024-03-01"            # Gazette publication date (if set by Gazette)
    note: "Updated annually via Government Gazette"
```

**Required fields:** `ref`, `value`, `effective_from`, `effective_until`, `effect`
**Monetary entries also require:** `currency`, `unit`
**Optional:** `gazette_date`, `note`

### Temporal rules

- `effective_from: null` means the value is from the original statute (no specific commencement date relevant).
- `effective_until: null` means the value is still current.
- When a threshold changes: add a new entry with the new `effective_from`, and set `effective_until` on the old entry to the day before the new value takes effect.
- Never overwrite an existing entry — append. Old values support historical queries ("what applied when this employee was dismissed 8 months ago?").

### Topic overlay markdown

Topic files are standard markdown with:
- A clear heading structure (H2 for major sections)
- SA statute references in the format `LRA s188`, `BCEA s9(1)`, `Schedule 8 Item 8`
- Flag tables matching the format used in the existing employment-legal skills
- No US-specific legal concepts (FMLA, FLSA, at-will, EEOC, NLRB, state-specific references)

### Practice profile template

Follows the same structure as `employment-legal/CLAUDE.md` but with SA-native sections:

| US template section | ZA template equivalent |
|---|---|
| `## Jurisdictional footprint` — US states with employees | Provinces, sectoral determinations, bargaining council coverage |
| `## Termination review` — FMLA, at-will flags | LRA s188 fairness, CCMA process, Schedule 8, SA high-risk flags |
| `## Hiring review` — state non-compete rules | Restraint of trade doctrine, probation (LRA Schedule 8 Item 8), EEA obligations |
| `## Wage & hour` — FLSA exempt/non-exempt | BCEA earnings threshold, ordinary hours, overtime, sectoral minimums |
| `## Handbook` — state supplements | Disciplinary code, grievance procedure, SA policy conventions |
| `## Escalation` — EEOC, DOL references | CCMA, Labour Court, bargaining council, external labour consultants |

## Adding a New Practice Area

To adapt another plugin (e.g., commercial-legal) for SA:

### Step 1: Create the directory structure

```
jurisdictions/za/commercial-legal/
├── practice-profile-template.md
├── router.md
└── topics/
    ├── <topic-1>.md
    └── <topic-2>.md
```

### Step 2: Add statute files (if needed)

If the practice area references statutes not already in `jurisdictions/za/statutes/`, add new YAML files following the statute schema above. Statutes shared across practice areas (e.g., BCEA is used by employment-legal and could be relevant to commercial-legal) live in the shared `statutes/` directory.

### Step 3: Identify skills needing overlays

Assess each skill in the plugin for SA divergence:
- **HIGH:** US defaults produce wrong legal guidance → needs overlay
- **MEDIUM:** Process is portable but legal framing differs → may need overlay
- **LOW:** Jurisdiction-neutral infrastructure → no overlay needed

### Step 4: Write topic overlays

Organize by legal topic, not by skill. A topic file referenced by multiple skills avoids duplication. Include:
- SA statutory framework and references
- Procedural checklists (e.g., hearing steps, filing timelines)
- Flag tables (high-risk indicators)
- Differences from the US default the skill assumes

### Step 5: Write the router

Map each skill to its relevant topic files and statute files.

### Step 6: Write the practice profile template

Replace US-specific sections with SA equivalents. Keep jurisdiction-neutral sections (output formatting, guardrails, matter workspaces) unchanged.

### Step 7: Fork the cold-start interview (if not already forked)

If the plugin's cold-start interview hasn't been forked for ZA yet, add a jurisdiction branch after Part 0 that asks SA-specific configuration questions and writes to the ZA practice profile template.

### Step 8: Add tests

- Structural: YAML schema validation, router cross-references, template completeness
- Scenario evals: 3-5 golden-path cases per overlaid skill
- Expert review: SA practitioner reviews overlay content before release

## Validation

### Structural (CI)

Run before every PR:

```bash
# Statute YAML schema validation
python3 scripts/validate-za-statutes.py

# Router cross-reference check
python3 scripts/validate-za-router.py

# Template completeness check
python3 scripts/validate-za-templates.py
```

### Scenario evaluation

Golden-path test cases in `jurisdictions/za/evals/`:

```
jurisdictions/za/evals/
├── employment-legal/
│   ├── termination-review/
│   │   ├── case-01-misconduct-no-hearing.yaml
│   │   ├── case-02-retrenchment-large-scale.yaml
│   │   └── case-03-auto-unfair-pregnancy.yaml
│   ├── hiring-review/
│   │   └── ...
│   └── ...
```

Each case specifies:
- `input`: fact pattern description
- `expected_flags`: list of flags that must fire
- `expected_statutes`: statute references that must appear
- `must_not_contain`: US concepts that must not appear (FMLA, FLSA, at-will, etc.)

### Expert review

Before release, an SA employment law practitioner reviews:
- Statute YAML values against current Government Gazette
- Topic overlay procedures against current LRA/BCEA/EEA
- High-risk flag table against current CCMA referral patterns
- Practice profile template for completeness and correctness

## MCP Connectors (Deferred)

Requirements documented in `project/mcp-requirements-za.md`. Priority order:

1. **SAFLII** (saflii.org) — free SA case law (Labour Court, Labour Appeal Court, Constitutional Court)
2. **Department of Employment and Labour** (labour.gov.za) — Gazette notices, sectoral determinations, BCEA amendments
3. **CCMA** (ccma.org.za) — arbitration awards, case outcomes
4. **LexisNexis SA / Juta** — commercial annotated statutes and case law (equivalent to Westlaw)

## Key Constraints

- **No US legal concepts in ZA outputs.** When jurisdiction = ZA, skills must not reference FMLA, FLSA, at-will employment, EEOC, NLRB, state-specific rules, or US case law.
- **One upstream file modification.** Only `employment-legal/skills/cold-start-interview/SKILL.md` is modified. All other changes are additive in `jurisdictions/za/`.
- **Temporal fields are mandatory.** Every statute entry must have `effective_from` and `effective_until`, even if both are null.
- **Multi-jurisdiction is out of scope.** The system serves SA-only companies in v1.
