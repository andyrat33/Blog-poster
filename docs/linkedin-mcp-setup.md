# LinkedIn MCP Server — Setup Guide

## What It Does

The LinkedIn MCP server lets Claude Code post to LinkedIn directly mid-conversation. No copy-pasting. You ask Claude to post, it calls the `post_to_linkedin` tool, and the post goes live.

## Files

| File | Purpose |
|------|---------|
| `linkedin_mcp.py` | The MCP server. Exposes `post_to_linkedin` as a tool. |
| `linkedin_auth.py` | OAuth flow. Run once to authenticate. |
| `linkedin_credentials.json` | Your LinkedIn app credentials (not committed). |
| `linkedin_token.json` | Cached OAuth token (not committed). |
| `.mcp.json` | Tells Claude Code to load the server on startup. |
| `linkedin_credentials.json.template` | Template — copy and fill in. |

---

## One-Time Setup

### 1. Create a LinkedIn Developer App

1. Go to https://www.linkedin.com/developers/apps → **Create app**
2. Fill in the name and associate with your LinkedIn page
3. **Auth tab** → OAuth 2.0 Settings → add redirect URI exactly:
   ```
   http://localhost:8765/callback
   ```
4. **Auth tab** → Request access for scopes: `openid`, `profile`, `w_member_social`
5. **Products tab** → request **"Share on LinkedIn"** (this grants `w_member_social`)
6. Copy your **Client ID** and **Client Secret**

### 2. Create `linkedin_credentials.json`

Copy the template:

```bash
cp linkedin_credentials.json.template linkedin_credentials.json
```

Fill in your values:

```json
{
  "client_id": "your_client_id_here",
  "client_secret": "your_client_secret_here",
  "redirect_uri": "http://localhost:8765/callback"
}
```

The redirect URI must match exactly what you entered in the LinkedIn app.

### 3. Authenticate

Run the auth script once:

```bash
python3 linkedin_auth.py
```

A browser window opens. Log in to LinkedIn and click **Allow**. The script captures the OAuth callback and saves `linkedin_token.json`. You should see:

```
Token saved to linkedin_token.json
Authentication complete. You can now use the LinkedIn MCP server.
```

**If the browser redirect fails** (connection refused page), the script falls back to manual entry — copy the full URL from the browser address bar and paste it into the terminal when prompted.

### 4. Restart Claude Code

The MCP server is loaded at startup via `.mcp.json`. Restart Claude Code to pick it up, then run `/mcp` — you should see `linkedin-poster` listed as connected.

---

## Day-to-Day Usage

### Generate post variations

Use the `linkedin-post` skill:

```
/linkedin-post [describe the blog post topic]
```

This writes 3 variations under 50 words each to `output/drafts/linkedin/`.

### Post to LinkedIn

After picking a variation:

```
post variation 2 to LinkedIn
```

Claude calls `post_to_linkedin` directly. You'll get a confirmation with the post ID.

---

## Token Refresh

LinkedIn access tokens last ~60 days. Refresh tokens last ~365 days. The auth module checks expiry on every call and refreshes automatically while the refresh token is valid.

When both expire, re-run:

```bash
python3 linkedin_auth.py
```

---

## Gotchas

- **Redirect URI must match exactly** — port 8765, path `/callback`. Any mismatch and LinkedIn rejects the auth.
- **`w_member_social` requires the "Share on LinkedIn" product** — add it in the Products tab, not just the scopes list.
- **Use `/v2/ugcPosts`, not `/rest/posts`** — the newer REST API requires specific quarterly API versions that rotate out and aren't publicly documented. The v2 ugcPosts endpoint is stable.
- **MCP server loads at startup** — always restart Claude Code after editing `.mcp.json` or `linkedin_mcp.py`.

---

## Dependencies

```bash
pip3 install mcp requests
```
