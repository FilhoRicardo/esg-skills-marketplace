# Plan: Complete And Publish The ESG Skills Marketplace

## Goal

Finish Linear issue RF-99 by repairing the trust-gate gaps, adding two useful text-only environmental, social, and governance (ESG) skills, building the Aster catalogue frontend, verifying the complete flow, and publishing the site permanently through here.now.

## Acceptance Criteria

- The GitHub repository and Linear project remain linked to RF-99, and RF-99 is closed only after every criterion below is evidenced.
- External pull requests cannot add, modify, rename, or delete platform files; they may change exactly one valid skill folder plus the generated catalogue.
- Tests reproduce the deleted-platform-file scope bug by proving `changed_paths()` returns a deleted `.github`, `scripts`, or site-code path and that `scope_errors()` rejects it for an external actor.
- `main` requires the two trust checks, resolved conversations, one code-owner approval, last-push approval, and administrator enforcement after this release lands.
- The approved catalogue contains exactly two text-only skills:
  - `esg-materiality-brief`, which turns user-provided business and stakeholder evidence into a bounded materiality briefing without making compliance or assurance claims.
  - `ghg-inventory-evidence-pack`, which organizes user-provided greenhouse-gas activity data, factors, boundaries, calculations, and source notes into a reviewable working evidence pack without presenting assurance or legal conclusions.
- Each seed skill uses the existing schema only: `SKILL.md` has `name` and `description` frontmatter, while `marketplace.json` has exactly `title` and `category`. The categories are `strategy` for the materiality brief and `data` for the greenhouse-gas evidence pack; both are already present in `ALLOWED_CATEGORIES` in `scripts/validate_skills.py`. No new pillar, tag, or `evidence_workflow` field is introduced.
- Both skills pass structural validation, catalogue integrity checks, and the pinned NVIDIA SkillSpector scan with a `SAFE` recommendation without executing skill content.
- The framework-free site contains semantic HTML, Aster tokens, small CSS and JavaScript files, and the generated `site/catalog.json`; it renders only merged catalogue data and links each card to its GitHub skill folder.
- The populated site explains the trust gate and professional-advice boundary in plain language, renders both skills from catalogue data, and handles loading, error, and empty-catalogue states honestly.
- The primary flow is keyboard accessible, has visible focus states, respects reduced motion, has no blocking console errors, and works at mobile, tablet, and desktop widths in the gstack `/browse` Chromium workflow.
- The permanent authenticated here.now publish succeeds, the live URL is reloaded and verified, and the URL is recorded in `README.md`, `MEMORY.md`, and RF-99.
- The installed Graphify CLI produces `graphify-out/graph.json` for the completed repository and its query or explain commands can read that graph; costs and caches remain ignored.
- The GitHub source is updated through a branch and pull request with both trust checks passing. The user's signoff on this reviewed plan is the one-time human approval for the bootstrap release that establishes administrator enforcement. If the connected GitHub app authors the pull request as a distinct actor, Ricardo also records that approval in GitHub; if GitHub attributes it to Ricardo and rejects self-approval, the administrator merge is permitted only for this explicitly approved bootstrap and enforcement is enabled immediately afterward.

## Approach

1. Add a regression test for deleted platform paths, then remove the deletion-excluding diff filter from `changed_paths` so every changed path reaches the existing external-contributor scope policy.
2. Author the two skill bundles using the existing template and editorial rules. Keep inputs user-provided, preserve source references, state uncertainty, and distinguish workflow guidance from legal, financial, compliance, certification, or assurance advice.
3. Regenerate `site/catalog.json` from validated skill metadata.
4. Extend the currently data-only `site/` directory by copying the canonical tokens from `/Users/ricardofilho/Documents/Projects/resources/branding/aster/aster-tokens.css` to `site/aster-tokens.css` and adding its first and only catalogue page, with small vanilla JavaScript for data loading and honest loading, error, and empty states. There is no existing `src/` frontend or second catalogue to preserve.
5. Extend tests only where they prove repository policy or catalogue/site invariants. Avoid a frontend framework, build step, package manager, backend, installer, or speculative feature.
6. Run structural validation, catalogue freshness, unit tests, and pinned SkillSpector. Serve `site/` locally and use gstack `/browse` for interaction, console, link, keyboard, and responsive evidence.
7. Create a release branch, push it, open the pull request through the connected GitHub app, and let both required checks run. Record GitHub approval when actor attribution permits it; otherwise use the user-approved bootstrap exception. Merge, enable administrator enforcement immediately, and verify the final branch-protection state.
8. Publish the exact merged `site/` directory with the here.now helper and saved credentials. Verify the returned live URL with `/browse`; never publish an expiring anonymous substitute as completion.
9. Run Graphify extraction against the final repository, verify the graph with a targeted query or explanation, record the permanent URL and durable release facts, close RF-99, and perform a requirement-by-requirement completion audit.

## Key Decisions And Tradeoffs

- The two seed skills are evidence-organization workflows, not promises of ESG compliance or professional conclusions. This makes them useful while keeping claims reviewable.
- The site stays framework-free. Four static files plus generated JSON are enough for two cards, filtering, and deployment.
- Aster is the concrete visual source. The implementation uses its canonical palette, typography, spacing, glass surfaces, and quiet motion rather than inventing another design direction.
- With only two cards, search and category filters add more interface than value. The primary interaction is opening each reviewed source skill on GitHub; accounts, ratings, installs, downloads, and submission forms remain out of scope.
- The site links to GitHub as the source of truth rather than duplicating full skill instructions into the frontend.
- Administrator enforcement is enabled only after this user-reviewed bootstrap release lands. The bootstrap exception expires with this release; future maintainer-authored platform work requires a second trusted reviewer or an explicitly documented maintenance window.
- The owner runbook will document the only emergency recovery path for broken required checks: record a maintenance window, temporarily disable administrator enforcement, repair the check through a pull request, and restore enforcement immediately. Normal contributions never use that exception.
- Permanent authenticated here.now publication is required; an anonymous 24-hour URL is not an acceptable final result.
- Here, authenticated means the helper reads the saved API key from `~/.herenow/credentials`; permanent means the publish reports authenticated mode and no expiry. The returned slug URL is the stable pointer for later updates, while its content is intentionally mutable only through explicit redeployment; the merged Git commit remains the immutable source that can reproduce it.

## Risks And Unknowns

- GitHub may attribute an app-created pull request to the same user who must approve it. This plan makes the user's post-review signoff the explicit bootstrap approval; no continuing bypass remains after administrator enforcement is enabled.
- SkillSpector may report a false positive. A non-`SAFE` result blocks publication until the content is narrowed or the user explicitly changes the acceptance criterion; the scanner will not be bypassed.
- SkillSpector success means `risk_assessment.recommendation` in each JSON report is exactly `SAFE`. The wrapper runs locally and in GitHub Actions. If the reviewed upstream commit becomes unavailable, the owner must review and pin a replacement commit in a separate platform change; the check is never weakened to unblock a contribution.
- Codex may make at most two content revisions in response to SkillSpector findings without changing either skill's promised job. If a skill is still not `SAFE`, publication pauses and the user decides whether to replace that skill or stop; no acceptance criterion is weakened.
- Graphify is installed locally and its `claude-cli` backend can use the authenticated Claude CLI without another API key. The release runs `graphify extract . --backend claude-cli --no-cluster --out .` and requires a readable `graphify-out/graph.json`.
- Preflight has confirmed the saved here.now credential is accepted by the authenticated sites endpoint with HTTP 200 and the pinned SkillSpector commit resolves at the expected SHA.
- Google-hosted Aster fonts are a network dependency. System fallbacks keep the site readable if the font request is unavailable.
- here.now live behavior can differ from local documentation. The publish helper's current structured result and a live browser reload are authoritative.

## Out Of Scope

- Payments, subscriptions, accounts, ratings, reviews, analytics, recommendations, or personalised content.
- Open self-service publication, a contributor portal, a package manager, remote installation, or automatic execution of skills.
- A backend, database, frontend framework, build service, single-page application routing, custom domain, or private access gate.
- Regulatory determinations, legal or financial advice, certification, audit, or assurance work.
- More than the two named seed skills.

## Verification

- `python3 scripts/build_catalog.py --check`
- `python3 scripts/validate_skills.py --all`
- `python3 -m unittest discover -s tests`
- `python3 scripts/run_skillspector.py --all --reports artifacts/skillspector` using NVIDIA SkillSpector pinned at `a5092dd9b9521ff57a9b53612bb129ce78019002`
- `graphify extract . --backend claude-cli --no-cluster --out .`, followed by a targeted `graphify query` or `graphify explain`
- GitHub Actions `trust / policy` and `trust / SkillSpector` pass for the release pull request.
- A manual editorial check confirms both skills describe a bounded job, preserve source references and uncertainty, and make no legal, financial, compliance, certification, audit, assurance, completeness, or guaranteed-outcome claim.
- GitHub branch protection reports strict checks, conversation resolution, code-owner and last-push approval, one approval, force-push/deletion denial, and administrator enforcement enabled.
- Local `/browse` checks cover content, both GitHub links, keyboard focus, console errors, failed network requests, and screenshots at 375x812, 768x1024, and 1280x720. Every viewport must show the brand, trust boundary, count, and both cards without horizontal overflow.
- here.now's current publish result reports authenticated mode and no expiry; `/browse` verifies the returned stable URL, two skill cards, source links, and clean console.
- `graphify-out/graph.json` exists and answers a targeted query or explanation, while `graphify-out/cost.json` and `graphify-out/cache/` remain untracked.
- Final `git status`, remote branch, pull request, Linear state, README, and project memory agree on the shipped URL and outcome.

## GitHub, Linear, And Memory Impact

- GitHub: deliver RF-99 on a `codex/` release branch, preserve the trust checks, close the disposable smoke branch if appropriate, land the release, and enable administrator enforcement after merge.
- Linear: keep RF-99 as the implementation issue, move it through active work, attach the release pull request and permanent site URL, then close it only after live verification.
- Project memory: record the two shipped skills, trust-gate deletion fix, permanent here.now URL, Aster frontend, final protection state, and Graphify outcome in one or two concise durable entries.
