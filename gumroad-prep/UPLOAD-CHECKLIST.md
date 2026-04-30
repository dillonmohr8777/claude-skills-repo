# Gumroad Upload Checklist

Use this as the human-only upload sequence. Stop before any Gumroad, Stripe, OAuth, payout, tax, or account-credential step. Do not script logins or API uploads.

## Upload order

1. Create and publish the mega-pack first.
2. Create and publish the 6 bundle products.
3. Create and publish the 30 individual skill products.
4. Add discount codes after all products exist.
5. Run the post-launch test plan with your own purchase.

## Global product settings

- Product type: Digital product
- File delivery: Attach the zip listed for each product
- License: Single-operator commercial license, unlimited client accounts unless a team license is purchased separately
- Refund policy: 14-day no-questions-asked
- Update promise: 12 months of updates
- Support: Gumroad messages
- Cover image size: 1280x720 pixels
- Long description for mega and bundles: paste the full rewritten markdown from the listed `sales-pages` file

## Primary products

| Upload # | Title | Price | Short description | Long description | File path on disk |
|---|---:|---|---|---|---|
| 1 | The Marketing Operator's Mega-Pack | $497 | 30 Claude Skills across paid search, HubSpot, SEO, paid social, lead gen, and analytics, built from named client results. | Paste full contents of `sales-pages\mega-pack.md`. | `gumroad-prep\dist\mega-pack-all-30-skills.zip` |
| 2 | Paid Search Operator Pack | $179 | 5 Google Ads Claude Skills built from the Secure Lending 314x ROAS paid-search system. | Paste full contents of `sales-pages\bundle-01-paid-search-operator.md`. | `gumroad-prep\dist\bundle-01-paid-search-operator.zip` |
| 3 | Real Estate & Lending Lead Gen Pack | $179 | 5 Claude Skills for mortgage and real estate lead generation, based on $1.7M closed from $5,400 spend. | Paste full contents of `sales-pages\bundle-02-real-estate-lending.md`. | `gumroad-prep\dist\bundle-02-real-estate-lending.zip` |
| 4 | HubSpot Operator Pack | $179 | 5 Claude Skills for HubSpot blog, workflow, scoring, pipeline, and sequence work. | Paste full contents of `sales-pages\bundle-03-hubspot-operator.md`. | `gumroad-prep\dist\bundle-03-hubspot-operator.zip` |
| 5 | SEO Authority Builder Pack | $179 | 5 Claude Skills for SEMrush keyword work, content briefs, internal links, and AI Overview optimization. | Paste full contents of `sales-pages\bundle-04-seo-authority-builder.md`. | `gumroad-prep\dist\bundle-04-seo-authority-builder.zip` |
| 6 | Multi-Market Paid Social Pack | $179 | 5 Claude Skills for multi-city paid social, event funnels, Reels, TikTok, and Meta structure. | Paste full contents of `sales-pages\bundle-05-multi-market-paid-social.md`. | `gumroad-prep\dist\bundle-05-multi-market-paid-social.zip` |
| 7 | Conversion + Analytics Pack | $179 | 5 Claude Skills for landing-page audits, A/B tests, funnel leakage, GA4, and attribution. | Paste full contents of `sales-pages\bundle-06-conversion-analytics.md`. | `gumroad-prep\dist\bundle-06-conversion-analytics.zip` |

## Individual products

For individual products, use this field pattern:

- Title: convert the skill slug into title case, then add `Claude Skill`. Example: `GA4 Setup Architect Claude Skill`.
- Price: use the table below.
- Short description: `A production-ready Claude Skill for [specific job], with commercial use and setup docs included.`
- Long description: `This individual skill is extracted from the [bundle name]. It includes the SKILL.md file, INSTALL.md, ABOUT-THE-AUTHOR.md, LICENSE.md, single-operator commercial use, and 12 months of updates. Use the full bundle if you want the surrounding workflow.`
- File path: `gumroad-prep\dist\individual\<skill-name>.zip`

| Skill product | Price | Bundle | File path on disk |
|---|---:|---|---|
| google-ads-campaign-architect | $29 | Paid Search Operator | `gumroad-prep\dist\individual\google-ads-campaign-architect.zip` |
| google-ads-quality-score-fixer | $29 | Paid Search Operator | `gumroad-prep\dist\individual\google-ads-quality-score-fixer.zip` |
| google-ads-keyword-strategist | $29 | Paid Search Operator | `gumroad-prep\dist\individual\google-ads-keyword-strategist.zip` |
| negative-keyword-mining | $29 | Paid Search Operator | `gumroad-prep\dist\individual\negative-keyword-mining.zip` |
| google-ads-ad-copy-tester | $29 | Paid Search Operator | `gumroad-prep\dist\individual\google-ads-ad-copy-tester.zip` |
| real-estate-lead-gen-architect | $49 | Real Estate & Lending Lead Gen | `gumroad-prep\dist\individual\real-estate-lead-gen-architect.zip` |
| mortgage-funnel-builder | $29 | Real Estate & Lending Lead Gen | `gumroad-prep\dist\individual\mortgage-funnel-builder.zip` |
| high-intent-buyer-persona-mapper | $29 | Real Estate & Lending Lead Gen | `gumroad-prep\dist\individual\high-intent-buyer-persona-mapper.zip` |
| property-listing-ad-generator | $29 | Real Estate & Lending Lead Gen | `gumroad-prep\dist\individual\property-listing-ad-generator.zip` |
| loan-officer-nurture-sequence | $29 | Real Estate & Lending Lead Gen | `gumroad-prep\dist\individual\loan-officer-nurture-sequence.zip` |
| hubspot-blog-optimizer | $49 | HubSpot Operator | `gumroad-prep\dist\individual\hubspot-blog-optimizer.zip` |
| hubspot-workflow-designer | $29 | HubSpot Operator | `gumroad-prep\dist\individual\hubspot-workflow-designer.zip` |
| hubspot-lead-scoring-builder | $29 | HubSpot Operator | `gumroad-prep\dist\individual\hubspot-lead-scoring-builder.zip` |
| hubspot-pipeline-architect | $29 | HubSpot Operator | `gumroad-prep\dist\individual\hubspot-pipeline-architect.zip` |
| hubspot-email-sequencer | $29 | HubSpot Operator | `gumroad-prep\dist\individual\hubspot-email-sequencer.zip` |
| semrush-keyword-extractor | $39 | SEO Authority Builder | `gumroad-prep\dist\individual\semrush-keyword-extractor.zip` |
| keyword-cluster-architect | $29 | SEO Authority Builder | `gumroad-prep\dist\individual\keyword-cluster-architect.zip` |
| content-brief-builder | $29 | SEO Authority Builder | `gumroad-prep\dist\individual\content-brief-builder.zip` |
| internal-link-strategist | $29 | SEO Authority Builder | `gumroad-prep\dist\individual\internal-link-strategist.zip` |
| ai-overview-optimizer | $29 | SEO Authority Builder | `gumroad-prep\dist\individual\ai-overview-optimizer.zip` |
| local-event-paid-social-playbook | $39 | Multi-Market Paid Social | `gumroad-prep\dist\individual\local-event-paid-social-playbook.zip` |
| multi-market-meta-campaign-launcher | $29 | Multi-Market Paid Social | `gumroad-prep\dist\individual\multi-market-meta-campaign-launcher.zip` |
| event-ticketing-funnel-builder | $29 | Multi-Market Paid Social | `gumroad-prep\dist\individual\event-ticketing-funnel-builder.zip` |
| instagram-reels-promo-script-writer | $29 | Multi-Market Paid Social | `gumroad-prep\dist\individual\instagram-reels-promo-script-writer.zip` |
| tiktok-ads-strategist | $29 | Multi-Market Paid Social | `gumroad-prep\dist\individual\tiktok-ads-strategist.zip` |
| landing-page-auditor | $29 | Conversion + Analytics | `gumroad-prep\dist\individual\landing-page-auditor.zip` |
| ab-test-designer | $29 | Conversion + Analytics | `gumroad-prep\dist\individual\ab-test-designer.zip` |
| funnel-leakage-mapper | $29 | Conversion + Analytics | `gumroad-prep\dist\individual\funnel-leakage-mapper.zip` |
| ga4-setup-architect | $29 | Conversion + Analytics | `gumroad-prep\dist\individual\ga4-setup-architect.zip` |
| attribution-model-picker | $29 | Conversion + Analytics | `gumroad-prep\dist\individual\attribution-model-picker.zip` |

## Cover image specs and prompts

Create 7 cover images at 1280x720. Use one style family across all products: premium dark operator dashboard, sharp typography space, proof-led visual cues, no fake app screenshots, no unreadable tiny text.

1. Mega-pack prompt: `1280x720 premium digital product cover for The Marketing Operator's Mega-Pack, dark graphite background with crisp white and orange accents, six connected marketing command panels for paid search, HubSpot, SEO, paid social, lead gen, and analytics, subtle grid, high-end SaaS operator aesthetic, strong empty space for title, no tiny text, no logos, no people.`
2. Paid Search prompt: `1280x720 digital product cover for Paid Search Operator Pack, Google Ads inspired command center without official logos, search query rows, campaign structure map, CPC and ROAS charts, orange and white accents on graphite, premium consultant toolkit look, empty title area, no tiny text.`
3. Real Estate & Lending prompt: `1280x720 digital product cover for Real Estate and Lending Lead Gen Pack, modern mortgage funnel map from ad click to CRM to closed deal, subtle home outline and loan pipeline cards, confident premium look, graphite background, orange and white accents, no stock photo feel, no tiny text.`
4. HubSpot Operator prompt: `1280x720 digital product cover for HubSpot Operator Pack, clean CRM and blog operations dashboard, workflow branches, lead scoring tiles, content optimization cards, warm orange accents, polished B2B operator aesthetic, no official logos, no tiny text.`
5. SEO Authority prompt: `1280x720 digital product cover for SEO Authority Builder Pack, SEMrush style keyword and authority dashboard without official logos, topic clusters, internal link map, ranking lift chart, AI Overview card motif, graphite and orange palette, premium and sharp, no tiny text.`
6. Multi-Market Paid Social prompt: `1280x720 digital product cover for Multi-Market Paid Social Pack, map with five city campaign nodes, event ticket sales curve, Meta style ad cards without official logos, vibrant but premium orange accents on dark graphite, designed for event marketers, no tiny text.`
7. Conversion + Analytics prompt: `1280x720 digital product cover for Conversion and Analytics Pack, funnel leakage map, GA4 style event stream without official logos, A/B test split view, attribution path lines, clean technical operator aesthetic, graphite background with orange and white accents, no tiny text.`

## Discount code matrix

Create these manually in Gumroad after all products exist.

| Code | Purpose | Discount | Applies to | Limit | Timing |
|---|---|---:|---|---:|---|
| FOUNDERSWEEK | Founder's-week launch push | 25% off | Mega-pack and bundles | 100 uses | First 7 days after launch |
| BUNDLECROSS | Bundle-buyer cross-sell to mega-pack | $100 off | Mega-pack only | 200 uses | Send to bundle buyers after purchase |
| EARLY100 | Mega-pack early-bird | $100 off | Mega-pack only | First 100 buyers | Keep live until 100 redemptions |
| BUNDLE50 | Single-bundle launch assist | $50 off | Any one bundle | 200 uses | Optional if bundle sales are slow |
| FRIEND | Private relationship code | $50 off | Any product | Manual use only | Use sparingly |

## Post-launch test plan

1. Open each product page in a logged-out browser window.
2. Confirm title, price, short description, long description, cover image, refund language, and file attachment.
3. Buy the mega-pack with your own card or a Gumroad test purchase path if available.
4. Confirm the receipt email arrives.
5. Confirm the download button works.
6. Download the attached zip.
7. Open the zip and confirm it contains `README.md`, `INSTALL.md`, `ABOUT-THE-AUTHOR.md`, `LICENSE.md`, and the expected `skills` folder.
8. Repeat one bundle purchase test.
9. Repeat one individual skill purchase test.
10. Refund the test purchases only after receipt, download, and file contents are confirmed.
11. Save screenshots of the product page, checkout, receipt email, and downloaded zip contents for launch records.
12. Do not connect API upload automation, payout settings, Stripe changes, or OAuth flows from Codex.
