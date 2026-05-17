# SA Employment Law Overlay — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the additive South African jurisdiction overlay for the employment-legal plugin — statute data, topic overlays, skill router, ZA practice profile template, cold-start interview fork, and validation suite.

**Architecture:** All SA content lives in `jurisdictions/za/`. Skills route to overlays via a router file referenced from the ZA practice profile template. Only one upstream file is modified (`employment-legal/skills/cold-start-interview/SKILL.md`). Statute thresholds use YAML with temporal fields; procedural guidance uses shared markdown topic files.

**Tech Stack:** YAML (statute data, router, eval cases), Markdown (topic overlays, practice profile template), Python 3 (validation scripts), Bash (test runner)

---

## File Map

### New files to create

| File | Responsibility |
|---|---|
| `jurisdictions/za/statutes/bcea.yaml` | BCEA thresholds: earnings threshold, ordinary hours, overtime, leave entitlements, notice periods |
| `jurisdictions/za/statutes/lra.yaml` | LRA references: fair dismissal (s188), retrenchment (s189/s189A), auto-unfair (s187), CCMA timelines |
| `jurisdictions/za/statutes/eea.yaml` | EEA: designated employer thresholds, protected grounds, reporting cycles |
| `jurisdictions/za/statutes/sectoral-determinations.yaml` | Per-sector overrides: domestic, hospitality, farm, retail, forestry |
| `jurisdictions/za/employment-legal/router.md` | Maps 7 skills → topic files + statute files |
| `jurisdictions/za/employment-legal/practice-profile-template.md` | ZA variant of the employment-legal CLAUDE.md template |
| `jurisdictions/za/employment-legal/topics/dismissal.md` | LRA s188/s189, CCMA, Schedule 8, 11 high-risk flags |
| `jurisdictions/za/employment-legal/topics/hiring.md` | Restraint of trade, probation, EEA at hire |
| `jurisdictions/za/employment-legal/topics/classification.md` | BCEA s213, common law control test, deemed employees |
| `jurisdictions/za/employment-legal/topics/leave-and-conditions.md` | BCEA leave (s20-28), working time, above-minimum handling |
| `jurisdictions/za/employment-legal/topics/policy-and-handbook.md` | SA disciplinary codes, grievance procedures, SA policy conventions |
| `jurisdictions/za/employment-legal/topics/investigation-privilege.md` | SA privilege, Protected Disclosures Act, POPIA witness data |
| `scripts/validate-za-statutes.py` | Schema validation for statute YAML files |
| `scripts/validate-za-router.py` | Cross-reference validation for router → topics/statutes |
| `scripts/validate-za-templates.py` | Template completeness and US-concept checks |
| `scripts/test-za-overlays.sh` | Runner that calls all three validators |
| `jurisdictions/za/evals/employment-legal/termination-review/case-01-misconduct-no-hearing.yaml` | Eval: misconduct dismissal without hearing |
| `jurisdictions/za/evals/employment-legal/termination-review/case-02-retrenchment-large-scale.yaml` | Eval: s189A large-scale retrenchment |
| `jurisdictions/za/evals/employment-legal/termination-review/case-03-auto-unfair-pregnancy.yaml` | Eval: automatically unfair — pregnancy |
| `jurisdictions/za/evals/employment-legal/termination-review/case-04-fixed-term-expectation.yaml` | Eval: fixed-term non-renewal |
| `jurisdictions/za/evals/employment-legal/termination-review/case-05-below-threshold-misconduct.yaml` | Eval: below-threshold employee misconduct |
| `jurisdictions/za/evals/employment-legal/hiring-review/case-01-restraint-of-trade.yaml` | Eval: restraint of trade clause review |
| `jurisdictions/za/evals/employment-legal/hiring-review/case-02-probation-clause.yaml` | Eval: probation clause review |
| `jurisdictions/za/evals/employment-legal/hiring-review/case-03-ee-obligations.yaml` | Eval: EEA obligations at hire |
| `jurisdictions/za/evals/employment-legal/worker-classification/case-01-contractor-control.yaml` | Eval: contractor vs employee control test |
| `jurisdictions/za/evals/employment-legal/worker-classification/case-02-deemed-employee.yaml` | Eval: deemed employee under s200A |
| `jurisdictions/za/evals/employment-legal/worker-classification/case-03-labour-broker.yaml` | Eval: labour broker / TES arrangement |
| `jurisdictions/za/evals/employment-legal/wage-hour-qa/case-01-overtime-below-threshold.yaml` | Eval: overtime for below-threshold employee |
| `jurisdictions/za/evals/employment-legal/wage-hour-qa/case-02-sunday-work.yaml` | Eval: Sunday/public holiday pay |
| `jurisdictions/za/evals/employment-legal/wage-hour-qa/case-03-night-work.yaml` | Eval: night work provisions |
| `jurisdictions/za/evals/employment-legal/leave-tracker/case-01-annual-leave.yaml` | Eval: BCEA annual leave entitlement |
| `jurisdictions/za/evals/employment-legal/leave-tracker/case-02-sick-leave-cycle.yaml` | Eval: sick leave 3-year cycle |
| `jurisdictions/za/evals/employment-legal/leave-tracker/case-03-maternity-leave.yaml` | Eval: maternity leave and UIF |
| `jurisdictions/za/evals/employment-legal/policy-drafting/case-01-disciplinary-code.yaml` | Eval: draft disciplinary code aligned to Schedule 8 |
| `jurisdictions/za/evals/employment-legal/policy-drafting/case-02-grievance-procedure.yaml` | Eval: draft grievance procedure |
| `jurisdictions/za/evals/employment-legal/policy-drafting/case-03-harassment-policy.yaml` | Eval: harassment policy per Code of Good Practice |
| `jurisdictions/za/evals/employment-legal/cold-start-interview/case-01-za-designated-employer.yaml` | Eval: cold-start for ZA designated employer |
| `jurisdictions/za/evals/employment-legal/cold-start-interview/case-02-za-small-employer.yaml` | Eval: cold-start for small non-designated employer |
| `jurisdictions/za/evals/employment-legal/cold-start-interview/case-03-za-sectoral.yaml` | Eval: cold-start for employer with sectoral determination |
| `scripts/za-statute-schema.yaml` | JSON Schema for statute YAML validation |

### Files to modify

| File | Change |
|---|---|
| `employment-legal/skills/cold-start-interview/SKILL.md` | Add ZA jurisdiction fork after Part 0 |

---

## Task 1: Statute Data Layer — BCEA

**Files:**
- Create: `jurisdictions/za/statutes/bcea.yaml`
- Create: `scripts/za-statute-schema.yaml`
- Create: `scripts/validate-za-statutes.py`

- [ ] **Step 1: Write the statute schema definition**

```yaml
# scripts/za-statute-schema.yaml
type: object
required: [statute, authority, last_confirmed, source_url, sections]
properties:
  statute:
    type: string
    minLength: 5
  authority:
    type: string
    minLength: 3
  last_confirmed:
    type: string
    pattern: "^\\d{4}-\\d{2}-\\d{2}$"
  source_url:
    type: string
    pattern: "^https?://"
  sections:
    type: object
    minProperties: 1
    additionalProperties:
      type: object
      required: [ref, value, effective_from, effective_until, effect]
      properties:
        ref:
          type: string
        value:
          oneOf:
            - type: number
            - type: string
        currency:
          type: string
          enum: [ZAR]
        unit:
          type: string
        effective_from:
          oneOf:
            - type: string
              pattern: "^\\d{4}-\\d{2}-\\d{2}$"
            - type: "null"
        effective_until:
          oneOf:
            - type: string
              pattern: "^\\d{4}-\\d{2}-\\d{2}$"
            - type: "null"
        effect:
          type: string
          minLength: 5
        gazette_date:
          oneOf:
            - type: string
              pattern: "^\\d{4}-\\d{2}-\\d{2}$"
            - type: "null"
        note:
          type: string
```

- [ ] **Step 2: Write the BCEA statute file**

```yaml
# jurisdictions/za/statutes/bcea.yaml
statute: "Basic Conditions of Employment Act 75 of 1997"
authority: "Department of Employment and Labour"
last_confirmed: "2025-03-01"
source_url: "https://www.labour.gov.za/DocumentCenter/Pages/Acts.aspx"

sections:
  earnings_threshold:
    ref: "BCEA s6(3), GN R2316 GG 48928"
    value: 254371.67
    currency: ZAR
    unit: per_annum
    effective_from: "2024-03-01"
    effective_until: null
    effect: "Employees earning above this threshold are excluded from ss9-16 (working time), s17(2) (overtime agreement), and s18(3) (compressed working week). Full BCEA protections apply to those earning below."
    gazette_date: "2024-03-01"
    note: "Updated annually via Government Gazette. Below-threshold employees enjoy full working-time and overtime protections; adverse changes to their conditions face higher scrutiny."

  ordinary_hours:
    ref: "BCEA s9(1)"
    value: 45
    unit: hours_per_week
    effective_from: null
    effective_until: null
    effect: "Maximum ordinary working hours per week. May not exceed 45. Reducible by collective agreement."

  daily_hours_5_day:
    ref: "BCEA s9(1)(a)"
    value: 9
    unit: hours_per_day
    effective_from: null
    effective_until: null
    effect: "Maximum ordinary hours per day for employees working 5 or fewer days per week."

  daily_hours_6_day:
    ref: "BCEA s9(1)(b)"
    value: 8
    unit: hours_per_day
    effective_from: null
    effective_until: null
    effect: "Maximum ordinary hours per day for employees working more than 5 days per week."

  overtime_max:
    ref: "BCEA s10(1)"
    value: 10
    unit: hours_per_week
    effective_from: null
    effective_until: null
    effect: "Maximum overtime hours per week. Overtime requires agreement. May not work more than 12 hours on any day."

  overtime_rate:
    ref: "BCEA s10(2)"
    value: 1.5
    unit: multiplier_of_ordinary_rate
    effective_from: null
    effective_until: null
    effect: "Overtime rate is 1.5x the employee's normal wage, or by agreement the employee may be granted paid time off equivalent to the overtime worked."

  sunday_rate:
    ref: "BCEA s16(1)"
    value: 2.0
    unit: multiplier_of_ordinary_rate
    effective_from: null
    effective_until: null
    effect: "Employees who do not ordinarily work on Sundays must be paid at double their normal wage rate. Employees who ordinarily work Sundays are paid at 1.5x."

  annual_leave:
    ref: "BCEA s20(2)"
    value: 21
    unit: consecutive_days_per_cycle
    effective_from: null
    effective_until: null
    effect: "Minimum annual leave entitlement: 21 consecutive days per annual leave cycle, or by agreement 1 day for every 17 days worked, or 1 hour for every 17 hours worked."

  sick_leave:
    ref: "BCEA s22(2)"
    value: 30
    unit: days_per_36_month_cycle
    effective_from: null
    effective_until: null
    effect: "Paid sick leave: 30 days over a 36-month cycle (equivalent to the number of days the employee would normally work during a period of 6 weeks). During the first 6 months, entitled to 1 day for every 26 days worked."

  family_responsibility_leave:
    ref: "BCEA s27(2)"
    value: 3
    unit: days_per_annual_cycle
    effective_from: null
    effective_until: null
    effect: "3 days paid family responsibility leave per annual leave cycle (birth of child, illness of child, death of specified family member). Only applies to employees who have worked for employer for longer than 4 months and who work at least 4 days per week."

  maternity_leave:
    ref: "BCEA s25(1)"
    value: 4
    unit: months
    effective_from: null
    effective_until: null
    effect: "Entitled to at least 4 consecutive months of maternity leave. Unpaid under BCEA; UIF provides partial income replacement. May commence 4 weeks before expected date of confinement or earlier if a medical practitioner certifies it is necessary."

  notice_period_less_than_6_months:
    ref: "BCEA s37(1)(a)"
    value: 1
    unit: weeks
    effective_from: null
    effective_until: null
    effect: "Minimum notice period for employees employed for 6 months or less."

  notice_period_6_to_12_months:
    ref: "BCEA s37(1)(b)"
    value: 2
    unit: weeks
    effective_from: null
    effective_until: null
    effect: "Minimum notice period for employees employed for more than 6 months but not more than 1 year."

  notice_period_over_12_months:
    ref: "BCEA s37(1)(c)"
    value: 4
    unit: weeks
    effective_from: null
    effective_until: null
    effect: "Minimum notice period for employees employed for 1 year or more."

  meal_interval:
    ref: "BCEA s14(1)"
    value: 60
    unit: minutes_after_5_hours
    effective_from: null
    effective_until: null
    effect: "Employer must give employee a meal interval of at least 1 continuous hour after 5 hours of work. May be reduced to 30 minutes by agreement. May be dispensed with for employees who work fewer than 6 hours per day."
```

- [ ] **Step 3: Write the validation script**

```python
#!/usr/bin/env python3
"""Validate statute YAML files in jurisdictions/za/statutes/ against the schema.

Usage: python3 scripts/validate-za-statutes.py
Exits 0 if all files valid, 1 if any invalid.
"""
import sys
from pathlib import Path

import yaml
import jsonschema

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "scripts" / "za-statute-schema.yaml"
STATUTES_DIR = ROOT / "jurisdictions" / "za" / "statutes"


def main() -> int:
    schema = yaml.safe_load(SCHEMA_PATH.read_text())
    errors = 0
    files_checked = 0

    if not STATUTES_DIR.exists():
        print(f"FAIL: {STATUTES_DIR} does not exist", file=sys.stderr)
        return 1

    for path in sorted(STATUTES_DIR.glob("*.yaml")):
        files_checked += 1
        try:
            data = yaml.safe_load(path.read_text())
        except yaml.YAMLError as e:
            print(f"FAIL: {path.name}: YAML parse error: {e}", file=sys.stderr)
            errors += 1
            continue

        try:
            jsonschema.validate(instance=data, schema=schema)
        except jsonschema.ValidationError as e:
            loc = "/".join(str(p) for p in e.absolute_path)
            print(f"FAIL: {path.name}: {e.message} at /{loc}", file=sys.stderr)
            errors += 1
            continue

        for key, section in data.get("sections", {}).items():
            eff_from = section.get("effective_from")
            eff_until = section.get("effective_until")
            if eff_from and eff_until and eff_until < eff_from:
                print(
                    f"FAIL: {path.name}: sections/{key}: "
                    f"effective_until ({eff_until}) is before effective_from ({eff_from})",
                    file=sys.stderr,
                )
                errors += 1

        if errors == 0:
            print(f"  OK: {path.name} ({len(data.get('sections', {}))} sections)")

    if files_checked == 0:
        print(f"FAIL: no .yaml files found in {STATUTES_DIR}", file=sys.stderr)
        return 1

    print(f"\n{files_checked} files checked, {errors} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run validation to verify BCEA passes**

Run: `python3 scripts/validate-za-statutes.py`
Expected: `OK: bcea.yaml (16 sections)` and exit 0

- [ ] **Step 5: Commit**

```bash
git add jurisdictions/za/statutes/bcea.yaml scripts/za-statute-schema.yaml scripts/validate-za-statutes.py
git commit -m "feat(za): add BCEA statute data and schema validator"
```

---

## Task 2: Statute Data Layer — LRA, EEA, Sectoral Determinations

**Files:**
- Create: `jurisdictions/za/statutes/lra.yaml`
- Create: `jurisdictions/za/statutes/eea.yaml`
- Create: `jurisdictions/za/statutes/sectoral-determinations.yaml`

- [ ] **Step 1: Write LRA statute file**

```yaml
# jurisdictions/za/statutes/lra.yaml
statute: "Labour Relations Act 66 of 1995"
authority: "Department of Employment and Labour"
last_confirmed: "2025-03-01"
source_url: "https://www.labour.gov.za/DocumentCenter/Pages/Acts.aspx"

sections:
  fair_dismissal:
    ref: "LRA s188(1)"
    value: "substantive and procedural fairness required"
    effective_from: null
    effective_until: null
    effect: "A dismissal is unfair if the employer fails to prove (a) a fair reason related to conduct, capacity, or operational requirements, and (b) a fair procedure. No at-will employment concept exists."

  automatically_unfair_dismissal:
    ref: "LRA s187(1)"
    value: "listed grounds"
    effective_from: null
    effective_until: null
    effect: "Dismissal is automatically unfair if the reason is: pregnancy, union membership/activity, exercise of rights under labour legislation, refusal to do work of a striker, protected disclosure, participation in lawful strike, arbitrary discrimination on listed grounds. Remedy: reinstatement and up to 24 months compensation."

  auto_unfair_discrimination:
    ref: "LRA s187(1)(f)"
    value: "direct or indirect unfair discrimination on arbitrary grounds"
    effective_from: null
    effective_until: null
    effect: "Dismissal is automatically unfair if it constitutes unfair discrimination on grounds including race, gender, sex, ethnic or social origin, colour, sexual orientation, age, disability, religion, conscience, belief, political opinion, culture, language, marital status, family responsibility, pregnancy, HIV status."

  protected_disclosure:
    ref: "LRA s187(1)(h), Protected Disclosures Act 26 of 2000"
    value: "protected disclosure"
    effective_from: null
    effective_until: null
    effect: "Dismissal is automatically unfair if the reason is that the employee made a protected disclosure as defined in the Protected Disclosures Act."

  ccma_referral_unfair_dismissal:
    ref: "LRA s191(1)"
    value: 30
    unit: days
    effective_from: null
    effective_until: null
    effect: "An employee who alleges unfair dismissal must refer the dispute to a bargaining council (if one has jurisdiction) or the CCMA within 30 days of the date of dismissal."

  ccma_conciliation_period:
    ref: "LRA s191(5)"
    value: 30
    unit: days
    effective_from: null
    effective_until: null
    effect: "The commissioner must attempt to resolve the dispute through conciliation within 30 days of the date the council or CCMA received the referral."

  ccma_arbitration_after_conciliation:
    ref: "LRA s191(5)(a)"
    value: 90
    unit: days
    effective_from: null
    effective_until: null
    effect: "If conciliation fails, the employee may refer the dispute to arbitration within 90 days of the certificate of non-resolution."

  compensation_cap_unfair_dismissal:
    ref: "LRA s194(1)"
    value: 12
    unit: months_remuneration
    effective_from: null
    effective_until: null
    effect: "Maximum compensation for ordinary unfair dismissal: 12 months' remuneration."

  compensation_cap_auto_unfair:
    ref: "LRA s194(3)"
    value: 24
    unit: months_remuneration
    effective_from: null
    effective_until: null
    effect: "Maximum compensation for automatically unfair dismissal: 24 months' remuneration."

  retrenchment_consultation:
    ref: "LRA s189(1)"
    value: "consultation required"
    effective_from: null
    effective_until: null
    effect: "Employer contemplating dismissal for operational requirements must consult the affected employees or their representatives. Must disclose reasons, alternatives considered, number of employees affected, selection criteria, timing, severance pay, possibility of re-employment, and any other relevant matters."

  large_scale_retrenchment_threshold:
    ref: "LRA s189A(1)"
    value: 50
    unit: employees_threshold
    effective_from: null
    effective_until: null
    effect: "s189A applies when employer employs more than 50 employees AND contemplates dismissing at least the number of employees set out in the schedule (10 for 50-200 employees, 20 for 200-300, 30 for 300-400, 40 for 400-500, 50 for 500+). Triggers facilitation, extended consultation (60 days minimum), and strike/lock-out rights."

  large_scale_retrenchment_facilitation:
    ref: "LRA s189A(3)"
    value: 60
    unit: days_minimum_consultation
    effective_from: null
    effective_until: null
    effect: "In large-scale retrenchments, consultation must run for at least 60 days. Either party may request the CCMA to appoint a facilitator."

  probation:
    ref: "LRA Schedule 8 Item 8"
    value: "fair procedure required during probation"
    effective_from: null
    effective_until: null
    effect: "An employer may not dismiss an employee on probation without following a fair procedure. The employer must provide the employee with evaluation, instruction, training, guidance, or counselling, and a reasonable opportunity to improve. A reasonable extension of the probation period should be considered before dismissal."

  fixed_term_reasonable_expectation:
    ref: "LRA s186(1)(b)"
    value: "non-renewal can be a dismissal"
    effective_from: null
    effective_until: null
    effect: "An employee employed under a fixed-term contract who reasonably expected the employer to renew the contract on the same or similar terms, and the employer did not renew it, is deemed to have been dismissed."

  unfair_labour_practice:
    ref: "LRA s186(2)"
    value: "listed acts or omissions"
    effective_from: null
    effective_until: null
    effect: "Unfair labour practice includes: unfair conduct relating to promotion, demotion, probation, training, provision of benefits, suspension, or failure to reinstate/re-employ a former employee."

  severance_pay:
    ref: "LRA s41(2)"
    value: 1
    unit: weeks_remuneration_per_completed_year
    effective_from: null
    effective_until: null
    effect: "Minimum severance pay for dismissal based on operational requirements: 1 week's remuneration for each completed year of continuous service."
```

- [ ] **Step 2: Write EEA statute file**

```yaml
# jurisdictions/za/statutes/eea.yaml
statute: "Employment Equity Act 55 of 1998"
authority: "Department of Employment and Labour"
last_confirmed: "2025-03-01"
source_url: "https://www.labour.gov.za/DocumentCenter/Pages/Acts.aspx"

sections:
  designated_employer_headcount:
    ref: "EEA s1 definition of designated employer"
    value: 50
    unit: employees
    effective_from: null
    effective_until: null
    effect: "An employer with 50 or more employees is a designated employer and must comply with Chapter III (affirmative action). Turnover thresholds are being phased out."
    note: "The Employment Equity Amendment Act 4 of 2022 removed the turnover threshold, making employee count the sole criterion."

  protected_grounds:
    ref: "EEA s6(1)"
    value: "race, gender, sex, pregnancy, marital status, family responsibility, ethnic or social origin, colour, sexual orientation, age, disability, religion, HIV status, conscience, belief, political opinion, culture, language, birth"
    effective_from: null
    effective_until: null
    effect: "No person may unfairly discriminate, directly or indirectly, against an employee in any employment policy or practice on any of the listed grounds."

  ee_plan_requirement:
    ref: "EEA s20(1)"
    value: "designated employers must prepare and implement an employment equity plan"
    effective_from: null
    effective_until: null
    effect: "Designated employers must prepare and implement an employment equity plan that will achieve reasonable progress towards employment equity. The plan must state the objectives, affirmative action measures, numerical goals, timetable, duration (not exceeding 5 years), internal monitoring and evaluation procedures, and the person(s) responsible."

  ee_reporting:
    ref: "EEA s21(1)"
    value: "annual report"
    effective_from: null
    effective_until: null
    effect: "Designated employers must submit a report to the Director-General on progress in implementing the employment equity plan. Reports are due annually (by 15 January for electronic submission, by 1 October for manual)."

  income_differentials:
    ref: "EEA s27(1)"
    value: "equal pay for work of equal value"
    effective_from: null
    effective_until: null
    effect: "Designated employers must take measures to progressively reduce disproportionate income differentials. Differences in terms and conditions of employment for work of equal value that are based on any of the listed grounds constitute unfair discrimination."

  sector_codes:
    ref: "B-BBEE Act s9(1), sector-specific codes"
    value: "sector-specific B-BBEE codes"
    effective_from: null
    effective_until: null
    effect: "Various industries have sector-specific BEE codes (ICT, financial services, mining, construction, etc.) that set specific targets for management control, skills development, enterprise and supplier development, and ownership. These override the generic B-BBEE codes where they apply."
    note: "BEE codes are governed by the Broad-Based Black Economic Empowerment Act 53 of 2003, not the EEA directly, but are closely interlinked in practice."
```

- [ ] **Step 3: Write sectoral determinations file**

```yaml
# jurisdictions/za/statutes/sectoral-determinations.yaml
statute: "Sectoral Determinations under BCEA s55"
authority: "Department of Employment and Labour"
last_confirmed: "2025-03-01"
source_url: "https://www.labour.gov.za/DocumentCenter/Pages/Legislation/Sectoral-Determinations.aspx"

sections:
  domestic_workers_minimum_wage:
    ref: "SD 7, National Minimum Wage Act 9 of 2018"
    value: 27.58
    currency: ZAR
    unit: per_hour
    effective_from: "2024-03-01"
    effective_until: null
    effect: "National minimum wage applies to domestic workers. Previously had a separate (lower) sectoral minimum; now aligned with the national minimum wage."
    gazette_date: "2024-03-01"
    note: "Domestic workers are also covered by SD 7 for conditions of employment (leave, hours, notice) that supplement or vary the BCEA."

  farm_workers_minimum_wage:
    ref: "SD 13, National Minimum Wage Act 9 of 2018"
    value: 27.58
    currency: ZAR
    unit: per_hour
    effective_from: "2024-03-01"
    effective_until: null
    effect: "National minimum wage applies to farm workers. SD 13 sets additional conditions for housing, deductions, and termination specific to the agricultural sector."
    gazette_date: "2024-03-01"

  hospitality_sector:
    ref: "SD 14"
    value: 27.58
    currency: ZAR
    unit: per_hour
    effective_from: "2024-03-01"
    effective_until: null
    effect: "Hospitality sector minimum wage aligned with national minimum. SD 14 sets specific rules for tips, meal deductions, and working hours in the hospitality industry."
    gazette_date: "2024-03-01"

  national_minimum_wage:
    ref: "National Minimum Wage Act 9 of 2018, GN R4279 GG 49975"
    value: 27.58
    currency: ZAR
    unit: per_hour
    effective_from: "2024-03-01"
    effective_until: null
    effect: "National minimum wage applicable to all workers (with limited exceptions for EPWP and learnership programmes). Adjusted annually."
    gazette_date: "2024-03-01"
    note: "EPWP workers: R13.97/hr. Learnership allowances have separate schedules."

  expanded_public_works_programme:
    ref: "National Minimum Wage Act s6(6)"
    value: 13.97
    currency: ZAR
    unit: per_hour
    effective_from: "2024-03-01"
    effective_until: null
    effect: "Reduced minimum wage for workers employed in the Expanded Public Works Programme (EPWP)."
    gazette_date: "2024-03-01"
```

- [ ] **Step 4: Run validation on all four statute files**

Run: `python3 scripts/validate-za-statutes.py`
Expected: All four files pass (bcea.yaml, lra.yaml, eea.yaml, sectoral-determinations.yaml), exit 0

- [ ] **Step 5: Commit**

```bash
git add jurisdictions/za/statutes/lra.yaml jurisdictions/za/statutes/eea.yaml jurisdictions/za/statutes/sectoral-determinations.yaml
git commit -m "feat(za): add LRA, EEA, and sectoral determination statute data"
```

---

## Task 3: Topic Overlay — Dismissal

**Files:**
- Create: `jurisdictions/za/employment-legal/topics/dismissal.md`

- [ ] **Step 1: Write the dismissal topic overlay**

This is the highest-priority overlay — used by `termination-review`, `policy-drafting`, and `handbook-updates`. It contains the full SA dismissal framework and the 11 high-risk flags.

```markdown
# Dismissal — South African Overlay

## Statutory framework

South African dismissal law is governed by the **Labour Relations Act 66 of 1995** (LRA) and the **Code of Good Practice: Dismissal** (Schedule 8 to the LRA). There is no at-will employment concept in SA — every dismissal must satisfy two requirements:

1. **Substantive fairness** (LRA s188(1)(a)) — the employer must prove a fair reason: misconduct, incapacity (poor performance or ill health/injury), or operational requirements (retrenchment).
2. **Procedural fairness** (LRA s188(1)(b)) — the employer must follow a fair procedure before dismissing.

Failure on either ground renders the dismissal unfair. An unfair dismissal may result in reinstatement or compensation of up to 12 months' remuneration (LRA s194(1)), or up to 24 months for automatically unfair dismissals (LRA s194(3)).

## Types of dismissal

### Misconduct (Schedule 8 Items 3-4)

**Substantive fairness:**
- The employee contravened a workplace rule or standard
- The rule was valid and reasonable
- The employee was aware of the rule (or should have been)
- The rule was consistently applied
- Dismissal is an appropriate sanction given: the gravity of the misconduct, the employee's circumstances (length of service, disciplinary record, personal circumstances), and the nature of the job

**Procedural fairness (Schedule 8 Item 4):**
1. Notify the employee of the allegations with sufficient detail to prepare a response
2. Allow the employee a reasonable time to prepare
3. Allow the employee to be assisted by a trade union representative or fellow employee
4. Hold a hearing (or an opportunity to respond to the allegations)
5. The employer must communicate the decision and the reasons for it
6. If the employee is dismissed, inform them of their right to refer the dispute to a bargaining council or the CCMA

### Incapacity — poor performance (Schedule 8 Items 8-9)

**Substantive fairness:**
- The employee failed to meet a performance standard
- The employee was aware of the required standard
- The employee was given a fair opportunity to meet the standard
- The employee received appropriate evaluation, instruction, training, guidance, or counselling
- A reasonable period was allowed for improvement
- Dismissal is appropriate after failure to improve despite support

**Probation (Schedule 8 Item 8):**
- Probation does not remove the requirement for fair dismissal
- The employer must provide evaluation, instruction, training, guidance, or counselling during probation
- The employer should consider extending the probation period before dismissing
- The procedure need not be as formal as for non-probationary employees, but must still be fair

### Incapacity — ill health or injury (Schedule 8 Items 10-11)

- The degree and duration of incapacity must be established
- The possibility of securing alternative employment must be investigated
- The employee's length of service and the likelihood of recovery must be considered
- Where injury is work-related, the employer must investigate compliance with OHSA and COIDA obligations

### Operational requirements / retrenchment (LRA s189, s189A)

**s189 consultation process (all retrenchments):**
1. Issue a written notice to affected employees or their representatives (s189(3))
2. Disclose: reasons for proposed dismissals, alternatives considered, number of employees affected, selection criteria, proposed timing, severance pay, possibility of future re-employment, and any other relevant matters
3. Engage in meaningful consultation — allow the consulting parties to make representations and consider alternatives
4. Selection criteria must be fair and objective (LIFO is common but not mandatory)
5. Severance pay: minimum 1 week's remuneration per completed year of service (LRA s41(2))

**s189A large-scale retrenchment (additional requirements):**
- Triggered when employer has 50+ employees AND contemplates dismissing at least: 10 (for 50-200 employees), 20 (201-300), 30 (301-400), 40 (401-500), or 50 (500+)
- Either party may request CCMA to appoint a facilitator
- Consultation must run for at least 60 days from the date notice is given
- If consultation fails, employees may strike or employer may lock out (or either may refer to Labour Court)

## CCMA dispute resolution

1. **Referral:** Employee refers dispute to CCMA (or bargaining council if applicable) within 30 days of dismissal (LRA s191(1))
2. **Conciliation:** Commissioner attempts resolution within 30 days (LRA s191(5))
3. **If conciliation fails:** Certificate of non-resolution issued. Employee refers to arbitration (CCMA) within 90 days, or to Labour Court for automatically unfair dismissals and operational requirements dismissals
4. **Con-arb:** For certain disputes (dismissals related to conduct or capacity where employee earns below BCEA threshold), conciliation and arbitration may be conducted in a single sitting

## High-risk termination flags — South Africa

Walk every flag before concluding a termination review. If any flag fires, escalate per the practice profile's escalation table — do not proceed without sign-off.

| # | Flag | Why it's high-risk | Check |
|---|---|---|---|
| 1 | **No hearing held** | Procedural unfairness — Schedule 8 requires the employee to be notified of allegations, given time to prepare, allowed representation, and given an opportunity to respond before dismissal | Was a disciplinary hearing held? Was the employee given notice of allegations, time to prepare, and the right to representation? |
| 2 | **Automatically unfair ground** | LRA s187 — no remedy other than reinstatement + compensation up to 24 months | Is the dismissal connected to pregnancy, union membership/activity, protected disclosure, exercise of any right under labour legislation, refusal to do work of a striker, or participation in a lawful strike? |
| 3 | **Discrimination / EEA-protected ground** | Potential automatically unfair dismissal under LRA s187(1)(f) and/or unfair discrimination claim under the Employment Equity Act | Is there any indication the dismissal is connected to race, gender, disability, age, religion, HIV status, or other EEA-protected characteristics, or to a grievance about unfair discrimination? |
| 4 | **Protected disclosure** | Protected Disclosures Act 26 of 2000 — dismissal for making a protected disclosure is automatically unfair | Has this employee made a protected disclosure (whistleblowing) to the employer, a regulatory body, or the media? |
| 5 | **Recent CCMA/union activity** | Retaliation / automatically unfair under LRA s187(1)(d) | Has the employee recently referred a dispute to the CCMA, participated in union activity, served as a shop steward, or participated in a lawful strike? |
| 6 | **Operational requirements without s189 process** | Unfair retrenchment — failure to follow the consultation process renders dismissal procedurally unfair | If the reason is operational requirements, has the s189 consultation process been followed? **Sub-check:** Does the employer fall into s189A large-scale retrenchment territory (50+ employees and numbers meeting the schedule)? If so, has the more onerous consultation, facilitation, and notice process been followed? |
| 7 | **Probation without Code compliance** | LRA Schedule 8 Item 8 — probation does not remove fair dismissal requirements | Is the employee on probation? Was proper evaluation, instruction, training, guidance, and counselling provided? Was a reasonable period for improvement allowed? Was a reasonable extension considered before dismissal? |
| 8 | **Fixed-term contract — reasonable expectation** | LRA s186(1)(b) — non-renewal can constitute a dismissal | Is this a fixed-term employee? Has a reasonable expectation of renewal been created through prior renewals, conduct, or representations? |
| 9 | **Earnings below BCEA threshold** | Full BCEA protections apply — higher scrutiny for adverse changes | Does the employee earn below the BCEA earnings threshold? Below-threshold employees enjoy full working-time and overtime protections; dismissals and changes to hours/conditions for this cohort are more likely to be scrutinised at the CCMA. |
| 10 | **Thin documentation** | "Why now?" problem — common CCMA defence for employers is undermined by absent records | For performance-based dismissals: is there a record of progressive discipline — verbal warning, written warning(s), final written warning, PIP or counselling? Or did this come out of nowhere? Was the employee given a fair opportunity to improve? |
| 11 | **Comparator problem / inconsistent discipline** | Inconsistent application of discipline — regularly undermines employer cases at the CCMA | Is someone else doing the same thing and not being dismissed? Has the employer applied its disciplinary code consistently across similar cases? |

## Notice periods

Per BCEA s37(1), minimum notice periods based on length of service:

| Service period | Minimum notice |
|---|---|
| 6 months or less | 1 week |
| More than 6 months, up to 1 year | 2 weeks |
| More than 1 year | 4 weeks |

The contract may provide for longer notice periods. Notice must be in writing (BCEA s37(4)). An employer may pay the employee in lieu of notice.

## Severance pay

For operational requirements dismissals only (not misconduct or incapacity): minimum 1 week's remuneration per completed year of continuous service (LRA s41(2)). The contract or company policy may provide more. Severance is not customary for misconduct or incapacity dismissals, though separation agreements may include a payment.
```

- [ ] **Step 2: Verify no US-specific concepts leaked in**

Run: `grep -inE '(FMLA|FLSA|at.will|EEOC|NLRB|WARN Act|Cal-WARN|PAGA|FRCP)' jurisdictions/za/employment-legal/topics/dismissal.md`
Expected: No matches (exit 1)

- [ ] **Step 3: Commit**

```bash
git add jurisdictions/za/employment-legal/topics/dismissal.md
git commit -m "feat(za): add dismissal topic overlay with LRA framework and 11 high-risk flags"
```

---

## Task 4: Topic Overlays — Hiring, Classification, Leave, Policy, Investigation

**Files:**
- Create: `jurisdictions/za/employment-legal/topics/hiring.md`
- Create: `jurisdictions/za/employment-legal/topics/classification.md`
- Create: `jurisdictions/za/employment-legal/topics/leave-and-conditions.md`
- Create: `jurisdictions/za/employment-legal/topics/policy-and-handbook.md`
- Create: `jurisdictions/za/employment-legal/topics/investigation-privilege.md`

- [ ] **Step 1: Write hiring topic overlay**

```markdown
# Hiring — South African Overlay

## Restraint of trade

SA restraint of trade clauses are enforceable but courts apply a strict reasonableness test. The leading authority is *Basson v Chilwan* 1993 (3) SA 742 (A), which established four factors:

1. **Is there a protectable interest?** (trade secrets, trade connections, confidential information — not merely employee skill or general knowledge)
2. **Is the restraint reasonable in scope?** (geographical area, duration, activities restricted)
3. **Is it reasonable in the interests of the parties?** (balance employer's interest against employee's right to earn a livelihood — s22 of the Constitution)
4. **Is enforcement contrary to the public interest?**

**Key differences from US approach:**
- No per-state enforceability map — SA is a single national jurisdiction for restraint law
- Constitutional right to choose a trade, occupation, or profession (s22 Bill of Rights) weighs heavily
- Courts may sever or read down unreasonable clauses rather than void them entirely
- Garden leave is rare in SA; notice periods serve a similar function
- Non-solicitation clauses (of clients and employees) are generally more readily enforced than non-compete clauses

**Review checklist for offer letters and employment contracts:**
- Is the restraint limited to a specific geographical area? (National restraints are harder to enforce)
- Is the duration reasonable? (6-12 months is common; beyond 24 months is very difficult to enforce)
- Is the activity restriction specific? (Broad "may not work in the industry" clauses are harder to enforce)
- Does the employee have access to genuine protectable interests?
- Is the restraint accompanied by consideration? (In SA, the employment itself is generally sufficient consideration — unlike some US jurisdictions)

## Probation

Governed by LRA Schedule 8 Item 8 and the Code of Good Practice: Dismissal.

**Probation is NOT a free pass to dismiss.** The employer must:
1. Clearly communicate the standards expected and the consequences of failure to meet them
2. Provide evaluation, instruction, training, guidance, or counselling during probation
3. Allow a reasonable period for improvement before dismissing
4. Consider extending the probation period before dismissing
5. Follow a fair procedure — less formal than for non-probationary employees, but still fair

**Probation periods:** Not prescribed by statute. 3-6 months is common practice. The BCEA does not set a maximum; the test is reasonableness given the nature of the job.

**Review checklist for probation clauses in employment contracts:**
- Is the probation period reasonable for the role? (3 months for administrative, 6 months for skilled, longer for senior/professional)
- Does the clause reference the employer's evaluation and support obligations?
- Does it provide for extension of probation as an alternative to dismissal?
- Does it reference the right to a fair hearing before dismissal during probation?

## EEA obligations at hire

For designated employers (50+ employees):
- The employment equity plan's numerical targets should inform hiring decisions
- Vacancy advertisements must reflect the employer's commitment to employment equity
- Selection criteria must be fair and non-discriminatory
- Psychometric testing must be scientifically valid, reliable, fair, and not biased against any group (EEA s8)
- Pre-employment medical testing is prohibited unless legislation permits or requires it, or it is justifiable given the inherent requirements of the job (EEA s7)
- Pre-employment HIV testing is prohibited (EEA s7(2)) except with Labour Court authorisation

## Employment contract requirements

SA employment contracts must specify (BCEA s29):
- Full name and address of the employer
- Name and occupation of the employee
- Place of work
- Date employment began
- Ordinary hours of work and days of work
- Wage or rate and method of payment
- Rate for overtime work
- Any other cash payments and payments in kind
- Frequency of remuneration
- Any deductions
- Leave entitlement
- Notice period
- Description of any council or sectoral determination applicable
- Any period of employment with a previous employer that counts towards period of employment
- List of any other documents forming part of the contract

Written particulars must be provided within the first day of commencement (or within 2 months for employees working fewer than 24 hours per month).
```

- [ ] **Step 2: Write classification topic overlay**

```markdown
# Worker Classification — South African Overlay

## Statutory definition of "employee"

The primary definition is in BCEA s213 and LRA s213:

> "employee" means —
> (a) any person, excluding an independent contractor, who works for another person or for the State and who receives, or is entitled to receive, any remuneration; and
> (b) any other person who in any manner assists in carrying on or conducting the business of an employer

## Presumption of employment (BCEA s200A)

Any person who works for or renders services to another person is **presumed to be an employee** if any one or more of the following factors is present:

1. The manner in which the person works is subject to the control or direction of the other person
2. The person's hours of work are subject to the control or direction of the other person
3. In the case of a person who works for an organisation, the person forms part of that organisation
4. The person has worked for the other person for an average of at least 40 hours per month over the last three months
5. The person is economically dependent on the other person for whom they work or render services
6. The person is provided with tools of trade or work equipment by the other person
7. The person only works for or renders services to one person

**This presumption applies only to employees earning below the BCEA earnings threshold.** For those earning above, the common law tests apply but the presumption does not.

The burden shifts to the employer to prove the person is an independent contractor if any of these factors is present.

## Common law control test

For employees above the BCEA threshold (and as the underlying framework for all classifications), SA courts apply the "dominant impression" test, weighing multiple factors. The leading case is *SABC v McKenzie* (1999) 20 ILJ 585 (LAC):

| Factor | Points to employee | Points to IC |
|---|---|---|
| **Control** | Employer dictates how, when, where work is done | Worker determines own methods and schedule |
| **Integration** | Worker is part of the employer's organisation | Worker operates their own independent business |
| **Economic dependence** | Worker depends on employer for income | Worker has multiple clients and bears own risk |
| **Tools and equipment** | Employer provides | Worker provides own |
| **Profit/loss risk** | Worker bears no financial risk | Worker bears risk of profit and loss |
| **Ability to delegate** | Worker must perform personally | Worker can subcontract or delegate |
| **Exclusivity** | Worker works only for employer | Worker serves multiple clients |
| **Tax and benefits** | Employer deducts PAYE, provides benefits | Worker invoices, handles own tax |

No single factor is determinative. The court looks at the "dominant impression" of the relationship as a whole.

## Deemed employees (labour brokers / TES)

The LRA s198A (inserted by 2014 amendments) provides that an employee placed by a temporary employment service (TES / labour broker) with a client for longer than 3 months is **deemed to be the employee of the client** if the employee earns below the BCEA earnings threshold. The client becomes jointly and severally liable.

**Key implications:**
- The 3-month trigger applies to the individual employee's placement, not the contract between the TES and the client
- Deemed employees are entitled to the same conditions of employment as the client's directly employed employees performing the same or similar work (LRA s198A(5))
- This provision does not apply to employees earning above the BCEA threshold
- The TES and the client are jointly and severally liable for any contravention

## Classification review checklist

When classifying a proposed worker arrangement in SA:

1. **Earnings check:** Is the worker likely to earn above or below the BCEA threshold? (This determines whether s200A presumption and s198A deemed-employee provisions apply)
2. **Presumption check (below threshold):** Do any of the 7 s200A factors apply? If yes, the person is presumed to be an employee
3. **Dominant impression (all workers):** Apply the multi-factor control test — what is the dominant impression of the relationship?
4. **TES/labour broker check:** Is the worker placed by a TES? If so, will the placement exceed 3 months? If the worker earns below threshold, the client becomes the deemed employer after 3 months
5. **Substance over form:** SA courts look at the reality of the relationship, not the label the parties attach to it. A contract labelled "independent contractor agreement" does not override the substance of the arrangement
```

- [ ] **Step 3: Write leave-and-conditions topic overlay**

```markdown
# Leave and Conditions of Employment — South African Overlay

## Statutory leave entitlements (BCEA)

All leave entitlements below are **minimums**. The employer may (and many do) offer more generous entitlements. The cold-start interview captures whether the employer is "at BCEA minimums" or "above minimums" — if above, the practice profile records the employer's actual entitlements.

### Annual leave (BCEA s20)

- **Entitlement:** 21 consecutive days per annual leave cycle, OR by agreement: 1 day for every 17 days worked, or 1 hour for every 17 hours worked
- **Leave cycle:** 12 months from date of employment (or from a date agreed in the contract — the cold-start interview captures non-standard leave cycles)
- **Timing:** Employer must grant leave within 6 months after the end of the leave cycle
- **No cashing out during employment:** Annual leave may not be paid out instead of taken, except on termination (BCEA s20(4))
- **Payment on termination:** Accrued but untaken annual leave must be paid out on termination

### Sick leave (BCEA s22)

- **Entitlement:** 30 days paid sick leave per 36-month cycle (equivalent to 6 weeks' worth of the employee's normal working days)
- **First 6 months:** 1 day for every 26 days worked
- **Medical certificate:** Employer may require a medical certificate for absences of more than 2 consecutive days, or if the employee has been absent on more than 2 occasions during an 8-week period
- **Cycle resets:** Every 3 years from date of employment

### Family responsibility leave (BCEA s27)

- **Entitlement:** 3 days per annual leave cycle
- **Qualifying events:** Birth of child, illness of child, death of spouse/life partner, parent, adoptive parent, grandparent, child, adopted child, grandchild, or sibling
- **Eligibility:** Employees who have been employed for longer than 4 months and who work at least 4 days per week

### Maternity leave (BCEA s25)

- **Entitlement:** At least 4 consecutive months
- **Commencement:** May begin 4 weeks before expected date of confinement, or earlier if a medical practitioner or midwife certifies it is necessary
- **Post-delivery:** Employee may not work for 6 weeks after birth unless a medical practitioner or midwife certifies she is fit
- **Payment:** BCEA does not require the employer to pay during maternity leave. UIF provides partial income replacement (up to 66% of earnings, capped). Many employers top up UIF benefits — the cold-start interview captures whether the employer pays maternity leave and how much
- **Miscarriage/stillbirth:** Employee is entitled to maternity leave for 6 weeks after a miscarriage in the third trimester or stillbirth

### Paternity leave

- **Not in BCEA.** The Labour Laws Amendment Act 10 of 2018 provides for 10 consecutive days of parental leave (unpaid, with UIF benefits available). This applies regardless of gender of the parent.

### Parental leave (Labour Laws Amendment Act 10 of 2018)

- **Entitlement:** 10 consecutive days, commencing on the date of birth or the date the adoption order is granted
- **Payment:** Unpaid under the statute; UIF benefits available
- **Both parents:** Each parent is entitled to parental leave (but only one parent may take maternity leave; the other takes parental leave)

## Working time (BCEA ss9-16)

**These provisions apply only to employees earning below the BCEA earnings threshold.** Employees above the threshold are excluded from ss9-16.

| Rule | Provision | Limit |
|---|---|---|
| Ordinary hours | BCEA s9(1) | 45 hours/week (9/day for 5-day week, 8/day for 6-day week) |
| Overtime | BCEA s10(1) | Max 10 hours/week; max 12 hours on any day |
| Overtime rate | BCEA s10(2) | 1.5x ordinary rate (or time off by agreement) |
| Sunday work | BCEA s16(1) | 2x rate if not ordinarily working Sundays; 1.5x if ordinarily working |
| Night work (18:00-06:00) | BCEA s17(1) | Only by agreement; employer must provide transport and allowance |
| Meal interval | BCEA s14(1) | 1 hour after 5 hours of work (reducible to 30 min by agreement) |

## Notice periods (BCEA s37)

| Service period | Minimum notice |
|---|---|
| 6 months or less | 1 week |
| More than 6 months, up to 1 year | 2 weeks |
| More than 1 year | 4 weeks |

Notice must be in writing. The employer may pay in lieu of notice.

## Deductions (BCEA s34)

An employer may not deduct from an employee's remuneration unless:
- The employee agrees in writing and the deduction is for a debt specified in the agreement
- The deduction is required by law (PAYE, UIF, SDL), a court order, a collective agreement, or an arbitration award
- Deductions for damage or loss: only if fair procedure followed, employee agrees, and the deduction does not exceed 25% of remuneration
```

- [ ] **Step 4: Write policy-and-handbook topic overlay**

```markdown
# Policy and Handbook — South African Overlay

## SA policy framework

South African employment policies operate within a statutory floor set by the BCEA, LRA, and EEA. Unlike US handbooks that vary by state, SA policies apply nationally but may be supplemented by:
- **Bargaining council agreements** (override BCEA where they provide better terms)
- **Sectoral determinations** (set industry-specific conditions)
- **Collective agreements** (negotiated with recognised unions)

There are no "state supplements" in SA. The national statutory framework is uniform.

## Mandatory/recommended policies

### Disciplinary code and procedure (essential)

Every employer should have a disciplinary code aligned with **LRA Schedule 8 — Code of Good Practice: Dismissal**. The code must:

1. List categories of misconduct and their severity (minor, serious, gross)
2. Specify the progressive discipline framework (verbal warning → written warning → final written warning → dismissal)
3. Set out the hearing procedure (notice of allegations, right to representation, right to respond, appeal process)
4. Define the chairperson's role and powers (calling evidence, making findings, determining sanction)
5. Specify sanction guidelines per category of offence — while noting that mitigating and aggravating factors must always be considered

**The disciplinary code is the employer's most important employment document in SA.** It is the primary evidence of what the employer's standards are, whether the employee knew them, and whether the employer applied them consistently. CCMA commissioners routinely measure dismissals against the employer's own code.

### Grievance procedure (essential)

A formal grievance procedure is critical because:
- Unresolved grievances can escalate to CCMA referrals
- The grievance history is relevant to dismissal proceedings (was the employee raising issues before being dismissed?)
- Code of Good Practice on Dismissal expects employers to have a mechanism for employees to raise concerns

Structure: informal discussion → formal written grievance → hearing/meeting with management → appeal → external referral (CCMA/bargaining council)

### Sexual harassment policy (strongly recommended)

The **Code of Good Practice on the Handling of Sexual Harassment Cases** (issued under the EEA) expects employers to:
- Have a policy prohibiting sexual harassment
- Define what constitutes sexual harassment
- Provide a complaints procedure separate from the general disciplinary procedure
- Protect complainants from victimisation
- Provide for investigation and disciplinary action

### Other recommended policies

| Policy | Legal basis | Notes |
|---|---|---|
| Leave policy | BCEA ss20-27 | Document entitlements above BCEA minimums; leave cycle; medical certificate requirements |
| Working hours policy | BCEA ss9-16 | Ordinary hours, overtime, compressed weeks, flexible arrangements |
| Health and safety | OHSA | Appoint health and safety representatives; establish committee for 20+ employees |
| HIV/AIDS policy | EEA s6; Code of Good Practice on HIV/AIDS | Non-discrimination, testing restrictions, confidentiality, reasonable accommodation |
| Substance abuse | n/a | Not legally required but standard practice; must align with disciplinary code |
| IT and social media | POPIA, RICA | Interception and monitoring must comply with RICA; personal data processing with POPIA |

## Drafting conventions for SA policies

When drafting policies for SA employers:
- Reference the controlling statute and section (e.g., "In terms of BCEA s20(2)...")
- Use "employee" as defined in BCEA s213 / LRA s213
- Include acknowledgement forms (employee confirms receipt and understanding)
- Specify the policy's relationship to any applicable bargaining council agreement or sectoral determination
- Note that policies form part of the employment contract where incorporated by reference
- Include a review date and version number (SA employment law changes; policies must keep up)
```

- [ ] **Step 5: Write investigation-privilege topic overlay**

```markdown
# Investigation and Legal Privilege — South African Overlay

## SA legal professional privilege

South African legal privilege derives from common law (English law tradition) and is significantly narrower than US attorney-client privilege combined with work product doctrine.

### What is protected

**Legal advice privilege:** Confidential communications between a legal adviser (admitted attorney or advocate) and their client, made for the purpose of obtaining or giving legal advice. The key elements:

1. **Communication** — not all documents; only communications between lawyer and client
2. **Confidential** — made in confidence
3. **For the purpose of legal advice** — not all communications with a lawyer; only those seeking or providing legal advice
4. **With a legal adviser** — an admitted attorney or advocate enrolled under the Legal Practice Act 28 of 2014

**Litigation privilege:** Documents and communications created for the dominant purpose of pending or contemplated litigation. Requires litigation to be in reasonable contemplation at the time the document was created.

### What is NOT protected

- Internal analysis, compliance assessments, and risk memoranda prepared by in-house counsel acting in a **commercial capacity** (not as a legal adviser)
- Documents prepared in the ordinary course of business, even if prepared by a legally qualified person
- Communications with non-lawyers (HR, compliance officers) about legal matters — these are NOT privileged unless they are part of a communication chain to/from a lawyer for the purpose of obtaining legal advice
- Pre-existing documents — privilege does not attach to documents that existed before the lawyer was consulted, even if they are later shared with the lawyer

### In-house counsel — the critical distinction

SA courts recognise privilege for in-house counsel, but only when the in-house lawyer is acting **in their capacity as legal adviser**, not as a business executive. The test (from *Euroshipping Corporation of Monrovia v Minister of Agricultural Economics and Marketing* 1979 (1) SA 637 (C) and subsequent cases):

- Was the communication made for the purpose of obtaining legal advice?
- Was the in-house lawyer acting as a legal adviser, or as a member of the management team?

**Practical implication for the work-product header:**
- When the user is an admitted attorney/advocate acting as legal adviser: the privilege header is appropriate
- When the user is in-house counsel attending a management meeting or making a commercial recommendation: the privilege may not attach, and the header should include the caveat about commercial-vs-legal capacity
- When in doubt: mark as privileged but include the caveat

## Protected Disclosures Act 26 of 2000

Employees who make protected disclosures (whistleblowing) are protected from occupational detriment, including dismissal. An internal investigation that involves a protected disclosure must:

1. **Not victimise the discloser** — any adverse action against the person who made the disclosure during or after the investigation may constitute automatically unfair dismissal (LRA s187(1)(h))
2. **Preserve confidentiality of the discloser's identity** where possible
3. **Not use the investigation to build a case against the discloser** for making the disclosure

## POPIA considerations for investigations

The Protection of Personal Information Act 4 of 2013 (POPIA) governs processing of personal information during investigations:

- **Lawful basis:** Processing witness statements, complainant information, and respondent information must have a lawful basis — typically "legitimate interests" (POPIA s11(1)(f)) or "legal obligation" (POPIA s11(1)(c))
- **Purpose limitation:** Information collected for the investigation may not be used for unrelated purposes
- **Minimality:** Collect only the personal information necessary for the investigation
- **Notification:** The Information Regulator requires that data subjects be informed of the processing of their personal information, unless an exemption applies (e.g., it would prejudice the investigation — POPIA s18(4)(b))
- **Security:** Investigation records containing personal information must be secured
- **Retention:** Investigation records should be retained only for as long as necessary — but note that labour dispute referral timelines (30 days for CCMA) and prescription periods may require retention

## Investigation procedure — SA-specific considerations

The investigation framework is largely portable from US practice, with these SA-specific adjustments:

- **Right to representation:** Any employee called to a disciplinary hearing (which may follow an investigation) is entitled to be represented by a trade union representative or fellow employee (not an external lawyer, unless the employer's code provides for it)
- **Evidentiary rules:** CCMA arbitrators apply a less formal evidentiary standard than courts. Hearsay is admissible but given less weight. The standard of proof is balance of probabilities.
- **Privilege log adjustments:** SA privilege is narrower — fewer documents will qualify as privileged. Internal analysis and investigation notes prepared by non-lawyers are generally not privileged. Only communications with/from an admitted attorney for the purpose of legal advice qualify.
```

- [ ] **Step 6: Verify no US-specific concepts in any topic file**

Run: `grep -rinE '(FMLA|FLSA|at.will|EEOC|NLRB|WARN Act|Cal-WARN|PAGA|FRCP|OSHA[^A])' jurisdictions/za/employment-legal/topics/`
Expected: No matches (exit 1). Note: OHSA (SA) is different from OSHA (US) — the regex excludes OHSA.

- [ ] **Step 7: Commit**

```bash
git add jurisdictions/za/employment-legal/topics/
git commit -m "feat(za): add 5 topic overlays — hiring, classification, leave, policy, investigation"
```

---

## Task 5: Skill Router

**Files:**
- Create: `jurisdictions/za/employment-legal/router.md`

- [ ] **Step 1: Write the router file**

```markdown
# Skill Router — South African Employment Law Overlay

When jurisdiction = ZA, skills load the topic overlays and statute files listed below.

Topic files resolve to: `jurisdictions/za/employment-legal/topics/{name}.md`
Statute files resolve to: `jurisdictions/za/statutes/{name}.yaml`

```yaml
termination-review:
  topics: [dismissal]
  statutes: [lra, bcea]

hiring-review:
  topics: [hiring]
  statutes: [bcea, eea]

worker-classification:
  topics: [classification]
  statutes: [bcea]

wage-hour-qa:
  topics: [leave-and-conditions]
  statutes: [bcea]

leave-tracker:
  topics: [leave-and-conditions]
  statutes: [bcea]

policy-drafting:
  topics: [policy-and-handbook, dismissal]
  statutes: [bcea, lra, eea]

cold-start-interview:
  topics: []
  statutes: [bcea, lra, eea]
```
```

- [ ] **Step 2: Write the router cross-reference validator**

```python
#!/usr/bin/env python3
"""Validate the ZA employment-legal router: every reference resolves.

Checks:
1. Every skill in the router exists in employment-legal/skills/
2. Every topic file referenced exists in jurisdictions/za/employment-legal/topics/
3. Every statute file referenced exists in jurisdictions/za/statutes/
4. No orphaned topic files (every topic is referenced by at least one skill)

Usage: python3 scripts/validate-za-router.py
Exits 0 if valid, 1 on errors.
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
ROUTER_PATH = ROOT / "jurisdictions" / "za" / "employment-legal" / "router.md"
SKILLS_DIR = ROOT / "employment-legal" / "skills"
TOPICS_DIR = ROOT / "jurisdictions" / "za" / "employment-legal" / "topics"
STATUTES_DIR = ROOT / "jurisdictions" / "za" / "statutes"


def extract_yaml_from_markdown(text: str) -> str:
    match = re.search(r"```yaml\n(.*?)```", text, re.DOTALL)
    if not match:
        return ""
    return match.group(1)


def main() -> int:
    if not ROUTER_PATH.exists():
        print(f"FAIL: {ROUTER_PATH} does not exist", file=sys.stderr)
        return 1

    raw = ROUTER_PATH.read_text()
    yaml_text = extract_yaml_from_markdown(raw)
    if not yaml_text:
        print("FAIL: no YAML block found in router.md", file=sys.stderr)
        return 1

    router = yaml.safe_load(yaml_text)
    errors = 0
    all_referenced_topics = set()

    for skill, config in router.items():
        if not (SKILLS_DIR / skill).is_dir():
            print(f"FAIL: skill '{skill}' not found in {SKILLS_DIR}", file=sys.stderr)
            errors += 1

        for topic in config.get("topics", []):
            all_referenced_topics.add(topic)
            topic_path = TOPICS_DIR / f"{topic}.md"
            if not topic_path.exists():
                print(
                    f"FAIL: skill '{skill}' references topic '{topic}' "
                    f"but {topic_path} does not exist",
                    file=sys.stderr,
                )
                errors += 1

        for statute in config.get("statutes", []):
            statute_path = STATUTES_DIR / f"{statute}.yaml"
            if not statute_path.exists():
                print(
                    f"FAIL: skill '{skill}' references statute '{statute}' "
                    f"but {statute_path} does not exist",
                    file=sys.stderr,
                )
                errors += 1

    existing_topics = {p.stem for p in TOPICS_DIR.glob("*.md")}
    orphaned = existing_topics - all_referenced_topics
    for orphan in sorted(orphaned):
        print(
            f"WARN: topic '{orphan}' exists but is not referenced by any skill in the router",
            file=sys.stderr,
        )

    if errors:
        print(f"\n{errors} errors found")
        return 1

    print(f"OK: {len(router)} skills, all references resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 3: Run router validator**

Run: `python3 scripts/validate-za-router.py`
Expected: `OK: 7 skills, all references resolve` and exit 0

- [ ] **Step 4: Commit**

```bash
git add jurisdictions/za/employment-legal/router.md scripts/validate-za-router.py
git commit -m "feat(za): add skill router and cross-reference validator"
```

---

## Task 6: ZA Practice Profile Template

**Files:**
- Create: `jurisdictions/za/employment-legal/practice-profile-template.md`
- Create: `scripts/validate-za-templates.py`

- [ ] **Step 1: Write the ZA practice profile template**

This is the SA variant of `employment-legal/CLAUDE.md`. It keeps jurisdiction-neutral sections (output formatting, guardrails, matter workspaces) but replaces US-specific sections with SA equivalents. The full content is long — key structural sections shown here with the instruction to use the existing `employment-legal/CLAUDE.md` as the base and replace the sections listed in the ARCHITECTURE.md mapping table.

The template must include these SA-native sections (replacing their US equivalents):

**Configuration header** (same HTML comment as US template, different path reference):
```html
<!--
CONFIGURATION LOCATION
User-specific configuration for this plugin lives at:
  ~/.claude/plugins/config/claude-for-legal/employment-legal/CLAUDE.md

JURISDICTION OVERLAY
When jurisdiction = ZA, after loading this configuration, read the router at:
  jurisdictions/za/employment-legal/router.md
Load the topic overlays and statute files listed for the active skill.
-->
```

**Outputs section** — SA work-product header:
```markdown
## Outputs

**Work-product header:**

- If Role is **Lawyer or legal professional** (admitted attorney or advocate under the Legal Practice Act 28 of 2014):
  `PRIVILEGED & CONFIDENTIAL — PREPARED BY/AT THE DIRECTION OF LEGAL COUNSEL FOR THE PURPOSE OF PROVIDING LEGAL ADVICE`
- If Role is **Non-lawyer** (either type):
  `CONFIDENTIAL — NOT LEGAL ADVICE — CONSULT AN ADMITTED ATTORNEY OR ADVOCATE BEFORE ACTING`

**SA privilege caveat.** SA legal professional privilege is narrower than US "attorney work product" (FRCP 26(b)(3)). It protects confidential communications between an admitted attorney/advocate and their client made for the purpose of obtaining or giving legal advice. It does NOT protect:
- Internal analysis or risk memoranda prepared by in-house counsel acting in a commercial capacity
- Documents prepared in the ordinary course of business
- Communications with non-lawyers about legal matters (unless part of a chain to/from a lawyer for legal advice)

When the user is in-house counsel, add to the header: `[Note: SA legal professional privilege attaches to communications made in a legal advisory capacity. If this document was prepared in a commercial or management capacity, the privilege marking may not withstand challenge. Confirm the applicable privilege position before relying on this marking to resist disclosure.]`
```

**Jurisdictional footprint** (replacing US states):
```markdown
## Jurisdictional footprint

**Provinces with employees:** [PLACEHOLDER — list]
**Sectoral determinations applicable:** [PLACEHOLDER — domestic workers / hospitality / farm / retail / forestry / none]
**Bargaining council coverage:** [PLACEHOLDER — council name(s) and bargaining units covered, or none]
**Remote-first or office-based:** [PLACEHOLDER]
```

**Statutory baseline:**
```markdown
## Statutory baseline

**BCEA earnings threshold:** [PLACEHOLDER — employees above / below / both]
**If both:** approximate split above/below threshold: [PLACEHOLDER]
**National minimum wage applicability:** [PLACEHOLDER — standard / sectoral rate / EPWP]
```

**Employment equity / BEE posture:**
```markdown
## Employment equity and BEE

**Designated employer:** [PLACEHOLDER — Yes (50+ employees) / No]
**EE plan status:** [PLACEHOLDER — active with reporting cycle / in preparation / not required]
**Sector-specific BEE codes:** [PLACEHOLDER — code name(s) or none]
```

**Dispute resolution:**
```markdown
## Dispute resolution

**Primary dispute channel:** [PLACEHOLDER — CCMA / bargaining council name / both]
**External labour consultants or law firm:** [PLACEHOLDER — firm name or none]
**Recognised unions:** [PLACEHOLDER — union name(s) and bargaining unit(s) covered, or none]
**Union recognition agreement:** [PLACEHOLDER — yes / no / in negotiation]
```

**Leave and conditions:**
```markdown
## Leave and conditions

**Leave entitlements:** [PLACEHOLDER — at BCEA minimums / above minimums]
**If above minimums:** key differences from BCEA: [PLACEHOLDER]
**Leave cycle:** [PLACEHOLDER — calendar year / employment anniversary / other]
**Maternity pay:** [PLACEHOLDER — UIF only / employer tops up to X% for Y months / full pay]
**Sick leave policy:** [PLACEHOLDER — BCEA 30 days per 3-year cycle / above BCEA]
```

**Retrenchment posture:**
```markdown
## Retrenchment

**Typically above s189A thresholds:** [PLACEHOLDER — Yes (50+ employees, assume large-scale process) / No]
**Consultation preference:** [PLACEHOLDER — in-house / facilitated by external consultant]
```

**Termination review** (replacing US flags):
```markdown
## Termination review

**When legal reviews terminations:** [PLACEHOLDER — all / misconduct only / retrenchments only / exec only]
**Standard severance for operational requirements:** [PLACEHOLDER — 1 week per year (LRA minimum) / above LRA minimum: formula]

**High-risk termination flags (auto-escalate):**
See `jurisdictions/za/employment-legal/topics/dismissal.md` for the full 11-flag table. Default set loaded from the topic overlay; customise below if your organisation has additional flags.
- [PLACEHOLDER — additional company-specific flags beyond the standard 11]
```

**Hiring review:**
```markdown
## Hiring review

**When legal reviews hires:** [PLACEHOLDER — all offers / exec only / only with restraint of trade clauses]
**Standard employment contract template:** [PLACEHOLDER — location]
**Restraint of trade policy:** [PLACEHOLDER — standard clause / case-by-case / none]
**Probation policy:** [PLACEHOLDER — standard period and terms]
```

**Handbook:**
```markdown
## Handbook / policies

**Disciplinary code:** [PLACEHOLDER — location, date]
**Grievance procedure:** [PLACEHOLDER — location, date]
**Sexual harassment policy:** [PLACEHOLDER — location, date / not yet drafted]
**Other key policies:** [PLACEHOLDER]
**Update cadence:** [PLACEHOLDER]
```

**Escalation** (replacing US agencies):
```markdown
## Escalation

| Issue | Handle at | Escalate to | When |
|---|---|---|---|
| Routine offer / contract | [HR] | [You] | Restraint of trade, exec, new role category |
| Performance dismissal | [HR + you] | [GC / senior counsel] | High-risk flags present |
| Misconduct dismissal | [HR + you] | [GC / senior counsel] | Gross misconduct, union member, auto-unfair risk |
| Retrenchment | — | [GC + external labour consultant] | Always |
| CCMA referral received | — | [GC immediately] | Always |
| Union dispute / strike action | — | [GC + external labour consultant] | Always |
| EEA compliance / reporting | [HR] | [You] | Designated employer annual report, DG review |
```

**Seed documents:**
```markdown
## Seed documents

| Doc | Location | Date | Notes |
|---|---|---|---|
| Disciplinary code | [PLACEHOLDER] | | |
| Employment contract template | [PLACEHOLDER] | | |
| CCMA outcome 1 | [PLACEHOLDER] | | (optional) |
| CCMA outcome 2 | [PLACEHOLDER] | | (optional) |
| Employment Equity Plan | [PLACEHOLDER] | | (optional, designated employers only) |
```

The full template must also carry forward the jurisdiction-neutral sections from `employment-legal/CLAUDE.md`:
- `## Who we are` (unchanged)
- `## Who's using this` (unchanged)
- Quiet mode for deliverables (unchanged)
- `## Available integrations` (unchanged)
- `## Decision posture on subjective legal calls` (unchanged)
- All shared guardrails (unchanged — citation hygiene, source attribution, currency trigger, etc.)
- `## Scaffolding, not blinders` (unchanged)
- `## Ad-hoc questions in this domain` (unchanged)
- `## Proportionality` (unchanged)
- `## Jurisdiction recognition` (unchanged — but for ZA users, this section is less likely to fire since they're already in the correct jurisdiction)
- `## Retrieved-content trust` (unchanged)
- `## Large input` / `## Large output` (unchanged)
- `## Matter workspaces` (unchanged)

- [ ] **Step 2: Write the template completeness validator**

```python
#!/usr/bin/env python3
"""Validate ZA practice profile templates for completeness and correctness.

Checks:
1. All required sections present (jurisdictional footprint, termination review, etc.)
2. SA-specific sections exist (CCMA posture, BEE/EEA status, bargaining council)
3. No US-specific sections (state supplements, FMLA, FLSA exemption)
4. Work-product header uses SA formulation
5. User-populated fields use [PLACEHOLDER] markers (not blank)

Usage: python3 scripts/validate-za-templates.py
Exits 0 if valid, 1 on errors.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ZA_TEMPLATES = [
    ROOT / "jurisdictions" / "za" / "employment-legal" / "practice-profile-template.md",
]

REQUIRED_SECTIONS = [
    "Jurisdictional footprint",
    "Statutory baseline",
    "Employment equity",
    "Dispute resolution",
    "Leave and conditions",
    "Termination review",
    "Hiring review",
    "Escalation",
    "Seed documents",
    "Outputs",
]

SA_REQUIRED_TERMS = [
    "CCMA",
    "BCEA",
    "LRA",
    "bargaining council",
    "Schedule 8",
    "admitted attorney",
]

US_FORBIDDEN_TERMS = [
    (r"\bFMLA\b", "FMLA"),
    (r"\bFLSA\b", "FLSA"),
    (r"\bat.will\b", "at-will"),
    (r"\bEEOC\b", "EEOC"),
    (r"\bNLRB\b", "NLRB"),
    (r"\bWARN Act\b", "WARN Act"),
    (r"\bCal-WARN\b", "Cal-WARN"),
    (r"\bstate supplements?\b", "state supplement(s)"),
]


def main() -> int:
    errors = 0

    for path in ZA_TEMPLATES:
        if not path.exists():
            print(f"FAIL: {path} does not exist", file=sys.stderr)
            errors += 1
            continue

        text = path.read_text()
        name = path.name

        for section in REQUIRED_SECTIONS:
            if f"## {section}" not in text and f"# {section}" not in text:
                print(f"FAIL: {name}: missing required section '## {section}'", file=sys.stderr)
                errors += 1

        for term in SA_REQUIRED_TERMS:
            if term not in text:
                print(f"FAIL: {name}: missing SA-required term '{term}'", file=sys.stderr)
                errors += 1

        for pattern, label in US_FORBIDDEN_TERMS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Allow US terms only inside the privilege caveat explanation
                caveat_section = re.search(
                    r"SA (legal professional )?privilege.*?(?=\n##|\Z)",
                    text,
                    re.DOTALL | re.IGNORECASE,
                )
                caveat_text = caveat_section.group(0) if caveat_section else ""
                non_caveat_text = text.replace(caveat_text, "")
                non_caveat_matches = re.findall(pattern, non_caveat_text, re.IGNORECASE)
                if non_caveat_matches:
                    print(
                        f"FAIL: {name}: US-specific term '{label}' found outside privilege caveat",
                        file=sys.stderr,
                    )
                    errors += 1

        print(f"  {'FAIL' if errors else 'OK'}: {name}")

    if errors:
        print(f"\n{errors} errors found")
    else:
        print(f"\n{len(ZA_TEMPLATES)} templates checked, no errors")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 3: Run template validator**

Run: `python3 scripts/validate-za-templates.py`
Expected: `OK: practice-profile-template.md` and exit 0

- [ ] **Step 4: Commit**

```bash
git add jurisdictions/za/employment-legal/practice-profile-template.md scripts/validate-za-templates.py
git commit -m "feat(za): add ZA practice profile template and template validator"
```

---

## Task 7: Cold-Start Interview Fork

**Files:**
- Modify: `employment-legal/skills/cold-start-interview/SKILL.md` (after line 180, within Part 1)

- [ ] **Step 1: Add the ZA jurisdiction fork after Part 0**

Insert the following block into `employment-legal/skills/cold-start-interview/SKILL.md` immediately after the `#### Write to the config CLAUDE.md` section (line 180) and before `### Part 1: The footprint`:

```markdown
### Jurisdiction check — South African overlay

After writing the Part 0 sections, check the company profile for jurisdiction:

- Read `~/.claude/plugins/config/claude-for-legal/company-profile.md` → `Primary jurisdiction`
- If the primary jurisdiction is **South Africa** (or ZA, or the user's company is SA-based based on the company profile answers):

**Fork to the SA interview path.** The rest of this interview (Parts 1-3) uses SA-specific questions. The output writes to the ZA practice profile template at `${CLAUDE_PLUGIN_ROOT}/../../../jurisdictions/za/employment-legal/practice-profile-template.md` instead of the US template at `${CLAUDE_PLUGIN_ROOT}/CLAUDE.md`.

If the primary jurisdiction is NOT South Africa, continue with the US interview path below (Parts 1-3 as written).

---

#### SA Part 1: The statutory footprint (2-3 min)

> South African employment law is national — there are no per-state variations like in the US. But there are three dimensions that shape how the law applies to your organisation: the BCEA earnings threshold, sectoral coverage, and bargaining council membership.

**Statutory baseline:**

> 1. **Do you have employees earning above AND below the BCEA earnings threshold?** (Currently R254,371.67/year. Employees below this threshold have full BCEA working-time and overtime protections. Employees above are excluded from some of those provisions but still covered by the LRA for dismissal, discrimination, etc.)
>    - All above threshold
>    - All below threshold
>    - Both — approximately what split?

> 2. **Is your organisation covered by any sectoral determination?** (Sectoral determinations set industry-specific minimum conditions that can override BCEA defaults. Common sectors: domestic work, hospitality, agriculture, forestry, retail.)
>    - Yes — which sector(s)?
>    - No
>    - Not sure — I can help you check if you tell me your industry

> 3. **Is your organisation covered by a bargaining council?** (Bargaining councils are industry-level bodies that set minimum terms and conditions and handle disputes. Coverage depends on the industry and whether the council's agreement has been extended to non-parties.)
>    - Yes — which council(s) and which categories of employees?
>    - No
>    - Not sure

**Employment equity / BEE posture:**

> 4. **Are you a designated employer under the Employment Equity Act?** (Currently: 50 or more employees. The turnover threshold is being phased out.)
>    - Yes — we have an active EE plan and reporting cycle
>    - Yes — but our EE plan is in preparation / overdue
>    - No — fewer than 50 employees
>    - Not sure

> 5. **Are you subject to any sector-specific BEE codes?** (e.g., ICT, financial services, mining, construction)
>    - Yes — which code(s)?
>    - No / generic codes apply
>    - Not sure

**Dispute resolution:**

> 6. **When labour disputes arise, where do they go?**
>    - CCMA (most common for employers without bargaining council coverage)
>    - Bargaining council (if covered)
>    - Both — CCMA for some categories, bargaining council for others
>
> Do you have a standing relationship with an external labour law firm or labour consultant? (Name, or "we handle it in-house")

> 7. **Do you have recognised unions?**
>    - Yes — which union(s) and which categories of employees?
>    - No
>    - We're in recognition negotiations

**Leave and conditions:**

> 8. **Are your leave entitlements at BCEA minimums or above?** (BCEA minimums: 21 days annual leave, 30 days sick leave per 3-year cycle, 3 days family responsibility leave, 4 months unpaid maternity leave.)
>    - At BCEA minimums
>    - Above minimums — briefly, what's different? (e.g., "25 days annual leave, full-pay maternity for 4 months")

> 9. **Does your leave year run on the calendar year, employment anniversary, or something else?**

**Retrenchment posture:**

> 10. **With your employee count, are you typically above the s189A large-scale retrenchment thresholds?** (50+ employees means the more onerous consultation and facilitation requirements apply to large retrenchments.)
>     - Yes — we assume large-scale process for any significant retrenchment
>     - No — below 50 employees
>     - Borderline — we're around 50

#### SA Part 2: Seed documents

> The two documents that make the biggest difference for SA employment law are your **disciplinary code** and a **standard employment contract template**. Everything else improves accuracy but isn't required to start.

> **Must-have:**
> 1. **Disciplinary code and procedure** — this is the backbone of fair dismissal in SA. I'll learn your offence categories, progressive discipline framework, hearing procedure, and sanction guidelines. Paste the contents, share a file path, or say 'skip for now.'
>
> 2. **Standard employment contract template** — SA contracts carry the real baseline on notice, hours, leave, probation, and restraints. Paste or share the path.

> **Nice-to-have (skip if you don't have them handy):**
> 3. **1-2 CCMA outcomes or settlement agreements** — these show me how you've handled disputes, your settlement posture, and common patterns.
> 4. **Employment Equity Plan** — if you're a designated employer, this helps me understand your EE targets and reporting status.

If they skip seed documents: flag every section built without seed documents with `[NO SEED — defaults used; accuracy improves with your disciplinary code and contract template]`.

#### SA Part 3: Build the configuration

Use the ZA practice profile template. Populate all sections from the interview answers and seed documents. Write to `~/.claude/plugins/config/claude-for-legal/employment-legal/CLAUDE.md`, creating parent directories as needed.

After writing, show the tailored capability list (same as the US close, but with SA-specific examples):

> **Here's what I can help with in SA employment law:**
>
> - **Termination review with SA risk flags** — LRA s188 fairness check, Schedule 8 compliance, CCMA referral risk, 11 high-risk flags. Try: `/employment-legal:termination-review`
> - **Hiring review for SA contracts** — restraint of trade analysis, probation clause review, EEA obligations at hire. Try: `/employment-legal:hiring-review`
> - **Worker classification (SA tests)** — BCEA s213, s200A presumption, common law control test, TES/labour broker analysis. Try: `/employment-legal:worker-classification`
> - **Wage and hour Q&A** — BCEA working-time rules, overtime, leave entitlements, earnings threshold implications. Try: `/employment-legal:wage-hour-qa`
> - **Leave tracking** — BCEA statutory leave (annual, sick, family responsibility, maternity), deadline alerts. Try: `/employment-legal:leave-tracker`
> - **Policy drafting** — disciplinary codes aligned to Schedule 8, grievance procedures, harassment policies per Code of Good Practice. Try: `/employment-legal:policy-drafting`

Then continue with the standard close (configuration path, "you can change anything later," "your practice profile learns").

---
```

- [ ] **Step 2: Verify the fork point is clean**

Run: `grep -n "Jurisdiction check — South African overlay" employment-legal/skills/cold-start-interview/SKILL.md`
Expected: One match at the inserted line

Run: `grep -n "### Part 1: The footprint" employment-legal/skills/cold-start-interview/SKILL.md`
Expected: Still present (the US path remains intact below the ZA fork)

- [ ] **Step 3: Commit**

```bash
git add employment-legal/skills/cold-start-interview/SKILL.md
git commit -m "feat(za): add ZA jurisdiction fork to cold-start interview"
```

---

## Task 8: Test Runner and Structural Validation

**Files:**
- Create: `scripts/test-za-overlays.sh`

- [ ] **Step 1: Write the combined test runner**

```bash
#!/usr/bin/env bash
# Run all ZA overlay validation checks.
# Usage: bash scripts/test-za-overlays.sh
# Exits 0 if all pass, 1 if any fail.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"
ERRORS=0

echo "=== ZA Overlay Validation ==="
echo ""

echo "--- 1. Statute YAML schema ---"
if python3 "$SCRIPT_DIR/validate-za-statutes.py"; then
    echo "PASS: statute validation"
else
    echo "FAIL: statute validation"
    ERRORS=$((ERRORS + 1))
fi
echo ""

echo "--- 2. Router cross-references ---"
if python3 "$SCRIPT_DIR/validate-za-router.py"; then
    echo "PASS: router validation"
else
    echo "FAIL: router validation"
    ERRORS=$((ERRORS + 1))
fi
echo ""

echo "--- 3. Template completeness ---"
if python3 "$SCRIPT_DIR/validate-za-templates.py"; then
    echo "PASS: template validation"
else
    echo "FAIL: template validation"
    ERRORS=$((ERRORS + 1))
fi
echo ""

echo "--- 4. US concept leak check ---"
US_CONCEPTS="FMLA|FLSA|at.will employment|EEOC|NLRB|WARN Act|Cal-WARN|PAGA"
LEAKS=$(grep -rinE "$US_CONCEPTS" \
    "$ROOT/jurisdictions/za/employment-legal/topics/" \
    "$ROOT/jurisdictions/za/statutes/" \
    2>/dev/null || true)

# Filter out legitimate references in privilege caveat explanations
FILTERED=$(echo "$LEAKS" | grep -v "privilege" | grep -v "FRCP" || true)

if [ -n "$FILTERED" ]; then
    echo "FAIL: US concepts found in ZA overlay files:"
    echo "$FILTERED"
    ERRORS=$((ERRORS + 1))
else
    echo "PASS: no US concept leaks"
fi
echo ""

echo "=== Results ==="
if [ "$ERRORS" -eq 0 ]; then
    echo "ALL CHECKS PASSED"
    exit 0
else
    echo "$ERRORS CHECK(S) FAILED"
    exit 1
fi
```

- [ ] **Step 2: Make it executable and run**

Run: `chmod +x scripts/test-za-overlays.sh && bash scripts/test-za-overlays.sh`
Expected: All 4 checks pass, exit 0

- [ ] **Step 3: Commit**

```bash
git add scripts/test-za-overlays.sh
git commit -m "feat(za): add combined ZA overlay test runner"
```

---

## Task 9: Scenario Evaluation Cases

**Files:**
- Create: all eval YAML files listed in the file map under `jurisdictions/za/evals/`

- [ ] **Step 1: Create eval directory structure**

```bash
mkdir -p jurisdictions/za/evals/employment-legal/{termination-review,hiring-review,worker-classification,wage-hour-qa,leave-tracker,policy-drafting,cold-start-interview}
```

- [ ] **Step 2: Write termination-review eval cases**

```yaml
# jurisdictions/za/evals/employment-legal/termination-review/case-01-misconduct-no-hearing.yaml
name: "Misconduct dismissal without hearing"
skill: termination-review
input: |
  We dismissed an employee for theft from the warehouse yesterday.
  He's been with us for 3 years, earns R180,000/year.
  We caught him on camera, confronted him, and told him he's fired.
  No hearing was held.

expected_flags:
  - "No hearing held"
  - "Earnings below BCEA threshold"

expected_statutes:
  - "LRA s188"
  - "Schedule 8"
  - "BCEA"

must_not_contain:
  - "FMLA"
  - "FLSA"
  - "at-will"
  - "EEOC"
  - "NLRB"
  - "WARN Act"

notes: |
  Classic procedural unfairness case. Despite clear misconduct (theft on camera),
  the lack of a hearing renders the dismissal procedurally unfair. The employee
  earns below the BCEA threshold, which means full BCEA protections apply and
  con-arb at the CCMA is available. Expected outcome: CCMA would likely find
  the dismissal procedurally unfair and award compensation (not reinstatement,
  given the theft).
```

```yaml
# jurisdictions/za/evals/employment-legal/termination-review/case-02-retrenchment-large-scale.yaml
name: "Large-scale retrenchment without facilitation"
skill: termination-review
input: |
  We're a manufacturing company with 250 employees. Due to a major client loss,
  we need to retrench 30 employees from the production floor.
  We've started individual meetings with affected employees to discuss severance.
  No formal s189 notice has been issued and no facilitator has been appointed.

expected_flags:
  - "Operational requirements without s189 process"

expected_statutes:
  - "LRA s189"
  - "LRA s189A"
  - "LRA s41(2)"

must_not_contain:
  - "WARN Act"
  - "Cal-WARN"
  - "at-will"
  - "FMLA"

notes: |
  This is a s189A large-scale retrenchment (250 employees, 30 affected — exceeds
  the schedule threshold of 20 for 200-300 employees). The employer has skipped
  the formal s189 notice, has not consulted with representatives, and has not
  requested CCMA facilitation. The 60-day minimum consultation period has not
  started. Individual meetings do not substitute for the statutory consultation process.
```

```yaml
# jurisdictions/za/evals/employment-legal/termination-review/case-03-auto-unfair-pregnancy.yaml
name: "Dismissal of pregnant employee"
skill: termination-review
input: |
  One of our sales managers (earning R400,000/year) told us she's pregnant last
  month. Her performance has been declining for 6 months and we've been
  documenting it. We want to proceed with a performance-based dismissal.
  We have a PIP from 4 months ago and two written warnings.

expected_flags:
  - "Automatically unfair ground"
  - "Discrimination / EEA-protected ground"

expected_statutes:
  - "LRA s187(1)"
  - "LRA s188"
  - "EEA"

must_not_contain:
  - "FMLA"
  - "FLSA"
  - "at-will"
  - "Title VII"
  - "PDA"

notes: |
  High-risk scenario. Even though there is documented poor performance (PIP + warnings),
  the timing — dismissal shortly after pregnancy announcement — creates strong
  inference of automatically unfair dismissal under s187(1)(e). The burden shifts
  to the employer to prove the reason was genuinely performance, not pregnancy.
  Compensation for auto-unfair dismissal is up to 24 months. The employee earns
  above the BCEA threshold, so the earnings flag does not fire.
```

```yaml
# jurisdictions/za/evals/employment-legal/termination-review/case-04-fixed-term-expectation.yaml
name: "Fixed-term contract non-renewal with reasonable expectation"
skill: termination-review
input: |
  We have a project manager on a 12-month fixed-term contract.
  This is her third consecutive renewal — she's been with us on
  rolling 12-month contracts for 3 years. The project is ending and
  we don't plan to renew. She earns R220,000/year.

expected_flags:
  - "Fixed-term contract — reasonable expectation"
  - "Earnings below BCEA threshold"

expected_statutes:
  - "LRA s186(1)(b)"
  - "BCEA"

must_not_contain:
  - "at-will"
  - "FMLA"
  - "FLSA"

notes: |
  Three consecutive renewals over 3 years creates a strong reasonable expectation
  of renewal under s186(1)(b). Non-renewal is deemed a dismissal. The employer
  must show a fair reason (operational requirements — project ending) and follow
  a fair procedure. Below BCEA threshold adds working-time protections and
  con-arb availability.
```

```yaml
# jurisdictions/za/evals/employment-legal/termination-review/case-05-below-threshold-misconduct.yaml
name: "Below-threshold employee — misconduct with hearing"
skill: termination-review
input: |
  An administrative assistant earning R150,000/year was found to have been
  falsifying timesheets over a period of 3 months. We held a full disciplinary
  hearing with proper notice, allowed a union representative, and the chairperson
  found the employee guilty and recommended dismissal. The employee has 5 years
  of service, no prior warnings.

expected_flags:
  - "Earnings below BCEA threshold"
  - "Comparator problem / inconsistent discipline"
  - "Thin documentation"

expected_statutes:
  - "LRA s188"
  - "Schedule 8"
  - "BCEA"

must_not_contain:
  - "FLSA"
  - "at-will"
  - "exempt"
  - "non-exempt"

notes: |
  Hearing was procedurally fair. However, the skill should flag: (1) below-threshold
  employee with full BCEA protections, (2) whether other employees have falsified
  timesheets and were not dismissed (comparator), and (3) whether 5 years with
  no prior warnings and dismissal for a first offence is proportionate — the
  Schedule 8 Code requires considering the employee's circumstances and length
  of service. The timesheet falsification over 3 months is serious (dishonesty),
  but the lack of prior warnings and long service should be noted.
```

- [ ] **Step 3: Write hiring-review eval cases**

```yaml
# jurisdictions/za/evals/employment-legal/hiring-review/case-01-restraint-of-trade.yaml
name: "Restraint of trade clause review"
skill: hiring-review
input: |
  Please review this clause in our standard employment contract for a senior
  software developer based in Johannesburg, earning R850,000/year:
  "The Employee shall not, for a period of 24 months after termination,
  directly or indirectly provide services to any competitor of the Company
  anywhere in the Republic of South Africa."

expected_flags: []

expected_statutes:
  - "Basson v Chilwan"
  - "Constitution s22"

must_not_contain:
  - "California"
  - "non-compete ban"
  - "state-by-state"
  - "FTC"

notes: |
  The restraint is likely unenforceable as drafted: 24-month duration is aggressive,
  national geographic scope is overbroad for a Johannesburg-based developer, and
  "any competitor" is vague. The skill should apply the Basson v Chilwan 4-factor
  test and recommend narrowing the scope, duration, and geographic area. Should
  reference s22 of the Constitution (right to choose a trade/occupation).
```

```yaml
# jurisdictions/za/evals/employment-legal/hiring-review/case-02-probation-clause.yaml
name: "Probation clause review"
skill: hiring-review
input: |
  Our standard contract says: "The Employee shall serve a probation period of
  12 months. During probation, the Company may terminate employment with
  1 week's notice without reason."

expected_flags: []

expected_statutes:
  - "LRA Schedule 8 Item 8"
  - "BCEA s37"

must_not_contain:
  - "at-will"
  - "FMLA"

notes: |
  The clause is problematic. While 12 months is long but potentially defensible
  for certain roles, "without reason" contradicts LRA Schedule 8 Item 8 which
  requires fair procedure and evaluation during probation. The skill should flag
  that probation does not remove fair dismissal requirements and recommend
  redrafting to include evaluation, counselling, and opportunity to improve.
```

```yaml
# jurisdictions/za/evals/employment-legal/hiring-review/case-03-ee-obligations.yaml
name: "EEA obligations at hire — designated employer"
skill: hiring-review
input: |
  We're a designated employer (120 employees, financial services). We're hiring
  a new Head of Compliance. We want to use a psychometric assessment as part
  of the selection process and we plan to do a medical examination including
  an HIV test. Is this permissible?

expected_flags: []

expected_statutes:
  - "EEA s7"
  - "EEA s8"

must_not_contain:
  - "ADA"
  - "Title VII"
  - "EEOC"

notes: |
  Psychometric testing is permissible but must be scientifically valid, reliable,
  fair, and not biased (EEA s8). HIV testing is prohibited except with Labour
  Court authorisation (EEA s7(2)) — the employer cannot simply include it.
  The general medical examination is only permissible if required by legislation
  or if justifiable given the inherent requirements of the job (EEA s7(1)).
  For a Head of Compliance, neither exception likely applies.
```

- [ ] **Step 4: Write worker-classification eval cases**

```yaml
# jurisdictions/za/evals/employment-legal/worker-classification/case-01-contractor-control.yaml
name: "Contractor vs employee — control test"
skill: worker-classification
input: |
  We want to engage a marketing consultant for 6 months. She'll work from our
  Cape Town office 3 days a week, use our laptop and software, attend our team
  meetings, and report to our CMO. She'll work exclusively for us during this
  period. She earns R180,000 for the 6-month engagement.

expected_flags: []

expected_statutes:
  - "BCEA s213"
  - "BCEA s200A"

must_not_contain:
  - "ABC test"
  - "IRS"
  - "1099"
  - "W-2"

notes: |
  Multiple s200A presumption factors are present: subject to control/direction,
  works at employer's premises, uses employer's equipment, works exclusively for
  one person. Earns below BCEA threshold (R180,000 for 6 months = R360,000/year
  annualised — actually above threshold). The dominant impression test also
  points to employment. The skill should flag that this arrangement would likely
  be found to be employment, not independent contracting.
```

```yaml
# jurisdictions/za/evals/employment-legal/worker-classification/case-02-deemed-employee.yaml
name: "Deemed employee — TES placement beyond 3 months"
skill: worker-classification
input: |
  We use a staffing agency to provide warehouse workers. Three of them have been
  with us for over a year now. They earn about R10,000/month each. The staffing
  agency handles their payroll and contracts. Can we continue this arrangement?

expected_flags: []

expected_statutes:
  - "LRA s198A"
  - "BCEA"

must_not_contain:
  - "temp agency"
  - "co-employment"
  - "joint employer"
  - "FLSA"

notes: |
  Workers placed by a TES for over 3 months and earning below the BCEA threshold
  (R10,000/month = R120,000/year, well below R254,371.67) are deemed employees
  of the client under s198A. The client is jointly and severally liable. These
  workers are entitled to the same conditions as directly employed warehouse
  workers. The skill should flag the deemed employment status and the obligation
  to provide equal conditions.
```

```yaml
# jurisdictions/za/evals/employment-legal/worker-classification/case-03-labour-broker.yaml
name: "Labour broker arrangement — above threshold"
skill: worker-classification
input: |
  We use a specialist IT consulting firm to provide a senior DevOps engineer.
  She's been embedded in our team for 8 months, earning R65,000/month through
  the consulting firm. She uses our systems and attends our standups but sets
  her own technical approach. Can we keep this arrangement?

expected_flags: []

expected_statutes:
  - "LRA s198A"
  - "BCEA s213"

must_not_contain:
  - "ABC test"
  - "1099"

notes: |
  R65,000/month = R780,000/year, above the BCEA threshold. The s198A deemed
  employment provision does NOT apply to employees earning above the threshold.
  However, the common law control test and BCEA s213 still apply — the skill
  should assess whether the dominant impression is employment or independent
  contracting. Key factors: uses employer systems (points to employee), sets own
  technical approach (points to IC), 8-month tenure (neutral). The TES/labour
  broker framework is less protective for above-threshold workers.
```

- [ ] **Step 5: Write remaining eval cases (wage-hour, leave, policy, cold-start)**

```yaml
# jurisdictions/za/evals/employment-legal/wage-hour-qa/case-01-overtime-below-threshold.yaml
name: "Overtime for below-threshold employee"
skill: wage-hour-qa
input: |
  One of our retail employees (earning R160,000/year) has been working 50 hours
  per week for the past month. Is this legal and what do we owe her?

expected_flags: []
expected_statutes:
  - "BCEA s9(1)"
  - "BCEA s10"
must_not_contain:
  - "FLSA"
  - "exempt"
  - "non-exempt"
  - "salary basis"
notes: |
  Below threshold, full BCEA working-time rules apply. 45 hours is the ordinary
  maximum; 5 hours overtime per week requires agreement and must be paid at 1.5x.
  Max overtime is 10 hours/week. The skill should calculate the overtime owed and
  flag whether an overtime agreement exists.
```

```yaml
# jurisdictions/za/evals/employment-legal/wage-hour-qa/case-02-sunday-work.yaml
name: "Sunday and public holiday work"
skill: wage-hour-qa
input: |
  We need our warehouse team to work on Youth Day (16 June, a public holiday)
  and the following Sunday. What are the pay requirements?

expected_flags: []
expected_statutes:
  - "BCEA s16"
  - "BCEA s18"
  - "Public Holidays Act"
must_not_contain:
  - "FLSA"
  - "time-and-a-half"
  - "federal holiday"
notes: |
  Public holiday: double pay (BCEA s18). Sunday for employees who don't ordinarily
  work Sundays: double pay (BCEA s16(1)). If they ordinarily work Sundays: 1.5x.
```

```yaml
# jurisdictions/za/evals/employment-legal/wage-hour-qa/case-03-night-work.yaml
name: "Night work provisions"
skill: wage-hour-qa
input: |
  We're setting up a night shift (22:00-06:00) for our call centre.
  What are the legal requirements?

expected_flags: []
expected_statutes:
  - "BCEA s17"
must_not_contain:
  - "FLSA"
  - "shift differential"
notes: |
  Night work (18:00-06:00) requires: agreement with employee, transport availability,
  and an allowance or reduced working hours. The skill should outline all three
  requirements and note that the employer may not require night work without agreement.
```

```yaml
# jurisdictions/za/evals/employment-legal/leave-tracker/case-01-annual-leave.yaml
name: "Annual leave entitlement calculation"
skill: leave-tracker
input: |
  An employee started on 15 March 2024. Today is 17 May 2026. She has taken
  12 days of annual leave. How much leave does she have remaining?

expected_flags: []
expected_statutes:
  - "BCEA s20"
must_not_contain:
  - "PTO"
  - "FMLA"
  - "accrual rate"
notes: |
  Two full leave cycles completed (March 2024-March 2025, March 2025-March 2026).
  21 consecutive days (15 working days) per cycle = 30 working days accrued.
  Minus 12 taken = 18 remaining. The skill should also note: employer must grant
  leave within 6 months after end of the cycle; current cycle (March 2026 onward)
  is accruing.
```

```yaml
# jurisdictions/za/evals/employment-legal/leave-tracker/case-02-sick-leave-cycle.yaml
name: "Sick leave cycle calculation"
skill: leave-tracker
input: |
  An employee started 1 January 2023. His 3-year sick leave cycle runs to
  31 December 2025. He has taken 25 days of sick leave so far. He's now
  asking for 10 more days for a planned surgery in March 2026.

expected_flags: []
expected_statutes:
  - "BCEA s22"
must_not_contain:
  - "FMLA"
  - "ADA"
  - "STD"
notes: |
  First cycle (2023-2025): 30 days total, 25 used, 5 remaining — but the cycle
  ends Dec 2025. The surgery in March 2026 falls in the new cycle (2026-2028)
  with a fresh 30 days. The skill should clarify that unused sick leave does
  not carry over, and the new cycle gives full entitlement.
```

```yaml
# jurisdictions/za/evals/employment-legal/leave-tracker/case-03-maternity-leave.yaml
name: "Maternity leave and UIF"
skill: leave-tracker
input: |
  An employee is expecting and wants to start maternity leave in 6 weeks.
  She earns R200,000/year. Does she get paid? How long can she take?

expected_flags: []
expected_statutes:
  - "BCEA s25"
  - "UIF"
must_not_contain:
  - "FMLA"
  - "short-term disability"
  - "PFL"
notes: |
  4 months minimum maternity leave. BCEA does not require employer to pay.
  UIF provides partial income replacement (up to 66% of earnings, capped at
  the UIF ceiling). The skill should check whether the employer tops up UIF
  (captured in the practice profile) and advise accordingly.
```

```yaml
# jurisdictions/za/evals/employment-legal/policy-drafting/case-01-disciplinary-code.yaml
name: "Draft disciplinary code"
skill: policy-drafting
input: |
  We need a disciplinary code for our company (80 employees, retail sector).
  We don't have one currently.

expected_flags: []
expected_statutes:
  - "LRA Schedule 8"
must_not_contain:
  - "state supplements"
  - "FMLA"
  - "at-will"
notes: |
  Draft must align with Schedule 8 Code of Good Practice. Should include:
  offence categories, progressive discipline, hearing procedure, sanction
  guidelines, appeal process. Retail sector — check for bargaining council
  coverage that may mandate a specific code format.
```

```yaml
# jurisdictions/za/evals/employment-legal/policy-drafting/case-02-grievance-procedure.yaml
name: "Draft grievance procedure"
skill: policy-drafting
input: |
  We need a formal grievance procedure. Currently employees just talk to
  their manager informally.

expected_flags: []
expected_statutes:
  - "LRA"
must_not_contain:
  - "EEOC"
  - "Title VII"
notes: |
  Should include: informal step, formal written grievance, management hearing,
  appeal, and external referral (CCMA/bargaining council) as final step.
  Reference the Code of Good Practice on Dismissal expectation that employers
  have a grievance mechanism.
```

```yaml
# jurisdictions/za/evals/employment-legal/policy-drafting/case-03-harassment-policy.yaml
name: "Sexual harassment policy per Code of Good Practice"
skill: policy-drafting
input: |
  Draft a sexual harassment policy compliant with the Code of Good Practice.

expected_flags: []
expected_statutes:
  - "EEA"
  - "Code of Good Practice on the Handling of Sexual Harassment"
must_not_contain:
  - "Title VII"
  - "EEOC"
  - "Title IX"
notes: |
  Must reference the EEA Code of Good Practice on Sexual Harassment. Should
  include: definition, prohibition, separate complaints procedure (not just
  the general disciplinary procedure), protection from victimisation,
  investigation process, and sanctions.
```

```yaml
# jurisdictions/za/evals/employment-legal/cold-start-interview/case-01-za-designated-employer.yaml
name: "Cold-start for ZA designated employer"
skill: cold-start-interview
input: |
  Company profile indicates: South Africa, 120 employees, financial services.

expected_questions:
  - "BCEA earnings threshold"
  - "bargaining council"
  - "designated employer"
  - "EE plan"
  - "CCMA"
  - "recognised unions"

must_not_ask:
  - "US states"
  - "which states"
  - "FMLA"
  - "state supplements"

notes: |
  Should ask all 10 SA-specific questions. Should NOT ask about US states,
  FMLA administrators, or state-specific rules. Should use the ZA practice
  profile template for output.
```

```yaml
# jurisdictions/za/evals/employment-legal/cold-start-interview/case-02-za-small-employer.yaml
name: "Cold-start for small non-designated employer"
skill: cold-start-interview
input: |
  Company profile indicates: South Africa, 25 employees, professional services.

expected_questions:
  - "BCEA earnings threshold"
  - "bargaining council"
  - "CCMA"

must_not_ask:
  - "US states"
  - "FMLA"
  - "EE plan"

notes: |
  Below 50 employees — not a designated employer. The interview should skip
  detailed EEA/BEE questions but still capture the statutory baseline
  (BCEA threshold, bargaining council coverage) and dispute resolution posture.
```

```yaml
# jurisdictions/za/evals/employment-legal/cold-start-interview/case-03-za-sectoral.yaml
name: "Cold-start for employer with sectoral determination"
skill: cold-start-interview
input: |
  Company profile indicates: South Africa, 40 employees, hospitality (hotel chain).

expected_questions:
  - "sectoral determination"
  - "SD 14"
  - "BCEA earnings threshold"
  - "CCMA"

must_not_ask:
  - "US states"
  - "FMLA"

notes: |
  Hospitality sector is covered by SD 14. The interview should identify this
  and capture the specific sectoral conditions that override BCEA defaults.
  Below 50 employees so not designated, but close to the threshold —
  could flag that designation is approaching.
```

- [ ] **Step 6: Commit all eval cases**

```bash
git add jurisdictions/za/evals/
git commit -m "feat(za): add 24 golden-path scenario evaluation cases"
```

---

## Task 10: Phase 2-3 Placeholder Directories

**Files:**
- Create: `jurisdictions/za/commercial-legal/.gitkeep`
- Create: `jurisdictions/za/privacy-legal/.gitkeep`

- [ ] **Step 1: Create placeholder directories**

```bash
mkdir -p jurisdictions/za/commercial-legal jurisdictions/za/privacy-legal
touch jurisdictions/za/commercial-legal/.gitkeep jurisdictions/za/privacy-legal/.gitkeep
```

- [ ] **Step 2: Commit**

```bash
git add jurisdictions/za/commercial-legal/.gitkeep jurisdictions/za/privacy-legal/.gitkeep
git commit -m "chore(za): add phase 2-3 placeholder directories"
```

---

## Task 11: Final Validation Run

**Files:** None new — this is a verification task

- [ ] **Step 1: Run the full validation suite**

Run: `bash scripts/test-za-overlays.sh`
Expected: All 4 checks pass, exit 0

- [ ] **Step 2: Verify file counts**

Run: `find jurisdictions/za -type f | wc -l`
Expected: At least 34 files (ARCHITECTURE.md + 4 statutes + router + practice profile template + 6 topics + 24 evals + 2 .gitkeeps)

Run: `find jurisdictions/za/evals -name "*.yaml" | wc -l`
Expected: 24 eval files

- [ ] **Step 3: Verify no US concepts leaked**

Run: `grep -rinE '(FMLA|FLSA|at.will employment|EEOC|NLRB)' jurisdictions/za/employment-legal/topics/ jurisdictions/za/statutes/`
Expected: No matches (exit 1)

- [ ] **Step 4: Verify the cold-start fork is in place**

Run: `grep -c "Jurisdiction check — South African overlay" employment-legal/skills/cold-start-interview/SKILL.md`
Expected: `1`

- [ ] **Step 5: Run existing repo validation to confirm nothing broken**

Run: `python3 -c "import json,glob; [json.load(open(f)) for f in glob.glob('**/*.json', recursive=True)]"`
Expected: No errors (all JSON in repo still valid)

Run: `python3 scripts/lint-tool-scope.py`
Expected: All cookbooks pass (we didn't touch them)

---

## Self-Review Checklist

**Spec coverage:**
- [x] Statute data layer (BCEA, LRA, EEA, sectoral) — Tasks 1-2
- [x] Topic overlays (6 files: dismissal, hiring, classification, leave, policy, investigation) — Tasks 3-4
- [x] Skill router — Task 5
- [x] ZA practice profile template — Task 6
- [x] Cold-start interview fork — Task 7
- [x] Structural validation scripts (3 validators + runner) — Tasks 1, 5, 6, 8
- [x] Scenario evaluation suite (24 cases across 7 skills) — Task 9
- [x] Phase 2-3 placeholders — Task 10
- [x] No US concepts in ZA files — verified in Tasks 3, 4, 11
- [x] 11 SA high-risk termination flags — Task 3 (dismissal.md)
- [x] SA work-product header with privilege caveat — Task 6
- [x] Temporal fields on all statute entries — Tasks 1-2
- [x] One upstream file modification only (cold-start) — Task 7
- [x] MCP requirements doc — already written in prior step (project/mcp-requirements-za.md)

**Placeholder scan:** No TBDs, TODOs, or "implement later" found.

**Type/name consistency:** Statute file names (bcea, lra, eea, sectoral-determinations) match router references. Topic file names match router references. Skill names match `employment-legal/skills/` directory names.
