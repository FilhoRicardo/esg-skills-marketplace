# Owner review runbook

This is the safe path for reviewing a submitted skill. You do not need to use the command line.

## When GitHub notifies you

1. Open the pull request from the GitHub notification.
2. Check that it changes one folder under `skills/` and the generated `site/catalog.json`. External contributors should not change `.github/`, `scripts/`, `site` code, or project policy files.
3. Wait for both required checks:
   - `trust / policy`
   - `trust / SkillSpector`
4. Do not approve while either check is red, missing, or still running.

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
