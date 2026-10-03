#!/bin/zsh
# 原稿データを GitHub に push する。サイトの生成と公開は GitHub Actions が行う（数分で反映）。
# ローカルでも build.py を実行して docs/ を作る（プレビュー・エラー確認用、push はしない）。
set -e
cd "${0:A:h}"
python3 build.py
git add -A
if git diff --cached --quiet; then echo "変更なし"; exit 0; fi
git commit -q -m "${1:-原稿を更新}"
git pull -q --rebase origin main
git push -q origin main
echo "push しました。数分で https://neochi-sekaishi.github.io/ に反映されます。"
