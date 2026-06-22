---
name: esg-materiality-brief
description: Turn user-provided business and stakeholder evidence into a traceable ESG materiality briefing with explicit uncertainty.
---

# ESG materiality brief

Prepare a bounded environmental, social, and governance (ESG) materiality briefing for a named decision. The briefing organizes supplied evidence; it does not determine regulatory compliance or provide assurance.

## Inputs

Ask the user for:

- the decision, audience, reporting period, and organisational boundary;
- business context, stakeholder notes, risk records, and other source material;
- any materiality definition, scoring scale, or threshold the organisation has already adopted;
- required citations, output length, and known evidence gaps.

If the user has not supplied a scoring method, produce an evidence map without inventing scores or thresholds.

## Workflow

1. Confirm the decision scope and label every supplied source with a short source ID.
2. Extract candidate ESG topics from the supplied material. Keep the user's wording where it carries a specific meaning.
3. For each topic, record the supporting source IDs, affected stakeholders, connection to the stated decision, time horizon, and uncertainty.
4. Apply only the materiality definition and scoring rules the user supplied. When no rules exist, group topics by strength of evidence instead of ranking them.
5. Separate direct evidence, stakeholder interpretation, assumptions, and open questions. Do not fill gaps with generic ESG topics.
6. Check that every conclusion points back to at least one supplied source and that limitations remain visible.

## Guardrails

- Do not claim that a topic set is complete, compliant, certified, audited, or assured.
- Do not invent stakeholder views, impacts, financial effects, thresholds, evidence, or regulatory conclusions.
- Treat external standards as context only when the user supplies or approves them.
- State when evidence is thin, contradictory, dated, or outside the agreed boundary.
- Present the result as working guidance, not legal, financial, compliance, certification, audit, or assurance advice.

## Output

Return:

1. a short decision context and boundary;
2. a source register;
3. a topic evidence table with traceable source IDs;
4. any user-defined assessment or an unranked evidence grouping;
5. key uncertainties, exclusions, and questions for follow-up;
6. a final traceability check confirming that each substantive statement is sourced or marked as an assumption.
