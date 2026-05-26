---
name: search
description: Free-text search across the Velvoite EU financial regulation corpus (EUR-Lex, EBA, ESMA, EIOPA, FIN-FSA, BaFin). Reads from ~/.claude/plugins/config/eu-finreg/CLAUDE.md. Use when the user has a specific phrase, article reference, or concept to look up that doesn't fit the structured obligations/deadlines/enforcement views. Note: the server's search tool does NOT filter by jurisdiction or entity type — results are corpus-wide.
argument-hint: "<query> [per_page]"
---

# /eu-finreg:search

Free-text keyword search across the Velvoite corpus (EUR-Lex, EBA, ESMA, EIOPA, FIN-FSA, BaFin). Use this when structured filters (regulation, role, entity type) aren't enough — e.g. when looking up a specific phrase, recital, or concept. Note: the underlying `search_regulations` MCP tool does NOT support jurisdiction or entity-type filters — results span the whole corpus regardless of profile.

---

## Step 1 — Load practice profile

1. Read `~/.claude/plugins/config/eu-finreg/CLAUDE.md`.
2. **If the file does not exist OR its contents still contain any `[PLACEHOLDER]` marker:** stop immediately and tell the user, verbatim:
   > Your eu-finreg practice profile is missing or unconfigured. Run `/eu-finreg:setup` to sync it from your Velvoite workspace. If you don't have a workspace yet, sign up at https://app.velvoite.eu/register?source=plugin (free 30-day Premium trial).
   Do not call any MCP tools. Do not fabricate scope. STOP.
3. From the profile, extract:
   - `entity_types` — from "Entity type(s)".
   - `jurisdictions` — pipe-separated list from "Jurisdiction(s)". Used only in the scoping footer (the server tool does NOT filter search results by jurisdiction).

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

- `$1` (required): the free-text query. May be multi-word — treat the whole remaining argument string as the query, except for the last token if it's a bare integer (treat that as the limit).
- `$2` (optional): integer `per_page` — number of results to return. Default `10`, max `100`.

If no query was supplied, print:

> Usage: `/eu-finreg:search <query> [limit]` — e.g. `/eu-finreg:search "operational resilience" 20`.

Then STOP.

---

## Step 4 — Call the MCP tool

Use the `velvoite` MCP server. Call:

```
search_regulations(
  query=<query>,
  per_page=<$2 or 10>
)
```

The server signature accepts ONLY `query` and `per_page` (verified against `velvoite-mcp/server.py`). Do NOT pass `jurisdiction`, `limit`, `entity_type`, or any other filter — they will be silently dropped by the MCP framework or rejected by the server.

If the call returns zero rows: print

> No matches for `<query>` in the corpus. Try a broader query, or different phrasing. (Note: search results are corpus-wide and not scoped to your jurisdictions / entity type — that scoping is only applied by the structured tools like `/eu-finreg:obligations` and `/eu-finreg:deadlines`.)

Then skip to Step 6 (footer).

---

## Step 5 — Render results

Numbered list, one block per result:

```
1. <title> — <regulation> Art. <article_ref> — <source>
     <snippet with query terms highlighted using **bold**>
     [Open] <url>
```

- `title` — document title, trimmed to ~100 chars.
- `regulation` — regulation code, uppercase (e.g. `DORA`). Blank if not classified.
- `Art. <article_ref>` — only include if an article reference is present.
- `source` — source name (e.g. `EUR-Lex`, `EBA`, `ESMA`, `BaFin`, `FIN-FSA`).
- `snippet` — short excerpt around the matched terms. Bold the query terms.
- `url` — the canonical source URL from the result.

After the list, print, on its own line:

> Run `/eu-finreg:obligations` or `/eu-finreg:deadlines` for structured views, or call `get_document(<id>)` via the velvoite MCP for full text.

---

## Step 6 — Footer

On its own line:

> Scoped to: `<entity_types>` / `<jurisdictions>`

Then a blank line, then the disclaimer:

> Drafts for compliance / legal review — not legal advice.

---

## Hard rules

- Never call MCP tools before the practice profile is loaded and validated.
- Never invent results, snippets, or URLs. If the MCP server returns nothing, say so.
- The disclaimer line is mandatory on every output.
