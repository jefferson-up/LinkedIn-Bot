import io
import sys
import os
import json
import requests
from auth import get_access_token

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# URNs
person_id = os.getenv("LINKEDIN_PERSON_ID")
if not person_id:
    print("ERRO: defina LINKEDIN_PERSON_ID no .env", file=sys.stderr)
    sys.exit(1)
author_urn = f"urn:li:person:{person_id}"

image_urn = os.getenv("LINKEDIN_IMAGE_URN")

MENTIONS = ["@Amazon", "@HashiCorp"]
HASHTAGS = ["#CloudCost", "#DevOps", "#AWS", "#Automation"]

EMOJI_PREFIX = "🚀 "
EMOJI_BULLET = "💡 "

def post_ugc(text: str, urn: str, token: str, image_urn: str = None) -> dict:
    """
    Publica um UGC Post no LinkedIn, incluindo opcionalmente imagem,
    menções, hashtags e emojis.
    """
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }

    mentions_str = " ".join(MENTIONS)
    hashtags_str = " ".join(HASHTAGS)
    footer = f"\n\n{mentions_str}  {hashtags_str}"

    text = f"🚨 IMPORTANTE:\n{text.strip()}\n\nO que você acha? Comente abaixo! 👇{footer}"

    share_content = {
        "shareCommentary": {"text": text},
        "shareMediaCategory": "NONE"
    }

    if image_urn:
        share_content["shareMediaCategory"] = "IMAGE"
        share_content["media"] = [
            {
                "status": "READY",
                "description": {"text": "Descrição acessível da imagem"},
                "media": image_urn,
                "title": {"text": "Thumbnail do artigo"}
            }
        ]

    payload = {
        "author": urn,
        "lifecycleState": "PUBLISHED",
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        "specificContent": {
            "com.linkedin.ugc.ShareContent": share_content
        }
    }

    resp = requests.post(url, headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()

def main():
    if len(sys.argv) != 2:
        print("Uso: python src/poster.py approved.json", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            posts = json.load(f)
    except Exception as e:
        print("❌ Não consegui ler", input_path, e, file=sys.stderr)
        sys.exit(1)

    token = get_access_token()
    results = []

    for post in posts:
        link = post.get("link", "")
        text = post.get("text", "").strip()

        try:
            res = post_ugc(text, author_urn, token, image_urn=image_urn)
            share_id = res.get("id") or res.get("activity") or "<unknown>"
            print(f"Publicado: {link} → {share_id}")
            results.append({"link": link, "id": share_id})
        except requests.HTTPError as err:
            code = err.response.status_code
            body = err.response.text
            print(f"❌ Falha ao publicar {link}: {code} {body}", file=sys.stderr)

    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()