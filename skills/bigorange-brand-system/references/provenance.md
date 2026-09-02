# Provenance and conflict rulings

| Item | Source | Date | Ruling |
|---|---|---|---|
| Logo PNGs | bigorange.marketing `/wp-content/uploads/2025/05/BOM-logo-orange.png`, `/2023/09/BOM-logo-white.png` | 2026-07-16 | Exact artwork. Pinned in `assets/SHA256SUMS`. |
| Brand orange `#FF7C00` | Dominant opaque pixel of the orange logo PNG | 2026-09-02 | Deck, document and social orange. |
| Theme orange `#F68326`, border `#D66509`, blue `#428BCA` | Beaver Builder skin CSS on the live site | 2026-09-02 | Web and editorial only. |
| Older theme orange `#FF7700` | Site CSS observed in the July audit | 2026-07-16 | Web ledger, legacy. |
| Site fonts Raleway, Open Sans, Poppins | Live site CSS | 2026-09-02 | Web and editorial only. Poppins is inherited, never added. |
| Montserrat for display | Wordmark letterforms in the logo | 2026-09-02 | Deck, document, social. |
| Deck reference | 15-slide Thursday review built with the kit | 2026-09-03 | Visual proof of the kit; not a template to hand-edit. |
| v0 PDFs (dark brown covers, Arial) | Superseded September 2 review copy | 2026-09-02 | Retired. `#2B1A10` is a banned colour. |
| Awards and certifications | `references/brand-research-2026-09.md` | 2026-09-02 | HubSpot tier is inconsistent on the site ("Partner" badge vs "Gold Partner" copy): say "HubSpot Partner" until BigOrange confirms. Review counts differ by source (site 50+, Birdeye 70, Clutch 10): quote "50+ five-star Google reviews" from the site only. |
| Pricing | `/pricing/` returns 404 | 2026-09-02 | Never state prices from memory. Hub pages carry tier language; quote it with attribution or use the proposal figure. |
| Client names | `bigorange-client-radar` roster only | rolling | A name appears in a deck only with roster evidence and a verified logo. Dillon's own portfolio (Align HCM, AMI, Shadow, Momentum 360) is never presented as BigOrange work. |

Conflicts get resolved here, not in individual decks. When a newer master or
brand kit arrives from BigOrange, run `scripts/extract_pptx_theme.py` on it,
update `tokens.md` and `brand_lint.py`, and add a row above.
