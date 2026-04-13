#!/bin/bash
set -e

echo ""
read -p "Commit message: " MSG
if [ -z "$MSG" ]; then
  echo "No message entered. Aborting."
  exit 1
fi

git add -A
git commit -m "$MSG"
git push

echo ""
echo "✓ Pushed. Cloudflare Pages will deploy in ~30 seconds."
echo "  https://carlandsally.pages.dev"
