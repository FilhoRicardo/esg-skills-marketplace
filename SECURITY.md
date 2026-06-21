# Security policy

## Trust boundary

All pull-request content is untrusted. Reviewers must inspect it in GitHub and must not install, execute, or open submitted files in privileged desktop applications.

V1 accepts text-only skills. The policy validator rejects executable bits, scripts, binaries, images, documents, archives, symlinks, Git submodules, hidden files, invisible Unicode controls, dependency manifests, oversized files, and changes outside one skill bundle from external contributors.

## Automated analysis

[NVIDIA SkillSpector](https://github.com/NVIDIA/SkillSpector) is installed from pinned commit `a5092dd9b9521ff57a9b53612bb129ce78019002` using its frozen lockfile and pinned uv `0.11.14`, then run with `--no-llm`. CI parses the JSON report and fails unless the recommendation is `SAFE`.

The scan does not execute contributed content and receives no repository secrets. The GitHub workflow has read-only repository permissions.

## Limits

Automated checks and human review reduce risk but cannot guarantee safety, correctness, regulatory compliance, or fitness for a particular purpose. SkillSpector does not dynamically execute skills and may miss attacks or report false positives.

## Reporting a vulnerability

Do not open a public issue for an active vulnerability that could put users at risk. Use GitHub's private vulnerability reporting feature on the repository Security page. Include the affected skill, the risk, reproduction details that do not expose secrets, and a suggested mitigation when available.
