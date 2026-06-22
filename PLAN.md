# Plan: Repair The Marketplace UX And Redeploy

## Goal

Finish the RF-100 public experience by replacing the broken fixed-height single-page composition with a calm, responsive Aster catalogue and a dedicated submission page, while leaving the reviewed-download and GitHub intake pipeline unchanged. Publish the verified redesign to the existing permanent here.now URL.

## Acceptance Criteria

- Work remains in `/Users/ricardofilho/Documents/Projects/active/esg-skills-marketplace`, on GitHub repository `FilhoRicardo/esg-skills-marketplace`, under Linear project `ESG Skills Marketplace` and implementation issue RF-100.
- The user selects one of three Aster-based visual directions generated from the live-site screenshots before implementation begins.
- The homepage has one primary job: help visitors understand and download reviewed environmental, social, and governance (ESG) skills.
- The homepage uses a short hero with one primary `Browse skills` action and a secondary `Submit a skill` link.
- Every approved skill exposes an immediately visible `Download .zip` action at desktop, tablet, and mobile widths.
- Submission moves to a dedicated `submit.html` page with the existing two-file intake, browser validation, preview, optional public attribution, attestations, and hidden proxy dispatch intact.
- User-facing copy describes the job and review boundary without exposing implementation terms such as repository scaffolding, approved slugs, workflow dispatch, or merge to `main`.
- The Aster system remains authoritative: Schibsted Grotesk, JetBrains Mono for data/labels, greyscale plus forest green, restrained glass surfaces, and no decorative new palette or assets.
- The public pages use normal document scrolling. No section receives a fixed/equal height that can clip content, no page-level `overflow: hidden` blocks content, and the footer remains in document flow.
- At 375×812, 768×1024, 1280×720, and 1440px wide:
  - no content overlaps or horizontal scrolling;
  - all visible controls are at least 44px high where practical, with usable checkbox hit areas;
  - every download link and form control passes browser hit testing;
  - the full submission form and preview are reachable through normal scrolling.
- The live site loads without console errors, downloads the reviewed zip artefacts, parses representative submission files, and shows honest local/live submission states.
- The existing proxy route, GitHub intake workflow, trust checks, review boundary, and main-branch deploy workflow are not broadened or bypassed.
- The verified branch snapshot is published to `https://royal-bugle-xgg7.here.now/` for UX testing, then browser-checked live.

## Approach

1. Generate three visual directions from the current desktop/mobile screenshots and the Aster rules. Vary hierarchy and catalogue structure, not the brand system or product scope. The user's selection becomes the visual target.
2. Replace `site/index.html` with a catalogue-focused page:
   - compact header and navigation;
   - concise, card-light hero;
   - reviewed skills rendered as self-contained rows/cards with persistent download actions;
   - short trust and professional-advice boundary copy;
   - normal footer flow.
3. Add `site/submit.html` for the existing intake flow. Preserve all current fields, validation, preview, and submission feedback, but present them as one clear task with styled 44px+ controls and plain-language guidance.
4. Split the current page script by responsibility only if needed for clarity: catalogue loading remains on the homepage, while submission logic runs only on the submission page. Do not change payload shape, endpoint, or validation rules.
5. Rewrite `site/styles.css` around content-sized sections and a small responsive scale. Reuse `site/aster-tokens.css`; reduce nested glass panels and use spacing, typography, and dividers for hierarchy.
6. Add the smallest useful static-page regression coverage for page separation and required asset/form hooks, then run all existing repository checks.
7. Serve locally and verify the selected visual target and all primary interactions with gstack `/browse`, including responsive screenshots, scroll reachability, touch-target measurements, hit testing, console errors, zip download, and form preview.
8. Run the pinned NVIDIA SkillSpector scan without executing skill content and refresh Graphify because meaningful frontend structure changed.
9. Commit and push the redesign to the existing RF-100 branch/PR, publish the verified `site/` directory to the permanent here.now slug, and recheck the live desktop/mobile flows.

## Key Decisions And Tradeoffs

- Aster's `fit-to-viewport` guidance is intentionally not used for this public catalogue. It suits app workspaces with bounded inner panes; applying it to variable public content caused the current clipping. Normal document scrolling is the safer, more familiar pattern.
- Submission becomes a separate page rather than a modal or collapsed homepage section. This gives catalogue visitors a focused first screen and gives contributors enough room for validation, preview, errors, and mobile use.
- The redesign changes information architecture and presentation, not the intake architecture. Keeping the proxy and GitHub workflow unchanged narrows risk and makes the visual repair independently verifiable.
- The catalogue stays simple with two skills. No search, filters, ratings, versioning UI, recommendations, or invented metadata are added.
- Visual options vary the homepage hierarchy only. The selected system will extend to the submission page without inventing a second style.
- Aster glass is reserved for a few meaningful surfaces. Skill rows/cards remain self-contained because each represents a downloadable object; nested decorative cards are removed.

## Risks And Unknowns

- Image-generated text may be imperfect. The selected mockup is a composition and hierarchy target; exact production copy remains the reviewed text in this plan.
- Splitting the submission page can break DOM assumptions in the current single script. Verification must prove both pages load without null-reference console errors and preserve the exact dispatch payload.
- Browser file inputs differ by operating system. The implementation must retain an accessible native input while presenting a consistent large picker state.
- The live branch snapshot will be ahead of `main` until PR #6 is reviewed and merged. The deployment is explicitly for UX testing; GitHub remains the source of truth.
- here.now publication can succeed while a stale asset remains cached. Live verification will use cache-busting/reload and check the rendered heading, page links, and submission preview.

## Out Of Scope

- Changes to skill validation, intake limits, proxy authentication, GitHub permissions, trust workflows, or publication policy.
- A real public submission during UX verification; browser parsing and UI states are tested without creating a noise PR.
- Accounts, submission tracking, analytics, search, filters, ratings, payments, or additional skills.
- New illustration, photography, icon library, animation system, or brand identity.
- Merging PR #6 into `main`; the user asked for a UX-test deployment of the branch snapshot.

## Verification

- `python3 scripts/build_catalog.py`
- `python3 scripts/build_catalog.py --check`
- `python3 scripts/validate_skills.py --all`
- `python3 -m unittest discover -s tests`
- the pinned NVIDIA SkillSpector command used by the repository trust workflow, without executing contributed content
- Graphify refresh using the existing authenticated `claude-cli` backend and ignored-output policy
- local gstack `/browse` verification:
  - homepage and submission page return successfully;
  - no console errors or failed static asset requests;
  - reviewed bundle count and both `Download .zip` links are visible and clickable;
  - a downloaded zip contains the reviewed bundle files;
  - representative `SKILL.md` and `marketplace.json` files populate the preview;
  - all form fields and confirmations remain reachable at mobile width;
  - 375×812, 768×1024, 1280×720, and 1440px layouts have no overlap or horizontal scroll;
  - interactive elements pass hit testing and target-size checks.
- live here.now verification repeats the homepage, download-link, dedicated submission-page, responsive, console, and preview checks without queueing a real submission.

## GitHub, Linear, And Memory Impact

- GitHub: update the existing `codex/rf-100-site-native-intake` branch and draft PR #6 with the verified frontend repair. Existing trust checks must remain green.
- Linear: RF-100 remains the active source-of-truth issue; no new issue is needed because this repairs the frontend acceptance quality of the same implementation.
- Project memory: after live publication, add one durable sentence recording that RF-100's public catalogue was redesigned into separate catalogue and submission pages and browser-verified at the permanent slug.
