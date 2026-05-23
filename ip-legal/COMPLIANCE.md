# ip-legal Compliance Baseline

> This file establishes the global confidentiality, data-handling, and output-management guardrails for the `ip-legal` plugin. Every skill and agent must read this file before execution.

---

## 1. Deployment Environment Classification

| Tier | Definition | Plugin Suitability |
|:---|:---|:---|
| **Public Cloud Model** | Third-party API (Claude API, ChatGPT, etc.) — data uploaded to service provider servers | ⚠️ Public-tier information only; no Internal/Confidential/Restricted data |
| **Private Deployment Model** | Self-hosted or private cloud (local LLM, VPC-hosted model) — data does not leave organizational control | ✅ Suitable for Public, Internal, and Confidential information |
| **Air-Gapped / Classified Network** | Physically isolated system for national-security or trade-secret information | ⚠️ Must be approved by security officer; Top Secret / classified info prohibited from any AI system |

---

## 2. Information Sensitivity Tiers

| Tier | Label | Examples | AI Processing Rule |
|:---|:---|:---|:---|
| **Public** | Public | Issued patents, published product materials, public court filings | May be submitted to any model |
| **Internal** | Internal | Internal workflows, non-critical training materials, org charts | May be submitted to public cloud (sanitization recommended) |
| **Confidential** | Confidential | Unpublished patent applications, invention disclosures, draft contracts, pre-litigation strategy | **Private deployment only** |
| **Restricted** | Restricted | Core algorithms, source code, trade secrets, active litigation strategy, M&A deal terms | **Private deployment + audit logging required** |
| **Prohibited** | Prohibited | Classified national security information, third-party information under strict NDA prohibiting AI disclosure | **Never submit to any AI system** |

---

## 3. Pre-Input Self-Assessment Checklist (Mandatory)

Before every skill invocation, the user must confirm:

- [ ] I have classified the information I am about to submit: □ Public  □ Internal  □ Confidential  □ Restricted  □ Prohibited
- [ ] The current AI deployment environment is authorized for this tier
- [ ] If submitting unpublished patent disclosures, core technical data, or trade secrets, I am operating in a private deployment environment
- [ ] The input does not contain classified national security information or third-party information explicitly barred from AI processing
- [ ] The input has been sanitized of unnecessary personal data (per applicable data protection laws)

**If any item cannot be confirmed, pause and escalate to the designated security or compliance officer before proceeding.**

---

## 4. Per-Skill Confidentiality Quick Reference

| Skill | Typical Input | Sensitivity Tier | Environment Requirement |
|:---|:---|:---|:---|
| `cold-start-interview` | Organizational policies, approval chains, external provider contacts | Internal / Confidential | Private deployment (recommended) |
| `invention-intake` | Invention disclosures, technical solutions | Confidential / Restricted | Private deployment |
| `fto-triage` | Product technical specifications, feature lists | Confidential / Restricted | Private deployment |
| `clearance` | Proposed marks, goods/services classifications | Internal / Confidential | Private deployment (recommended) |
| `infringement-triage` | Infringement evidence, trade secret descriptions, litigation strategy | Confidential / Restricted | Private deployment |
| `ip-clause-review` | Contract text, license terms | Confidential / Restricted | Private deployment |
| `oss-review` | SBOM, dependency manifests, source code snippets | Internal / Confidential | Private deployment (recommended) |
| `portfolio` | Portfolio database, maintenance fee records | Internal / Confidential | Private deployment (recommended) |
| `claim-chart-builder` | Patent text, litigation materials, infringement analysis | Confidential / Restricted | Private deployment |
| `cease-desist` | Infringement facts, enforcement strategy, settlement positions | Confidential / Restricted | Private deployment |
| `takedown` | Infringement URLs, platform account data, purchase records | Internal / Confidential | Private deployment (recommended) |
| `matter-workspace` | Case files, correspondence, billing records | Confidential / Restricted | Private deployment |
| `customize` | Configuration preferences, integration settings | Internal | Private deployment (recommended) |

---

## 5. Prohibited Inputs (Bright-Line Rules)

The following information **must not** be submitted to any AI system, regardless of deployment environment:

1. **Classified national security information**: Any material marked as classified, top secret, or equivalent under applicable law
2. **Third-party confidential information**: Information received from clients, partners, or counterparties under an NDA that explicitly prohibits AI processing — unless the disclosing party has given express written consent
3. **Core trade-secret source code**: Unpatented, unpublished core algorithm implementations whose disclosure would destroy trade-secret protection
4. **Unredacted personal data**: Government-issued identifiers, biometric data, health records, financial account numbers, or precise geolocation — unless redacted per applicable data protection law
5. **Undisclosed M&A / securities information**: Material non-public information that could violate insider-trading or market-abuse regulations
6. **Attorney work product subject to litigation hold**: Information whose submission to a third-party AI service could waive privilege or work-product protection — unless counsel has cleared the specific use

---

## 6. Output Management

1. **Mandatory disclaimer**: All outputs must carry the notice — *"This document is an AI-generated draft. It must be reviewed by a qualified legal professional before any reliance or filing."*
2. **Output tier inheritance**: The sensitivity tier of the output is the highest tier of any input used to generate it. If Confidential inputs were used, the output is Confidential.
3. **No direct official submission**: AI-generated application drafts, legal briefs, cease-and-desist letters, and platform complaints must not be filed with courts, patent/trademark offices, or administrative bodies without qualified human review and sign-off.
4. **Output storage**: Confidential and Restricted outputs must be stored on organizational internal networks or encrypted storage. Do not store on public cloud note-taking services, personal devices, or unencrypted external drives.

---

## 7. Audit & Logging

1. **Invocation logs**: Record skill name, timestamp, input summary (sanitized), output summary, and operating user for every invocation.
2. **Retention**: Log retention periods should match the recordkeeping requirements of the underlying legal matter (e.g., patent prosecution files are typically retained for the life of the patent plus a jurisdiction-specific post-expiration period).
3. **Access control**: Log access is limited to the security/compliance officer, the IP practice lead, and IT audit personnel.
4. **Incident reporting**: Any suspected exposure of Restricted-tier information to an unauthorized environment, data exfiltration, or credential leak must be reported to the security officer within 24 hours.

---

## 8. Privilege & Work-Product Considerations

1. **Attorney-client privilege**: Submitting privileged communications to an AI system may waive privilege in some jurisdictions. Confirm with supervising counsel whether the specific use is covered by the jurisdiction's privilege rules.
2. **Patent agent privilege**: In jurisdictions that recognize patent-agent privilege (e.g., U.S. under *In re Queen's University at Kingston*), confirm the scope is limited to USPTO practice. Non-patent matters submitted to an AI system through a patent-agent role may lack privilege protection.
3. **Work-product doctrine**: Documents prepared in anticipation of litigation retain work-product protection only if kept confidential. Assess whether AI processing in the chosen deployment environment maintains the required confidentiality.

---

## 9. Violation Consequences

Failure to adhere to this compliance baseline may result in:

- **Regulatory penalties** under applicable data protection, trade-secret, or confidentiality laws
- **Civil liability** for damages to the organization or third parties
- **Professional discipline** including bar or patent-office sanctions
- **Loss of privilege or trade-secret protection** for the affected information
- **Organizational disciplinary action** up to and including termination

---

*This compliance baseline is maintained by the plugin security owner. Version v1.0. Review at least annually and after any material change to the deployment environment or applicable regulatory framework.*
