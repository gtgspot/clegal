# MCP Connector Requirements — South Africa

**Status:** Deferred (phase 2+)
**Date:** 2026-05-17

## Context

The SA employment law overlay (phase 1) ships without live MCP connections to SA legal data sources. Statute thresholds are maintained in YAML files with manual updates. This document specifies the requirements for future MCP connectors so that integration work has clear specifications when these sources become available.

## Priority Order

### 1. SAFLII (Southern African Legal Information Institute)

**URL:** https://www.saflii.org
**Access:** Public, free
**What it provides:** Full-text judgments from Labour Court, Labour Appeal Court, Constitutional Court, Supreme Court of Appeal, High Courts, and CCMA arbitration awards (selected)
**Value:** Primary legal research for SA employment law — case law citations, precedent checking, ratio decidendi extraction
**Integration pattern:** Search by keyword/citation → return case metadata + full text
**Equivalent in upstream:** CourtListener (US)

**Required capabilities:**
- Search by case name, citation, keyword, court, date range
- Return structured metadata (case name, citation, court, date, judges, headnote)
- Return full judgment text (for analysis by skills)
- Filter by court (Labour Court, LAC, CC, SCA)
- Filter by subject matter (employment, labour, discrimination, unfair dismissal)

**Source attribution tag:** `[SAFLII]` — used only when citation appears in tool result this session

### 2. Department of Employment and Labour

**URL:** https://www.labour.gov.za
**Access:** Public, free
**What it provides:** Government Gazette notices (BCEA threshold updates, minimum wage determinations, sectoral determinations), EEA reporting forms, Codes of Good Practice, policy documents
**Value:** Authoritative source for statutory threshold updates; enables automated statute YAML updates via reg-monitor cookbook
**Integration pattern:** Monitor Gazette feed → flag threshold changes → open PR with proposed YAML updates

**Required capabilities:**
- Monitor Government Gazette for employment-related notices
- Parse threshold values from Gazette notices (earnings threshold, minimum wages, sectoral rates)
- Return structured data (Gazette number, notice number, effective date, new value)
- Access current versions of Codes of Good Practice (Schedule 8, harassment, dismissal)

**Source attribution tag:** `[statute / regulator site]`

**Phase 2 integration with reg-monitor cookbook:**
- Add DoEL Gazette as a feed source in a new SA variant of the reg-monitor cookbook
- Digest-writer subagent produces PR with proposed YAML changes (new `effective_from`, `effective_until` on old entry, updated `last_confirmed`)
- Human reviewer confirms before merge

### 3. CCMA (Commission for Conciliation, Mediation and Arbitration)

**URL:** https://www.ccma.org.za
**Access:** Public (limited programmatic access)
**What it provides:** Arbitration awards, conciliation statistics, jurisdictional rulings, practice notes
**Value:** CCMA outcomes inform dispute posture, flag common employer failures, provide precedent for unfair dismissal and unfair labour practice cases
**Integration pattern:** Search awards by employer/sector/issue → return structured outcome data

**Required capabilities:**
- Search arbitration awards by keyword, sector, issue type, date range
- Return structured metadata (case number, commissioner, date, parties, issue, outcome, remedy)
- Return award text (for analysis)
- Access practice notes and guidelines

**Source attribution tag:** `[CCMA]`

**Note:** CCMA's digital infrastructure is less mature than SAFLII. Programmatic access may require scraping or partnership. Arbitration awards are not always published. This connector may need to start as a curated subset.

### 4. LexisNexis SA / Juta

**URL:** Commercial (subscription required)
**What it provides:** Annotated statutes, case law with headnotes and annotations, academic commentary, practice guides
**Value:** Premium legal research equivalent to Westlaw in the US; annotated statutes are particularly valuable for understanding how courts have interpreted specific sections
**Integration pattern:** Similar to CoCounsel/Westlaw — search → return annotated results with citations
**Equivalent in upstream:** CoCounsel (Westlaw) external plugin

**Required capabilities:**
- Search by statute section, case citation, keyword
- Return annotated statute text with court interpretation notes
- Return case law with headnotes and editorial commentary
- Cross-reference between statutes and interpreting cases

**Source attribution tag:** `[LexisNexis SA]` or `[Juta]`

**Note:** This is a commercial integration. The CoCounsel plugin in `external_plugins/` provides a model — vendor builds and maintains the plugin, changes land via PR. A LexisNexis SA or Juta integration would follow the same pattern under `external_plugins/`.

## Integration Architecture

### How connectors plug into the overlay system

MCP connectors are registered in the plugin's `.mcp.json` file. For SA-specific connectors:

1. Add entries to `employment-legal/.mcp.json` (or a ZA-specific override if the connector should only activate for ZA jurisdiction)
2. Topic overlays reference the connector by name when citing research steps (e.g., "search SAFLII for [citation]")
3. Source attribution tags in the guardrails section of the practice profile template map to the connector names
4. The pre-flight citation check in the guardrails tests whether the connector is responding before each session

### Source attribution with SA connectors

The existing guardrail framework applies unchanged:

| Tag | When to use |
|---|---|
| `[SAFLII]` | Citation appeared in SAFLII tool result this session |
| `[CCMA]` | Award/ruling appeared in CCMA tool result this session |
| `[statute / regulator site]` | Text fetched from labour.gov.za this session |
| `[LexisNexis SA]` / `[Juta]` | Citation appeared in commercial research tool result this session |
| `[user provided]` | User pasted or linked the source |
| `[model knowledge — verify]` | Everything else (default) |

### Automated statute monitoring (phase 2)

The reg-monitor managed-agent cookbook (`managed-agent-cookbooks/reg-monitor/`) already monitors US regulatory feeds (Federal Register, agency feeds). An SA variant would:

1. Add Government Gazette / DoEL feeds as sources
2. The `feed-reader` subagent monitors for employment-related notices
3. The `materiality-filter` subagent identifies threshold changes
4. The `digest-writer` subagent produces a PR with proposed YAML updates to `jurisdictions/za/statutes/`
5. A human reviewer verifies the values and merges

This follows the existing cookbook security model (reader/analyzer/writer tiers, no MCP on orchestrator).
