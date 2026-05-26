---
name: setup
description: Syncs your Velvoite workspace profile to the local CLAUDE.md so every other eu-finreg command runs scoped to your entity types, jurisdictions, and regulatory posture. Requires an existing Velvoite workspace (free 30-day Premium trial available at app.velvoite.eu).
argument-hint: "[--redo]"
---

# /eu-finreg:setup

Thin sync from the user's Velvoite workspace to `~/.claude/plugins/config/eu-finreg/CLAUDE.md`. The real profile lives at app.velvoite.eu — this command just mirrors it locally so every other command in this plugin runs in the user's scope.

`--redo` is accepted for compatibility but has no effect: this command always re-fetches.

---

## Step 1 — Check the API key

Run `echo "${VELVOITE_API_KEY:+set}"`. If it prints `set`, continue. If it prints nothing, stop and tell the user, verbatim:

> `VELVOITE_API_KEY` is not set. The plugin needs a Velvoite API key.
>
> No workspace yet? Sign up at https://app.velvoite.eu/register?source=plugin (free 30-day Premium trial).
> Have a workspace? Create a key at https://app.velvoite.eu/account?source=plugin, then:
>
> ```
> export VELVOITE_API_KEY=vv_your_key_here
> ```
>
> Then re-run `/eu-finreg:setup`.

Do not call any MCP tools. STOP.

## Step 2 — Sync

Call the `velvoite` MCP tool `get_company_profile()`.

**On failure:** tell the user in one line what went wrong and how to fix it (bad key → re-create at /account?source=plugin; no profile yet → finish workspace setup at /account?source=plugin; network → retry). Do not fall back to manual entry. Do not invent a profile. STOP.

**On success:** populate the template and write the file, following the exact substitution protocol below.

### 2a — Read the template

Read the template file at `${CLAUDE_PLUGIN_ROOT}/CLAUDE.md` using the Read tool. This is the canonical structure. You will mutate ONLY the `[PLACEHOLDER]` markers and the `[DATE]` marker. Everything else — headings, table column headers, section names, bullet structure, the HTML/italic comment lines — stays byte-for-byte identical.

Other plugin skills parse this file looking for specific heading text (e.g. `Entity type(s)`, `Jurisdiction(s)`, `Actor roles per regulation`). If you rename any heading or change a table into bullets, those skills break.

### 2b — Substitute placeholders

**API response shape** (from `get_company_profile()` — use these exact field paths):

```
company_name: str                            # top-level
jurisdictions: list[str]                     # top-level; always includes 'eu'; codes are lowercase ('fi', 'de', 'eu')
profile.entity_types: list[str]              # codes like 'credit_institution', 'payment_institution'
profile.actor_roles: dict[str, list[str]]    # regulation_code (lowercase) -> list of role codes
                                             # e.g. {'dora': ['financial_entity'], 'ai_act': ['ai_deployer']}
profile.conditions: dict[str, list[str]]     # regulation_code (lowercase) -> list of conditions
                                             # e.g. {'dora': ['uses_ict_third_party']}
profile_complete: bool                       # false = user hasn't finished onboarding
```

**Regulation code → display name** (use this mapping wherever a display name is needed; codes from the API are lowercase snake_case, the template uses display names):

| Code | Display name |
|---|---|
| `gdpr` | GDPR |
| `ai_act` | AI Act |
| `dora` | DORA |
| `mica` | MiCA |
| `mifid2` | MiFID II |
| `aml` | AML/CFT |
| `crd_crr` | CRD/CRR |
| `psd` | PSD |
| `idd` | IDD |
| `solvency_2` | Solvency II |
| `solvency` | Solvency II |
| `sfdr` | SFDR |
| `csrd` | CSRD |
| `emir` | EMIR |
| `bmr` | BMR |
| `irrd` | IRRD |

If the API returns a regulation code not in this table, use the code as-is for the display name (lowercase snake_case).

Apply these substitutions in order. Each rule says exactly what to replace and what to write.

**Top-of-file date:**
- `[DATE]` in the italic line under the H1 → today's ISO date (YYYY-MM-DD).

**Company table** (preserve the `| Field | Value |` two-column layout):
- `[PLACEHOLDER]` in the `Name` row → the top-level `company_name` field. If missing/empty, write `(none)`.
- `[PLACEHOLDER — credit_institution | ... | reinsurance]` in the `Entity type(s)` row → `profile.entity_types` joined with ` | ` (space-pipe-space), values AS-IS (lowercase snake_case). If empty or missing, write `(none)`.
- `[PLACEHOLDER — FI | DE | EU-wide | ...]` in the `Jurisdiction(s)` row → top-level `jurisdictions`, each code UPPER-cased, joined with ` | ` (e.g. `['fi', 'eu']` → `FI | EU`). If empty or missing, write `(none)`.
- `[PLACEHOLDER — FIN-FSA | BaFin | ECB SSM | ...]` in the `Regulatory authority` row → derive from jurisdictions and entity types:
  - `fi` → `FIN-FSA`
  - `de` → `BaFin`
  - `eu` AND `profile.entity_types` contains `credit_institution` → `ECB SSM`
  - Combine derived values with ` | ` when multiple apply.
  - If nothing can be derived, write `(none)`.

**Actor roles per regulation table** (preserve the `| Regulation | Role(s) |` layout and every row that ships in the template):
- For each template row (`GDPR`, `DORA`, `AI Act`, `MiCA`, `MiFID II`, `AML/CFT`), look up the corresponding lowercase code (`gdpr`, `dora`, `ai_act`, `mica`, `mifid2`, `aml`) in `profile.actor_roles`. If present, replace the `[PLACEHOLDER — ...]` with the role codes joined by ` | ` (role codes stay AS-IS — lowercase snake_case, e.g. `financial_entity | ict_third_party`). If absent from the API response, replace the `[PLACEHOLDER — ...]` with the literal text `(not configured)`. Do not delete any template row.
- For each remaining entry in `profile.actor_roles` that is NOT already covered by a template row, append a new row at the bottom of this table using the same `| Regulation | Role(s) |` format. Use the display name from the mapping table above; role codes joined by ` | ` AS-IS. Do not re-order the existing template rows.

**Active conditions** (preserve the section heading and the explanatory paragraph):
- Flatten `profile.conditions` (a dict of `regulation_code -> list[str]`) into one bullet per condition. Format each bullet as `- <regulation_display_name>: <condition>` (e.g. `- DORA: uses_ict_third_party`). Replace ALL three `- [PLACEHOLDER ...]` bullets with the flattened list. If the API returns zero conditions across all regulations, replace the three placeholder bullets with a single bullet `- (none specified)`.

**Velvoite workspace table** (preserve the `| Field | Value |` layout and the `API key env var` row exactly):
- `[PLACEHOLDER — UUID from get_company_profile()]` in the `Workspace ID` row → write the literal text `(determined by API key)`. The API does not return a workspace UUID — identity is bound to the `VELVOITE_API_KEY`.

**Last updated:**
- `[PLACEHOLDER — YYYY-MM-DD by /eu-finreg:setup]` → `<today's ISO date> by /eu-finreg:setup`.

Do NOT touch anything else. Do not add new sections, remove the trailing italics, or rewrap tables.

### 2c — Write the file

`mkdir -p ~/.claude/plugins/config/eu-finreg`, then write the populated content to `~/.claude/plugins/config/eu-finreg/CLAUDE.md`.

### 2d — Verify the written file

After writing the file, verify it contains the literal strings `Entity type(s)` and `Jurisdiction(s)` (with the parenthetical `(s)`) — these are the heading patterns the other skills parse. Also verify `Actor roles per regulation`, `Active conditions`, and `Velvoite workspace` are present.

If any of these strings is missing, you did NOT follow the template — re-do the substitution preserving template structure exactly. Do not proceed to Step 2e until verification passes.

### 2e — Print the success message

Print: `Synced from workspace <company_name>. Saved to ~/.claude/plugins/config/eu-finreg/CLAUDE.md.`

### 2f — Profile-complete check

If `profile_complete` is `false` in the API response, append this note (verbatim) on a new line after the success message:

> Note: your workspace profile is incomplete — finish onboarding at https://app.velvoite.eu/account?source=plugin to populate entity types and actor roles per regulation. The current sync may be sparse.

If `profile_complete` is `true`, skip this note.

### 2g — Non-finreg scope check

Inspect the regulation codes present in `profile.actor_roles` (the keys of the dict).

- **Finreg codes** (any one of these means the user IS in scope): `dora`, `mica`, `psd`, `aml`, `crd_crr`, `mifid2`, `idd`, `solvency_2`, `solvency`, `sfdr`, `emir`, `bmr`, `irrd`.
- **Non-finreg codes** (these alone mean the user is OUT of primary scope): `gdpr`, `ai_act`, `csrd`.

If the user has ZERO finreg regulations configured (i.e. `profile.actor_roles` keys are all in the non-finreg list, or the dict is empty), append this disclaimer (verbatim) on a new line after any prior messages:

> Note: your workspace has no EU financial regulations configured (only GDPR/AI Act). This plugin specializes in EU financial regulation — corpus depth for DORA, MiCA, PSD, AML, etc. is much greater than for GDPR or AI Act. For GDPR-specific work, consider `privacy-legal` from claude-for-legal; for AI Act, consider `ai-governance-legal`. The plugin will still work for your configured regulations, but results will be thinner.

If the user has at least one finreg regulation, do NOT print this disclaimer.

Both the profile-complete note (2f) and the non-finreg disclaimer (2g) can appear together — print 2f first, then 2g.

---

## Hard rules

- Write to `~/.claude/plugins/config/eu-finreg/CLAUDE.md`, never to the current working directory.
- Never persist `VELVOITE_API_KEY` to any file.
- On `get_company_profile()` failure, surface the error and stop — never substitute defaults.
- **MUST use the template structure exactly. Replace only `[PLACEHOLDER]` and `[DATE]` markers. Do not change headings, table structure, column headers, or section names — other skills parse for specific heading text (`Entity type(s)`, `Jurisdiction(s)`, `Actor roles per regulation`, `Active conditions`, `Velvoite workspace`, `Last updated`).** Do not convert tables to bullets or vice versa. Do not paraphrase. If the API has no value for a field, write the documented sentinel (`(none)`, `(not configured)`, `(none specified)`, `(determined by API key)`) — do not invent or omit the row.

---

eu-finreg outputs are drafts for compliance / legal review — not legal advice.
