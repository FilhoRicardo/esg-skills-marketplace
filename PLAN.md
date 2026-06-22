# Plan: Move Category Assignment Into Maintainer Review

## Goal

Let public contributors upload `SKILL.md` and enter a public title without choosing a category. A maintainer assigns the category after reading the submitted skill.

## Acceptance Criteria

- Work remains in the linked GitHub repository, Linear project, and RF-100 issue.
- `submit.html` has no contributor-facing category control or category requirement copy.
- A valid `SKILL.md` and public title are sufficient to populate the preview and enable submission after the existing confirmations.
- The preview says the category will be assigned during review.
- The browser keeps the existing dispatch endpoint and `marketplace_json` input, but generates title-only intake metadata.
- Site intake accepts and writes title-only marketplace metadata for a draft submission.
- The site-submission workflow opens the draft pull request without attempting to build publishable catalogue artefacts.
- The draft pull-request body tells maintainers to add an allowed category and run `python3 scripts/build_catalog.py`.
- The normal approved-skill validator remains unchanged and strict, so title-only metadata cannot pass policy checks or merge until a category is assigned.
- The Aster/Calm Ledger layout remains responsive and otherwise unchanged.
- The verified branch snapshot is republished to the permanent here.now site.

## Approach

1. Remove the category field, related DOM handling, generated public config, and contributor-facing copy.
2. Generate `{ "title": "…" }` as the hidden intake metadata and show `Assigned during review` in the preview.
3. Add a site-intake-only validation path that permits exactly title-only metadata while retaining all current skill, size, title, duplication, and attestation checks.
4. Stop the site-submission workflow before catalogue generation and add explicit maintainer completion instructions to the draft pull request.
5. Update focused tests and documentation, then verify locally and in gstack `/browse` without sending a real submission.
6. Push the existing branch, refresh draft PR #6, republish here.now, and verify the live mobile and desktop flow.

## Key Decisions And Tradeoffs

- Pending category is represented honestly by an absent `category` key, not by silently assigning a real but potentially wrong category.
- Only site intake accepts the pending state. `validate_skills.py` stays strict for approved repository content, making category assignment a hard pre-merge requirement.
- A newly opened submission pull request is expected to have a failing policy check until a maintainer adds the category and rebuilds the catalogue. The pull-request body explains this workflow.
- The public workflow-dispatch field remains named `marketplace_json` to avoid changing the here.now proxy contract.

## Risks And Unknowns

- Stale category references in JavaScript or HTML could break preview initialization; browser QA must cover the empty and valid states.
- The intentionally incomplete draft must not be mistaken for a broken intake. The generated pull-request body must state the exact maintainer steps.
- Site intake must not weaken the normal validator or allow arbitrary missing metadata fields.

## Out Of Scope

- Automatic category classification.
- Changes to the approved category taxonomy.
- Changes to proxy authentication, GitHub permissions, scanner behavior, or merge policy.
- A real live submission during verification.
- Any visual redesign beyond removing the category field and reflowing the existing title field.

## Verification

- `node --check site/app.js`
- `python3 scripts/build_catalog.py`
- `python3 scripts/build_catalog.py --check`
- `python3 scripts/validate_skills.py --all`
- `python3 -m unittest discover -s tests`
- Pinned NVIDIA SkillSpector scan without executing contributed content.
- Focused tests prove site intake accepts title-only metadata and normal validation rejects it.
- Local and live gstack `/browse` checks prove the category control is absent, title-only preview works, submission enables after confirmations, responsive layouts have no overflow, and the console has no errors.

## GitHub, Linear, And Memory Impact

- GitHub: update `codex/rf-100-site-native-intake` and draft PR #6; future site-submission PRs require a maintainer category edit before checks pass.
- Linear: RF-100 remains the active linked issue; no new issue is needed.
- Memory: record the durable decision that public contributors no longer choose categories and maintainers assign them during draft review.
