# Plan: Add Site-Native Skill Download And Submission

## Goal

Deliver RF-100 by turning the ESG Skills Marketplace into a true site-first intake surface: visitors can download approved skills directly from the public site, submit a new skill from the public site without navigating GitHub, and the existing trust gate still controls what reaches `main` and the live catalogue.

## Acceptance Criteria

- The GitHub repository remains `https://github.com/FilhoRicardo/esg-skills-marketplace`, the Linear project remains `ESG Skills Marketplace`, and implementation is tracked in RF-100.
- The public site keeps the Aster visual system and still explains the trust boundary in plain language.
- Each approved skill card exposes a direct frontend download action that does not send the user to GitHub.
- Approved downloads are generated from merged repository content and contain the reviewed skill bundle, not an ad hoc frontend reconstruction.
- The homepage exposes a site-native submission flow titled and worded for non-GitHub users.
- The site-native submission flow accepts the conservative v1 bundle only:
  - `SKILL.md`
  - `marketplace.json`
  - both UTF-8 text, non-executable, and within tighter site-intake size caps chosen to fit the hidden dispatch flow safely
- The browser performs honest client-side checks before submission:
  - both required files are present
  - `SKILL.md` frontmatter contains `name` and `description`
  - `marketplace.json` contains only `title` and `category`
  - the slug matches across folder intent and frontmatter
  - the category is one of the repository's allowed categories
  - the user confirms redistribution rights and the professional-advice boundary
- The public site does not expose GitHub tokens, here.now credentials, or a generic authenticated proxy surface in client-side code.
- Submission from the site uses an authenticated here.now proxy route with:
  - an exact local path rather than a broad wildcard
  - a server-side injected secret variable
  - a route-specific rate limit stricter than the default
  - no public serving of `.herenow/proxy.json`
- A dedicated GitHub intake workflow receives the proxied submission, reconstructs the uploaded bundle, runs the repository build steps needed to stage it, and opens a draft pull request automatically.
- The intake workflow uses a repository secret token rather than `GITHUB_TOKEN` when creating the pull request so the normal trust-check workflows still run on the created PR.
- Automatically created PRs contain enough review context for the maintainer without exposing private or unnecessary user data.
- Merged `main` can republish the static site automatically to the permanent authenticated here.now slug, so approved submissions flow back to the live catalogue without manual GitHub browsing by the submitter.
- Existing trust protections remain intact:
  - `trust / policy`
  - `trust / SkillSpector`
  - human review
  - merge to `main` before catalogue publication
- The repository documentation and maintainer runbooks explain the new site-native flow, required secrets/variables, and what stays intentionally out of scope.

## Approach

1. Keep the repository as the source of truth, but shift the public UX to site-first language and controls.
2. Extend the generated public artefacts so approved skills produce downloadable bundles under `site/` and the frontend links to those bundles directly.
3. Add a new submission section to the static Aster homepage that accepts the two-file v1 bundle, previews the parsed metadata, and performs conservative client-side validation before any network call.
4. Add `.herenow/proxy.json` to the published site so `fetch('/api/submit-skill')` forwards only to the GitHub workflow-dispatch endpoint, with a server-side injected token variable and a strict per-IP rate limit.
5. Implement a dedicated GitHub Actions intake workflow that:
   - validates the submission payload shape again server-side
   - writes the submitted `SKILL.md` and `marketplace.json` into a branch
   - regenerates catalogue/download artefacts
   - opens a draft PR using a dedicated secret token
6. Keep the existing trust gate as the only route to publication. The intake workflow creates the PR; the current trust checks and maintainer review decide whether it lands.
7. Add a separate deploy workflow for `main` that republishes the authenticated here.now site automatically after merged changes affecting the public catalogue surface.
8. Configure the required external state as part of implementation rather than leaving it as manual follow-up:
   - GitHub repo secrets and variables
   - here.now account variables used by proxy routes
   - the permanent site slug used by automated publish
9. Verify the whole story locally and live:
   - build artefacts
   - upload flow in browser
   - workflow dispatch route
   - auto-created PR
   - required checks on that PR
   - automatic republish after merge

## Key Decisions And Tradeoffs

- The best possible option in this stack is not a separate backend service. It is a static here.now site plus a narrow authenticated proxy route into a dedicated GitHub intake workflow.
- The site-native uploader is intentionally narrower than the repository's raw skill intake. It supports the common two-file v1 bundle only, because that gives non-GitHub users a clean flow without exposing a high-power general write API.
- Downloads are generated from merged source bundles and published with the site. The user gets a real reviewed bundle, not a synthetic export assembled on click.
- The proxy route will expose exactly one submission endpoint, not a broad GitHub API passthrough. This keeps the public surface narrow even though the underlying secret token has repository power.
- The hidden-dispatch path needs tighter file-size limits than the repository validator because GitHub workflow-dispatch payloads are better treated as a bounded transport. Larger or more complex future bundles can still remain a repository-only path if needed.
- The submitter-facing flow will prefer public attribution fields or a public contact URL rather than collecting private data that would be awkward to handle safely in a public-repo workflow.
- Automatic republish on merged `main` is part of the product, not a convenience. Without it, the site would still depend on maintainer GitHub operations and would not feel like the front door of the marketplace.

## Risks And Unknowns

- GitHub workflow-dispatch payload size is a practical transport limit even if the repo validator allows larger text bundles. The site flow must enforce smaller caps explicitly and document that it is a conservative intake path.
- A proxied public submission endpoint can still be spammed. The route-specific rate limit, conservative payload validation, and draft-PR creation reduce impact but do not eliminate abuse entirely.
- A PR created by automation must still trigger the required trust workflows. The implementation must use a dedicated secret token path and prove that the resulting PR receives `trust / policy` and `trust / SkillSpector`.
- here.now proxy routes require an authenticated site and configured account variables. This implementation is blocked if the account cannot store the necessary variables or if the permanent site slug is not writable by the configured API key.
- GitHub repo secrets are currently absent. The implementation must create the required secrets and variables as part of the rollout, or it is not complete.
- If the deploy workflow republishes a broken site automatically, production could drift immediately after merge. The workflow therefore needs a local build/validation gate before publish, and the live site must be rechecked after rollout.

## Out Of Scope

- Accounts, passwords, user dashboards, submitter login, or submission-status tracking.
- Arbitrary multi-file skill bundles, binary attachments, archives, images, PDFs, or executable skill content.
- Replacing GitHub review with a custom moderation system.
- Payments, ratings, recommendations, analytics-heavy growth features, or social marketplace features.
- Private contact storage, hidden inboxes, or CRM-like submitter management.
- Full background moderation automation after PR creation; human review remains required.

## Verification

- `python3 scripts/validate_skills.py --all`
- `python3 scripts/build_catalog.py --check`
- `python3 -m unittest discover -s tests`
- any new build/check command for downloadable public artefacts returns clean results
- browser verification with gstack `/browse` covers:
  - homepage rendering
  - download buttons
  - successful local parsing of the submission files
  - honest validation errors
  - successful POST to the proxied submission endpoint
  - responsive layout at mobile, tablet, and desktop widths
- a live submission from the site creates a draft PR automatically
- the created PR runs `trust / policy` and `trust / SkillSpector`
- merging a reviewed submission to `main` republishes the permanent here.now site automatically and the new public download appears live
- final GitHub, Linear, README, and project memory all agree on the new RF-100 flow and configuration

## GitHub, Linear, And Memory Impact

- GitHub: add submission-intake and deploy workflows, generated download artefacts, frontend submission/download UX, configuration docs, and any supporting scripts/tests on a `codex/` branch and PR.
- Linear: RF-100 is the source-of-truth implementation issue. It should move to active work during implementation and close only after live submission and republish verification.
- Project memory: record RF-100, the site-first intake architecture, the exact required proxy/secret configuration, and the final durable public workflow once it ships.
