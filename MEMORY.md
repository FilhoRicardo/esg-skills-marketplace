# ESG Skills Marketplace Memory

## Contacts

_None recorded yet._

## Source Links

- here.now documentation: https://here.now/docs
- GitHub repository: https://github.com/FilhoRicardo/esg-skills-marketplace
- Linear project: https://linear.app/rf-ai-workspace/project/esg-skills-marketplace-2a2095348777
- First implementation issue: https://linear.app/rf-ai-workspace/issue/RF-99/initialize-esg-skills-marketplace
- Security scanner: https://github.com/NVIDIA/SkillSpector

## Key Decisions

- The first release is a public, curated catalogue of Codex-compatible environmental, social, and governance skills; accounts, payments, ratings, and open submissions are out of scope.
- GitHub will store the public skills and source files, while a public here.now site will provide the catalogue frontend.
- The frontend uses Aster by default. Graphify will be prepared after the repository exists and ignore rules are safe.
- Contributions enter through GitHub pull requests. V1 accepts text-only skill bundles; structural checks, NVIDIA SkillSpector pinned at commit `a5092dd9b9521ff57a9b53612bb129ce78019002`, and approval from `@FilhoRicardo` are required before merge and publication.
- Automated review reduces risk but cannot guarantee a skill is safe; runtime execution and language-model analysis are not part of the initial public pull-request check.

## Durable Outcomes

- The public GitHub repository, Linear project, and first issue `RF-99` were created on 2026-06-21.
