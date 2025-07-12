import os
import json
import time
import yaml
import feedparser
import sys
from typing import List, Dict

CONFIG_PATH  = os.path.join(os.path.dirname(__file__), "..", "config", "themes.yaml")
HISTORY_FILE = os.path.join(os.path.dirname(__file__), "..", "history.json")
ONE_WEEK     = 7 * 24 * 60 * 60


def load_config() -> Dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_history() -> set:
    if os.path.exists(HISTORY_FILE):
        return set(json.load(open(HISTORY_FILE)))
    return set()


def save_history(history: set):
    with open(HISTORY_FILE, "w", encoding="utf-8") as hf:
        json.dump(list(history), hf, indent=2)


def fetch_all() -> List[Dict]:
    cfg     = load_config()
    history = load_history()
    cutoff  = time.time() - ONE_WEEK
    results = []

    for theme in cfg["themes"]:
        print(f"🔍 Tema: {theme['name']}", file=sys.stderr)
        article = None

        for feed_url in theme["rss_feeds"]:
            print(f"   ⏳ Lendo feed {feed_url}", file=sys.stderr)
            d = feedparser.parse(feed_url)
            for entry in d.entries:
                pub = entry.get("published_parsed") or entry.get("updated_parsed")
                ts  = time.mktime(pub) if pub else None
                if not ts or ts < cutoff:
                    continue

                link = entry.get("link", "").strip()
                if not link or link in history:
                    continue

                summary = entry.get("summary") or entry.get("description", "")
                article = {
                    "theme":   theme["name"],
                    "title":   entry.get("title", "").strip(),
                    "link":    link,
                    "summary": summary.strip()
                }
                history.add(link)
                break

            if article:
                break

        if article:
            results.append(article)
        else:
            print(f"⚠️ Nenhum artigo recente achado para o tema {theme['name']}", file=sys.stderr)

    save_history(history)
    return results