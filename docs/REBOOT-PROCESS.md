# Reboot Process

After the Mac mini reboots, the Cloudflare quick tunnel gets a new URL.
The intake server and tunnel start automatically, but the here.now proxy
must be updated with the new URL before the site can accept submissions again.

## Steps (takes ~2 minutes)

### 1. Find the new tunnel URL

```bash
grep trycloudflare ~/Library/Logs/esg-marketplace/tunnel.log | tail -1
```

Extract the hostname, e.g. `abc-def-123.trycloudflare.com`.

### 2. Verify the tunnel and server are up

```bash
curl -s http://localhost:8766/health
curl -s https://<new-tunnel-hostname>/health
```

Both should return `{"ok": true}`. If not, check:
```bash
launchctl list | grep esg-marketplace
```

To restart a service manually:
```bash
launchctl stop com.esg-marketplace.intake-server
launchctl start com.esg-marketplace.intake-server

launchctl stop com.esg-marketplace.tunnel
launchctl start com.esg-marketplace.tunnel
```

### 3. Update proxy.json

Edit `site/.herenow/proxy.json` and replace the old hostname with the new one:

```json
"upstream": "https://<new-tunnel-hostname>/intake"
```

### 4. Redeploy the site

```bash
HERENOW_API_KEY=$(cat ~/.herenow/credentials) python3 scripts/publish_site.py site --slug royal-bugle-xgg7
```

### 5. Verify end-to-end

```bash
curl -s https://<new-tunnel-hostname>/health
```

Should return `{"ok": true}`. The site is now accepting submissions again.

---

## If you have Codex available

Tell Codex: "the Mac mini rebooted — update the tunnel URL and redeploy."
Codex will read this file and do steps 1–5 automatically.

---

## Services reference

| Label | What it does | Log |
|---|---|---|
| `com.esg-marketplace.intake-server` | HTTP server on :8766, writes to `skills-to-review/` | `~/Library/Logs/esg-marketplace/intake-server.log` |
| `com.esg-marketplace.tunnel` | Cloudflare quick tunnel → :8766 | `~/Library/Logs/esg-marketplace/tunnel.log` |

Both are LaunchAgents — they start on user login, not at system boot.
The Mac mini must be logged in for them to run.
