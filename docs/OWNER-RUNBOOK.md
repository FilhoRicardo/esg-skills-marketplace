# Owner review runbook

This is the safe path for reviewing a submitted skill. You do not need to use the command line.

Site-native submissions arrive as draft pull requests created by the public intake workflow. Their Markdown may not have frontmatter yet. The trust gate is unchanged: nothing becomes public until the submission is normalized, both checks pass, and you approve the pull request.

## When GitHub notifies you

1. Open the pull request from the GitHub notification.
2. Check that the initial site submission changes one folder under `skills/`. External contributors should not change `.github/`, `scripts/`, `site` code, or project policy files.
3. Read the raw instructions before making any structural edits. Do not download, install, or run them.

## Normalize a site submission

Ask Codex to update the same draft branch after your content review:

1. Add YAML frontmatter to `SKILL.md` with a `name` equal to the folder slug and a factual 20–300 character `description`.
2. Add one allowed `category` to `marketplace.json`.
3. Preserve the submitted instructions unless a review finding requires a clearly documented change.
4. Run `python3 scripts/build_catalog.py` and commit the generated catalogue.
5. Run the repository tests and push the normalized draft.

Then wait for both required checks:

   - `trust / policy`
   - `trust / SkillSpector`

Do not approve while either check is red, missing, or still running. A red policy check before normalization is expected.

## Read the submission

Open **Files changed** and inspect the text in GitHub. Do not download, install, or run the proposed skill.

Confirm:

- the skill does one understandable ESG job;
- its instructions match its stated description;
- it does not request secrets, broad filesystem access, hidden persistence, or unnecessary external access;
- links point to expected, reputable destinations;
- claims do not promise certification, assurance, compliance, legal conclusions, or guaranteed outcomes;
- the author has confirmed the right to redistribute the content.

Open the SkillSpector check details and download its JSON report artifact if you need the individual findings. `SAFE` is required, but it does not replace reading the skill.

## Decide

- If anything is unclear, select **Request changes** and explain the exact concern.
- If the checks are green and the manual review is satisfactory, select **Approve**.
- Merge with **Squash and merge** only after approval.
- Close the pull request without merging when the content is unsafe, unverifiable, out of scope, or cannot be redistributed.

After merge, publish the catalogue only from the current `main` branch. Never publish files directly from a contributor branch.

## Emergency protection maintenance

Administrator enforcement applies to normal work. If a required check itself is broken and prevents its repair:

1. Record the maintenance reason and affected check before changing protection.
2. Temporarily disable administrator enforcement only; keep the pull-request boundary and other protections in place.
3. Repair and verify the check through a pull request.
4. Restore administrator enforcement immediately after merge and confirm the final protection state.

This is a recovery procedure for the trust gate, not a way to bypass a failed skill review.
