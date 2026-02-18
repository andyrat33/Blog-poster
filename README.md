# Blog Poster

Generates and publishes technical blog posts for [blog.infosecmatters.net](https://blog.infosecmatters.net). Posts go to Blogger and LinkedIn.

## How It Works

1. Give Claude Code a GitHub repo or topic
2. It generates 2 draft HTML posts in `output/drafts/`, with SVG diagrams in `assets/images/`
3. Review and pick your favourite
4. Publish to Blogger and post to LinkedIn from within the conversation

Writing style is governed by `STYLE_GUIDE.md`. Claude Code behaviour is configured in `CLAUDE.md`.

## Project Structure

```
Blog-poster/
├── publish_to_blogger.py       # Publish drafts to Blogger
├── linkedin_mcp.py             # MCP server — post_to_linkedin tool
├── linkedin_auth.py            # LinkedIn OAuth flow
├── STYLE_GUIDE.md              # Writing tone and structure rules
├── CLAUDE.md                   # Claude Code instructions
├── credentials.json            # Google OAuth secrets (not committed)
├── token.json                  # Google OAuth token (not committed)
├── linkedin_credentials.json   # LinkedIn app secrets (not committed)
├── linkedin_token.json         # LinkedIn OAuth token (not committed)
├── output/
│   └── drafts/                 # Generated HTML posts
│       └── linkedin/           # LinkedIn post variations
└── assets/
    └── images/                 # SVG diagrams referenced from drafts
```

## Publishing

### Blogger

```bash
python3 publish_to_blogger.py output/drafts/2026-02-18-my-post.html
```

See [docs/blogger-publish-setup.md](docs/blogger-publish-setup.md) for full setup.

### LinkedIn

Ask Claude Code directly:

```
post variation 1 to LinkedIn
```

The `post_to_linkedin` MCP tool posts on your behalf. Use the `linkedin-post` skill to generate post variations from a blog post first.

See [docs/linkedin-mcp-setup.md](docs/linkedin-mcp-setup.md) for full setup.

## Dependencies

```bash
pip3 install mcp requests google-auth google-auth-oauthlib google-api-python-client
```
