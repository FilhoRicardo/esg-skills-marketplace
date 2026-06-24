# Agent Instructions

## Identity

This project is `ESG Skills Marketplace` in `/Users/ricardofilho/Documents/Projects/active/esg-skills-marketplace`. Route here when the user asks about publishing, maintaining, or presenting the ESG skills catalogue and its here.now frontend. Do not route unrelated environmental, social, and governance research or other marketplace work here.

## Source of Truth

- GitHub repo: `https://github.com/FilhoRicardo/esg-skills-marketplace`
- Linear project: `https://linear.app/rf-ai-workspace/project/esg-skills-marketplace-2a2095348777`
- Current implementation issue: `RF-99` — `https://linear.app/rf-ai-workspace/issue/RF-99/initialize-esg-skills-marketplace`
- Linear is the project-management source of truth for roadmap, issue scope, and acceptance criteria.
- GitHub is the code and PR source of truth for the skills collection, catalogue frontend, branches, review, and shipped changes.
- Codex is the executor for this project.
- Claude is the devil's advocate for non-trivial planning.
- Do not mirror `CLAUDE.md` from this file; keep `CLAUDE.md` critic-only.
- At the start of every project task, check and stay aware of four fields: project folder, GitHub repo, Linear project, and Linear issue.
- Before code work, say whether the GitHub repo and Linear project/issue are linked. If either is missing, create or link it before implementation unless the user explicitly says the work is local-only.
- Before non-trivial implementation, work from a Linear issue. If no issue exists, create or link one unless the user explicitly opts out.

## Planning Gate

- Before non-trivial implementation, use the `claude-devil-review` skill when available.
- Codex drafts or updates `PLAN.md`.
- Claude challenges the plan for up to five rounds.
- Codex accepts useful critique, rejects weak critique with reasons, and logs the exchange in `PLAN-REVIEW-LOG.md`.
- Code starts only after user signoff on the reviewed plan.

## Graph Layer

- Set up Graphify after the GitHub repo exists and `.gitignore` protects credentials, local here.now state, logs, generated output, and personal files.
- When `graphify-out/graph.json` exists, use `graphify query`, `graphify path`, or `graphify explain` before broad codebase exploration.
- Do not commit `graphify-out/cost.json` or `graphify-out/cache/`.

## App Design System

- Use Aster for the catalogue frontend unless the user explicitly provides a project-specific brand.
- Before UI work, read `/Users/ricardofilho/Documents/Projects/resources/branding/aster/BRAND.md`.
- Copy or import `/Users/ricardofilho/Documents/Projects/resources/branding/aster/aster-tokens.css` into the site style layer.

## Resources

| Resource | Read when... |
|---|---|
| `/Users/ricardofilho/Documents/Projects/resources/branding/aster/BRAND.md` | Building or changing the catalogue frontend. |
| `/Users/ricardofilho/Documents/Projects/resources/branding/aster/aster-tokens.css` | Implementing theme tokens, surfaces, controls, or selected states. |

## Workflow

1. Read `MEMORY.md`, this file, the linked Linear issue, and relevant local files.
2. Define the skill or frontend change, acceptance criteria, non-goals, and verification.
3. Run the Planning Gate unless the work is trivial or explicitly exempted.
4. Inspect git status before editing.
5. Add or update skills under `skills/` and keep their catalogue metadata current.
6. Apply the Aster design system to frontend changes.
7. Make the smallest change that satisfies the issue.
8. Verify skill structure locally and test the catalogue in Chrome.
9. Publish the verified static site to the linked here.now site when the issue includes deployment.
10. Update Graphify when meaningful code changed and a graph exists.
11. Update `MEMORY.md` only when durable project context changed.

## Memory Rules

- Read `MEMORY.md` at the start of project work.
- Update `MEMORY.md` after project setup and when durable context changes.
- Every Linear issue creation or closure requires a memory touch; add an entry only when durable knowledge changed.
- Keep each memory entry to one or two sentences.

## Intake Review Workflow

When asked to review or process the intake queue:

1. List pending submissions:
   ```
   ls skills-to-review/
   ```
2. For each submission directory, read `skills-to-review/<uuid>/SKILL.md` and
   `skills-to-review/<uuid>/submission.json`.
3. Evaluate whether the skill is appropriate for the ESG Skills Marketplace:
   - Is it genuinely ESG-related?
   - Is it safe to redistribute? No credentials, no PII, no misleading claims.
   - Is the quality good enough to publish?
4. If **approved**, run:
   ```
   python3 scripts/accept_submission.py <uuid> \
     --slug <url-slug> \
     --description "<one-line description, 20-300 chars>" \
     --category <data|disclosure|operations|reporting|risk|strategy>
   ```
   This copies the skill to `skills/`, rebuilds the catalogue, commits to `main`,
   pushes to GitHub, and redeploys the here.now site automatically.
5. If **rejected**, move the submission directory to `var/intake/needs-attention/<uuid>/`
   and write a short `rejection-reason.txt` explaining why.
6. Process one submission at a time. Confirm with the user before publishing.

## Verification

- Run `python3 scripts/validate_skills.py --all` and `python3 -m unittest discover -s tests`.
- Run the pinned NVIDIA SkillSpector scan without executing contributed skill content.
- Serve the static catalogue locally and verify its primary flow and responsive layout in Chrome before publishing.

## PR Standard

Every PR should explain what changed, why, the Linear issue, acceptance criteria checked, risk, how to test, what was intentionally excluded, agent involvement, and any follow-up issues.

## Editorial Rules

Follow my voice principles in `/Users/ricardofilho/Documents/Projects/resources/voice-principles.md`.

- Spell out environmental, social, and governance (ESG) on first use.
- Describe each skill by the job it helps the user complete; avoid unsupported impact or compliance claims.
- Distinguish guidance and workflow automation from professional legal, financial, or assurance advice.
