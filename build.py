"""寝落ち世界史 原稿サイトの生成。

content/scripts/<YYYY-MM-DD>.json を読み、docs/ に静的HTMLを書き出す（GitHub Pages は main ブランチの /docs を配信）。
  - docs/index.html                 原稿一覧（新しい順）
  - docs/scripts/<YYYY-MM-DD>/      各動画の原稿ページ（YouTube 概要欄に貼るリンク）
  - docs/privacy/                   プライバシーポリシー（Google OAuth 本番化・API 監査用）
公開日時（publishAt）が未来の原稿も生成する（予約投稿の概要欄リンクが公開前から有効になるように）が、
一覧には公開日時を過ぎたものだけを載せる。
"""
from __future__ import annotations

import html
import json
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content" / "scripts"
OUT = ROOT / "docs"
JST = timezone(timedelta(hours=9))

SITE_NAME = "寝落ち世界史 原稿集"
BASE_URL = "https://neochi-sekaishi.github.io"
CHANNEL_URL = "https://www.youtube.com/channel/UCiVQYX6sL4hjHsi-wYDUaDA"
NOTE_URL = "https://note.com/sleephistory/n/n39ab6f3c5a6e"

CSS = """
:root {
  --bg: #0e131d; --surface: #151c29; --text: #e8e2d4; --muted: #9c968a;
  --accent: #d6a45a; --line: #263042;
  color-scheme: dark;
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body {
  margin: 0; background: var(--bg); color: var(--text);
  font-family: "Shippori Mincho", "Hiragino Mincho ProN", "Yu Mincho", serif;
  font-size: 18px; line-height: 2; letter-spacing: .03em;
}
a { color: var(--accent); text-underline-offset: .2em; }
.wrap { max-width: 40rem; margin: 0 auto; padding: 0 16px; }
header.site { border-bottom: 1px solid var(--line); }
header.site .wrap { display: flex; justify-content: space-between; align-items: center; min-height: 56px; }
header.site a.brand { color: var(--text); text-decoration: none; font-weight: 700; letter-spacing: .08em; white-space: nowrap; }
header.site nav { white-space: nowrap; }
header.site nav a { color: var(--muted); font-size: 14px; text-decoration: none; margin-left: 1em; }
main { padding: 48px 0 64px; }
h1 { font-size: 1.6rem; line-height: 1.6; margin: 0 0 .6em; letter-spacing: .05em; }
h2 { font-size: 1.15rem; margin: 2.4em 0 .6em; }
.lead { color: var(--muted); font-size: 16px; }
.meta { color: var(--muted); font-size: 14px; margin-bottom: 2em; }
.watch {
  display: inline-block; margin: .4em 0 2.4em; padding: .5em 1.2em; border: 1px solid var(--accent);
  border-radius: 999px; text-decoration: none; font-size: 15px;
}
.body p { margin: 0 0 1.8em; text-align: justify; }
ul.list { list-style: none; padding: 0; margin: 0; }
ul.list li { border-top: 1px solid var(--line); }
ul.list li:last-child { border-bottom: 1px solid var(--line); }
ul.list a { display: block; padding: 1em 0; color: var(--text); text-decoration: none; }
ul.list a:hover .t { color: var(--accent); }
ul.list .d { display: block; color: var(--muted); font-size: 13px; }
ul.list .t { line-height: 1.7; }
.empty { color: var(--muted); }
footer.site { border-top: 1px solid var(--line); color: var(--muted); font-size: 13px; padding: 24px 0 40px; line-height: 1.9; }
footer.site a { color: var(--muted); }
@media (max-width: 480px) { body { font-size: 17px; } h1 { font-size: 1.35rem; } main { padding-top: 32px; } }
@media (max-width: 360px) { header.site a.brand { letter-spacing: .02em; } header.site nav a { font-size: 12px; margin-left: .7em; letter-spacing: 0; } }
"""

import hashlib
CSS_VERSION = hashlib.sha1(CSS.encode()).hexdigest()[:8]


def page(title: str, body: str, *, depth: int, description: str = "") -> str:
    rel = "../" * depth
    full_title = f"{title} | {SITE_NAME}" if title != SITE_NAME else SITE_NAME
    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(description or '眠る前にゆっくり聞ける世界史チャンネル「寝落ち世界史」の原稿集です。')}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{rel}style.css?v={CSS_VERSION}">
</head>
<body>
<header class="site"><div class="wrap">
  <a class="brand" href="{rel}">寝落ち世界史</a>
  <nav><a href="{CHANNEL_URL}">YouTube</a><a href="{rel}privacy/">プライバシー</a></nav>
</div></header>
<main><div class="wrap">
{body}
</div></main>
<footer class="site"><div class="wrap">
  「寝落ち世界史」は、眠る前にゆっくり聞ける世界史の YouTube チャンネルです。<br>
  <a href="{CHANNEL_URL}">YouTube チャンネル</a> ・ <a href="{NOTE_URL}">note</a> ・ <a href="{rel}privacy/">プライバシーポリシー</a>
</div></footer>
</body>
</html>
"""


def paragraphs(text: str) -> str:
    blocks = [b.strip() for b in text.replace("\r\n", "\n").split("\n\n") if b.strip()]
    return "\n".join(
        "<p>" + "<br>".join(html.escape(line) for line in b.split("\n")) + "</p>" for b in blocks
    )


def load_entries() -> list[dict]:
    entries = []
    for f in sorted(CONTENT.glob("*.json")):
        e = json.loads(f.read_text(encoding="utf-8"))
        e["slug"] = f.stem
        e["_publish"] = datetime.fromisoformat(e["publishAt"]).astimezone(JST)
        entries.append(e)
    return sorted(entries, key=lambda e: e["_publish"], reverse=True)


def build() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "scripts").mkdir(parents=True)
    (OUT / "style.css").write_text(CSS.strip() + "\n", encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    now = datetime.now(JST)
    entries = load_entries()
    for e in entries:
        d = OUT / "scripts" / e["slug"]
        d.mkdir()
        watch = f'<a class="watch" href="{html.escape(e["videoUrl"])}">▶ YouTube で動画を見る</a>' if e.get("videoUrl") else ""
        body = (
            f"<h1>{html.escape(e['title'])}</h1>\n"
            f'<div class="meta">{e["_publish"]:%Y年%-m月%-d日} 公開</div>\n'
            f"{watch}\n<div class=\"body\">\n{paragraphs(e['body'])}\n</div>\n{watch}"
        )
        desc = e["body"].replace("\n", "")[:110] + "…"
        (d / "index.html").write_text(page(e["title"], body, depth=2, description=desc), encoding="utf-8")

    published = [e for e in entries if e["_publish"] <= now]
    items = "\n".join(
        f'<li><a href="scripts/{e["slug"]}/"><span class="d">{e["_publish"]:%Y.%m.%d}</span>'
        f'<span class="t">{html.escape(e["title"])}</span></a></li>'
        for e in published
    ) or '<li class="empty">原稿は準備中です。</li>'
    index = (
        f"<h1>{SITE_NAME}</h1>\n"
        '<p class="lead">歴史を、眠るように楽しむ。<br>YouTube チャンネル「寝落ち世界史」で朗読している原稿を掲載しています。'
        "動画と一緒に、または文字でゆっくりお楽しみください。</p>\n"
        f'<h2>原稿一覧</h2>\n<ul class="list">\n{items}\n</ul>'
    )
    (OUT / "index.html").write_text(page(SITE_NAME, index, depth=0), encoding="utf-8")

    privacy = (OUT / "privacy")
    privacy.mkdir()
    (privacy / "index.html").write_text(
        page("プライバシーポリシー", (ROOT / "privacy.html").read_text(encoding="utf-8"), depth=1), encoding="utf-8"
    )
    print(f"built {len(entries)} script pages ({len(published)} listed) → {OUT}")


if __name__ == "__main__":
    build()
