# ESG Skills Marketplace

A curated catalogue of Codex-compatible skills for environmental, social, and governance (ESG) work.

The marketplace is intentionally conservative. The public site is the front door: approved skills download directly from the site, and new submissions can be queued from the site without exposing repository scaffolding. GitHub still remains the source of truth behind the scenes: every submission becomes a draft pull request, is checked automatically, reviewed by a human, and is published only after merge to `main`.

## Trust gate

Every proposed skill must pass five gates:

1. **Restricted format** — v1 accepts text-only bundles. Executables, binaries, symlinks, hidden files, and dependency manifests are rejected.
2. **Structural policy** — deterministic checks enforce naming, frontmatter, allowed paths, file sizes, and catalogue consistency.
3. **Security scan** — [NVIDIA SkillSpector](https://github.com/NVIDIA/SkillSpector) runs static analysis from a pinned commit without executing submitted content.
4. **Human review** — GitHub requests review from `@FilhoRicardo`; the reviewer reads the changes and the scanner report.
5. **Protected merge** — only approved pull requests with all required checks can enter `main`. The public catalogue reads only merged content.

These controls reduce risk; they do not prove that a skill is safe or correct. SkillSpector documents limits including no dynamic execution and possible false positives or missed attacks. Users should still read a skill before installing it and apply normal professional judgement.

## Browse or contribute

- Open the permanent [ESG Skills Marketplace catalogue](https://royal-bugle-xgg7.here.now/).
- Download approved skills from the public catalogue.
- Submit any Markdown skill instructions with a public title. The maintainer normalizes frontmatter and assigns the category during review.
- Read the beginner-friendly [contribution guide](CONTRIBUTING.md) if you want the repository-first fallback.
- Use the [skill template](templates/skill-template/) to prepare a bundle.
- Maintainers follow the [owner review runbook](docs/OWNER-RUNBOOK.md).
- Maintainers configure and operate the hidden intake/deploy path through [site operations](docs/SITE-OPERATIONS.md).

## Current catalogue

- **ESG materiality brief** — turns supplied business and stakeholder evidence into a traceable briefing with explicit uncertainty.
- **GHG inventory evidence pack** — organizes supplied activity data, factors, calculations, and source notes for internal review.

Both workflows organize evidence. They do not provide legal, financial, compliance, certification, audit, or assurance advice.

## Repository structure

```text
skills/                    Approved skill bundles
templates/skill-template/  Copyable submission template
scripts/                   Deterministic policy and catalogue tools
site/                      Static public catalogue, download bundles, and hidden intake proxy
tests/                     Policy tests
.github/                   Review ownership and required CI checks
```

## Security tooling

CI pins NVIDIA SkillSpector to commit `a5092dd9b9521ff57a9b53612bb129ce78019002` (Apache-2.0) and installs its frozen dependency lockfile with uv `0.11.14`. Updating either pin requires a maintainer platform change and a fresh review.

## Licence

Repository code and original templates are available under the [MIT License](LICENSE). Individual submitted skills must be original or redistributable under compatible terms.
