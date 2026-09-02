# Fonts

All faces are SIL Open Font License and are not committed (see `.gitignore`).
Fetch the variable TTFs from the Google Fonts repository before rendering PDFs:

```bash
cd assets/fonts
for u in \
  "ofl/montserrat/Montserrat%5Bwght%5D.ttf" \
  "ofl/montserrat/Montserrat-Italic%5Bwght%5D.ttf" \
  "ofl/sourceserif4/SourceSerif4%5Bopsz,wght%5D.ttf" \
  "ofl/sourceserif4/SourceSerif4-Italic%5Bopsz,wght%5D.ttf" \
  "ofl/inter/Inter%5Bopsz,wght%5D.ttf"; do
  curl -sSL -o "$(basename "$u" | sed 's/%5B/[/;s/%5D/]/;s/%2C/,/')" "https://raw.githubusercontent.com/google/fonts/main/$u"
done
mkdir -p ~/.fonts && cp *.ttf ~/.fonts/ && fc-cache -f
```

`lib/doc-kit/theme.css` references these files relative to the HTML being
rendered (`assets/...`). When rendering from another folder, copy or symlink
`assets/` next to the HTML.

Decks do not embed fonts. They set Montserrat for display and Arial for body;
PowerPoint substitutes when Montserrat is absent, and the layouts leave slack
for that.

Web and editorial surfaces use the live theme's Raleway and Open Sans; do not
ship Montserrat into WordPress.
