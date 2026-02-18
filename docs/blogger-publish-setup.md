# Blogger Publishing — Setup Guide

## What It Does

`publish_to_blogger.py` takes a draft HTML file from `output/drafts/`, inlines any local SVG images, and publishes or updates the post on Blogger. It handles OAuth, duplicate detection, and image embedding automatically.

---

## Files

| File | Purpose |
|------|---------|
| `publish_to_blogger.py` | The publish script. |
| `credentials.json` | Google OAuth client secrets (not committed). |
| `token.json` | Cached OAuth token (not committed). |
| `output/drafts/` | Draft HTML files ready to publish. |
| `assets/images/` | SVG diagrams referenced from drafts. |

---

## One-Time Setup

### 1. Create a Google Cloud Project

1. Go to https://console.cloud.google.com → create a new project (or use an existing one)
2. **APIs & Services** → **Enable APIs** → search for **Blogger API v3** → enable it
3. **APIs & Services** → **OAuth consent screen**:
   - User type: **External**
   - Add your Gmail address as a **test user**
4. **APIs & Services** → **Credentials** → **Create Credentials** → **OAuth client ID**:
   - Application type: **Desktop app**
   - Name it anything
5. Download the JSON and save it as `credentials.json` in the project root

### 2. Install Dependencies

```bash
pip3 install google-auth google-auth-oauthlib google-api-python-client
```

### 3. First Run — Authenticate

```bash
python3 publish_to_blogger.py
```

On first run with no `token.json`, the script prints an authorisation URL. Open it in a browser, log in with your Google account, and grant access. The token is saved to `token.json` and reused on every subsequent run — no browser login needed again until the token expires.

---

## Publishing a Post

### Publish a specific draft

```bash
python3 publish_to_blogger.py output/drafts/2026-02-18-my-post.html
```

### Publish the most recently modified draft

```bash
python3 publish_to_blogger.py
```

### Non-interactive (for scripting)

```bash
echo "y" | python3 publish_to_blogger.py output/drafts/2026-02-18-my-post.html
```

The script always asks **"Publish now? [y/N]"** before posting. Pipe `y` to skip the prompt.

---

## What the Script Does

1. Loads `credentials.json` and either reuses `token.json` or prompts for OAuth
2. Lists your Blogger blogs and asks which one to publish to (or auto-selects if you only have one)
3. Reads the HTML draft and extracts the `<title>` and `<body>`
4. Inlines all local image references:
   - SVGs are embedded directly as `<svg>` elements
   - PNGs/JPEGs are base64-encoded as data URIs
5. Checks if a post with the same title already exists:
   - If yes → updates the existing post
   - If no → creates a new published post
6. Confirms before posting

---

## Draft File Conventions

- **Location**: `output/drafts/YYYY-MM-DD-topic.html`
- **Title**: extracted from `<title>Your Post Title</title>` in the HTML
- **Images**: referenced relative to the draft file, e.g. `../../assets/images/diagram.svg`
- **SVGs**: stored in `assets/images/` — always create at least one diagram per post

The script resolves image paths relative to the draft file location, so the `../../assets/images/` convention works as long as you keep drafts in `output/drafts/`.

---

## Gotchas

- **`credentials.json` must be the Desktop app type** — not a web app client. Web app clients require a registered redirect URI and won't work with the local server flow.
- **Add yourself as a test user** — while the OAuth consent screen is in "testing" mode, only listed test users can authenticate. Go to OAuth consent screen → Test users → add your Gmail.
- **Token lasts ~1 hour but auto-refreshes** — the script refreshes the access token automatically using the refresh token. You only need to re-authenticate if the refresh token itself expires (rare) or is revoked.
- **Duplicate detection checks the last 20 posts** — if a post with the same title is older than that, it may create a duplicate. The script will update rather than duplicate in most cases.
- **Images must exist on disk at publish time** — if SVGs are missing, the script warns but continues. Broken image references won't block the post.

---

## Google Cloud Setup Reference (already done for this project)

- Project ID: 151014483318
- OAuth client type: Desktop app
- Blogger API v3: enabled
- Redirect URI: `http://localhost` (works with `port=0` local server)
- Test user: Andy's Gmail