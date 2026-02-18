"""
LinkedIn MCP server — exposes post_to_linkedin as an MCP tool.

Start automatically via .mcp.json (Claude Code loads it on startup).
Manual test:
    echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python3 linkedin_mcp.py
"""

import requests
from mcp.server.fastmcp import FastMCP

from linkedin_auth import get_linkedin_token

LINKEDIN_USERINFO_URL = "https://api.linkedin.com/v2/userinfo"
LINKEDIN_POSTS_URL = "https://api.linkedin.com/v2/ugcPosts"
MAX_CHARS = 3000

mcp = FastMCP("linkedin-poster")


def _get_author_urn(token: str) -> str:
    """Fetch the user's person URN via the OpenID userinfo endpoint."""
    resp = requests.get(
        LINKEDIN_USERINFO_URL,
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    resp.raise_for_status()
    sub = resp.json().get("sub")
    if not sub:
        raise RuntimeError("Could not retrieve LinkedIn user ID from /v2/userinfo")
    return f"urn:li:person:{sub}"


def _post_text(token: str, author_urn: str, text: str) -> str:
    """Post a text share to LinkedIn. Returns the created post URN."""
    payload = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        },
    }
    resp = requests.post(
        LINKEDIN_POSTS_URL,
        json=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        },
        timeout=20,
    )
    resp.raise_for_status()
    post_id = resp.json().get("id", "unknown")
    return post_id


@mcp.tool()
def post_to_linkedin(text: str) -> str:
    """
    Post a text update to LinkedIn on behalf of the authenticated user.

    Args:
        text: The post content. Maximum 3000 characters.

    Returns:
        Confirmation message with the created post ID, or an error description.
    """
    # Guards
    if not text or not text.strip():
        return "Error: post text is empty. Provide some content to post."

    if len(text) > MAX_CHARS:
        return (
            f"Error: post is {len(text)} characters, which exceeds the LinkedIn "
            f"limit of {MAX_CHARS}. Shorten the text and try again."
        )

    try:
        token = get_linkedin_token()
    except RuntimeError as exc:
        return f"Auth error: {exc}"

    try:
        author_urn = _get_author_urn(token)
    except requests.HTTPError as exc:
        return f"Failed to fetch LinkedIn profile: {exc.response.status_code} {exc.response.text}"
    except Exception as exc:
        return f"Unexpected error fetching profile: {exc}"

    try:
        post_id = _post_text(token, author_urn, text)
    except requests.HTTPError as exc:
        return (
            f"LinkedIn API error when posting: "
            f"{exc.response.status_code} {exc.response.text}"
        )
    except Exception as exc:
        return f"Unexpected error posting to LinkedIn: {exc}"

    return f"Posted successfully. LinkedIn post ID: {post_id}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
