# Intake Pipeline Setup

This guide covers the one-time setup required before the Mac mini intake
pipeline can process public submissions end to end.

## Architecture

```
Browser → here.now proxy (/api/intake/submit)
        → Cloudflare Tunnel (stable public URL)
        → intake_server.py (localhost:8765)
        → var/intake/inbox/<uuid>/
        → launchd QueueDirectories watcher
        → local_review.py (Codex review)
        → submission_publisher.py (SSH push → GitHub draft PR)
```

## Prerequisites

- Mac mini that stays powered on
- Cloudflare account (free tier is enough for a named tunnel)
- GitHub repository `FilhoRicardo/esg-skills-marketplace`
- Codex CLI (`npm install -g @openai/codex` or equivalent)
- Python 3.10+

---

## Step 1 — Generate the shared intake secret

This secret authenticates the here.now proxy to your Mac mini. It is never
visible to the browser.

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Save the output — you will use it in Step 2 and Step 4.

---

## Step 2 — Store the secret as a here.now account variable

```bash
curl -sS -X PUT https://here.now/api/v1/me/variables/MAC_MINI_INTAKE_SECRET \
  -H "Authorization: Bearer $(cat ~/.herenow/credentials)" \
  -H "Content-Type: application/json" \
  -d '{"value": "PASTE_SECRET_HERE"}'
```

here.now injects this as `Authorization: Bearer <secret>` into every proxied
request. The browser never sees it.

---

## Step 3 — Create a named Cloudflare Tunnel

Install `cloudflared`:
```bash
brew install cloudflare/cloudflare/cloudflared
```

Authenticate and create the tunnel (requires a domain on Cloudflare):
```bash
cloudflared tunnel login
cloudflared tunnel create esg-intake
```

Route traffic to the tunnel:
```bash
cloudflared tunnel route dns esg-intake esg-intake.yourdomain.com
```

Create `~/.cloudflared/config.yml`:
```yaml
tunnel: esg-intake
credentials-file: /Users/ricardofilho/.cloudflared/<tunnel-id>.json

ingress:
  - hostname: esg-intake.yourdomain.com
    service: http://localhost:8765
  - service: http_status:404
```

Start the tunnel (it will run as a LaunchAgent after Step 5):
```bash
cloudflared tunnel run esg-intake
```

**No custom domain?** Use the free quick-tunnel for testing:
```bash
cloudflared tunnel --url http://localhost:8765
```
It prints a temporary `*.trycloudflare.com` URL. Fine for smoke tests but
restarts generate a new URL — use a named tunnel for production.

---

## Step 4 — Update proxy.json with the tunnel hostname

Edit `site/.herenow/proxy.json` and replace `REPLACE_WITH_TUNNEL_URL` with
your tunnel hostname (e.g. `esg-intake.yourdomain.com`). Do **not** add a
scheme prefix — the entry must look like:

```json
"upstream": "https://esg-intake.yourdomain.com/intake"
```

Then redeploy the site:

```bash
python3 scripts/publish_site.py
```

---

## Step 5 — Configure and load the intake server LaunchAgent

Edit `launchd/com.esg-marketplace.intake-server.plist`:
- Set `MAC_MINI_INTAKE_SECRET` to the secret from Step 1

```bash
mkdir -p ~/Library/Logs/esg-marketplace
cp launchd/com.esg-marketplace.intake-server.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.esg-marketplace.intake-server.plist
```

Verify it started:
```bash
curl -s http://localhost:8765/health
# → {"ok": true}
```

Install the Cloudflare Tunnel as a LaunchAgent too:
```bash
cloudflared service install
```

---

## Step 6 — Obtain a dedicated OpenAI API key for Codex review

1. Go to platform.openai.com → Projects → create a new project named
   `ESG Marketplace Intake`.
2. Create a new API key scoped to that project.
3. Set a **monthly spend limit** (e.g. $5) in the project settings.
4. Copy the key — you will paste it into the reviewer LaunchAgent below.

---

## Step 7 — Create an SSH deploy key for GitHub

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

## Step 8 — Configure and load the reviewer LaunchAgent

Edit `launchd/com.esg-marketplace.reviewer.plist`:
- Set `CODEX_API_KEY` to the OpenAI key from Step 6

```bash
cp launchd/com.esg-marketplace.reviewer.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.esg-marketplace.reviewer.plist
```

---

## Step 9 — End-to-end smoke test

1. Submit a test skill through the live site.
2. Within seconds the intake server logs `Queued: <uuid>`.
3. The reviewer watcher triggers and runs Codex review.
4. The publisher pushes a `submission-reviewed/<slug>-<id>` branch.
5. The GitHub workflow opens a draft PR.
6. Close the smoke-test PR and delete the branch without merging.

Check logs at any step:
```bash
tail -f ~/Library/Logs/esg-marketplace/intake-server.log
tail -f ~/Library/Logs/esg-marketplace/reviewer.log
```

---

## Secret rotation

To rotate the shared secret:

1. Generate a new secret (Step 1).
2. Update the `MAC_MINI_INTAKE_SECRET` here.now variable (Step 2).
3. Update `MAC_MINI_INTAKE_SECRET` in the intake server LaunchAgent and reload:
   ```bash
   launchctl unload ~/Library/LaunchAgents/com.esg-marketplace.intake-server.plist
   # edit plist — update MAC_MINI_INTAKE_SECRET
   launchctl load ~/Library/LaunchAgents/com.esg-marketplace.intake-server.plist
   ```
4. Redeploy the site so the proxy picks up the new variable (Step 4).
