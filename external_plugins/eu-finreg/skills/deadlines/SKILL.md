---
name: deadlines
description: Upcoming EU financial regulation compliance deadlines in the user's regulatory scope. Reads from ~/.claude/plugins/config/eu-finreg/CLAUDE.md. Use when the user asks "what's coming up", "deadlines next quarter", "DORA / MiCA / AI Act key dates", or wants a compliance calendar filtered to their actor roles.
argument-hint: "[days] [regulation]"
---

# /eu-finreg:deadlines

Returns upcoming compliance deadlines from the Velvoite corpus, filtered to the user's practice profile (actor roles per regulation).

---

## Step 1 — Load practice profile

1. Read `~/.claude/plugins/config/eu-finreg/CLAUDE.md`.
2. **If the file does not exist OR its contents still contain any `[PLACEHOLDER]` marker:** stop immediately and tell the user, verbatim:
   > Your eu-finreg practice profile is missing or unconfigured. Run `/eu-finreg:setup` to sync it from your Velvoite workspace. If you don't have a workspace yet, sign up at https://app.velvoite.eu/register?source=plugin (free 30-day Premium trial).
   Do not call any MCP tools. STOP.
3. From the profile, extract:
   - `entity_types` — pipe-separated list.
   - `jurisdictions` — pipe-separated list.
   - `actor_roles_by_reg` — mapping of regulation → role(s) from the "Actor roles per regulation" table. Skip rows whose value is empty or still `[PLACEHOLDER]`.
   - `all_roles` — flat de-duplicated list of every role across every regulation in the table.

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

- `$1` (optional): integer number of days to look ahead. Default `90`. Accept `30`, `60`, `90`, `180`, `365` — any positive integer is fine.
- `$2` (optional): regulation filter — e.g. `dora`, `mica`. Lowercase.

If `$1` is non-integer and looks like a regulation code, treat it as the regulation arg and use the default `90` days.

---

## Step 4 — Call the MCP tool

Pick the primary entity type from `entity_types` (if the user has multiple, pick the first — the server expects a single value, not a comma-joined list, for `entity_type`).

**Empty entity_type handling:** If the profile's "Entity type(s)" value is empty, `(none)`, `(none configured)`, or `[PLACEHOLDER]`:
- OMIT the `entity_type` param from the MCP call entirely (do not pass an empty string — that's a different filter behavior server-side).
- Continue with other filters (regulation, days_ahead, etc.).
- Add this line to the output FOOTER (before the disclaimer): `Note: results are unscoped to entity type (your workspace has no entity type configured). For sharper results, set an entity type at https://app.velvoite.eu/account.`

If `regulation` is given and the user has no role recorded for that regulation in `actor_roles_by_reg`, warn them once at the top of the output:

> No actor role recorded for `<regulation>` in your profile. Run `/eu-finreg:setup --redo` to add role-scoped filtering. Returning unscoped deadlines for the regulation.

(Then proceed — the server doesn't filter by actor_role on this tool anyway, see below.)

Call:

```
get_deadlines(
  entity_type=<primary entity type from profile — OMIT if empty/none/placeholder>,
  regulation=<regulation if given, else omit>,
  days_ahead=<days or 90>,
  include_overdue=false
)
```

**Do NOT pass `actor_role` — the server does not accept it on `get_deadlines`.** (Confirmed by reading `velvoite-mcp/server.py` lines 442-466.) `include_overdue=false` is critical — without it, all past-due deadlines come back regardless of `days_ahead`.

---

## Step 5 — Render

Sort the response by deadline date ascending. Markdown table:

| Date | Days away | Regulation | Obligation | Source |

- `Date` — ISO `YYYY-MM-DD`. **Bold the cell** if the date is within 30 days of today. Prepend `⚠ ` (the only emoji in this plugin; surfaces urgency) to the date if it is within 7 days.
- `Days away` — integer difference between the deadline and today. Negative values (overdue) should still render and be marked `⚠`.
- `Regulation` — uppercase code, e.g. `DORA`.
- `Obligation` — short summary, trim to ~120 chars.
- `Source` — markdown link `[<doc title trimmed>](<url>)` if the response includes a source URL, else the document title alone.

If the MCP call returns zero rows: print

> No upcoming deadlines in the next `<days>` days for `<entity_type>`. (Note: most EU financial regulation obligations are continuously applicable once their regulation enters force; this view shows future application / transition dates within the window.) Widen with `/eu-finreg:deadlines 365` or remove the regulation filter.

---

## Step 6 — Footer

Below the table, on its own line:

> Scoped to: `<entity_types>` / `<jurisdictions>` / actor roles: `<reg1>:<role1>, <reg2>:<role2>, …`

Then a blank line, then the disclaimer:

> Drafts for compliance / legal review — not legal advice.

---

## Hard rules

- Never call MCP tools before the practice profile is loaded and validated.
- Always sort by date ascending — never by regulation or any other field.
- `⚠` is the only emoji this plugin uses. Do not add others.
- The disclaimer line is mandatory on every output.
