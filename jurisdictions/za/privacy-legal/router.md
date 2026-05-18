# Skill Router — South African Privacy Law Overlay

When jurisdiction = ZA, skills load the topic overlays and statute files listed below.

Topic files resolve to: `jurisdictions/za/privacy-legal/topics/{name}.md`
Statute files resolve to: `jurisdictions/za/statutes/{name}.yaml`

```yaml
dpa-review:
  topics: [operator-agreements, cross-border-and-special-categories, lawful-processing]
  statutes: [popia, cybercrimes]

dsar-response:
  topics: [data-subject-rights, enforcement-and-compliance]
  statutes: [popia, paia]

pia-generation:
  topics: [impact-assessment, lawful-processing, cross-border-and-special-categories]
  statutes: [popia, cybercrimes]

use-case-triage:
  topics: [impact-assessment, lawful-processing, cross-border-and-special-categories]
  statutes: [popia]

policy-monitor:
  topics: [data-subject-rights, operator-agreements, lawful-processing, enforcement-and-compliance]
  statutes: [popia]

reg-gap-analysis:
  topics: [impact-assessment, lawful-processing, enforcement-and-compliance]
  statutes: [popia, cybercrimes, paia]

cold-start-interview:
  topics: []
  statutes: [popia, cybercrimes, paia]
```
