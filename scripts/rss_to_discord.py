import json
import os
import sys
from pathlib import Path

import feedparser
import requests

FEEDS_FILE = Path("feeds.txt")
STATE_FILE = Path("state/seen.json")
WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]
MAX_ENTRIES_PER_RUN = 5


def load_feeds():
    urls = []
    for line in FEEDS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            urls.append(line)
    return urls


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}


def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def entry_id(entry):
    return entry.get("id") or entry.get("link")


def post_to_discord(feed_title, entry):
    embed = {
        "title": entry.get("title", "(no title)")[:256],
        "url": entry.get("link", ""),
        "footer": {"text": feed_title},
    }
    resp = requests.post(WEBHOOK_URL, json={"embeds": [embed]}, timeout=15)
    resp.raise_for_status()


def main():
    feeds = load_feeds()
    state = load_state()
    changed = False

    for url in feeds:
        parsed = feedparser.parse(url)
        if parsed.bozo and not parsed.entries:
            print(f"[warn] failed to parse {url}: {parsed.bozo_exception}", file=sys.stderr)
            continue

        feed_title = parsed.feed.get("title", url)

        if url not in state:
            # 初回は今ある記事を「既読」扱いにするだけで通知はしない（過去記事が一斉に流れるのを防ぐ）
            state[url] = [entry_id(e) for e in parsed.entries if entry_id(e)]
            changed = True
            print(f"[init] seeded {feed_title} with {len(state[url])} entries")
            continue

        seen = set(state.get(url, []))
        new_entries = [e for e in parsed.entries if entry_id(e) not in seen]
        # 古い記事から順に投稿されるよう反転し、暴走投稿を防ぐため件数を絞る
        new_entries = list(reversed(new_entries))[:MAX_ENTRIES_PER_RUN]

        for entry in new_entries:
            post_to_discord(feed_title, entry)
            seen.add(entry_id(entry))
            changed = True
            print(f"[post] {feed_title}: {entry.get('title')}")

        state[url] = list(seen)

    if changed:
        save_state(state)


if __name__ == "__main__":
    main()
