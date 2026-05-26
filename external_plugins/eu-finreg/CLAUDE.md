<!--
CONFIGURATION LOCATION

User-specific configuration for this plugin lives at a version-independent path that survives plugin updates:

  ~/.claude/plugins/config/eu-finreg/CLAUDE.md

Rules for every skill, command, and agent in this plugin:
1. READ configuration from that path. Not from this file.
2. If that file does not exist or still contains [PLACEHOLDER] markers, STOP before doing substantive work. Say: "Your eu-finreg practice profile is missing or unconfigured. Run /eu-finreg:setup to sync it from your Velvoite workspace. If you don't have a workspace yet, sign up at https://app.velvoite.eu/register?source=plugin (free 30-day Premium trial)." Do NOT proceed with placeholder or default configuration. The only skill that runs without setup is /eu-finreg:setup itself.
3. Setup WRITES to that path, creating parent directories as needed. It fetches the user's regulatory posture (entity types, jurisdictions, actor roles per regulation, active conditions) from the Velvoite workspace via the `get_company_profile()` MCP tool. The values map 1:1 to the `companies.regulatory_posture` schema in the Velvoite app.
4. On first run after a plugin update, if a populated CLAUDE.md exists at an old cache path
   (~/.claude/plugins/cache/eu-finreg/<version>/CLAUDE.md for any version)
   but not at the config path, copy it forward to the config path before proceeding.
5. This file (the one you are reading) is the TEMPLATE. It ships with the plugin and shows the
   structure the config should have. It is replaced on every plugin update. Never write user data here.
-->

# eu-finreg Practice Profile
*Written by `/eu-finreg:setup` on [DATE]. If you see `[PLACEHOLDER]` below, run `/eu-finreg:setup` to sync from your Velvoite workspace.*

---

## Company

| Field | Value |
|---|---|
| Name | [PLACEHOLDER] |
| Entity type(s) | [PLACEHOLDER — credit_institution \| payment_institution \| e_money_institution \| casp \| investment_firm \| aifm \| ucits \| insurance \| reinsurance] |
| Jurisdiction(s) | [PLACEHOLDER — FI \| DE \| EU-wide \| ...] |
| Regulatory authority | [PLACEHOLDER — FIN-FSA \| BaFin \| ECB SSM \| ...] |

*Entity type and jurisdiction together determine which scrapers' output is relevant (e.g. a Finnish credit institution sees EU-wide + FIN-FSA; a German CASP sees EU-wide + BaFin).*

---

## Actor roles per regulation

The role determines which obligations apply. A "controller" under GDPR has different duties than a "processor"; a "deployer" under the AI Act has different duties than a "provider".

| Regulation | Role(s) |
|---|---|
| GDPR | [PLACEHOLDER — controller \| processor \| joint_controller] |
| DORA | [PLACEHOLDER — financial_entity \| ict_third_party \| critical_ict] |
| AI Act | [PLACEHOLDER — provider \| deployer \| distributor \| importer] |
| MiCA | [PLACEHOLDER — casp \| issuer \| offeror] |
| MiFID II | [PLACEHOLDER — investment_firm \| trading_venue \| data_reporting_service_provider] |
| AML/CFT | [PLACEHOLDER — obliged_entity \| fiu_reporting_party] |

*The actual rows here come from your Velvoite workspace — one row per regulation you've configured. Add or remove regulations in the workspace UI, then re-run `/eu-finreg:setup`.*

---

## Active conditions

Conditions that toggle specific obligations on (e.g. employee headcount thresholds, transaction volumes, criticality designations).

- [PLACEHOLDER — e.g., "more than 250 employees"]
- [PLACEHOLDER — e.g., "annual transaction volume > €X"]
- [PLACEHOLDER — e.g., "uses third-party ICT services classified as critical"]

---

## Velvoite workspace

The plugin is a thin client over your Velvoite workspace. The sync writes this profile from the workspace; the workspace at app.velvoite.eu is where the real setup lives.

| Field | Value |
|---|---|
| API key env var | `VELVOITE_API_KEY` |
| Workspace ID | [PLACEHOLDER — UUID from get_company_profile()] |

*Re-run `/eu-finreg:setup` any time to re-sync after changing your workspace posture.*

---

## Last updated

- [PLACEHOLDER — YYYY-MM-DD by /eu-finreg:setup]
