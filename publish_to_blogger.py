#!/usr/bin/env python3
"""Publish a draft HTML post to Blogger."""

import re
import sys
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/blogger"]
BASE_DIR = Path(__file__).parent
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"

# Accept draft file as CLI argument, e.g.:
#   python3 publish_to_blogger.py output/drafts/2026-02-18-my-post.html
if len(sys.argv) > 1:
    DRAFT_FILE = Path(sys.argv[1])
    if not DRAFT_FILE.is_absolute():
        DRAFT_FILE = BASE_DIR / DRAFT_FILE
else:
    # Fall back to most recent draft
    drafts = sorted((BASE_DIR / "output/drafts").glob("*.html"), key=lambda p: p.stat().st_mtime)
    if not drafts:
        print("No draft files found in output/drafts/. Pass a filename as argument.")
        sys.exit(1)
    DRAFT_FILE = drafts[-1]
    print(f"No file specified — using most recent draft: {DRAFT_FILE.name}")


def get_credentials():
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0, open_browser=False)
        TOKEN_FILE.write_text(creds.to_json())
    return creds


def extract_title(html: str) -> str:
    match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE)
    return match.group(1).strip() if match else "planetary-api post"


def extract_body(html: str) -> str:
    match = re.search(r"<body>(.*?)</body>", html, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else html


def inline_local_images(html: str, draft_path: Path) -> str:
    """Replace local image src paths with inline SVG content or base64 data URIs."""
    draft_dir = draft_path.parent

    def replace_img(match):
        tag = match.group(0)
        src_match = re.search(r'src=["\']([^"\']+)["\']', tag)
        if not src_match:
            return tag
        src = src_match.group(1)
        # Only handle local (non-http) paths
        if src.startswith("http://") or src.startswith("https://") or src.startswith("data:"):
            return tag
        img_path = (draft_dir / src).resolve()
        if not img_path.exists():
            print(f"  Warning: image not found: {img_path}")
            return tag
        if img_path.suffix.lower() == ".svg":
            # Inline the SVG directly, preserving alt and style from the <img> tag
            alt_match = re.search(r'alt=["\']([^"\']*)["\']', tag)
            style_match = re.search(r'style=["\']([^"\']*)["\']', tag)
            svg_content = img_path.read_text(encoding="utf-8")
            # Inject style and aria-label onto the <svg> root element
            extra = ""
            if style_match:
                extra += f' style="{style_match.group(1)}"'
            if alt_match:
                extra += f' aria-label="{alt_match.group(1)}"'
            svg_content = re.sub(r"^<svg\b", f"<svg{extra}", svg_content, count=1)
            return svg_content
        else:
            # Base64-encode other image types
            import base64
            suffix = img_path.suffix.lower().lstrip(".")
            mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
                    "gif": "image/gif", "webp": "image/webp"}.get(suffix, "image/png")
            b64 = base64.b64encode(img_path.read_bytes()).decode()
            return re.sub(r'src=["\'][^"\']+["\']', f'src="data:{mime};base64,{b64}"', tag)

    return re.sub(r'<img\b[^>]*>', replace_img, html)


def find_existing_post(service, blog_id: str, title: str) -> str | None:
    """Return the post ID if a post with this title already exists."""
    result = service.posts().list(blogId=blog_id, maxResults=20).execute()
    for post in result.get("items", []):
        if post.get("title", "").strip() == title.strip():
            return post["id"]
    return None


def main():
    creds = get_credentials()
    service = build("blogger", "v3", credentials=creds)

    blogs = service.blogs().listByUser(userId="self").execute()
    blog_items = blogs.get("items", [])

    if not blog_items:
        print("No blogs found on this account.")
        return

    print("\nBlogs found on your account:")
    for i, blog in enumerate(blog_items):
        print(f"  [{i}] {blog['name']}  —  {blog['url']}  (id: {blog['id']})")

    if len(blog_items) == 1:
        chosen = blog_items[0]
        print(f"\nUsing: {chosen['name']}")
    else:
        idx = int(input("\nEnter the number of the blog to publish to: "))
        chosen = blog_items[idx]

    blog_id = chosen["id"]

    html = DRAFT_FILE.read_text(encoding="utf-8")
    title = extract_title(html)

    print("\nInlining local images...")
    html = inline_local_images(html, DRAFT_FILE)
    body = extract_body(html)

    print(f"Title  : {title}")
    print(f"Blog   : {chosen['name']}")

    # Check if post already exists — update rather than duplicate
    existing_id = find_existing_post(service, blog_id, title)
    if existing_id:
        print(f"\nPost already exists (id: {existing_id}). Will update it with inlined images.")
        action = "Update"
    else:
        action = "Publish new"

    confirm = input(f"\n{action} post? [y/N]: ").strip().lower()
    if confirm != "y":
        print("Aborted.")
        return

    if existing_id:
        post = service.posts().update(
            blogId=blog_id,
            postId=existing_id,
            body={"title": title, "content": body},
        ).execute()
        print(f"\nUpdated successfully!")
    else:
        post = service.posts().insert(
            blogId=blog_id,
            body={"title": title, "content": body},
            isDraft=False,
        ).execute()
        print(f"\nPublished successfully!")

    print(f"URL: {post.get('url')}")


if __name__ == "__main__":
    main()
