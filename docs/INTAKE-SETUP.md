# Intake Pipeline Setup

This guide covers the one-time setup required before the local folder-triggered
intake pipeline can process public submissions end to end.

## Prerequisites

- here.now authenticated account with API key in `~/.herenow/credentials`
- GitHub repository `FilhoRicardo/esg-skills-marketplace`
- Mac mini that remains powered on
- Codex CLI installed (`npm install -g @openai/codex` or equivalent)

---

## Step 1 — Create the ESG Skills Intake Drive

```bash
curl -sS https://here.now/api/v1/drives \
  -H "Authorization: Bearer $(cat ~/.herenow/credentials)" \
  -H "Content-Type: application/json" \
  -d '{"name": "ESG Skills Intake"}'
```

Note the returned `id` field (e.g. `drv_01abc...`). This is your `INTAKE_DRIVE_ID`.

---

## Step 2 — Mint a path-scoped write token for the site

The site proxy needs a write-only token scoped to `incoming/` only.

```bash
curl -sS https://here.now/api/v1/drives/INTAKE_DRIVE_ID/tokens \
  -H "Authorization: Bearer $(cat ~/.herenow/credentials)" \
  -H "Content-Type: application/json" \
  -d '{"perms": "write", "pathPrefix": "incoming/", "label": "site-intake-proxy"}'
```

The response includes `secret` — this is shown **only once**. Copy it immediately.

---

## Step 3 — Store the token as a here.now account variable

```bash
curl -sS -X PUT https://here.now/api/v1/me/variables/HERENOW_INTAKE_DRIVE_TOKEN \
  -H "Authorization: Bearer $(cat ~/.herenow/credentials)" \
  -H "Content-Type: application/json" \
  -d '{"value": "PASTE_TOKEN_SECRET_HERE"}'
```

---

## Step 4 — Update the proxy.json with the Drive ID

Edit `site/.herenow/proxy.json` and replace both occurrences of
`REPLACE_WITH_INTAKE_DRIVE_ID` with the actual Drive ID from Step 1.

Then redeploy the site:

```bash
python3 scripts/publish_site.py
```

Verify: submit a test bundle on the live site. The browser should complete
all three steps (stage → upload → finalize) without errors.

> **CORS note**: if the PUT to the presigned URL fails with a CORS error in
> the browser console, the Drive presigned URLs do not support cross-origin PUT
> from the browser. In that case, add a third proxy route `/api/intake/upload`
> that relays the bundle body to the Drive upload URL, and update `app.js` to
> use a single relay call instead of a direct PUT.

---

## Step 5 — Obtain a dedicated OpenAI API key for Codex review

1. Go to platform.openai.com → Projects → create a new project named
   `ESG Marketplace Intake`.
2. Create a new API key scoped to that project.
3. Set a **monthly spend limit** (e.g. $5) in the project settings.
4. Copy the key — you will paste it into the reviewer LaunchAgent below.

---

## Step 6 — Create an SSH deploy key for GitHub

```bash
ssh-keygen -t ed25519 -C "esg-marketplace-deploy" \
  -f ~/.ssh/esg-marketplace-deploy -N ""
```

Add the **public** key (`~/.ssh/esg-marketplace-deploy.pub`) to the GitHub
repository under Settings → Deploy keys → Add deploy key. Enable
**Allow write access**.

Verify:
```bash
GIT_SSH_COMMAND="ssh -i ~/.ssh/esg-marketplace-deploy -o StrictHostKeyChecking=accept-new" \
  git ls-remote git@github.com:FilhoRicardo/esg-skills-marketplace.git HEAD
```

---

## Step 7 — Configure and load the LaunchAgents

### Drive sync

Edit `launchd/com.esg-marketplace.drive-sync.plist`:
- Set `HERENOW_API_KEY` to your here.now owner API key
- Set `HERENOW_INTAKE_DRIVE_ID` to the Drive ID from Step 1

```bash
mkdir -p ~/Library/Logs/esg-marketplace
cp launchd/com.esg-marketplace.drive-sync.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.esg-marketplace.drive-sync.plist
```

### Reviewer watcher

Edit `launchd/com.esg-marketplace.reviewer.plist`:
- Set `CODEX_API_KEY` to the OpenAI key from Step 5

```bash
cp launchd/com.esg-marketplace.reviewer.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.esg-marketplace.reviewer.plist
```

---

## Step 8 — Verify the LaunchAgents survive reboot

```bash
# Force a sync run now
launchctl start com.esg-marketplace.drive-sync

# Check logs
tail -20 ~/Library/Logs/esg-marketplace/drive-sync.log
```

After reboot, confirm both agents are loaded:

```bash
launchctl list | grep esg-marketplace
```

---

## Step 9 — End-to-end smoke test

1. Submit a test skill through the live site.
2. Wait up to 60 seconds for the drive-sync agent to write it to
   `var/intake/inbox/`.
3. The reviewer watcher triggers automatically and runs Codex review.
4. The publisher pushes a `submission-reviewed/<slug>-<id>` branch.
5. The GitHub workflow opens a draft PR.
6. Close the smoke-test PR and delete the branch without merging.

---

## Token rotation

The Drive write token is stored once as a here.now variable. To rotate it:

1. Mint a new token (Step 2 above).
2. Update the `HERENOW_INTAKE_DRIVE_TOKEN` variable (Step 3 above).
3. Revoke the old token:
   ```bash
   curl -sS -X DELETE https://here.now/api/v1/drives/INTAKE_DRIVE_ID/tokens/OLD_TOKEN_ID \
     -H "Authorization: Bearer $(cat ~/.herenow/credentials)"
   ```

The token ID (not the secret) is visible in the token list:
```bash
curl -sS https://here.now/api/v1/drives/INTAKE_DRIVE_ID/tokens \
  -H "Authorization: Bearer $(cat ~/.herenow/credentials)"
```
