---
name: reg-feed-watcher
description: Weekly EU financial regulation digest — recent changes, upcoming deadlines, new enforcement, scoped to the user's practice profile. Used by the scheduled reg-feed-watcher agent and also invocable directly when the user wants to see this week's digest on demand.
argument-hint: "[days]"
---

# /eu-finreg:reg-feed-watcher

Composes a three-section weekly digest from the Velvoite corpus, filtered to the user's practice profile (entity types, jurisdictions, actor roles).

Invoke manually any time, or let the scheduled `reg-feed-watcher` agent run it on cadence and route the output to your inbox / Slack / Cowork channel.

---

## Step 1 — Load practice profile

1. Read `~/.claude/plugins/config/eu-finreg/CLAUDE.md`.
2. **If the file does not exist OR its contents still contain any `[PLACEHOLDER]` marker:** stop immediately and tell the user, verbatim:
   > Your eu-finreg practice profile is missing or unconfigured. Run `/eu-finreg:setup` to sync it from your Velvoite workspace. If you don't have a workspace yet, sign up at https://app.velvoite.eu/register?source=plugin (free 30-day Premium trial).
   Do not call any MCP tools. Do not fabricate scope. STOP.
3. From the profile, extract:
   - `entity_types` — pipe-separated list from "Entity type(s)".
   - `jurisdictions` — pipe-separated list from "Jurisdiction(s)". Map to lowercase ISO codes for the corpus (e.g. `FI` → `fi`, `DE` → `de`, `EU-wide` → `eu`).
   - `actor_roles_by_reg` — mapping of regulation → role(s) from the "Actor roles per regulation" table. Skip rows whose value is empty or `[PLACEHOLDER]`.
   - `all_roles` — flat de-duplicated list of every role across every regulation in the table.
   - `last_updated` — ISO date from the "Last updated" section.

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

## Step 3 — Check config freshness

Parse `last_updated` as an ISO date. If today minus `last_updated` is greater than 90 days, surface a one-line reminder at the very top of the digest (above the three sections):

> Your practice profile was last updated `<last_updated>`. Consider running `/eu-finreg:setup` to refresh it.

If `last_updated` cannot be parsed (missing, malformed), include the same reminder with `<unknown>` in place of the date. Do not stop — continue with the digest.

---

## Step 4 — Parse arguments

- `$1` (optional): integer lookback window in days for the "what changed" section. Default `7`.

---

## Step 5 — Fetch data (in parallel)

Pick the primary `entity_type` (first of the pipe-separated list) — the three tools below all expect a single value for `entity_type`, not a comma-joined list.

**Empty entity_type handling:** If the profile's "Entity type(s)" value is empty, `(none)`, `(none configured)`, or `[PLACEHOLDER]`:
- OMIT the `entity_type` param from ALL THREE MCP calls below (do not pass an empty string — that's a different filter behavior server-side).
- Continue with other filters (days, days_ahead, per_page, etc.).
- Add this line to the output FOOTER (before the disclaimer / scoped line): `Note: results are unscoped to entity type (your workspace has no entity type configured). For sharper results, set an entity type at https://app.velvoite.eu/account.`

Make these three MCP calls in parallel — they're independent. Use the `velvoite` MCP server.

```
get_recent_changes(
  days=<days or 7>,
  entity_type=<primary entity type from profile — OMIT if empty/none/placeholder>
)
```

```
get_deadlines(
  entity_type=<primary entity type from profile — OMIT if empty/none/placeholder>,
  days_ahead=30,
  include_overdue=false
)
```

```
get_enforcement_decisions(
  entity_type=<primary entity type from profile — OMIT if empty/none/placeholder>,
  per_page=20
)
```

**Param-name reality check** (verified against `velvoite-mcp/server.py`):
- `get_recent_changes` accepts: `days`, `entity_type`, `regulation`, `urgency_max`. It does NOT accept `actor_role` or `jurisdiction`.
- `get_deadlines` accepts: `entity_type`, `regulation`, `days_ahead`, `include_overdue`. It does NOT accept `actor_role` or `days` (the param is `days_ahead`). `include_overdue=false` is critical — the server default is `true`.
- `get_enforcement_decisions` accepts: `regulation`, `entity_type`, `authority`, `penalty_min`, `violation_category`, `page`, `per_page`. It does NOT accept `days`, `min_fine_eur`, or `actor_role`. There is no time-window filter — results are all-time.

If a call errors entirely (network, auth), omit that section from the digest and note the failure in the footer.

---

## Step 6 — Compose the digest

Sections appear in this fixed order. **Skip any section whose underlying call returned zero rows** — do not emit empty headers.

### What changed this week

Group recent changes by regulation, most active regulation first. Within each regulation, newest first.

```
## What changed this week

### <Regulation name> (<n> new)

- <YYYY-MM-DD>: <doc title> — <doc_type> — [<source name>](<url>)
- ...
```

### Deadlines in the next 30 days

Markdown table sorted by date ascending. Bold the date cell if within 30 days (which they all are, but keep the convention consistent with `/eu-finreg:deadlines`). Prepend `⚠ ` to the date if within 7 days or overdue.

```
## Deadlines in the next 30 days

| Date | Days away | Regulation | Obligation | Source |
| ---- | --------- | ---------- | ---------- | ------ |
```

### Enforcement decisions in scope

Top 5 by fine amount, descending. One-line summary each. The corpus returns all-time decisions for the entity type (no time-window filter on this tool); sort by date descending first to surface the most recent, then take the top 5 by fine amount.

```
## Enforcement decisions in scope (top 5 by fine, all-time)

1. **<YYYY-MM-DD> — <Authority>** fined **<Entity>** €<formatted fine> for <one-line violation> (<REG> Art. <article_ref>). [Source](<url>)
2. ...
```

If fewer than 5 decisions match, show all of them. If a decision has no monetary fine (e.g. withdrawal of authorisation), include it but say `no monetary fine` in place of the amount.

---

## Step 7 — Empty-corpus fallback

If **all three** calls returned zero rows (after the freshness reminder, if any), emit only:

> No movement in your scope this week — corpus quiet.

Then go straight to the footer.

---

## Step 8 — Footer

After the last section, on its own line:

> Scoped to `<entity_types>` / `<jurisdictions>`. Edit `~/.claude/plugins/config/eu-finreg/CLAUDE.md` to change scope. — Drafts for compliance / legal review, not legal advice.

If any calls failed (network, auth), append them on a separate line above the disclaimer:

> `(get_deadlines failed: <error>)`

---

## Hard rules

- Never call MCP tools before the practice profile is loaded and validated.
- Skip empty sections. Never emit a header above an empty list.
- The footer disclaimer is mandatory on every output.
- The stale-config reminder fires at >90 days, not earlier — don't nag.
- `⚠` is the only emoji this plugin uses.
