# 寝落ち世界史 原稿集

YouTube チャンネル「寝落ち世界史」の原稿を公開するサイト（GitHub Pages: https://neochi-sekaishi.github.io/ ）。

- `content/scripts/<公開日>.json` … 原稿データ（`add_script.py` で追加）
- `build.py` … `docs/` に静的 HTML を生成。公開用の生成は GitHub Actions（`.github/workflows/pages.yml`）が push 時と毎時5分に行う（公開時刻を過ぎた原稿が一覧に載る）
- `publish.sh` … 原稿データを push（ローカルの docs/ はプレビュー用で push しない）
- `privacy.html` … プライバシーポリシー本文
