---
ecm_schema: "1.0"
id: {measure-slug}
name: "{measure-title}"
version: "1.0"
category: "{category}"
author: "Ricardo Filho"
license: "CC-BY-4.0"
dateCreated: {YYYY-MM-DD}
dateModified: {YYYY-MM-DD}
tags: [ecm, energy-optimization]
sources: ["Storm ECM research", "{primary-source-label}"]
summary: "{one-sentence verified or caveated summary}"
type: article

applicability:
  property_types: [{property-types}]
  climates: [{climates}]
  notes: "{site-fit notes and key prerequisites}"

impacts:
  - carrier: {carrier}
    operation: reduce
    mode: percent
    value_low: {number-or-null}
    value_typical: {number-or-null}
    value_high: {number-or-null}
    note: "{screening-grade impact note and mechanism}"

cost:
  capex_per_m2_low: null
  capex_per_m2_typical: null
  capex_per_m2_high: null
  capex_currency: GBP
  payback_years_low: {number-or-null}
  payback_years_typical: {number-or-null}
  payback_years_high: {number-or-null}
  notes: "{screening-grade cost and payback caveat}"

interactions:
  overlaps_with: []
  prerequisites: []
  excludes: []
---

# ECM: {measure-title}

## Summary
{Concise description of the measure, what changes, why it saves energy, and the GO or CONDITIONAL GO caveat.}

## Estimated Savings
- **Screening-grade range**: {range-or-caveat}
- **End-use affected**: {end-use}
- **Confidence**: {high|medium-high|medium|low} based on verified evidence and site data availability.

## Basis / References
- {Verified standard, guide, paper, utility guidance, or authoritative source}
- {Second source}
- {Third source}

## Assumptions
{List the key site and operating assumptions. Do not invent missing data; say what remains unknown.}

## Interaction Notes
{Describe overlaps, non-additive savings, prerequisites, and conflicts with related ECMs.}

## Implementation Essentials
- {Action 1}
- {Action 2}
- {Action 3}

## Risks / Constraints
- {Risk 1 and mitigation}
- {Risk 2 and mitigation}
- {Risk 3 and mitigation}

## KPIs
- {KPI 1}
- {KPI 2}
- {KPI 3}

## M&V Plan
{State the recommended IPMVP-style option or screening approach, baseline period, post-implementation period, normalization variables, and acceptance criteria.}

## Costs & Payback (Indicative)
- Capex: {known range or "site-specific; not estimated without quote"}
- Opex: {maintenance, calibration, monitoring, or tuning}
- Simple payback: {known range or caveat}

## Templates / Reuse
- {Checklist or worksheet}
- {Trend review template}
- {Commissioning checklist}

## Notes
- {Important caveat}
- {Claim safety note}
- {Related ECM wiki link if useful}
