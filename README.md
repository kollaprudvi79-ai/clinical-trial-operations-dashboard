# Clinical Trial Operations Dashboard (Power BI)

Portfolio-grade clinical trial operations dashboard built in **Power BI Desktop**, driven by 100% synthetic trial data — no real patient information.

**📖 Full click-by-click build guide:** https://kollaprudvi79-ai.github.io/clinical-trial-operations-dashboard/
**▶ Live interactive dashboard (synthetic v2, in-browser):** https://kollaprudvi79-ai.github.io/clinical-trial-operations-dashboard/live.html
**🔴 REAL live registry dashboard (ClinicalTrials.gov, auto-refresh ~3h):** https://kollaprudvi79-ai.github.io/clinical-trial-operations-dashboard/live-clinical.html
**📊 Tracker this complements:** [Career Radar](https://kollaprudvi79-ai.github.io/company-career-job-tracker/)

## What it shows

Five report pages — **Study Overview, Site Performance, Visit & Form Completion, Query Management, Safety & Deviations** — tracking enrollment vs target, screen failure rate, EDC query workload and aging, visit/form completion, adverse events (AEs/SAEs), and protocol deviations, with conditional formatting that flags high-risk sites, overdue visits, old open queries, missing eCRFs, major deviations, and SAEs.

## Model (star schema)

```
            Sites ──< Subjects >── Visits
                        ├── Forms
                        ├── Queries
                        ├── AdverseEvents
                        └── Deviations
            Calendar ── Subjects (ScreenDate / RandomizationDate)
```

## Headline numbers (validation set in the guide)

| Measure | Value |
|---|---|
| Total / Randomized subjects | 549 / 421 |
| Screen failure rate | 20.6% |
| Enrollment achievement | 87.7% of 480 |
| Open queries · avg age | 730 · ≈61 days |
| Form completion | 83.8% (13,615 of 16,254) |
| AEs / SAEs | 316 / 26 |
| Open major deviations | 22 |

## Contents

- `docs/` — the complete build guide (imports, relationships, exact DAX, page-by-page visuals, conditional formatting, theme, validation checklist)
- `dax/measures.dax` — every measure + calendar table, copy-paste ready
- `data/` — seven synthetic CSVs (Sites, Subjects, Visits, Forms, Queries, AdverseEvents, Deviations)
- `scripts/generate_synthetic_data.py` — seeded generator that reproduces the CSVs

## Build it

1. Download the CSVs from `data/` (or regenerate: `python3 scripts/generate_synthetic_data.py`).
2. Follow the guide: import → star schema → Calendar → measures → five pages → conditional formatting → validation.
