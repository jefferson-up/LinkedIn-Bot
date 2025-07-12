import os, time, json, requests
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()
REDIRECT_URI = os.getenv("LINKEDIN_REDIRECT_URI")
print("⚙️  [DEBUG] LINKEDIN_REDIRECT_URI =", REDIRECT_URI)

CLIENT_ID     = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI  = os.getenv("LINKEDIN_REDIRECT_URI")
TOKEN_FILE    = os.path.join(os.path.dirname(__file__), "..", "token.json")

AUTH_URL  = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
SCOPES = ["r_liteprofile", "w_member_social"]

def build_auth_url(state: str) -> str:
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(SCOPES),
        "state": state,
    }
    return f"{AUTH_URL}?{urlencode(params)}"

def exchange_code_for_token(code: str) -> dict:
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logging.debug(f"Exchanging code for token. code='{code}', redirect_uri='{REDIRECT_URI}'")
    data = {
        "grant_type":    "authorization_code",
        "code":          code,
        "redirect_uri":  REDIRECT_URI,
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    logging.debug(f"POST {TOKEN_URL} payload={data}")
    resp = requests.post(TOKEN_URL, data=data)
    logging.debug(f"Response status: {resp.status_code}")
    logging.debug(f"Response headers: {resp.headers}")
    logging.debug(f"Response body: {resp.text}")
    resp.raise_for_status()
    t = resp.json()
    t["expires_at"] = int(time.time()) + t.get("expires_in", 0)
    with open(TOKEN_FILE, "w") as f:
        json.dump(t, f, indent=2)
    return t

def get_access_token() -> str:
    with open(os.path.join(os.path.dirname(__file__),"..","token.json"),"r") as f:
        return json.load(f)["access_token"]
