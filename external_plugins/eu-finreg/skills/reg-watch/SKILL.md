---
name: reg-watch
description: What changed in EU financial regulation since the user last checked. Reads from ~/.claude/plugins/config/eu-finreg/CLAUDE.md. Use when the user asks "what's new", "what changed this week", "any new DORA / MiCA / AI Act updates", or wants a digest of recent supervisory publications filtered to their actor roles and jurisdictions.
argument-hint: "[days]"
---

# /eu-finreg:reg-watch

Returns recent EU financial regulation documents (publications, guidelines, Q&As, RTS, supervisory notices) filtered to the user's practice profile.

---

## Step 1 — Load practice profile

1. Read `~/.claude/plugins/config/eu-finreg/CLAUDE.md`.
2. **If the file does not exist OR its contents still contain any `[PLACEHOLDER]` marker:** stop immediately and tell the user, verbatim:
   > Your eu-finreg practice profile is missing or unconfigured. Run `/eu-finreg:setup` to sync it from your Velvoite workspace. If you don't have a workspace yet, sign up at https://app.velvoite.eu/register?source=plugin (free 30-day Premium trial).
   Do not call any MCP tools. STOP.
3. From the profile, extract:
   - `entity_types` — pipe-separated list.
   - `jurisdictions` — pipe-separated list from "Jurisdiction(s)". Map to lowercase ISO codes used by the corpus (e.g. `FI` → `fi`, `DE` → `de`, `EU-wide` → `eu`).
   - `actor_roles_by_reg` — mapping of regulation → role(s).
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

- `$1` (optional): integer number of days to look back. Default `7`.

---

## Step 4 — Call the MCP tool

Pick the primary `entity_type` (first of the pipe-separated list).

**Empty entity_type handling:** If the profile's "Entity type(s)" value is empty, `(none)`, `(none configured)`, or `[PLACEHOLDER]`:
- OMIT the `entity_type` param from the MCP call entirely (do not pass an empty string — that's a different filter behavior server-side).
- Continue with other filters (regulation, days, urgency_max, etc.).
- Add this line to the output FOOTER (before the disclaimer): `Note: results are unscoped to entity type (your workspace has no entity type configured). For sharper results, set an entity type at https://app.velvoite.eu/account.`

Optionally pick a primary regulation to scope by — if the user has only one regulation in `actor_roles_by_reg`, use it; otherwise omit `regulation` and let the call return changes across the full corpus filtered only by entity type.

Call:

```
get_recent_changes(
  days=<days or 7>,
  entity_type=<primary entity type from profile — OMIT if empty/none/placeholder>,
  regulation=<optional — primary regulation if profile has only one, else omit>,
  urgency_max=<optional — pass 3 for high-signal only if the user wants a tighter view>
)
```

**Do NOT pass `actor_role` or `jurisdiction` — the server does not accept them on `get_recent_changes`.** (Confirmed by reading `velvoite-mcp/server.py` lines 500-525.)

---

## Step 5 — Render

Group the response by regulation. For each regulation, emit:

```
## <Regulation name> (<n> new)

- <YYYY-MM-DD>: <doc title> — <doc_type> — [<source name>](<url>)
- ...
```

- Regulations should appear in descending order of `n` (most active first).
- Within each regulation, list newest first.
- `doc_type` is the document type from the corpus (e.g. `guidelines`, `qa`, `rts`, `supervisory_release`, `consultation`). Render lowercase.
- If a document has no URL, render the source name as plain text.

If the response is empty:

> No new documents matching your profile in the last `<days>` days.

---

## Step 6 — Footer

After the grouped sections, on its own line:

> Scoped to: `<entity_types>` / `<jurisdictions>` / actor roles: `<reg1>:<role1>, <reg2>:<role2>, …`

Then a blank line, then the disclaimer:

> Drafts for compliance / legal review — not legal advice.

---

## Hard rules

- Never call MCP tools before the practice profile is loaded and validated.
- Group by regulation. Do not return a flat chronological dump — readability matters when there are 30+ docs.
- The disclaimer line is mandatory on every output.
