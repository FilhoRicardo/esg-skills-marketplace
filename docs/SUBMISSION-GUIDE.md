# Skill Submission Guide

## For contributors — submitting a skill

### What you need

Two things:

1. **A `SKILL.md` file** — plain Markdown with your skill instructions. At minimum it needs a heading and a few sentences of instructions (80+ characters). No special format required; frontmatter is optional and will be added by the maintainer during review.

2. **A public title** — the name that will appear in the catalogue (4–80 characters).

Optional: your name and a contact URL or email, shown in the review notes only, not published to the site.

---

### How to submit

1. Go to **[https://royal-bugle-xgg7.here.now/submit.html](https://royal-bugle-xgg7.here.now/submit.html)**
2. Upload your `SKILL.md` file.
3. Enter a public title.
4. Tick both confirmation statements:
   - *I created this bundle or have permission to publish it.*
   - *I understand that automated checks and maintainer approval are still required.*
5. Click **Send for review**.

You will see **"Submission queued for intake"** within a few seconds. That means your skill has been received.

There is no account or login required.

---

### What happens next

You will not receive a notification (the site has no user accounts). The maintainer reviews submissions periodically. If your skill is approved, it will appear in the catalogue at [https://royal-bugle-xgg7.here.now/](https://royal-bugle-xgg7.here.now/) — usually within a few days.

---

### Why a submission might be declined

- The skill content is not related to ESG, sustainability, or environmental/social/governance work.
- The instructions are too vague to be useful as an AI prompt.
- The content makes specific legal, financial, or medical claims without adequate disclaimers.
- The title or content duplicates an existing skill.

---

## For the maintainer — reviewing a submission

### What triggers when a submission arrives

The moment a user clicks "Send for review", the site's hidden proxy forwards the submission to a GitHub Actions workflow (`site-submission-intake.yml`). Within about 10 seconds, that workflow:

1. Validates the skill file (size, content, title format).
2. Writes the files to a new branch: `submission/<slug>-<run-id>`.
3. Opens a **draft pull request** on the repository.

You will see a new draft PR appear at [https://github.com/FilhoRicardo/esg-skills-marketplace/pulls](https://github.com/FilhoRicardo/esg-skills-marketplace/pulls).

---

### How to review and publish a skill

**Step 1 — Check out the PR branch**

```bash
git fetch origin
git checkout -b review-<slug> origin/submission/<slug>-<run-id>
```

**Step 2 — Read the skill**

Open `skills/<slug>/SKILL.md`. Ask yourself:
- Is this genuinely ESG-related?
- Are the instructions clear and safe to run as an AI prompt?
- Does it make any claims it cannot support?

**Step 3 — Add the required fields**

The intake workflow writes only the raw content. Before merging you must add:

*In `skills/<slug>/SKILL.md`* — add YAML frontmatter at the top:
```markdown
---
name: <slug>
description: One sentence, 20–300 characters, describing what the skill does.
---
```

*In `skills/<slug>/marketplace.json`* — add a category:
```json
{"title": "Public Title", "category": "operations"}
```

Allowed categories: `data`, `disclosure`, `operations`, `reporting`, `risk`, `strategy`.

**Step 4 — Commit and push**

```bash
git add skills/<slug>/
git commit -m "Maintainer review: add frontmatter, description, and category"
git push origin review-<slug>:submission/<slug>-<run-id>
```

**Step 5 — Merge the PR**

On GitHub, mark the PR as "Ready for review", then merge it (squash merge is fine). The CI gate (`trust / policy`) will run automatically.

**Step 6 — Auto-deploy**

Within 15 seconds of the merge, the `Publish public marketplace` workflow rebuilds the catalogue and redeploys the site. The skill appears in the catalogue at [https://royal-bugle-xgg7.here.now/](https://royal-bugle-xgg7.here.now/) with a Download .zip button.

---

### How to reject a submission

Simply close the draft PR with a short comment explaining why. No further action needed.

---

### Timing summary

| Step | Who | Time |
|---|---|---|
| User submits | Contributor | — |
| Draft PR opens | GitHub Actions | ~10 seconds |
| Maintainer review | You | When you check GitHub |
| Skill goes live after merge | GitHub Actions | ~15 seconds |
