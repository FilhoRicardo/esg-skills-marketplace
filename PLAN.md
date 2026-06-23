# Plan: Accept Unnormalized Skill Markdown

## Goal

Let public contributors submit ordinary Markdown instructions without preparing Codex frontmatter. Preserve the raw Markdown in a draft pull request so a maintainer can review it, then add the required frontmatter and category before publication.

## Acceptance Criteria

- Work remains in the linked GitHub repository, Linear project, and RF-100 issue.
- The public form accepts any UTF-8 Markdown file with meaningful instruction content; YAML frontmatter, a `name`, and a `description` are not required at upload time.
- The contributor still supplies a public title. The browser and server derive the same lowercase URL slug from that title.
- The form copy says frontmatter and category will be completed during review without exposing a technical metadata preview.
- Existing file-size, title, redistribution, review-boundary, duplicate-slug, NUL, and invisible-control protections remain enforced.
- Site intake writes the submitted Markdown unchanged as `SKILL.md` plus title-only marketplace metadata into a draft pull request.
- The draft pull-request body tells maintainers to review the raw instructions, add valid `name` and `description` frontmatter, assign a category, rebuild the catalogue, and run the trust checks.
- The normal approved-skill validator remains strict and does not gain a pending-mode escape hatch. Raw submissions cannot pass policy or merge until normalized.
- The Aster/Calm Ledger layout stays otherwise unchanged and responsive.
- The verified branch snapshot is republished to the permanent here.now site.

## Approach

1. Replace browser frontmatter parsing with minimal Markdown checks and title-derived slugging. Keep a small meaningful-content minimum without imposing headings or sections.
2. Replace site intake's temporary strict-bundle validation with dedicated raw Markdown, title-only metadata, and derived-slug validation.
3. Remove the pending-category option from the approved-skill validator so its only behavior is the strict publication contract.
4. Expand draft pull-request instructions to make frontmatter normalization and category assignment explicit maintainer steps.
5. Update focused tests, generated config, contributor documentation, operations guidance, and project memory.
6. Run local checks and gstack `/browse` with an ordinary Markdown file that has no frontmatter, without creating a live submission.
7. Push the existing branch, refresh draft PR #6, republish here.now, and verify the live mobile and desktop flow.

## Key Decisions And Tradeoffs

- Intake accepts raw Markdown, not arbitrary file types. Text-only and size boundaries remain.
- The temporary folder slug comes from the public title because raw content cannot be trusted to contain a usable `name`.
- The submitted Markdown is preserved rather than auto-rewritten. A maintainer normalizes it only after reading the content, avoiding invented descriptions or accidental instruction changes.
- The normal validator remains the sole publication gate. A newly opened submission pull request is intentionally incomplete until frontmatter, category, and generated catalogue artefacts are added.
- No submitted skill content is executed during intake or verification.

## Risks And Unknowns

- Two submissions with the same public-title slug conflict. The server will reject a slug already present in the approved catalogue; concurrent draft collisions remain a maintainer concern.
- Titles that cannot produce the repository's ASCII slug format must receive a clear correction message.
- A raw draft initially fails policy checks. The pull-request body must explain that expected state and the exact normalization steps.
- Relaxed intake must not allow control characters, empty content, oversized files, or bypass the strict approved-skill validator.

## Out Of Scope

- Automatically inventing or rewriting skill instructions, descriptions, or categories.
- Executing contributed skill content.
- Automatic category classification.
- Changes to proxy authentication, GitHub permissions, scanner behavior, or merge policy.
- A real live submission during verification.
- Any visual redesign beyond copy and preview-state changes.

## Verification

- `node --check site/app.js`
- `python3 scripts/build_catalog.py`
- `python3 scripts/build_catalog.py --check`
- `python3 scripts/validate_skills.py --all`
- `python3 -m unittest discover -s tests`
- Pinned NVIDIA SkillSpector checks on the approved catalogue without executing skill content.
- Focused tests prove raw Markdown without frontmatter passes site intake while the normal approved-skill validator rejects it.
- Local and live gstack `/browse` checks prove an ordinary Markdown file validates successfully, the derived slug matches the server rule, the public form stays compact, responsive layouts have no overflow, and the console has no errors.

## GitHub, Linear, And Memory Impact

- GitHub: update `codex/rf-100-site-native-intake` and draft PR #6. Future site-submission PRs require maintainer normalization before checks pass.
- Linear: RF-100 remains the active linked issue; no new issue is needed.
- Memory: record that public intake accepts unnormalized Markdown and the strict approved-skill schema is applied during maintainer review.
