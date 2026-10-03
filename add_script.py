"""原稿を1本追加（または更新）する。公開URLを表示する。

使い方:
  python3 add_script.py --publish-at "2026-10-15 21:00" --title "..." --body-file input/script.txt \
      [--video-url https://youtu.be/xxxx] [--project 1015_...]

スラッグ（URL）は公開日（YYYY-MM-DD）。1日1本の運用なので重複しない前提で、
同じ日付の原稿が既にあり --force がなければ止まる。
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from build import BASE_URL, CONTENT

JST = timezone(timedelta(hours=9))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--publish-at", required=True, help='"2026-10-15 21:00"（日本時間）')
    p.add_argument("--title", required=True)
    p.add_argument("--body-file", required=True, type=Path)
    p.add_argument("--video-url", default="")
    p.add_argument("--project", default="")
    p.add_argument("--force", action="store_true")
    args = p.parse_args()

    dt = datetime.fromisoformat(args.publish_at)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=JST)
    slug = f"{dt.astimezone(JST):%Y-%m-%d}"
    path = CONTENT / f"{slug}.json"
    if path.exists() and not args.force:
        existing = json.loads(path.read_text(encoding="utf-8"))
        if existing.get("title") != args.title:
            raise SystemExit(f"[重複] {slug} には別の原稿「{existing['title']}」があります。--force で上書き。")

    body = args.body_file.read_text(encoding="utf-8").strip()
    if len(body) < 1000:
        raise SystemExit(f"[原稿が短すぎます] {len(body)} 文字")
    entry = {
        "title": args.title,
        "publishAt": dt.isoformat(),
        "videoUrl": args.video_url,
        "project": args.project,
        "body": body,
    }
    CONTENT.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{BASE_URL}/scripts/{slug}/")


if __name__ == "__main__":
    main()
