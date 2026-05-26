---
name: enforcement
description: Recent EU financial regulation enforcement decisions in the user's scope (fines, sanctions, withdrawal of authorisation). Reads from ~/.claude/plugins/config/eu-finreg/CLAUDE.md. Use when the user asks "what got fined recently", "enforcement trends", "penalties under DORA / MiCA / AML", or wants to see how regulators are punishing similar entities.
argument-hint: "[regulation_code] [min_fine_eur] — NOTE: no time-window arg (server limitation)"
---

# /eu-finreg:enforcement

Returns enforcement decisions (fines, sanctions, withdrawal of authorisation, public reprimands) from EU and national regulators, scoped to the user's entity type and jurisdictions. Returns all-time results from the corpus — the MCP tool does not currently support a time-window filter.

---

## Step 1 — Load practice profile

1. Read `~/.claude/plugins/config/eu-finreg/CLAUDE.md`.
2. **If the file does not exist OR its contents still contain any `[PLACEHOLDER]` marker:** stop immediately and tell the user, verbatim:
   > Your eu-finreg practice profile is missing or unconfigured. Run `/eu-finreg:setup` to sync it from your Velvoite workspace. If you don't have a workspace yet, sign up at https://app.velvoite.eu/register?source=plugin (free 30-day Premium trial).
   Do not call any MCP tools. Do not fabricate scope. STOP.
3. From the profile, extract:
   - `entity_types` — pipe-separated list from the Company table row "Entity type(s)".
   - `jurisdictions` — pipe-separated list from "Jurisdiction(s)".
   - `actor_roles_by_reg` — mapping of regulation → role(s) from the "Actor roles per regulation" table. Used to determine which regulations are "in scope" for the intelligence section.

---

## Step 2 — Check API key

Run: `echo "${VELVOITE_API_KEY:+set}"`. If it prints `set`, continue. If it prints nothing, stop immediately and tell the user, verbatim:

> `VELVOITE_API_KEY` is not set. The plugin needs a Velvoite API key to call the corpus.
>
> Either export your existing key:
>
> ```
> export VELVOITE_API_KEY=vv_your_key_here
> ```
>
> Or run `/eu-finreg:setup` for full setup instructions (including how to get a key).

Do not call any MCP tools. STOP.

---

## Step 3 — Parse arguments

- `$1` (optional): regulation filter — must be a lowercase canonical code like `dora`, `mica`, `aml`, `gdpr`, `psd`, `mifid2`, `crd_crr`, `idd`, `solvency_2`, `sfdr`, `emir`, `bmr`, `irrd`, `ai_act`, `csrd`.
- `$2` (optional): minimum penalty in EUR (passed as `penalty_min`). Default unset (no minimum).

**Argument disambiguation:**
- If `$1` matches a known regulation code (from the list above) → treat as `regulation`.
- If `$1` is a number → the user likely meant a time window (e.g. `/eu-finreg:enforcement 365` = "last 365 days"). The server does NOT support time windows. Tell the user explicitly:

  > Note: `/eu-finreg:enforcement` does not support a time-window argument — the underlying corpus tool returns all-time enforcement results. If you meant a minimum penalty in EUR, re-run as `/eu-finreg:enforcement <regulation_code> <amount>` (e.g. `/eu-finreg:enforcement aml 10000`). Continuing with all-time results, no filter applied.

  Then proceed with no `regulation` or `penalty_min` filter — return all-time results scoped to entity type only.

- If `$1` is anything else (unknown string) → treat as `regulation` and pass it through; the server will return zero rows if it's not recognised.

> **Time-window limitation:** the MCP `get_enforcement_decisions` tool does NOT support a `days` / lookback filter. The corpus returns all-time enforcement decisions matching the other filters. This limitation is also surfaced in the output footer (see Step 7).

---

## Step 4 — Fetch enforcement decisions

Pick the primary `entity_type` (first of the pipe-separated list — the server expects a single value).

**Empty entity_type handling:** If the profile's "Entity type(s)" value is empty, `(none)`, `(none configured)`, or `[PLACEHOLDER]`:
- OMIT the `entity_type` param from the MCP call entirely (do not pass an empty string — that's a different filter behavior server-side).
- Continue with other filters (regulation, authority, penalty_min, etc.).
- Add this line to the output FOOTER (before the disclaimer): `Note: results are unscoped to entity type (your workspace has no entity type configured). For sharper results, set an entity type at https://app.velvoite.eu/account.`

Optionally derive `authority` from the profile's "Regulatory authority" row (e.g. `BaFin`, `FIN-FSA`). If the row is `[PLACEHOLDER]` or empty, omit it.

Use the `velvoite` MCP server. Call:

```
get_enforcement_decisions(
  regulation=<regulation if given, else omit>,
  entity_type=<primary entity type from profile — OMIT if empty/none/placeholder>,
  authority=<optional — from profile's regulatory_authority, else omit>,
  penalty_min=<$2 if given, else omit>,
  violation_category=<optional, only if user explicitly asks>,
  per_page=20
)
```

**Do NOT pass `days`, `min_fine_eur`, or `actor_role` — the server does not accept them.** (Confirmed by reading `velvoite-mcp/server.py` lines 612-655.) The real param names are `penalty_min` (not `min_fine_eur`) and there is no time-window filter at all.

If the MCP call returns zero rows: print

> No enforcement decisions match this scope. Try lowering the minimum penalty or dropping the regulation filter.

Then skip to Step 7 (footer) — no intelligence section.

---

## Step 5 — Render the table

Markdown table, sorted by **fine (€) descending**, then by **date descending**:

| Date | Authority | Entity | Regulation | Article | Fine (€) | Violation |

- `Date` — ISO `YYYY-MM-DD`.
- `Authority` — issuing regulator (e.g. `BaFin`, `FIN-FSA`, `CSSF`, `ECB`).
- `Entity` — sanctioned party name. Trim to ~40 chars.
- `Regulation` — regulation code, uppercase (e.g. `DORA`, `MiCA`, `AML`).
- `Article` — `article_ref` if present, else blank.
- `Fine (€)` — formatted with thousands separators, e.g. `1,250,000`. Blank if no monetary penalty (e.g. withdrawal of authorisation only).
- `Violation` — short violation summary or category. Trim to ~80 chars; add `…` if truncated.

---

## Step 6 — Top enforced obligations in scope

After the decisions table, determine the regulation(s) to use:

- If `$3` (regulation filter) was given, use that.
- Otherwise, use the regulations the user has an actor role for in `actor_roles_by_reg`, joined comma-separated.

Call:

```
get_enforcement_intelligence(
  regulation=<scope>,
  limit=5
)
```

Render as a short section:

> ### Top enforced obligations in your scope
>
> 1. **`<REG> Art. <article_ref>`** — `<obligation summary, ~120 chars>` (`<enforcement_count>` decisions)
> 2. …

If `get_enforcement_intelligence` returns nothing useful or errors, omit this section silently — don't fabricate.

---

## Step 7 — Footer

On its own line:

> Scoped to: `<entity_types>` / `<jurisdictions>`

Then on its own line:

> Note: enforcement results are all-time — the corpus does not currently support time-windowed enforcement queries.

Then a blank line, then the disclaimer:

> Drafts for compliance / legal review — not legal advice.

---

## Hard rules

- Never call MCP tools before the practice profile is loaded and validated.
- Never invent enforcement decisions, fines, or article references. If the MCP server returns nothing, say so.
- The disclaimer line is mandatory on every output.
