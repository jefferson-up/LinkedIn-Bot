import os
import yaml
import json
from openai import OpenAI
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "themes.yaml")

SYSTEM_PROMPT = """
Você é um redator profissional de posts para LinkedIn.
Seu perfil está em config/themes.yaml.

Para cada artigo, gere TRÊS variações de post **rico e completo** (300–600 palavras), seguindo estas regras:
1. Comece com um **título** em negrito;
2. Use parágrafos curtos de 2–3 linhas, separados por uma linha em branco;
3. Inclua uma lista numerada de 3–5 itens principais, cada item em linha própria;
4. Termine com uma chamada à ação (“O que você acha?” ou similar);
5. **Retorne apenas um JSON array** com as três strings, nada mais (ex:
[
  "primeiro post completo…",
  "segundo post completo…",
  "terceiro post completo…"
]).
"""

def load_profile() -> Dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f).get("profile", {})

def build_prompt(profile: Dict, theme: str, article: Dict) -> str:
    headline = profile.get("headline", "")
    specs    = ", ".join(profile.get("specialties", []))
    return (
        f"Perfil: {headline} ({specs})\n"
        f"Tema: {theme}\n"
        f"Artigo: {article['title']} – {article['link']}\n"
        f"Resumo: {article['summary']}\n\n"
        "Gere **3 sugestões numeradas** de post para LinkedIn conforme o sistema acima,"
        "e devolva exclusivamente um JSON array de 3 strings."
    )

def generate_suggestions(article: Dict) -> List[str]:
    profile = load_profile()
    prompt  = build_prompt(profile, article["theme"], article)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt}
        ],
        temperature=0.7
    )
    content = resp.choices[0].message.content.strip()

    try:
        arr = json.loads(content)
        if isinstance(arr, list) and all(isinstance(x, str) for x in arr):
            return arr[:3]
    except json.JSONDecodeError:
        pass

    parts = content.split("\n\n2.")
    suggestions = []
    for i, part in enumerate(parts, start=1):
        prefix = f"{i}. " if not part.lstrip().startswith(f"{i}.") else ""
        suggestions.append((prefix + part).strip())
        if len(suggestions) == 3:
            break
    return suggestions

def generate_all(articles: List[Dict]) -> Dict[str, List[str]]:
    return { art["link"]: generate_suggestions(art) for art in articles }

if __name__ == "__main__":
    from fetcher import fetch_all
    arts = fetch_all()
    gens = generate_all(arts)
    for link, sugs in gens.items():
        print(f"\nArtigo: {link}")
        for i, s in enumerate(sugs, 1):
            print(f"{i}. {s}\n")