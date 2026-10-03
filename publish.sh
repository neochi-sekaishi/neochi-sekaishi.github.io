#!/bin/zsh
# サイトを再生成して GitHub に push する（GitHub Pages が数十秒〜数分で反映）
set -e
cd "${0:A:h}"
python3 build.py
git add -A
if git diff --cached --quiet; then echo "変更なし"; exit 0; fi
git commit -q -m "${1:-原稿を更新}"
git push -q origin main
echo "公開しました: https://neochi-sekaishi.github.io/"
