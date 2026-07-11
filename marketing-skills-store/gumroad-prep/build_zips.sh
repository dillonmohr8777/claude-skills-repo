#!/usr/bin/env bash
# Build the Gumroad-ready zip files from the marketing-skills-store/ source tree.
#
# Output: marketing-skills-store/gumroad-prep/dist/
#   - bundle-01-paid-search-operator.zip
#   - bundle-02-real-estate-lending.zip
#   - bundle-03-hubspot-operator.zip
#   - bundle-04-seo-authority-builder.zip
#   - bundle-05-multi-market-paid-social.zip
#   - bundle-06-conversion-analytics.zip
#   - mega-pack-all-30-skills.zip
#   - individual/<skill-name>.zip   (30 individual skill zips)
#
# Each zip contains:
#   - the skill folder(s) with SKILL.md
#   - INSTALL.md
#   - ABOUT-THE-AUTHOR.md
#   - LICENSE.md
#   - the bundle's sales page as README.md (the customer's first read on unzip)

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$ROOT/gumroad-prep/dist"
SKILLS="$ROOT/skills"
SHARED="$ROOT/shared"
SALES="$ROOT/sales-pages"

rm -rf "$DIST"
mkdir -p "$DIST/individual"

# --- Bundle zips ---
for bundle_dir in "$SKILLS"/bundle-*; do
  bundle_id=$(basename "$bundle_dir")             # e.g. bundle-01-paid-search-operator
  short_id="${bundle_id#bundle-}"                  # e.g. 01-paid-search-operator
  sales_page="$SALES/$bundle_id.md"
  if [[ ! -f "$sales_page" ]]; then
    echo "SKIP: missing sales page for $bundle_id"
    continue
  fi
  echo "Building zip for $bundle_id..."
  staging="$DIST/$bundle_id"
  mkdir -p "$staging/skills"
  cp -r "$bundle_dir"/* "$staging/skills/"
  cp "$SHARED/INSTALL.md"           "$staging/INSTALL.md"
  cp "$SHARED/ABOUT-THE-AUTHOR.md"  "$staging/ABOUT-THE-AUTHOR.md"
  cp "$SHARED/LICENSE.md"           "$staging/LICENSE.md"
  cp "$sales_page"                  "$staging/README.md"
  (cd "$DIST" && zip -qr "$bundle_id.zip" "$bundle_id")
  rm -rf "$staging"
done

# --- Mega-pack zip (all 30) ---
echo "Building mega-pack zip..."
mega="$DIST/mega-pack-all-30-skills"
mkdir -p "$mega/skills"
cp -r "$SKILLS"/bundle-* "$mega/skills/"
cp "$SHARED/INSTALL.md"           "$mega/INSTALL.md"
cp "$SHARED/ABOUT-THE-AUTHOR.md"  "$mega/ABOUT-THE-AUTHOR.md"
cp "$SHARED/LICENSE.md"           "$mega/LICENSE.md"
cp "$SALES/mega-pack.md"          "$mega/README.md"
(cd "$DIST" && zip -qr "mega-pack-all-30-skills.zip" "mega-pack-all-30-skills")
rm -rf "$mega"

# --- Individual skill zips (30) ---
echo "Building 30 individual skill zips..."
for skill_dir in "$SKILLS"/bundle-*/*/; do
  skill_name=$(basename "$skill_dir")
  staging="$DIST/individual/$skill_name"
  mkdir -p "$staging"
  cp -r "$skill_dir"* "$staging/"
  cp "$SHARED/INSTALL.md"           "$staging/INSTALL.md"
  cp "$SHARED/ABOUT-THE-AUTHOR.md"  "$staging/ABOUT-THE-AUTHOR.md"
  cp "$SHARED/LICENSE.md"           "$staging/LICENSE.md"
  (cd "$DIST/individual" && zip -qr "$skill_name.zip" "$skill_name")
  rm -rf "$staging"
done

# --- Summary ---
echo ""
echo "Done. Output:"
ls -lh "$DIST"/*.zip 2>/dev/null | awk '{print "  " $9, "(" $5 ")"}'
echo ""
echo "Individual skill zips: $(ls "$DIST/individual"/*.zip | wc -l) files in $DIST/individual/"
echo ""
echo "Total zips ready for Gumroad: $(find "$DIST" -name '*.zip' | wc -l)"
