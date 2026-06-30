---
name: storm-ecm
description: Screens energy conservation measure ideas with five evidence lenses, then produces verified HTML and Markdown notes only for credible candidates.
---

# Storm ECM

## What this does

Evaluate one Energy Conservation Measure idea through five energy-management lenses, decide whether it is a credible screening candidate, and only then create verified ECM outputs: an HTML report and an Obsidian-style Markdown ECM note. Treat the output as a screening-grade decision aid, not investment approval.

Use current, real sources. Follow the thread or project browsing rules. If browsing is unavailable, say that verification cannot be completed and do not present unverified figures as facts.

## Phase 0: Capture the ECM idea

1. If the user's prompt contains the ECM idea, use it. Otherwise ask for the idea.
2. State the interpreted measure in one line.
3. Identify or infer the site context: building or process type, main energy source, affected system, operating pattern, climate or location, and known constraints.
4. Ask at most three clarifying questions only when missing context could flip the go/no-go decision. If the user has not provided enough context but the idea is still screenable, proceed with explicit assumptions.
5. Derive a kebab-case `measure-slug` for filenames.
6. Tell the user the ECM review is running: five energy lenses, go/no-go gate, then report if it passes.

## Phase 1: Five ECM lenses

Run the five lenses concurrently with agents if available. If agents are unavailable, run the lenses inline one by one. Each lens must use real web research where needed and cite source URLs. Keep each lens under 350 words.

Use the same ECM framing for all five prompts:

`ECM IDEA: {ECM_IDEA}. SITE CONTEXT: {SITE_CONTEXT}. ASSUMPTIONS: {ASSUMPTIONS}.`

### 1. The Building Operator

Prompt:

`You are THE BUILDING OPERATOR reviewing this ECM: {FRAMING}. You care about real operation, occupant complaints, maintenance access, schedules, overrides, alarms, and what breaks after consultants leave. Research practical case studies, operator guidance, O&M requirements, and common failure modes. Return exactly: 1) CORE POSITION in 2 sentences. 2) PRACTICAL EVIDENCE, 3-5 bullets with a source URL each. 3) OPERATOR REALITY CHECK: the one condition that determines whether this will survive day-to-day operation. 4) SCORE 1-5 for operational practicality.`

### 2. The Energy Engineer and M&V Analyst

Prompt:

`You are THE ENERGY ENGINEER AND M&V ANALYST reviewing this ECM: {FRAMING}. You care about the physics of the saving, baseline definition, interactive effects, persistence, and whether the savings can be measured under IPMVP-style thinking. Research engineering guidance, measured case studies, standards, and credible benchmarks. Return exactly: 1) CORE POSITION in 2 sentences. 2) ENERGY EVIDENCE, 3-5 bullets with quantified savings ranges or conditions and source URLs. 3) M&V TEST: how to prove or disprove the saving. 4) SCORE 1-5 for technical energy credibility.`

### 3. The Controls and Commissioning Specialist

Prompt:

`You are THE CONTROLS AND COMMISSIONING SPECIALIST reviewing this ECM: {FRAMING}. You care about BMS/controls sequences, sensor quality, commissioning effort, integration, trend data, lockouts, setpoints, overrides, and handover. Research controls guidance, commissioning resources, and known pitfalls. Return exactly: 1) CORE POSITION in 2 sentences. 2) IMPLEMENTATION EVIDENCE, 3-5 bullets with source URLs. 3) COMMISSIONING MUST-HAVE: the acceptance test or trend that must be in place. 4) SCORE 1-5 for implementation feasibility.`

### 4. The Finance and Commercial Reviewer

Prompt:

`You are THE FINANCE AND COMMERCIAL REVIEWER reviewing this ECM: {FRAMING}. You care about capex, opex, avoided cost, maintenance impact, incentives, payback, disruption cost, procurement risk, and whether the business case can survive conservative assumptions. Research cost ranges, utility or government guidance, incentives, and project examples. Return exactly: 1) CORE POSITION in 2 sentences. 2) COMMERCIAL EVIDENCE, 3-5 bullets with real figures where possible and source URLs. 3) BUSINESS-CASE KILLER: the assumption most likely to make this uneconomic. 4) SCORE 1-5 for financial viability.`

### 5. The Risk, Comfort, and Compliance Reviewer

Prompt:

`You are THE RISK, COMFORT, AND COMPLIANCE REVIEWER reviewing this ECM: {FRAMING}. You care about health and safety, comfort, IAQ, process quality, statutory compliance, warranties, resilience, carbon-accounting claims, and unintended consequences. Research standards, guidance, regulations, and documented risks. Return exactly: 1) CORE POSITION in 2 sentences. 2) RISK EVIDENCE, 3-5 bullets with source URLs. 3) RED LINE: the condition that would make this a no-go. 4) SCORE 1-5 for risk acceptability, where 5 means low/manageable risk.`

After all five lenses return, summarize in chat in 2-3 lines: convergence, sharpest disagreement, and whether the idea is headed toward GO, CONDITIONAL GO, or NO-GO.

## Phase 2: Go/no-go gate

Work from the five briefs and the user's context. Do not create HTML or Markdown outputs until this gate passes.

Score six dimensions from 0-5:

- Energy mechanism: clear physical saving tied to a real load or process.
- Technical feasibility: compatible with the stated site, equipment, and operating pattern.
- Operational practicality: maintainable by the site team without constant workarounds.
- Financial viability: likely positive payback or strategic value under conservative assumptions.
- M&V credibility: baseline, boundary, variables, and post-install proof are realistic.
- Risk acceptability: comfort, safety, compliance, IAQ, resilience, and process risks are manageable.

Decision rules:

- **GO**: total score is 23 or higher, no dimension below 3, and no red-line risk.
- **CONDITIONAL GO**: total score is 18-22, no red-line risk, and the weak dimensions have clear mitigation or data requests.
- **NO-GO**: any red-line risk, total score below 18, any critical dimension scored 0-1, or the claimed saving depends on unrealistic behavior, broken comfort, code violations, or unverifiable assumptions.

If the decision is NO-GO, stop. Tell the user plainly that this is not a good ECM idea as stated. Include:

- Decision: NO-GO.
- The 3-5 decisive reasons.
- What evidence or redesign would be needed to reconsider it.
- Any safer or simpler alternative ECM worth considering.

Do not write HTML or Markdown outputs for NO-GO ideas.

## Phase 3: Build the ECM outputs for GO or CONDITIONAL GO

Read `assets/report-template.txt` in this skill folder. Use it as the visual shell and keep the CSS style intact. Rewrite labels and content so the final report is clearly an ECM report, not a generic Storm Research report.

Write the report to:

`storm-ecm-reports/{measure-slug}-ecm-report.html`

Create the folder if needed.

The report must include:

1. **Decision banner**: GO or CONDITIONAL GO, screening score, and the main reason.
2. **Measure summary**: what changes, affected systems, assumptions, and site fit.
3. **Energy mechanism**: why energy should reduce, what can offset savings, and expected savings range if supportable.
4. **Five lens findings**: operator, energy/M&V, controls/commissioning, finance, and risk/compliance findings ranked by reliability.
5. **Business case**: capex/opex ranges where available, avoided-cost logic, incentives if relevant, and payback sensitivity.
6. **Implementation plan**: prerequisites, sequence, commissioning checks, handover requirements, and persistence controls.
7. **M&V plan**: baseline, boundary, independent variables, metering/trend data, normalization, and acceptance criteria.
8. **Risks and mitigations**: comfort, safety, compliance, IAQ, process, cyber/controls, operational, and rebound risks.
9. **Claim safety guide**: what is safe to assert, what needs caveats, and what to avoid claiming.
10. **References**: every source used, each tagged Confirmed, Partially confirmed, Unverified, or Demoted.

Also read `assets/ecm-note-template.md` and create a companion Markdown ECM note for GO or CONDITIONAL GO measures.

Default Markdown output:

`storm-ecm-reports/{measure-slug}.md`

If the user explicitly asks to add the note to an Obsidian vault or provides a destination such as `/Users/ricardofilho/Documents/2ndBrain/3 - Areas/ecms`, write it there instead. Before writing into a vault, verify the destination folder exists and do not overwrite an existing file; add a collision suffix such as `-2` if needed.

The Markdown note must follow the user's ECM library style:

1. YAML frontmatter with `ecm_schema: "1.0"`, `id`, `name`, `version`, `category`, `author`, `license`, `dateCreated`, `dateModified`, `tags`, `sources`, `summary`, `type`, `applicability`, `impacts`, `cost`, and `interactions`.
2. Body sections in this order: `# ECM: ...`, `## Summary`, `## Estimated Savings`, `## Basis / References`, `## Assumptions`, `## Interaction Notes`, `## Implementation Essentials`, `## Risks / Constraints`, `## KPIs`, `## M&V Plan`, `## Costs & Payback (Indicative)`, `## Templates / Reuse`, and `## Notes`.
3. Obsidian-compatible wiki links where useful, especially for related ECMs. Keep the note useful in plain Markdown; do not rely on Dataview or community plugin syntax.
4. Screening-grade ranges only. Use `null` in frontmatter for unknown numeric cost fields. Do not invent capex, savings, tariffs, property types, climates, or payback values.
5. Include only verified or clearly caveated claims. If a source is weak or demoted in the HTML report, either omit it from the note's headline claims or mark it as indicative in the body.

## Phase 4: Verification and correction

Before delivering outputs, verify all material claims.

1. Self-review the report:
   - Check whether one lens dominated unfairly.
   - Identify the weakest assumption.
   - Downgrade the decision from GO to CONDITIONAL GO if any important evidence is weaker than expected.
   - Convert to NO-GO and do not deliver either output if verification reveals a red-line blocker.
2. Verify citation clusters against primary or authoritative sources:
   - Prefer standards, utility or government guidance, manufacturer technical docs, peer-reviewed studies, measured case studies, and official incentive pages.
   - Treat vendor-only savings claims, single commissioned surveys, and uncited benchmark claims as weak unless independently supported.
3. Apply corrections:
   - Fix wrong figures, titles, dates, standards, and source attributions.
   - Demote unsupported savings ranges or payback claims.
   - Mark unverified claims clearly or remove them.
   - Fill the report's verification banner honestly.

## Output

For GO or CONDITIONAL GO:

1. Open the final HTML report with the platform default opener if possible.
2. Reply with the HTML report path, Markdown note path, decision, score, verification tally, top implementation condition, top risk, and claim safety summary.

For NO-GO:

1. Do not create HTML or Markdown outputs.
2. Reply with the concise no-go explanation and the most promising redesign or alternative.

## Guardrails

- Do not sell the ECM. Screen it.
- Do not invent site data, tariffs, run hours, costs, savings, or incentives.
- Do not treat benchmark savings as guaranteed savings.
- Do not ignore interactive effects such as heating/cooling penalties, ventilation, humidity, process quality, or occupant behavior.
- Do not recommend measures that compromise safety, statutory compliance, indoor air quality, resilience, or required process conditions.
- Use the phrase "screening-grade" for estimates unless the user provides measured baseline data and site-specific pricing.
- If the user asks for investment-grade analysis, state what extra data is required before producing investment-grade conclusions.
