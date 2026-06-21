# Plan: Launch the ESG Skills Marketplace

## Goal

Launch a small public catalogue that helps people discover and download Codex-compatible environmental, social, and governance (ESG) skills from a public GitHub repository, presented through a permanent public here.now site.

## Acceptance Criteria

- The managed project scaffold is registered in the Projects workspace with clear GitHub, Linear, Aster, Graphify, and memory guidance.
- A public GitHub repository named `esg-skills-marketplace` contains the skills collection and catalogue source.
- The repository uses a simple documented structure for `skills/`, `site/`, and a catalogue data file, plus a reusable skill template and contribution instructions.
- Contributors propose skills through pull requests; there is no direct upload-to-publication path.
- V1 skills are text-only and cannot contain executables, binaries, symlinks, hidden files, or dependency manifests.
- Every proposed skill passes structural validation and NVIDIA SkillSpector static analysis before it can be approved.
- `main` requires passing checks, resolved conversations, and code-owner approval from `@FilhoRicardo` before merge.
- The catalogue frontend uses Aster, explains what the collection is, lists available skills from local catalogue data, links each listing to its GitHub skill folder, and handles an empty catalogue honestly.
- The first release requires no account, payment, rating, submission workflow, database, framework, or build service.
- The static frontend passes desktop and mobile checks in Chrome with no blocking console errors or broken primary links.
- The verified site is published permanently to here.now and its live URL is recorded in project memory and the repository documentation.
- A Linear project and first implementation issue record the approved scope and acceptance criteria.
- The repository uses the MIT License unless the user changes that choice at signoff.

## Approach

1. Create and link the public GitHub repository, Linear project, and first Linear issue.
2. Keep the repository framework-free: store text-only skills under `skills/<slug>/SKILL.md`, catalogue metadata in one JSON file, and the static frontend under `site/`.
3. Add a deterministic validator for allowed paths, text-only files, size limits, frontmatter, slug consistency, duplicate entries, and catalogue integrity.
4. Pin NVIDIA SkillSpector to reviewed commit `a5092dd9b9521ff57a9b53612bb129ce78019002`; run static analysis on proposed skills and fail the required check unless its recommendation is `SAFE`.
5. Add CODEOWNERS, a pull-request template, contributor instructions, and protected-branch rules that require checks and approval from `@FilhoRicardo`.
6. Build a single responsive catalogue page using semantic HTML, small vanilla JavaScript for loading the catalogue JSON, and Aster-based CSS. Render only content merged into `main`.
7. Verify locally in Chrome at desktop and mobile widths, then publish the `site/` directory through the here.now helper.
8. Configure Graphify hooks after ignore rules are confirmed safe and build the initial graph once code exists.

## Key Decisions And Tradeoffs

- A curated catalogue is the v1 marketplace model. This avoids prematurely building commerce, identity, moderation, and submission systems.
- GitHub is the source of truth for skills. The here.now site is a discovery layer, not a second package registry.
- A framework-free static site keeps hosting and maintenance small. Client-side loading of one local catalogue JSON file avoids a generator or backend.
- MIT is recommended because the collection is intended for broad reuse and contains both instructional and code-like material; this is a product choice, not legal advice.
- The first publish must be authenticated so the site is permanent. If here.now credentials are unavailable, Codex will pause for the documented email-code sign-in flow rather than launch an expiring site.
- SkillSpector is a required security signal, not a safety guarantee. It is pinned by commit, runs without executing contributed content, and is combined with restrictive file policy and human approval.
- V1 rejects executable skills entirely. This sacrifices flexibility to make review understandable and materially reduce supply-chain risk.

## Risks And Unknowns

- No initial ESG skills have been specified. The first site may ship with an honest empty state and a skill template unless the user supplies or requests seed skills.
- Public skills may be mistaken for legal, financial, compliance, or assurance advice. Copy and contribution rules must avoid unsupported claims and state the boundary clearly.
- Repository licensing does not prove that every future contribution is original or safe to redistribute; contribution guidance must require contributors to confirm rights.
- The final here.now URL is unknown until authenticated publishing succeeds.
- SkillSpector does not perform dynamic execution, may miss non-English or image-based attacks, and has false positives. Review documentation must state these limits plainly.

## Out Of Scope

- Payments, subscriptions, accounts, ratings, reviews, analytics, and personalised recommendations.
- Open self-service submissions, moderation queues, or a contributor portal.
- A package manager, remote installer, backend API, database, or automated GitHub ingestion.
- Creating the first substantive ESG skills without a separate approved scope.
- Executable scripts, binaries, dependency manifests, symlinks, and non-text attachments inside contributed skills.
- Custom domains and project-specific branding.

## Verification

- Confirm the expected scaffold and repository paths exist and no placeholders remain where links are known.
- Validate catalogue JSON syntax and confirm every listed skill path resolves to a repository folder containing `SKILL.md`.
- Confirm rejected fixtures fail the structural validator and safe fixtures pass.
- Run pinned SkillSpector against every proposed skill, retain its report, and confirm any non-`SAFE` recommendation blocks the check.
- Serve `site/` locally and use Chrome to verify the page content, skill links, empty state, mobile layout, keyboard navigation, and console output.
- Publish with the here.now helper, then reload the returned live URL in Chrome and repeat the primary checks.
- Confirm the GitHub remote, Linear project URL, first issue identifier, here.now URL, Routing Map entry, `PROJECTS.md` row, and durable memory entries.

## GitHub, Linear, And Memory Impact

- GitHub: `https://github.com/FilhoRicardo/esg-skills-marketplace`.
- Linear: project `ESG Skills Marketplace`; first issue `RF-99` (`Initialize ESG Skills Marketplace`).
- Memory: record the approved v1 boundaries, MIT license choice, GitHub and Linear links, here.now URL, Aster adoption, and Graphify setup as they become durable facts.
