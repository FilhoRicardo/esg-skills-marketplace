# Plan Review Log

Claude challenges and Codex responses go here. Keep full critique rounds in this file; store only durable decisions and outcomes in `MEMORY.md`.

## 2026-06-21 — Review attempt

- Claude CLI version `2.1.185` passed the required no-tools authentication smoke test.
- Four no-tools, plan-mode review calls returned no critique or verdict, including full and compressed versions of the plan.
- Codex stopped before GitHub, Linear, code, and here.now publishing. The review was not treated as clear.

## 2026-06-21 — User approval and security scope

- The user approved the plan and explicitly authorized a Codex-only review after Claude returned no verdict.
- The user required NVIDIA SkillSpector in the intake workflow and asked for a trustworthy, beginner-friendly GitHub gate.
- Codex narrowed v1 to text-only skills and added structural validation, pinned SkillSpector analysis, CODEOWNERS approval, protected `main`, and publication only after merge.

## 2026-06-22 — Completion plan prepared

- The user asked Codex to fix the remaining issues, add two ESG skills, and publish the webpage through here.now.
- Codex revised `PLAN.md` to cover the deleted-path scope regression, final branch protection, two bounded evidence-workflow skills, the Aster static frontend, full browser and scanner verification, permanent here.now publication, Graphify, and RF-99 closure.
- Claude review is pending. No implementation code has started.

### Round 1

- Claude CLI received the full revised plan in authenticated no-tools plan mode and returned no critique or verdict.
- Codex did not treat silence as `CLEAR` and queued a compressed retry.

### Round 2 — Claude verdict: REVISE

Claude raised eight concerns:

1. The deleted-path regression was not defined precisely enough.
2. The two skills allegedly lacked identifiers and a schema definition.
3. The catalogue allegedly duplicated an existing `src/index.html` frontend.
4. The pinned SkillSpector dependency lacked an exact success assertion and replacement procedure.
5. Administrator enforcement could deadlock a sole-maintainer repository if required checks break.
6. Authenticated and permanent here.now publication needed a concrete definition and retention model.
7. Conditional Graphify work was not a falsifiable acceptance criterion.
8. Responsive browser testing needed explicit pass criteria.

`VERDICT: REVISE`

Codex response:

- Accepted and sharpened concerns 1, 4, 5, 6, 7, and 8. `PLAN.md` now names the affected functions and assertion, the exact SkillSpector JSON field, the pin replacement rule, the emergency protection maintenance procedure, here.now API-key/no-expiry semantics, unconditional Graphify output, and per-viewport checks.
- Concern 2 was partly rejected because the plan already named both skill slugs and the repository already defines the text-only schema. Codex still added the exact existing frontmatter, metadata fields, and categories so no new schema can be inferred.
- Concern 3 was rejected as based on fabricated repository paths. This repository has no `src/` directory or existing frontend; `site/` contains only `catalog.json`. The plan now says the new page is the sole catalogue frontend.

### Round 3 — Claude verdict: REVISE

Claude raised six concerns:

1. Landing before code-owner approval would contradict the trust model.
2. The meaning of a permanent but mutable here.now site needed sharper wording.
3. Graphify's non-clustered extraction path was not named.
4. Repeatedly narrowing skills for SkillSpector needed a stopping rule.
5. Automated checks did not replace a named editorial review for misleading ESG claims.
6. The planned search and filter surface was unnecessary for two cards and made "small" code undefined.

`VERDICT: REVISE`

Codex response:

- Accepted concern 1. The release will not bypass review; if the app-authored pull request is still attributed to Ricardo, work pauses for a second trusted reviewer.
- Clarified concern 2: authenticated means the saved API key, permanent means no expiry, the slug URL remains stable for later explicit redeployments, and Git remains the immutable source.
- Accepted concerns 3 through 5 by naming `graphify extract . --no-cluster --out .`, limiting scanner-driven revisions to two before user escalation, and adding a manual ESG-claims editorial gate.
- Accepted the simplicity point in concern 6 more strongly than suggested: search and filters are removed entirely because two cards do not need them. The page only loads catalogue data, handles honest states, and opens source skills.

### Round 4 — Claude verdict: REVISE

Claude raised four concerns:

1. No second reviewer was named for a possible GitHub self-approval deadlock.
2. The here.now credential was assumed rather than verified.
3. The Graphify backend dependency was unspecified.
4. The pinned SkillSpector commit was not proven reachable before authoring content.

`VERDICT: REVISE`

Codex response:

- The here.now credential now returns HTTP 200 from the authenticated sites endpoint, and GitHub resolves the SkillSpector pin at the exact expected SHA.
- Graphify will use `--backend claude`; the authenticated Claude CLI is available, so no extra API key is required.
- This is a sole-maintainer bootstrap. The revised plan makes the user's post-review signoff the one-time human approval for this rule-establishing release. Both checks remain mandatory, administrator enforcement is enabled immediately after merge, and the exception expires with this release. Future platform work requires a second reviewer or a documented maintenance window.

### Round 5 — Claude verdict: REVISE

Claude raised two remaining factual concerns:

1. The authoritative Aster token source was not written into the plan.
2. The plan did not explicitly confirm that `strategy` and `data` are allowed validator categories.

`VERDICT: REVISE`

Codex response:

- Both concerns are valid and now resolved in `PLAN.md`: the source is `/Users/ricardofilho/Documents/Projects/resources/branding/aster/aster-tokens.css`, and both category values already exist in `ALLOWED_CATEGORIES`.
- The five-round cap has been reached. Claude did not return `CLEAR`; Codex is therefore presenting the fully revised plan and the resolved final concerns to the user for the required decision rather than inventing consensus.

## 2026-06-22 — User signoff

- The user approved the reviewed completion plan and its one-time sole-maintainer bootstrap exception.
- Implementation may proceed; both trust checks remain mandatory, and administrator enforcement must be enabled immediately after this release lands.

## 2026-06-22 — Implementation correction

- Graphify distinguishes its API-backed `claude` backend from the subscription-backed `claude-cli` backend. The initial command correctly refused to run without `ANTHROPIC_API_KEY`.
- Codex corrected the reviewed command to `--backend claude-cli`, which uses the already-authenticated local Claude CLI without exposing or requesting an API key.

## 2026-06-22 — RF-100 planning gate

- The user requested the stronger marketplace UX: site-native download, site-native submission, hidden GitHub scaffolding, PR creation behind the scenes, and publication back to the live site after approval.
- Codex created Linear issue RF-100 to track this new scope: `https://linear.app/rf-ai-workspace/issue/RF-100/add-site-native-skill-download-and-submission-flow`.
- GitHub remains linked to `FilhoRicardo/esg-skills-marketplace`, and the Linear project remains `ESG Skills Marketplace`.
- Codex checked the current external configuration before plan review:
  - GitHub repo secrets: none configured
  - GitHub repo variables: none configured
  - here.now account variables: none configured
  - authenticated here.now default Drive exists, but the reviewed plan currently prefers a narrower workflow-dispatch intake path over a Drive-backed submission store
- Codex read the current here.now docs through the required gstack `/browse` path and confirmed two implementation-relevant capabilities:
  - authenticated proxy routes from `.herenow/proxy.json` can inject server-side variables into exact or prefix paths
  - proxy routes support stricter per-route rate limits and are never served directly to visitors
- No RF-100 implementation code has started.

### Round 1

- Claude CLI was invoked in authenticated no-tools plan mode with the full `PLAN.md` content.
- The process did not return critique or a verdict within two 30-second waits.
- Codex did not treat silence as `CLEAR` and moved to a shorter retry.

### Round 2

- Claude CLI was invoked again in authenticated no-tools plan mode with a compressed review prompt over the same plan.
- The process again returned no critique or verdict within 30 seconds.
- Codex did not treat silence as `CLEAR` and moved to a tightly summarized third retry.

### Round 3

- Claude CLI received a compact plan summary focused on the hidden-proxy, workflow-dispatch, PR-creation, and auto-republish architecture.
- The process again returned no critique or verdict within 30 seconds.
- Codex is stopping the review loop here rather than inventing a `CLEAR` result. The reviewed plan is being presented to the user for the required signoff before any RF-100 code starts.

## 2026-06-22 — RF-100 frontend repair planning gate

- Live gstack `/browse` design review graded the branch snapshot D and found structural overlap at desktop and mobile sizes: fixed-height panels held substantially taller content, covered download links, and made the mobile form visually unusable.
- The user approved the redesign direction and asked Codex to implement and redeploy it to the existing here.now site.
- Product Design playback locked the brief to Aster, a catalogue-focused homepage, visible downloads, a dedicated fully functional submission page, and no changes to the hidden GitHub intake architecture.
- Product Design requires the user to select one of three generated visual targets before code begins. Codex is combining that selection with final signoff on this reviewed plan.

### Round 1

- Claude CLI passed the required authenticated no-tools smoke test, then received the full frontend repair plan in no-tools plan mode.
- The review call returned no critique and no verdict. Codex did not treat silence as `CLEAR` and moved to a compressed retry.

### Round 2

- Claude CLI received a compressed review prompt covering the page split, unchanged intake architecture, responsive acceptance checks, deploy scope, and Product Design selection gate.
- The call again returned no critique and no verdict. Codex did not treat silence as agreement and moved to a minimal structured retry.

### Round 3

- Claude CLI received a minimal structured prompt and was asked to return JSON-formatted review text with an exact verdict line.
- The call again returned no critique and no verdict. Three differently shaped authenticated no-tools attempts reproduced the same silent critic behavior already documented for RF-100.
- Codex stopped the loop rather than inventing consensus. The plan remains bounded to the frontend repair, and the user must select one generated visual target and approve the reviewed plan before implementation.

## 2026-06-22 — Frontend repair signoff

- The user selected visual direction 3, `Calm Ledger`, and thereby approved the reviewed frontend repair plan presented with the three options.
- Implementation may proceed on the existing RF-100 branch. The visual target is the generated Calm Ledger mockup, and the GitHub intake architecture remains unchanged.

## 2026-06-22 — Category assignment follow-up

- The user explicitly requested removal of the public category requirement so maintainers can classify a skill after reading it.
- Codex proposed title-only intake metadata, strict approved-skill validation, and an intentionally blocked draft pull request until the maintainer assigns a category and rebuilds the catalogue.

### Round 1

- Claude CLI passed the required authenticated no-tools smoke test.
- Claude received the full follow-up plan in no-tools plan mode and returned no critique or verdict.
- Codex did not treat silence as `CLEAR`; it tightened `PLAN.md` to the contained category-assignment change and removed stale redesign scope before retrying.

### Round 2

- Claude received the tightened plan with a focused question about title-only intake and the strict pre-merge category gate.
- The call again returned no critique or verdict. Codex did not treat silence as approval and moved to one minimal risk check.

### Round 3

- Claude received only the proposed data flow and strict-validator boundary, with no surrounding plan prose.
- The third call again returned no critique or verdict. This reproduces the documented silent-critic behavior for RF-100.
- The user's request explicitly approves the exact product change, and Codex's implementation remains bounded to title-only draft intake with the unchanged validator preventing publication until category assignment. Implementation proceeds without inventing a Claude verdict.

## 2026-06-23 — Unnormalized Markdown intake follow-up

- The user requested removal of the frontmatter-format requirement at public upload time so maintainers can normalize accepted skills after review.
- Codex's bounded interpretation is: accept meaningful UTF-8 Markdown, derive the temporary slug from the public title, preserve the instructions unchanged, and keep strict frontmatter plus category as hard pre-merge requirements.

### Round 1

- Claude CLI passed the authenticated no-tools smoke test and received the full plan.
- The review returned no critique or verdict. Codex did not treat silence as `CLEAR` and moved to a focused data-boundary retry.

### Round 2

- Claude received only the raw-Markdown intake boundary, title-derived slug, unchanged strict merge gate, and no-execution constraint.
- The call again returned no critique or verdict. Codex did not treat silence as approval and moved to one minimal safety question.

### Round 3 — Claude verdict: CLEAR

Claude found the intake boundary materially contained by size, UTF-8, control-character, slug-collision, attestation, no-execution, and strict merge-gate controls. It raised one conditional concern: raw Markdown must not be rendered as unsanitized HTML in downstream views.

`VERDICT: CLEAR`

Codex response:

- Accepted the concern as a verification requirement. The browser preview inserts only fixed plain text and metadata through `textContent`; it does not render submitted Markdown. The public catalogue also renders validated metadata through `textContent`, while GitHub owns and sanitizes its pull-request Markdown view.
- The user's request is the final signoff for this exact bounded change: raw Markdown intake now, maintainer normalization before merge, and no execution or automatic rewriting of submitted instructions.

## 2026-06-23 — Submission UI regression repair

- Live empty-state screenshots confirmed the regression: the technical preview used browser-default definition-list indentation, producing a stair-step layout on mobile and tablet after the frontmatter row was added.
- The public preview duplicated information contributors do not need. Codex removed the panel, kept validation state in the existing status line, expanded the form to the full workspace width, and added a clear disabled-button state.
- The intake payload, validation, review workflow, and publication gate are unchanged.
- The regression was amplified by mixed asset versions: `app.js` was cache-busted but `styles.css` was not. Both shared assets are now versioned together and must be bumped as a pair.

## 2026-06-23 — Automated intake wiring planning gate

- The user asked for a successful public submission to reach Codex, receive low-cost safety review and normalization, enter GitHub, and appear on the portal after approval.
- Codex confirmed the immediate outage: `.github/workflows/site-submission-intake.yml` exists on draft PR #6 but not on `main`, so GitHub returns `404` for the workflow-dispatch endpoint. The here.now `GITHUB_INTAKE_TOKEN`, GitHub `MARKETPLACE_INTAKE_TOKEN`, `HERENOW_API_KEY`, and `HERENOW_SITE_SLUG` configuration entries all exist.
- Codex chose the event-driven official Codex GitHub Action for the production worker. Native Codex Desktop automations are scheduled and require the local machine plus app to remain available, so an optional Desktop automation is limited to stalled-PR observability.

### Round 1

- Claude received the full revised `PLAN.md` in authenticated no-tools plan mode.
- The call produced no critique or verdict after repeated waits. Codex did not treat silence as `CLEAR` and moved to a compressed retry.

### Round 2

- Claude received a compressed architecture and security summary.
- The call again produced no critique or verdict after repeated waits. Codex did not treat silence as agreement and moved to one tightly bounded security question.

### Round 3 — Claude verdict: REVISE

Claude raised three concerns:

1. Schema-valid JSON can still contain semantically dangerous paths, URLs, or other values that trusted code acts upon.
2. Anonymous submitted Markdown can prompt-inject the model into returning manipulated but schema-valid values.
3. The API proxy and static model credential remain trust and exposure points.

`VERDICT: REVISE`

Codex response:

- Accepted concern 1. The plan now restricts model output to a single-line description, one exact category enum, and fixed advisory risk flags. Model output cannot control paths, filenames, URLs, commands, labels, approvals, or merges, and every value receives semantic validation.
- Accepted concern 2 as a threat-model correction. The model is explicitly not a trust boundary. It runs read-only with no write token; the submitted body is preserved; trusted policy, pinned no-LLM SkillSpector, and human review remain authoritative.
- Accepted concern 3 within the official action's supported model. The action will be pinned by commit, use a dedicated low-budget OpenAI project key, retain `drop-sudo`, run in a read-only sandbox as the final job step, and pass output to a separate deterministic write job that never receives the OpenAI key.

### Round 4 — Claude verdict: REVISE

Claude found nine remaining concerns:

1. The phrase `semantic validation` did not say whether validation was deterministic or another model call.
2. Byte preservation could have a time-of-check/time-of-use race if the PR branch changed between jobs.
3. The write token's repository-wide blast radius remained material.
4. Unexpected files in the one-skill diff needed an explicit fail-closed rule.
5. OpenAI budget exhaustion needed a visible fallback behavior.
6. Prompt injection could still manipulate the advisory category or risk flags.
7. Unicode format characters could spoof rendered descriptions.
8. A hardcoded category enum could drift from the validator.
9. Anonymous submissions could exhaust model budget without a rate boundary.

`VERDICT: REVISE`

Codex response:

- Accepted concerns 1, 2, 4, 5, 6, 7, and 8. Validation is now explicitly deterministic; both jobs bind to the event-time head SHA and fail if it changes; unexpected diffs fail closed; model failure leaves a visible failed run and raw draft for manual normalization; prompt injection is documented as advisory-data risk; descriptions require NFC and reject Unicode control/format categories; and category validation imports the trusted validator's live allowlist.
- Accepted concern 3 as a residual platform constraint. GitHub does not provide path-scoped repository write tokens, while pushes made with the short-lived `GITHUB_TOKEN` would not trigger the required follow-on workflow. The existing fine-grained token will be limited to this repository's contents and pull requests and exposed only to the small deterministic apply job.
- Partly accepted concern 9. The workflow runs only once per newly opened server-marked submission PR, here.now already enforces `6/hour/IP`, and the dedicated OpenAI project has a spend cap. A global Actions concurrency group would silently replace queued runs, so it is rejected; distributed denial-of-service remains documented residual risk rather than adding a database-backed quota system to RF-100.

### Round 5 — Claude verdict: REVISE

Claude raised three final concerns:

1. The fine-grained write token needed explicit handling and exposure limits.
2. The apply job needed an explicit second deterministic validation of model output immediately before writing.
3. The allowed post-normalization diff needed a machine-checkable definition.

`VERDICT: REVISE`

Codex response:

- Accepted concern 2. The apply job now explicitly re-validates the actual model output immediately before applying it.
- Accepted concern 3 and corrected Claude's proposed two-file shape to this repository's real generated-output contract. The only allowed paths relative to `main` are the submitted `SKILL.md`, its `marketplace.json`, `site/catalog.json`, and the new skill ZIP. No deletions, renames, symlinks, executable modes, unrelated archives, or other paths may change. ZIP creation becomes deterministic so old bundles remain byte-stable.
- Partly accepted concern 1. The token will be stored as a repository secret, unavailable to the model job, omitted from checkout via `persist-credentials: false`, and exposed only to the final push step. Claude's requested branch-scoped fine-grained PAT is not a GitHub capability; the repository-scoped token remains necessary because a short-lived `GITHUB_TOKEN` push would not trigger the required follow-on checks.
- The five-round review cap is reached without `CLEAR`. The remaining disagreement is the unavailable branch/path-scoped token, so Codex is presenting the tightened plan and this residual platform constraint for user signoff rather than inventing consensus.

## 2026-06-23 — Always-on Codex automation revision

- The user confirmed the Mac mini is always on and explicitly approved treating it as a production dependency, so Codex replaced the API-backed GitHub Action plan with an hourly native Codex project automation.
- GitHub remains the durable intake queue because native Codex automations are scheduled rather than webhook-triggered.
- The revised plan uses the lowest-cost selectable Codex model, one PR per run, a dedicated worktree, a project-local review skill, deterministic exact-diff helpers, unchanged required checks, and mandatory human merge.
- The user's message is treated as signoff for this architecture. Codex will pause only if the review identifies a new material product decision.

### Review rounds 1 and 2

- Claude received the full native-automation plan and then a compressed architecture review prompt in authenticated no-tools plan mode.
- Both calls produced no critique or verdict after repeated waits. Codex did not treat silence as `CLEAR` and moved to a minimal security question.

### Review round 3 — Claude verdict: REVISE

Claude identified three blockers for an unattended local agent with GitHub write access:

1. Pull-request automation must not let anonymous content modify workflow or policy files that CI may execute with repository privileges.
2. Exact-diff enforcement is only a boundary if anonymous text never controls paths, commands, commit metadata, or the enforcement step itself.
3. A broad local GitHub credential lets a prompt-injected agent mutate branches, workflows, or repository configuration outside the intended submission branch.

`VERDICT: REVISE`

Codex response:

- The first two concerns are addressed by the existing trusted-main `pull_request_target` design, fixed submission paths, candidate-scope validation, no execution, static SkillSpector, and the planned exact-diff helper.
- The third concern is confirmed by live configuration and is a material blocker: the Mac's active `gh` token has classic `repo` and `workflow` scopes. A native full-access automation reading anonymous text would inherit substantially more authority than the task requires, and deterministic helpers cannot prevent the agent from bypassing them before a push.
- The always-on Mac resolves availability but not credential isolation. Codex paused implementation as promised because the user must choose between the safer event-driven Codex GitHub Action with separated model/write jobs, or additional local isolation such as a dedicated automation account and narrow credential.

## 2026-06-23 — Local folder-triggered intake revision

- The user clarified the desired product flow: upload on here.now, save into a designated Mac mini folder, trigger Codex when a file arrives, push the reviewed skill to GitHub, and republish the portal.
- Current here.now documentation confirms private Drives, path-scoped write tokens, presigned staged uploads, ETag-protected finalization/moves, and owner-side export. GitHub Pages would not add storage or local delivery, so here.now remains the better host.
- Current Codex documentation confirms native App automations are scheduled rather than filesystem-triggered, while `codex exec` is the supported non-interactive pipeline surface. The revised design uses `launchd` for the file trigger and an isolated, schema-constrained Codex CLI review.
- The revised security boundary removes both broad local `gh` access and ChatGPT-managed `auth.json` from the untrusted review process. A dedicated API key reaches only the Codex parent process, model-proposed subprocesses inherit no secrets, a deny-all tool hook blocks tool use, and a deterministic publisher holds only a repository deploy key.

### Review rounds 1 and 2

- Claude received the full local-folder plan and then a compressed architecture prompt in authenticated no-tools plan mode.
- Both calls produced no critique or verdict after repeated waits. Codex did not treat silence as `CLEAR` and moved to a single-risk review.

### Review round 3 — Claude verdict: REVISE

- Claude identified prompt injection as the largest risk, asserting that Codex was the only validation gate and that the publisher would commit its JSON verbatim.
- Claude recommended deterministic input/output validation and a source content hash.

`VERDICT: REVISE`

Codex response:

- The central assertion is rejected as factually inconsistent with the plan. Codex is advisory only; its output is restricted to description, one category enum, and fixed risk flags, then deterministically schema- and value-validated. It cannot approve or merge. The raw body is preserved, exact-diff validation runs, pinned no-LLM SkillSpector remains required, and a human reviews the draft PR before publication.
- The source-traceability recommendation is accepted. The staged SHA-256 is rechecked after download and recorded in local state, fixed commit metadata, and the PR body. Any mismatch fails closed.
- Prompt injection remains a residual data-quality risk for description/category suggestions, not a code-execution or publication boundary.

### Review round 4 — Claude verdict: CLEAR

- Claude re-reviewed the corrected boundary and agreed that prompt injection can affect only bounded advisory metadata.
- With no tools or GitHub credentials available to Codex, deterministic schema/value/hash/diff validation, preserved raw instructions, pinned no-LLM SkillSpector, and mandatory human merge, the residual risk is equivalent to a contributor supplying misleading metadata rather than a publication or code-execution bypass.

`VERDICT: CLEAR`

- The plan is ready for the user's final signoff before implementation.
