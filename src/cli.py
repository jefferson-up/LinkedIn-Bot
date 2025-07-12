import io
import sys
import os
import json
import tempfile
import subprocess
import argparse
import re
from typing import List, Dict
from fetcher import fetch_all
from generator import generate_all

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def to_bold(c: str) -> str:
    code = ord(c)
    if 0x41 <= code <= 0x5A:
        return chr(0x1D400 + code - 0x41)
    if 0x61 <= code <= 0x7A:
        return chr(0x1D41A + code - 0x61)
    if 0x30 <= code <= 0x39:
        return chr(0x1D7CE + code - 0x30)
    return c

def to_italic(c: str) -> str:
    code = ord(c)
    if 0x41 <= code <= 0x5A:
        return chr(0x1D434 + code - 0x41)
    if 0x61 <= code <= 0x7A:
        return chr(0x1D44E + code - 0x61)
    return c

def markdown_to_unicode(s: str) -> str:
    """
    Converte:
      **texto** → texto em negrito unicode
      _texto_   → texto em itálico unicode
    Preserva parágrafos e listas.
    """
    def bold_repl(m):
        return "".join(to_bold(c) for c in m.group(1))
    def italic_repl(m):
        return "".join(to_italic(c) for c in m.group(1))

    s = re.sub(r"\*\*(.+?)\*\*", bold_repl, s)
    s = re.sub(r"_(.+?)_", italic_repl, s)
    return s

def edit_text(initial: str) -> str:
    editor = os.environ.get("EDITOR", "vi")
    with tempfile.NamedTemporaryFile(suffix=".md", mode="w+", delete=False) as tmp:
        tmp.write(initial)
        tmp.flush()
        subprocess.call([editor, tmp.name])
        return open(tmp.name, encoding="utf-8").read().rstrip()

def main():
    p = argparse.ArgumentParser(description="CLI de aprovação de posts")
    p.add_argument("-o", "--output", help="Arquivo para gravar JSON final")
    args = p.parse_args()

    articles = fetch_all()
    if not articles:
        print("Nenhum artigo encontrado.")
        return

    gens = generate_all(articles)
    approved: List[Dict[str, str]] = []

    for art in articles:
        print("\n" + "=" * 60)
        print(f"{art['title']} ({art['theme']})")
        print(art['link'])
        print("=" * 60 + "\n")

        sugs = gens.get(art["link"], [])
        for i, sug in enumerate(sugs, 1):
            print(f"[{i}]\n{sug}\n{'-' * 40}\n")

        print("0 = pular / 1-3 = selecionar")
        choice = input("> ").strip().lower()

        if choice == "0":
            continue
        elif choice in ("1", "2", "3"):
            selected = sugs[int(choice) - 1]
        else:
            continue

        formatted = markdown_to_unicode(selected.strip())

        approved.append({
            "link": art["link"],
            "theme": art["theme"],
            "text":  formatted
        })

    out = json.dumps(approved, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"\n✅ JSON salvo em {args.output}")
    else:
        print("\n" + out)

if __name__ == "__main__":
    main()


