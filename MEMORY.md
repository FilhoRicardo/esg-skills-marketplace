# ESG Skills Marketplace Memory

## Contacts

_None recorded yet._

## Source Links

- here.now documentation: https://here.now/docs
- GitHub repository: https://github.com/FilhoRicardo/esg-skills-marketplace
- Linear project: https://linear.app/rf-ai-workspace/project/esg-skills-marketplace-2a2095348777
- First implementation issue: https://linear.app/rf-ai-workspace/issue/RF-99/initialize-esg-skills-marketplace
- Site-first submission issue: https://linear.app/rf-ai-workspace/issue/RF-100/add-site-native-skill-download-and-submission-flow
- Permanent catalogue: https://royal-bugle-xgg7.here.now/
- Security scanner: https://github.com/NVIDIA/SkillSpector

## Key Decisions

- The first release is a public, curated catalogue of Codex-compatible environmental, social, and governance skills; accounts, payments, ratings, and open submissions are out of scope.
- GitHub will store the public skills and source files, while a public here.now site will provide the catalogue frontend.
- The frontend uses Aster by default. Graphify will be prepared after the repository exists and ignore rules are safe.
- Contributions enter through GitHub pull requests. V1 accepts text-only skill bundles; structural checks, NVIDIA SkillSpector pinned at commit `a5092dd9b9521ff57a9b53612bb129ce78019002`, and approval from `@FilhoRicardo` are required before merge and publication.
- Automated review reduces risk but cannot guarantee a skill is safe; runtime execution and language-model analysis are not part of the initial public pull-request check.

## Durable Outcomes

- The public GitHub repository, Linear project, and first issue `RF-99` were created on 2026-06-21.
- V1 was published permanently through authenticated here.now hosting on 2026-06-22 with the `esg-materiality-brief` and `ghg-inventory-evidence-pack` skills; the deleted-platform-file scope regression is covered and the Aster catalogue is browser-verified.
- The trust-gate workflow was narrowed on 2026-06-22 to `opened`, `synchronize`, and `reopened` pull-request events so draft-to-ready transitions do not queue a redundant post-merge race against the deleted merge ref.
- RF-100 was created on 2026-06-22 to add site-native skill downloads, a site-native submission flow, hidden GitHub intake orchestration, and post-merge republishing from the public site surface.
- RF-100's public UX was redesigned on 2026-06-22 using the selected Calm Ledger direction: the catalogue and submission now have separate responsive pages, direct downloads and live file preview were browser-verified, and the branch snapshot is published at the permanent here.now slug.
- The public intake was simplified on 2026-06-22 so contributors upload only `SKILL.md` and enter a public title. Category assignment now happens during draft review, and strict repository validation prevents publication until the maintainer adds an allowed category and rebuilds the catalogue.
