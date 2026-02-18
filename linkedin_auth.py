"""
LinkedIn OAuth 2.0 Authorization Code flow.

Run once to authenticate:
    python3 linkedin_auth.py

This saves linkedin_token.json. Subsequent calls to get_linkedin_token()
auto-refresh the token if it has expired.
"""

import json
import os
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

import requests

CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "linkedin_credentials.json")
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "linkedin_token.json")

LINKEDIN_AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
SCOPES = "openid profile w_member_social"

# Captured by the local callback server
_auth_code = None


def _load_credentials():
    if not os.path.exists(CREDENTIALS_FILE):
        raise FileNotFoundError(
            f"{CREDENTIALS_FILE} not found. "
            "Create it with your LinkedIn app's client_id, client_secret, and redirect_uri. "
            "See the project README for instructions."
        )
    with open(CREDENTIALS_FILE) as f:
        return json.load(f)


class _CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global _auth_code
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        if "code" in params:
            _auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h2>Authorised. You can close this tab.</h2>")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"<h2>No code returned. Check LinkedIn app settings.</h2>")

    def log_message(self, *args):
        pass  # Suppress request logs


def _run_server(port):
    server = HTTPServer(("localhost", port), _CallbackHandler)
    server.handle_request()  # Handles exactly one request then exits


def _exchange_code(code, creds):
    resp = requests.post(
        LINKEDIN_TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": creds["redirect_uri"],
            "client_id": creds["client_id"],
            "client_secret": creds["client_secret"],
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def _refresh_token(refresh_tok, creds):
    resp = requests.post(
        LINKEDIN_TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_tok,
            "client_id": creds["client_id"],
            "client_secret": creds["client_secret"],
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def _save_token(token_data):
    # Annotate with expiry timestamp so we can check later
    token_data["expires_at"] = time.time() + token_data.get("expires_in", 3600) - 60
    if "refresh_token_expires_in" in token_data:
        token_data["refresh_token_expires_at"] = (
            time.time() + token_data["refresh_token_expires_in"] - 60
        )
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f, indent=2)


def _do_auth_flow():
    global _auth_code
    _auth_code = None

    creds = _load_credentials()
    redirect_uri = creds["redirect_uri"]
    parsed = urllib.parse.urlparse(redirect_uri)
    port = parsed.port or 8765

    # Start local callback server before opening browser
    thread = Thread(target=_run_server, args=(port,), daemon=True)
    thread.start()

    params = {
        "response_type": "code",
        "client_id": creds["client_id"],
        "redirect_uri": redirect_uri,
        "scope": SCOPES,
        "state": "linkedin_mcp_auth",
    }
    auth_url = LINKEDIN_AUTH_URL + "?" + urllib.parse.urlencode(params)
    print(f"\nOpening browser for LinkedIn authorisation...\n{auth_url}\n")
    webbrowser.open(auth_url)

    print("Waiting for callback on", redirect_uri)
    print("(If the browser doesn't redirect automatically, paste the full redirect URL below)\n")
    thread.join(timeout=30)

    if not _auth_code:
        # Fallback: ask user to paste the redirect URL manually
        print("\nAutomatic capture timed out. After authorising in the browser,")
        print("copy the full URL from the browser address bar and paste it here.")
        pasted = input("Paste redirect URL: ").strip()
        parsed_pasted = urllib.parse.urlparse(pasted)
        params_pasted = urllib.parse.parse_qs(parsed_pasted.query)
        if "code" not in params_pasted:
            raise RuntimeError("No 'code' parameter found in the pasted URL. Check the URL and try again.")
        _auth_code = params_pasted["code"][0]

    token_data = _exchange_code(_auth_code, creds)
    _save_token(token_data)
    print(f"Token saved to {TOKEN_FILE}")
    return token_data["access_token"]


def get_linkedin_token() -> str:
    """
    Return a valid LinkedIn access token.
    - If token.json exists and is not expired, return it directly.
    - If expired and a refresh token is available, refresh automatically.
    - Otherwise, raise RuntimeError telling the user to run linkedin_auth.py.
    """
    if not os.path.exists(TOKEN_FILE):
        raise RuntimeError(
            "No LinkedIn token found. Run: python3 linkedin_auth.py"
        )

    with open(TOKEN_FILE) as f:
        token_data = json.load(f)

    # Still valid
    if time.time() < token_data.get("expires_at", 0):
        return token_data["access_token"]

    # Try refresh
    refresh_tok = token_data.get("refresh_token")
    if not refresh_tok:
        raise RuntimeError(
            "LinkedIn access token expired and no refresh token available. "
            "Run: python3 linkedin_auth.py"
        )

    refresh_expires = token_data.get("refresh_token_expires_at", float("inf"))
    if time.time() >= refresh_expires:
        raise RuntimeError(
            "LinkedIn refresh token also expired. Run: python3 linkedin_auth.py"
        )

    creds = _load_credentials()
    new_token = _refresh_token(refresh_tok, creds)
    _save_token(new_token)
    return new_token["access_token"]


if __name__ == "__main__":
    _do_auth_flow()
    print("Authentication complete. You can now use the LinkedIn MCP server.")
