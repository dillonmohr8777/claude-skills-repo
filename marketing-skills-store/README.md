# Marketing Skills Store

The 30-skill Claude Skills product catalog, packaged for sale on Gumroad.

## What's here

```
marketing-skills-store/
├── skills/                              # 30 production Claude Skills, organized into 6 bundles
│   ├── bundle-01-paid-search-operator/      # 5 skills
│   ├── bundle-02-real-estate-lending/       # 5 skills
│   ├── bundle-03-hubspot-operator/          # 5 skills
│   ├── bundle-04-seo-authority-builder/     # 5 skills
│   ├── bundle-05-multi-market-paid-social/  # 5 skills
│   └── bundle-06-conversion-analytics/      # 5 skills
├── shared/                              # Shipped with every product
│   ├── ABOUT-THE-AUTHOR.md
│   ├── INSTALL.md                       # Claude Code + MCP setup (PowerShell + macOS)
│   └── LICENSE.md                       # Single-operator commercial license
├── sales-pages/                         # Gumroad product descriptions (paste into product editor)
│   ├── bundle-01-paid-search-operator.md
│   ├── ... (6 bundle pages)
│   └── mega-pack.md                     # All-30 mega-pack sales page
└── gumroad-prep/
    ├── build_zips.sh                    # Generates all 37 product zips
    ├── GUMROAD-UPLOAD-RUNBOOK.md        # Step-by-step launch guide
    ├── PRICING.md                       # Full pricing matrix
    └── dist/                            # (gitignored) generated zips
```

## Quick start

```bash
# 1. Generate the zips
bash gumroad-prep/build_zips.sh

# 2. Output appears in gumroad-prep/dist/
ls gumroad-prep/dist/
# - 6 bundle zips
# - 1 mega-pack zip (all 30 skills)
# - 30 individual skill zips (in dist/individual/)

# 3. Follow gumroad-prep/GUMROAD-UPLOAD-RUNBOOK.md to upload
```

## The catalog at a glance

| Product | Skills | Price | Anchor receipt |
|---|---|---|---|
| **Mega-Pack** | 30 | $497 | All combined |
| Paid Search Operator | 5 | $179 | $1.7M / $5,400 |
| Real Estate & Lending Lead Gen | 5 | $179 | 314x ROAS |
| HubSpot Operator | 5 | $179 | +17.2% organic in 30 days |
| SEO Authority Builder | 5 | $179 | AS 2→24 |
| Multi-Market Paid Social | 5 | $179 | 3,100 tickets / 14 days |
| Conversion + Analytics | 5 | $179 | (cross-cutting) |

Total catalog value: ~$870 à la carte, $1,074 as 6 bundles, **$497 mega-pack** (saves $577).

## Built by

**Dillon Mohr** — MS in Integrated Marketing Communications (WVU), doctoral candidate in Strategic Media (Liberty). Currently runs paid + SEO across 16+ active client accounts.

Receipts (the same agents in this catalog produced these):
- $1.7M closed deals on $5,400 ad spend (Secure Lending Inc.)
- SEMrush AS 2 → 24 (Datastrike)
- 3,100 tickets across multi-city Meta campaigns (Bar Crawl USA)
- +17.2% organic in 30 days, 2 blogs in Google AI Overview (Align HCM)

## Next moves

1. Generate covers (1280x720) for each product — see runbook step 3
2. Upload mega-pack first — biggest revenue per upload
3. Then 6 bundles (~5 min each on Gumroad)
4. Then 30 individual skills (~2 min each, batch over a couple days)
5. Launch announcement: Twitter thread + LinkedIn post + DMs to network
