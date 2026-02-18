# Blog Poster Project

## Purpose
This project generates blog posts for technical projects, matching the writing style of blog.infosecmatters.net (Andy Ratcliffe).

# How It Works
- Generated posts go into /output/drafts as html files
- Images assets are stored in /assets/images

## Writing Style
When generating any blog post content, always follow the style guide in `STYLE_GUIDE.md`. Key points:
- Practical, hands-on, demonstration-driven — not theoretical
- Conversational first-person tone ("I", "my") — honest and humble
- Direct introductions — state what the post covers and why, no waffle
- Step-by-step walkthroughs with code blocks and screenshots as the core content
- Flag real-world gotchas and practical tips from experience
- Short wrap-up summarising what was demonstrated
- Descriptive technical titles, no clickbait
- Avoid formal/academic language, buzzwords, and excessive bullet lists

# Platform Rules
## Important to follow these exactly
IMPORTANT — follow these exactly:
- Write like you're talking to one person over coffee, not presenting to a boardroom
- Use "you" and "I", never "we" or "our team"
- Short sentences. One idea per sentence. Punch, don't waffle.
- OK to start sentences with "And", "But", "So"
- Never use: "unlock", "leverage", "game-changer", "synergy", "deep dive"
- Every time you write some content - Make sure to use the humanizer skill in /skills/humanizer

## Steps to follow
- Generated posts go into /output/drafts as html files
- ALWAYS create SVG graphics for each post — diagrams, architecture maps, workflow visuals
- Image assets are stored in /assets/images and referenced from the HTML
- To preview: open the draft files and review before copying to scheduling tool

## Content Rules
- Every post must teach something or share a real experience — no fluff
- Reference specific tools, numbers, or results wherever possible
- When mentioning AI tools, position them as assistants not replacements
- My audience is technical architects and engineers
- Minimise jargon, keep it relevant to the specific topic
- Introduce acronyms on first use 

# Workflow
- Use the github repo that I enter as the basis for the post
- Always generate 2 variations of each post so I can pick my favourite
- File naming: [date]-[platform]-[topic].html (e.g. 2026-02-04-claude-code-tips.html)
- Never publish or schedule anything — drafts only, I review everything
- If a topic is unclear, write a 1-line interpretation at the top of the draft
- When I approve the post, publish to blogger.com using the steps below

## Publishing to Blogger
Use `publish_to_blogger.py` — it handles OAuth, SVG inlining, and duplicate detection automatically.

```bash
# Publish a specific draft:
python3 publish_to_blogger.py output/drafts/2026-02-18-my-post.html

# Or omit the filename to auto-pick the most recently modified draft:
python3 publish_to_blogger.py
```

- OAuth token is cached in `token.json` — no browser login needed after first run
- Local SVG images are inlined automatically — no external image hosting required
- If the post title already exists on the blog, the script updates it rather than duplicating
- The script will always ask "Publish now? [y/N]" before posting — confirm to proceed
- `credentials.json` must be present (Google Cloud OAuth client, "Desktop app" type, Blogger API enabled)


