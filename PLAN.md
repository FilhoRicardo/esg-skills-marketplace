# Plan: Local Folder-Triggered Skill Intake

## Goal

Accept a skill on the here.now website, store it privately, materialize it in a designated inbox on the always-on Mac mini, trigger an isolated Codex review when the file arrives, push a bounded review branch to GitHub, and publish the approved skill back to here.now after human merge.

## Acceptance Criteria

- Work remains linked to `FilhoRicardo/esg-skills-marketplace`, the `ESG Skills Marketplace` Linear project, and RF-100.
- The public catalogue remains on the permanent here.now site; GitHub Pages is not introduced because it does not provide server-side intake or local file delivery.
- The public form uploads one validated JSON bundle to a private `ESG Skills Intake` here.now Drive under `incoming/`; the Drive token is write-only, path-scoped, stored as a here.now service variable, and never reaches browser JavaScript.
- The upload preserves the existing 40 KB Markdown limit, title, optional public name/contact, and attestations. A UUID path plus `ifNoneMatch: "*"` prevents overwrite collisions.
- A Mac mini sync job polls the Drive at most once per minute, atomically writes each bundle to `var/intake/inbox/<submission-id>/SKILL.md` plus `submission.json`, and moves the remote bundle from `incoming/` to `claimed/` only after the local write succeeds.
- The staged upload SHA-256 is rechecked after download and recorded in local state, the review branch commit, and the draft PR body; any mismatch fails closed.
- A macOS `launchd` queue watcher triggers when the inbox becomes non-empty and processes one submission at a time.
- The reviewer invokes `codex exec` with `gpt-5.4-mini`, low reasoning, a dedicated `CODEX_API_KEY`, a clean temporary HOME/CODEX_HOME, read-only sandboxing, disabled web search, no MCP/plugins, an empty tool environment, a deny-all `PreToolUse` hook, and a strict output schema.
- Submitted Markdown is passed as untrusted stdin data. Codex cannot execute it, edit files, access GitHub credentials, or control paths, commands, labels, approvals, or merge state.
- Codex may output only a single-line description, one existing allowed category, and fixed advisory risk flags. Trusted code deterministically validates every value.
- A separate deterministic publisher preserves the instruction body byte-for-byte, adds canonical frontmatter/category, rebuilds deterministic catalogue/download outputs, and permits exactly four changed paths relative to `main`.
- The publisher uses a dedicated repository SSH deploy key, not the Mac's broad `gh` token. It can push the review branch but cannot call the GitHub API or change repository settings.
- A trusted workflow on `main` reacts to `submission-reviewed/**` branch pushes, validates the exact diff, and opens or updates a draft pull request using GitHub's short-lived workflow token.
- Existing policy validation and pinned NVIDIA SkillSpector `--no-llm` scanning remain authoritative. Human approval and merge remain mandatory.
- Merge to `main` triggers the existing here.now deployment and the approved skill appears on the catalogue.
- Successful local items move to `var/intake/processed/` and remote `processed/`; ambiguous, rejected, or failed items move to `var/intake/needs-attention/` and remain unpublished.

## Approach

1. Create a private `ESG Skills Intake` Drive and mint a renewable write token restricted to `incoming/`. Store it as a here.now account variable allowed only to `here.now`.
2. Replace the GitHub workflow-dispatch proxy with two Drive proxy routes: stage upload and finalize upload. Update the browser submission handler to hash the JSON bundle, request a staged upload, PUT to the presigned URL, finalize it, and show a receipt id.
3. Add a local sync script that lists `incoming/`, downloads unseen bundles through the owner API, validates and writes them atomically under `var/intake/inbox/`, then moves claimed remote files with ETag protection.
4. Add a deterministic local reviewer runner and JSON schema. Run Codex from a clean temporary directory with a dedicated config and deny-all tool hook; pass the raw bundle through stdin and keep `CODEX_API_KEY` out of all model-proposed subprocess environments.
5. Add a deterministic normalizer/publisher that revalidates the source hash and model output, preserves body bytes, creates canonical frontmatter and category metadata, rebuilds deterministic outputs, verifies the exact diff, and pushes `submission-reviewed/<slug>-<id>` using a repository deploy key. Include the source SHA-256 in fixed commit and pull-request metadata.
6. Add a trusted branch-push workflow that validates the candidate using trusted `main` scripts and opens a draft PR. Keep the existing required policy and SkillSpector workflows unchanged.
7. Install two user LaunchAgents: a one-minute Drive sync and a `QueueDirectories` reviewer watcher. Keep logs bounded and exclude submitted content, contact data, keys, and tokens.
8. Test a controlled submission through the live form, observe it land in the local inbox, run through Codex and GitHub checks, then close the smoke-test PR and remove its branch without merging.
9. Land the production change, republish here.now, confirm the LaunchAgents survive logout/reboot, and complete one approved end-to-end publication only when a real reviewed skill is available.

## Key Decisions And Tradeoffs

- here.now stays because its private Drive, scoped tokens, and authenticated proxy solve the public-to-private handoff. GitHub Pages would still need the same external storage or webhook bridge.
- `launchd`, not a native Codex App automation, supplies the filesystem event trigger. The triggered reviewer is Codex CLI in non-interactive mode, which is the supported pipeline surface.
- A dedicated API key is used instead of ChatGPT-managed `auth.json`; official Codex guidance recommends API keys for automation touching public/open-source repositories.
- The model is deliberately separated from GitHub credentials and file writes. Its only product is schema-constrained advisory metadata.
- The deterministic publisher, required checks, and human merge are the security boundary.
- Drive polling adds up to one minute of delivery latency but avoids exposing the Mac mini through a public tunnel.
- Processing is serial to keep costs and race conditions bounded.

## Risks And Unknowns

- Browser PUT support for the Drive presigned upload URL must be verified for CORS before implementation is considered complete. If it is not supported, use a minimal authenticated upload relay; do not reduce the 40 KB limit to Site Data's 16 KB record cap silently.
- `CODEX_API_KEY` is not configured yet. The user must provide a dedicated key with a low project spend limit before the reviewer can run end to end.
- The deploy key can push any unprotected branch in the repository. The publisher must construct paths and git arguments itself, use no shell interpolation from model output, and fail closed on any unexpected diff.
- A malicious submission can manipulate the advisory description/category/risk flags, but cannot execute tools or publish; human review remains required.
- The Mac mini, here.now API key, local LaunchAgents, network connection, and Codex CLI become production dependencies. Failures must leave recoverable files in `needs-attention/`.
- here.now Drive tokens are shown only once. The setup must store the scoped token directly as a service variable and record only its token id/expiry for rotation.

## Out Of Scope

- Exposing the Mac mini through Cloudflare Tunnel, ngrok, or a public webhook.
- GitHub Pages migration.
- Executing submitted skills or installing dependencies.
- Auto-merge, auto-approval, or bypassing required checks.
- Accounts, public submission status pages, email notifications, ratings, or payments.
- Rewriting contributor instructions or expanding the category taxonomy.

## Verification

- Unit tests for bundle validation, source-hash mismatch, atomic inbox writes, ETag/idempotency behavior, claim/retry state, schema and Unicode validation, body preservation, exact diff allowlisting, deterministic ZIP output, and safe subprocess argument construction.
- Verify the deny-all Codex hook blocks Bash, apply-patch, and MCP tool attempts; verify web search and user config/plugins are disabled.
- Run a malicious prompt-injection fixture and confirm the only accepted output is the bounded JSON schema.
- `python3 scripts/build_catalog.py --check`
- `python3 scripts/validate_skills.py --all`
- `python3 -m unittest discover -s tests`
- Pinned NVIDIA SkillSpector scan with `--no-llm` and `SAFE` required.
- Validate both LaunchAgent plists and test restart/reboot loading.
- gstack `/browse` verification of Drive staging, presigned upload, finalization, success/error states, and responsive layout.
- GitHub verification that only the expected branch/diff can create a draft PR and that required checks block merge on failure.
- Live here.now verification that a merged approved skill appears as a downloadable catalogue entry.

## GitHub, Linear, And Memory Impact

- GitHub: update PR #6 with Drive-backed intake, local automation scripts/config, trusted branch-push PR workflow, deterministic bundles, tests, and operations guidance; keep human merge and current required checks.
- Linear: RF-100 remains the active linked issue because this implements hidden intake, local automated review, and post-merge publication.
- Memory: record here.now Drive as the private inbox, `var/intake/` as the local handoff folder, launchd-triggered isolated Codex review, deploy-key publishing, and human merge as the release gate.
