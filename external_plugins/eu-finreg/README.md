# eu-finreg — EU financial regulation specialist plugin

The EU financial regulation specialist plugin in Anthropic's
[claude-for-legal](https://github.com/anthropics/claude-for-legal) ecosystem.
Companion to `regulatory-legal` — when your legal or compliance team needs
EU finreg specifics (DORA actor roles, MiCA CASP taxonomy, FIN-FSA / BaFin /
EBA / ESMA / EIOPA jurisdictions, enforcement intelligence), install both.

`regulatory-legal` gives you generic regulatory workflows. `eu-finreg` gives you
the structured EU financial regulation corpus underneath, with scoping by your
entity type and actor roles per regulation.

Designed for compliance analysts, in-house counsel, and AI/automation leads at
EU-regulated financial institutions: payment institutions, CASPs, investment
firms, AIFMs, e-money institutions, insurers, credit institutions.

**Powered by [Velvoite](https://velvoite.eu)** — the EU financial regulation corpus
covering EUR-Lex, EBA, ESMA, EIOPA, FIN-FSA, BaFin (and growing).

## What it does

- `/eu-finreg:setup` — syncs your practice profile from your Velvoite workspace
- `/eu-finreg:obligations` — applicable obligations for your entity & roles
- `/eu-finreg:deadlines` — upcoming compliance deadlines
- `/eu-finreg:reg-watch` — what changed since you last checked
- `/eu-finreg:enforcement` — recent enforcement decisions in your scope
- `/eu-finreg:search` — free-text search across the corpus
- Scheduled `eu-finreg:reg-feed-watcher` — Monday-morning digest

## Setup

1. Sign up at https://app.velvoite.eu/register?source=plugin (free 30-day Premium trial — no card)
2. Configure your workspace: entity types, jurisdictions, applicable regulations, actor roles per regulation. This is your **regulatory posture** — the plugin uses it to scope every query.
3. Create an API key at https://app.velvoite.eu/account?source=plugin
4. `export VELVOITE_API_KEY=vv_...` in your shell (or Cowork secret), then run `/eu-finreg:setup` in Claude. It mirrors your workspace profile into `~/.claude/plugins/config/eu-finreg/CLAUDE.md`. Every other command reads from there.

## Why it requires an account

The plugin scopes every query (obligations, deadlines, enforcement, recent
changes, search) to your specific regulatory posture. Building that posture
properly — entity types, actor roles per regulation, conditions, license-level
details — isn't well-suited to a CLI interview; it lives in the workspace UI at
app.velvoite.eu. The plugin syncs **from** that workspace and provides the
inline slash-command interface. The workspace is where the real setup lives.

If you only want to poke around the corpus without configuring anything, a free
30-day Premium trial gives you full access — sign up, click through entity types
and regulations once, then `/eu-finreg:setup` and you're running.

## How eu-finreg fits in claude-for-legal

`claude-for-legal` ships 10+ practice-area plugins from Anthropic (`regulatory-legal`,
`privacy-legal`, `commercial-legal`, `corporate-legal`, `litigation-legal`,
`ip-legal`, `employment-legal`, `ai-governance-legal`, etc.). `eu-finreg` is the
EU financial regulation specialist that slots in alongside them.

- `regulatory-legal` = generic across all regimes (US, EU, UK, sectoral)
- `eu-finreg` = deep on EU financial regulation specifically — uses our corpus,
  our actor-role taxonomy, our jurisdiction model, our enforcement intelligence
- Install both: regulatory-legal for the workflows, eu-finreg for the data
  underneath when EU finreg is involved

When a query is "what's the regulatory pattern around AI deployment?" → `regulatory-legal`.
When the query is "what does DORA Art 28(3) require for our payment institution's
ICT third-party register?" → `eu-finreg`.

## License & disclaimers

All outputs are drafts for compliance / legal review — not legal advice. See
https://velvoite.eu/legal for terms.
