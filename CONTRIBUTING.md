# Contributing a skill

Thank you for proposing an ESG skill. GitHub calls your proposal a **pull request**. Nothing becomes public when you open one: it must pass the automated checks and receive maintainer approval first.

## Before you start

Your v1 submission must:

- solve one clear ESG job;
- contain only UTF-8 text files;
- include `SKILL.md` and `marketplace.json`;
- avoid legal, financial, compliance, certification, or assurance guarantees;
- avoid scripts, binaries, images, PDFs, archives, symlinks, hidden files, and dependency manifests;
- be your original work or content you have permission to redistribute.

## Prepare the folder

1. Copy `templates/skill-template/` into `skills/`.
2. Rename the folder using lowercase words separated by hyphens, such as `esg-materiality-brief`.
3. Set the same name in the `SKILL.md` frontmatter.
4. Replace every placeholder in `SKILL.md` and `marketplace.json`.
5. Run:

   ```bash
   python3 scripts/build_catalog.py
   python3 scripts/validate_skills.py --all
   python3 -m unittest discover -s tests
   ```

## Open the request on GitHub

If you are new to GitHub:

1. Open this repository and select **Fork**.
2. In your fork, select **Add file → Upload files** and upload your skill folder plus the regenerated `site/catalog.json`.
3. Select **Contribute → Open pull request**.
4. Complete the checklist and submit the pull request.

GitHub will automatically request review from `@FilhoRicardo`. Wait for both checks to turn green. If a check fails, open its details, make the requested change in your fork, and update the pull request.

## What the checks do

- `trust / policy` rejects unsafe file types, malformed metadata, catalogue drift, and external changes to platform files.
- `trust / SkillSpector` scans the changed skill with a pinned version of NVIDIA SkillSpector. Any result above `SAFE` blocks approval.

Passing checks is necessary but not sufficient. The maintainer also reviews purpose, claims, instructions, external links, and data handling. Never ask the reviewer to download or run submitted content.

## Categories

Use one category in `marketplace.json`:

- `data`
- `disclosure`
- `operations`
- `reporting`
- `risk`
- `strategy`

## Review outcomes

- **Changes requested** — fix the named concern and update the same pull request.
- **Approved** — the checks and human review passed; the maintainer may merge.
- **Closed** — the submission is out of scope, unsafe, unverifiable, or cannot be redistributed.

Merging places the skill in the approved source of truth. The public catalogue is updated only from merged content.
