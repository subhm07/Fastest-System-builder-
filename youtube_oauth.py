#!/usr/bin/env python3
"""
YouTube OAuth connector for Shubham Studio / Hermes.

Purpose:
- Safely connect Hermes to Shubham's YouTube channel through Google OAuth.
- No Google password is stored or used.
- Stores OAuth token locally at ~/.hermes/youtube_token.json.

Usage:
  python3 youtube_oauth.py auth-url --client-secret /path/to/client_secret.json
  python3 youtube_oauth.py auth-code "http://localhost:1/?code=..."
  python3 youtube_oauth.py check
  python3 youtube_oauth.py channel
  python3 youtube_oauth.py revoke-local
"""

import argparse
import base64
import hashlib
import json
import os
import secrets
import sys
import time
import urllib.parse
import urllib.request

HOME = os.path.expanduser("~")
HERMES_DIR = os.path.join(HOME, ".hermes")
CLIENT_PATH = os.path.join(HERMES_DIR, "youtube_client_secret.json")
TOKEN_PATH = os.path.join(HERMES_DIR, "youtube_token.json")
PENDING_PATH = os.path.join(HERMES_DIR, "youtube_oauth_pending.json")
AUTH_URL_PATH = os.path.join(HERMES_DIR, "youtube_oauth_last_url.txt")
TOKEN_URL = "https://oauth2.googleapis.com/token"
AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
REVOKE_ENDPOINT = "https://oauth2.googleapis.com/revoke"
REDIRECT_URI = "http://localhost:1/"
SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]


def ensure_dir():
    os.makedirs(HERMES_DIR, exist_ok=True)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    ensure_dir()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.chmod(path, 0o600)


def parse_client_secret(data):
    cfg = data.get("installed") or data.get("web") or data
    client_id = cfg.get("client_id")
    client_secret = cfg.get("client_secret")
    if not client_id:
        raise SystemExit("client_id not found in OAuth JSON")
    return client_id, client_secret


def pkce_pair():
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(64)).rstrip(b"=").decode()
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    return verifier, challenge


def http_post(url, data, headers=None):
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=body, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        msg = e.read().decode(errors="replace")
        raise SystemExit(f"HTTP {e.code}: {msg}")


def http_get(url, token):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        msg = e.read().decode(errors="replace")
        raise SystemExit(f"HTTP {e.code}: {msg}")


def cmd_auth_url(args):
    ensure_dir()
    src = os.path.expanduser(args.client_secret)
    if not os.path.exists(src):
        raise SystemExit(f"Client secret file not found: {src}")
    data = load_json(src)
    client_id, client_secret = parse_client_secret(data)
    save_json(CLIENT_PATH, data)
    verifier, challenge = pkce_pair()
    state = secrets.token_urlsafe(24)
    save_json(PENDING_PATH, {
        "client_id": client_id,
        "client_secret": client_secret,
        "code_verifier": verifier,
        "state": state,
        "created_at": int(time.time()),
        "scopes": SCOPES,
    })
    params = {
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "state": state,
    }
    url = AUTH_ENDPOINT + "?" + urllib.parse.urlencode(params)
    with open(AUTH_URL_PATH, "w", encoding="utf-8") as f:
        f.write(url + "\n")
    print(json.dumps({"auth_url": url, "saved_to": AUTH_URL_PATH}, indent=2))


def extract_code(value):
    value = value.strip()
    if value.startswith("http://") or value.startswith("https://"):
        parsed = urllib.parse.urlparse(value)
        qs = urllib.parse.parse_qs(parsed.query)
        if "error" in qs:
            raise SystemExit(f"OAuth error: {qs['error'][0]}")
        code = qs.get("code", [None])[0]
        state = qs.get("state", [None])[0]
        return code, state
    return value, None


def cmd_auth_code(args):
    if not os.path.exists(PENDING_PATH):
        raise SystemExit("No pending OAuth session. Run auth-url first.")
    pending = load_json(PENDING_PATH)
    code, state = extract_code(args.code_or_url)
    if not code:
        raise SystemExit("No OAuth code found.")
    if state and state != pending.get("state"):
        raise SystemExit("State mismatch. Restart auth-url and use the newest URL.")
    data = {
        "client_id": pending["client_id"],
        "code": code,
        "code_verifier": pending["code_verifier"],
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
    }
    if pending.get("client_secret"):
        data["client_secret"] = pending["client_secret"]
    token = http_post(TOKEN_URL, data)
    token["created_at"] = int(time.time())
    token["scopes_requested"] = pending.get("scopes")
    save_json(TOKEN_PATH, token)
    try:
        os.remove(PENDING_PATH)
    except FileNotFoundError:
        pass
    print(json.dumps({"status": "connected", "token_path": TOKEN_PATH, "scope": token.get("scope")}, indent=2))


def refresh_if_needed():
    if not os.path.exists(TOKEN_PATH):
        raise SystemExit("NOT_CONNECTED: No token. Run auth-url and auth-code first.")
    token = load_json(TOKEN_PATH)
    expires_in = int(token.get("expires_in", 0))
    created = int(token.get("created_at", 0))
    if token.get("access_token") and time.time() < created + expires_in - 120:
        return token
    refresh = token.get("refresh_token")
    if not refresh:
        raise SystemExit("Token expired and no refresh_token exists. Reconnect with auth-url.")
    client = load_json(CLIENT_PATH)
    client_id, client_secret = parse_client_secret(client)
    data = {
        "client_id": client_id,
        "refresh_token": refresh,
        "grant_type": "refresh_token",
    }
    if client_secret:
        data["client_secret"] = client_secret
    new_token = http_post(TOKEN_URL, data)
    token.update(new_token)
    token["created_at"] = int(time.time())
    save_json(TOKEN_PATH, token)
    return token


def cmd_check(_args):
    if os.path.exists(TOKEN_PATH):
        try:
            refresh_if_needed()
            print("CONNECTED")
        except SystemExit as e:
            print(str(e))
            sys.exit(1)
    else:
        print("NOT_CONNECTED")
        sys.exit(1)


def cmd_channel(_args):
    token = refresh_if_needed()
    url = "https://www.googleapis.com/youtube/v3/channels?" + urllib.parse.urlencode({
        "part": "snippet,contentDetails,statistics,status",
        "mine": "true",
    })
    data = http_get(url, token["access_token"])
    print(json.dumps(data, indent=2))


def cmd_revoke_local(_args):
    for path in [TOKEN_PATH, PENDING_PATH, AUTH_URL_PATH]:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
    print(json.dumps({"status": "local_token_removed", "note": "Also revoke app access at https://myaccount.google.com/permissions if needed."}, indent=2))


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("auth-url")
    a.add_argument("--client-secret", required=True)
    a.set_defaults(func=cmd_auth_url)
    c = sub.add_parser("auth-code")
    c.add_argument("code_or_url")
    c.set_defaults(func=cmd_auth_code)
    chk = sub.add_parser("check")
    chk.set_defaults(func=cmd_check)
    ch = sub.add_parser("channel")
    ch.set_defaults(func=cmd_channel)
    r = sub.add_parser("revoke-local")
    r.set_defaults(func=cmd_revoke_local)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
