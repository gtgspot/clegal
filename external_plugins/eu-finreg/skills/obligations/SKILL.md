---
name: obligations
description: Lists EU financial regulation obligations applicable to the user's practice profile. Reads from ~/.claude/plugins/config/eu-finreg/CLAUDE.md. Honors filters: regulation, role, entity_type. Use when the user asks "what obligations apply to us", "which DORA / MiCA / AI Act duties hit my entity", or wants a scoped list of canonical legal requirements from the EU corpus.
argument-hint: "[regulation] [limit]"
---

# /eu-finreg:obligations

Returns a scoped list of canonical obligations from the Velvoite corpus, filtered to match the user's saved practice profile (entity type, jurisdictions, actor roles per regulation).

---

## Step 1 — Load practice profile

1. Read `~/.claude/plugins/config/eu-finreg/CLAUDE.md`.
2. **If the file does not exist OR its contents still contain any `[PLACEHOLDER]` marker:** stop immediately and tell the user, verbatim:
   > Your eu-finreg practice profile is missing or unconfigured. Run `/eu-finreg:setup` to sync it from your Velvoite workspace. If you don't have a workspace yet, sign up at https://app.velvoite.eu/register?source=plugin (free 30-day Premium trial).
   Do not call any MCP tools. Do not fabricate scope. STOP.
3. From the profile, extract:
   - `entity_types` — pipe-separated list from the Company table row "Entity type(s)".
   - `jurisdictions` — pipe-separated list from "Jurisdiction(s)".
   - `actor_roles_by_reg` — a mapping of regulation → role(s) from the "Actor roles per regulation" table. Skip rows whose value is empty or still `[PLACEHOLDER]`.
   - `active_conditions` — bullet list from the "Active conditions" section.

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

- `$1` (optional): regulation filter — e.g. `dora`, `mica`, `ai_act`, `gdpr`. Lowercase. Map to the canonical code used by the corpus.
- `$2` (optional): integer limit on rows returned. Default `50`.

If `$1` looks like an integer, treat it as the limit and leave `regulation` unset.

---

## Step 4 — Call the MCP tool

Use the `velvoite` MCP server. Prefer canonical obligations (deduplicated legal requirements with enforcement metrics).

**If `regulation` is given:**

Resolve the actor role for that regulation from `actor_roles_by_reg`. If the user has no role recorded for the requested regulation, tell them:

> No actor role recorded for `<regulation>` in your profile. Run `/eu-finreg:setup --redo` to add it, or pass a different regulation.

Pick the primary `entity_type` (first of the pipe-separated list) — the server's `entity_type` filter on `get_canonical_obligations` takes a single value, not a comma-joined list.

**Empty entity_type handling:** If the profile's "Entity type(s)" value is empty, `(none)`, `(none configured)`, or `[PLACEHOLDER]`:
- OMIT the `entity_type` param from the MCP call entirely (do not pass an empty string — that's a different filter behavior server-side).
- Continue with other filters (regulation, actor_role, etc.).
- Add this line to the output FOOTER (before the disclaimer): `Note: results are unscoped to entity type (your workspace has no entity type configured). For sharper results, set an entity type at https://app.velvoite.eu/account.`

Then call:

```
get_canonical_obligations(
  regulation=<regulation>,
  actor_role=<comma-joined roles for that regulation>,
  entity_type=<primary entity type from profile — OMIT if empty/none/placeholder>,
  per_page=<limit>
)
```

**Note:** the server param is `per_page` (max 100), not `limit`. (Confirmed by reading `velvoite-mcp/server.py` lines 351-390.)

**If `regulation` is not given:**

1. Call `get_obligation_summary(actor_role=<comma-joined roles across ALL regulations in actor_roles_by_reg>)` to get counts grouped by regulation.
2. Pick the regulation with the highest count as the default focus.
3. Call `get_canonical_obligations(regulation=<that regulation>, actor_role=<role for it>, entity_type=<primary entity type>, per_page=<limit>)`.
4. After rendering the table, append a short line listing the other regulations from the summary with their counts, so the user knows what's available: e.g. `Also in scope: mica (87), gdpr (52), mifid2 (41) — pass a regulation arg to drill into one.`

If `get_obligation_summary` is unavailable or returns nothing useful, fall back to calling `get_canonical_obligations(actor_role=<all roles joined>, entity_type=<primary entity type>, per_page=<limit>)` directly and skip the cross-regulation summary footer.

---

## Step 5 — Render

Markdown table, one row per obligation:

| # | Reg | Article | Obligation (summary) | Difficulty | Enforcement count |

- `#` — 1-indexed row number.
- `Reg` — regulation code (uppercase, e.g. `DORA`).
- `Article` — `article_ref` field from the canonical obligation, e.g. `Art. 6(2)`.
- `Obligation (summary)` — the canonical's short summary / `obligation_text`. Trim to ~140 chars; add `…` if truncated.
- `Difficulty` — the `compliance_difficulty` field (`low` | `medium` | `high` | `critical`). Render `—` if null. (Newer regulations like DORA may have many nulls until enrichment runs — that's expected.) The corpus does not expose a separate "risk tier" field; this is the closest analog.
- `Enforcement count` — `enforcement_count` if present, else `0`.

Sort by enforcement count descending, then by article ascending.

If the MCP call returns zero rows: print

> No obligations match this scope. Try widening the regulation filter, or check `/eu-finreg:setup` to confirm your actor role for this regulation.

---

## Step 6 — Footer

Below the table, on its own line, print:

> Scoped to: `<entity_types>` / `<jurisdictions>` / actor roles: `<reg1>:<role1>, <reg2>:<role2>, …`

Then a blank line, then the disclaimer:

> Drafts for compliance / legal review — not legal advice.

---

## Hard rules

- Never call MCP tools before the practice profile is loaded and validated.
- Never invent obligations. If the MCP server returns nothing, say so.
- The disclaimer line is mandatory on every output.
