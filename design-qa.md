# Design QA: Calm Ledger frontend repair

- Source visual truth: `artifacts/design/calm-ledger-reference.png`
- Implementation screenshot: `artifacts/design/calm-ledger-implementation.png`
- Combined comparison: `artifacts/design/calm-ledger-comparison.png`
- Viewport: 1536 × 1024
- State: homepage with two reviewed skills loaded
- Mobile evidence: `artifacts/design/calm-ledger-home-mobile.png`
- Submission evidence: `artifacts/design/calm-ledger-submit-mobile.png`

## Full-view comparison evidence

The combined comparison uses the selected Image Gen target and the local homepage capture at the same desktop dimensions. The implementation preserves the target's composition: compact brand/navigation, large left-aligned headline, factual trust rail, catalogue-led second section, numbered skill rows, mono metadata, and persistent green download actions.

The production page intentionally keeps Aster's rounded-square brand mark instead of the mockup's uncontained asterisk. It also uses the generated catalogue descriptions as the content source of truth. Both differences preserve the selected hierarchy without changing the product.

## Focused region comparison evidence

A separate crop was not needed. The page has no photography, illustration, or third-party iconography, and the combined 1600px comparison keeps the typography, trust rail, catalogue rows, badges, and actions readable. Original-resolution source and implementation images were also inspected before this report.

## Required fidelity surfaces

- Fonts and typography: Schibsted Grotesk and JetBrains Mono match Aster and the selected target. Heading weight, line height, tracking, and two-line wrap match the target hierarchy. Body copy remains at 16px or above on mobile.
- Spacing and layout rhythm: the two-column hero, trust rail, catalogue columns, row dividers, and action alignment match the target. The page uses normal document scrolling, and no fixed-height section or clipped overflow remains.
- Colors and visual tokens: the implementation uses the existing Aster greyscale, forest green, tinted background, borders, gradient button, and restrained glass surface. No new palette was introduced.
- Image quality and asset fidelity: the selected design contains no raster imagery. The existing Aster brand mark is retained as the project's authoritative identity; no placeholder imagery, inline SVG, or CSS illustration was added.
- Copy and content: homepage copy follows the approved brief. Dynamic skill titles, descriptions, and categories come directly from `catalog.json`. Internal GitHub and repository terminology is absent from the public homepage.
- Interactions and accessibility: visible links and buttons are at least 44px high, focus-visible styles remain, download links are persistent, the document has no horizontal overflow, and reduced-motion preferences are respected.

## Findings

No actionable P0, P1, or P2 mismatches remain.

Acceptable differences:

- The target's plain asterisk is implemented as the established Aster rounded-square mark.
- The catalogue uses one restrained glass surface to stay consistent with the project design system.
- The professional-advice boundary and footer follow the catalogue in normal document flow instead of being forced into the initial viewport.

## Patches made since the first comparison

- Removed explanatory copy from the trust rail to match the selected compact target.
- Reduced hero padding and catalogue row height so both download actions fit in the desktop first viewport.
- Changed the live count from “reviewed bundles” to the target's simpler “skills.”
- Increased the brand link hit area to 44px.

## Implementation checklist

- [x] Selected Calm Ledger composition implemented.
- [x] Catalogue and submission are separate pages.
- [x] Both reviewed download actions remain visible and functional.
- [x] Mobile, tablet, and desktop layouts use normal scrolling without overlap.
- [x] Submission files parse and populate the preview without console errors.
- [x] Existing intake endpoint and payload remain unchanged.

## Follow-up polish

No blocking polish remains for this release.

final result: passed
