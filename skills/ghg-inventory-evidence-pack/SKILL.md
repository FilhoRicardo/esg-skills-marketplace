---
name: ghg-inventory-evidence-pack
description: Organize user-provided greenhouse-gas inventory data and factors into a traceable working evidence pack for review.
---

# Greenhouse-gas inventory evidence pack

Organize supplied greenhouse-gas (GHG) activity data, emission factors, boundaries, calculations, and source notes into a reviewable working evidence pack. The pack supports internal review; it is not an audit or assurance conclusion.

## Inputs

Ask the user for:

- the reporting period, organisational boundary, operational boundary, and intended audience;
- activity data with quantities, units, sites or entities, dates, owners, and source references;
- emission factors, factor units, factor sources, versions, and any supplied global-warming-potential values;
- the calculation method, approved unit conversions, exclusions, estimates, and prior-period comparison data;
- the user's preferred output format and review checklist.

## Workflow

1. Create a source register and assign a stable source ID to every supplied dataset, factor, note, and approval.
2. Build an activity-data table that preserves the original value and unit alongside any user-approved normalized value.
3. Build a separate factor register with factor value, numerator and denominator units, gas coverage, geography, year, version, and source ID when supplied.
4. Pair activity data with factors only when units and boundaries are compatible. Flag unmatched rows instead of selecting or inventing a factor.
5. Show each calculation as activity quantity multiplied by the supplied factor, followed by any supplied conversion or global-warming-potential step. Retain units through every step.
6. Reconcile calculated rows to source totals where possible. Record duplicates, missing periods, unmatched entities, estimates, exclusions, and unexplained differences.
7. Package the tables, calculation notes, assumptions, evidence links, and review questions in a consistent order.

## Guardrails

- Do not choose emission factors, boundaries, consolidation methods, or global-warming-potential values without user-supplied authority.
- Do not claim the inventory covers every relevant source or any particular emissions scope unless the evidence demonstrates that boundary.
- Do not conceal estimates, exclusions, missing units, factor mismatches, or unavailable source records.
- Preserve supplied precision and explain any user-approved rounding separately.
- Present the pack as working evidence, not legal, financial, compliance, certification, audit, verification, or assurance advice.

## Output

Return:

1. boundary and method notes;
2. a source register;
3. activity-data and emission-factor registers;
4. a calculation ledger with units and source IDs;
5. reconciliation results and exception flags;
6. assumptions, estimates, exclusions, and unresolved review questions;
7. a traceability summary showing whether each calculated row has activity and factor evidence.
