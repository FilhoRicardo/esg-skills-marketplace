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
