# Site operations

This is the maintainer setup for the site-native download and submission flow.

## What the public site does

- serves reviewed skill downloads directly from the live catalogue;
- accepts `SKILL.md` and a public title from the site-native submission form, then generates title-only intake metadata before dispatch;
- forwards only one hidden path, `/api/submit-skill`, through a here.now proxy route;
- relies on GitHub Actions to create the draft pull request and on `main` deploys to republish the site.

## Required GitHub configuration

Set these repository secrets and variables:

- `MARKETPLACE_INTAKE_TOKEN`
  - a token that can dispatch workflows, push branches, and open pull requests in `FilhoRicardo/esg-skills-marketplace`;
  - this must be a real token secret rather than `GITHUB_TOKEN`, because the created pull request still needs to trigger the required trust-check workflows.
- `HERENOW_API_KEY`
  - the authenticated here.now API key used to republish the permanent public site from `main`.
- `HERENOW_SITE_SLUG`
  - the permanent here.now slug for the live marketplace site.

## Required here.now configuration

On the here.now account that owns the public site, create this variable:

- `GITHUB_INTAKE_TOKEN`
  - the token injected into `site/.herenow/proxy.json`;
  - restrict `allowedUpstreams` to `api.github.com`.

The proxy manifest is committed in `site/.herenow/proxy.json`. here.now does not serve this file publicly, but it is still part of the published site bundle and should stay narrow.

## Safety boundaries

- The public site never receives a broad GitHub API proxy surface.
- The proxy manifest exposes one exact path only: `/api/submit-skill`.
- Rate limiting is applied at the proxy route.
- The intake workflow writes only the submitted skill folder. The draft remains blocked until a maintainer assigns a category and regenerates the catalogue artefacts.
- Publication still requires the trust checks, human review, and merge to `main`.

## Operational checks

After changing the submission or deploy path:

1. Run `python3 scripts/build_catalog.py`.
2. Run `python3 scripts/build_catalog.py --check`.
3. Run `python3 scripts/validate_skills.py --all`.
4. Run `python3 -m unittest discover -s tests`.
5. Verify the form and downloads in the browser.
6. Verify a real site submission creates a draft pull request.
7. Verify a merged change to `main` republishes the permanent here.now site.

The HTML uses a versioned `app.js` URL because here.now may retain a prior static asset between rapid updates. Bump the version whenever submission behavior changes.
