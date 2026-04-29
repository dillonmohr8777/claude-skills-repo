# Gumroad Upload Runbook

Step-by-step to get all 37 products live on Gumroad. Total time: ~2 hours.

## Before you start

1. **Create your Gumroad seller account** if you don't have one: https://gumroad.com/signup
2. **Set up payouts:** Settings → Payouts → connect Stripe or PayPal
3. **Verify your tax info:** Gumroad will withhold otherwise
4. **Optional but recommended:** custom domain (e.g. `skills.dillonmohr.com`) — connect via Gumroad Settings → Domains

## Step 1: Generate the zips

```bash
cd /home/user/claude-skills-repo
bash marketing-skills-store/gumroad-prep/build_zips.sh
```

This produces all 37 `.zip` files in `marketing-skills-store/gumroad-prep/dist/`:

- 6 bundle zips (~30K each)
- 1 mega-pack zip (~131K)
- 30 individual skill zips (in `dist/individual/`)

## Step 2: Upload order (start with mega-pack + bundles, individuals can follow)

Recommended sequence — each one takes ~5 minutes once you've done one:

### Phase A: List the mega-pack first (highest leverage)

1. Gumroad → New Product → Digital Product
2. **Name:** "The Marketing Operator's Mega-Pack — 30 Claude Skills"
3. **Description:** paste contents of `marketing-skills-store/sales-pages/mega-pack.md` (Gumroad accepts Markdown)
4. **Cover image:** create a 1280×720 image. See "Image specs" below.
5. **Price:** $497
6. **File:** upload `mega-pack-all-30-skills.zip`
7. **URL slug:** `marketing-mega-pack`
8. **Tags:** marketing, claude-skills, ai-agents, automation, hubspot, google-ads, seo, meta-ads
9. **Refund policy:** 14-day, set in Gumroad's policy
10. **Publish:** start as DRAFT to preview; publish when ready

### Phase B: List the 6 bundles ($179 each)

For each bundle, repeat the above with:
- Name: e.g. "Paid Search Operator Pack — 5 Claude Skills"
- Description: contents of corresponding `sales-pages/bundle-XX-*.md`
- Price: $179
- File: corresponding bundle .zip
- Slug: e.g. `paid-search-operator-pack`

### Phase C: List the 30 individual skills (optional but recommended)

For each individual, list at $19-49:
- Hero skills ($39-49): real-estate-lead-gen-architect, hubspot-blog-optimizer, semrush-keyword-extractor
- Standard skills ($29): most of the rest
- Lower-volume / niche skills ($19): some long-tail picks

Pricing matrix in `marketing-skills-store/gumroad-prep/PRICING.md` (next file).

## Step 3: Cover image specs

Gumroad recommends 1280×720 or 600×600. Use Canva, Figma, or Photoshop.

For each bundle, the cover should include:
- Bundle name (large, top-left)
- "5 Claude Skills" (subhead)
- The receipt headline (e.g., "$1.7M / $5,400 ad spend, 314x ROAS" for bundle 2)
- Visual: a simple terminal-style screenshot or abstract code-ish background
- Your name in bottom-right ("Built by Dillon Mohr")

For the mega-pack, lean into "30 Skills" prominently + the consolidated proof points.

**Quick option:** generate covers via Claude / DALL-E with prompts like:
> "Marketing skills bundle cover image, 1280x720, dark navy + electric blue, terminal-style code overlay, large title 'Paid Search Operator Pack', subhead '5 Claude Skills', proof line '$1.7M closed deals on $5,400 ad spend', author tag 'Built by Dillon Mohr'"

## Step 4: Set up bundle discounts

In each bundle product, add a discount code:
- **MEGAPACK497** — discounts $1,074 (sum of all 6 bundles à la carte) to $497
- **EARLY50** — first 50 buyers of the mega-pack pay $397 (drives launch urgency on tweet)

## Step 5: Set up affiliates (optional, do this in week 2)

Settings → Affiliates → enable
- Default commission: 30%
- Cookie window: 60 days
- Approve affiliates manually for the first 30 days (avoid spammers)

## Step 6: Launch announcements

### Day 0 — Twitter/X thread

```
After 6 months of running Claude Code 5 hours a day, I've turned my actual production marketing agents into something I can sell.

30 skills. 6 bundles. The same agents that drove:
• $1.7M / $5,400 ad spend at Secure Lending
• AS 2 → 24 at Datastrike
• +17.2% organic in 30 days at Align HCM
• 3,100 tickets across 5 Bar Crawl USA cities

Receipts in thread ↓
```

Then 5-7 follow-up tweets, each highlighting one bundle with a specific receipt + Gumroad link.

### Day 0 — LinkedIn post

Same content, tightened and reformatted for LinkedIn's slower-scrolling audience.

### Day 0 — Direct DMs

Reach out to 10-15 marketers in your network with a personalized message. Each gets a free coupon code (`FRIEND100` for $100 off mega-pack).

### Day 1-7 — Daily content

Pick one skill per day, post a 60-second screen recording demoing it. End each post with the Gumroad link.

## Step 7: Monitor + iterate

First 7 days, watch:
- Page views per product (Gumroad → Analytics)
- Conversion rate per product (visits → purchases)
- Top traffic sources

After 7 days:
- Highest-converting product gets more marketing attention
- Lowest-performing products: A/B test cover image + first paragraph of description
- Add testimonials as buyers send feedback (with permission)

## Step 8: Customer support

Gumroad inbox handles messages. Set up:
- Auto-response on purchase: thank-you + INSTALL.md highlights + "reply if you hit any issues"
- 24-hour SLA on inbound messages
- FAQ doc you reuse: setup, MCP issues, refund process

## Step 9: Updates

When you ship updates to skills:
- Bump version in SKILL.md frontmatter (1.0.0 → 1.1.0)
- Re-run `build_zips.sh`
- Replace the file in each Gumroad product
- Email customers via Gumroad's "send update" feature: "Updated [bundle] with [improvement]. Re-download for free."

This is one of Gumroad's killer features — keeps customers happy + drives word-of-mouth.

## Troubleshooting

| Issue | Fix |
|---|---|
| "File too large" | Gumroad allows up to 16GB per file; should be fine for these zips (≤ 131K) |
| "Description shows raw markdown" | Gumroad sometimes needs you to paste then re-edit; use the WYSIWYG view |
| Customer says "skill won't install" | Walk them through INSTALL.md verification: `~/.claude/skills/<name>/SKILL.md` exists? Restart Claude Code? |
| Refund request | Issue immediately via Gumroad → Sales → Refund. Don't argue. |

## Pricing summary table

(See `PRICING.md` in this folder for the full matrix.)

| Tier | Product | Price |
|---|---|---|
| Mega-pack | All 30 skills | $497 |
| Bundle | 5 skills (any of 6 bundles) | $179 |
| Hero individual | 3 specific high-value skills | $39-49 |
| Standard individual | Most others | $29 |
| Long-tail individual | Niche / supporting | $19 |
