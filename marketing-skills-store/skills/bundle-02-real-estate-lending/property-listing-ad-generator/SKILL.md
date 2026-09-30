---
name: "property-listing-ad-generator"
description: "Generates platform-specific listing ads for real estate agents — Meta carousel, Google Display, Zillow Premier Agent, and YouTube — from a single property MLS feed or detail sheet. Outputs headlines, ad copy, image-selection guidance, and per-platform compliance. Use when the user is a real estate agent with a new listing, doing a price-drop relaunch, marketing a coming-soon, or running ads on a portfolio of properties."
license: proprietary
metadata:
  version: 1.0.0
  author: Dillon Mohr
  category: marketing/lead-gen
  domain: real-estate
  updated: 2026-04-26
  mcp_servers: ["meta-ads"]
---

# Property Listing Ad Generator

You write ads for individual properties that sell the *outcome of owning the home*, not the property's bullet-list specs. Most listing ads are MLS data scraped into ad copy. They underperform by 3-5x.

## When to use

- Agent has a new listing and wants ads in 30 minutes, not 3 hours
- Price-drop relaunch needs new creative angle (don't reuse the original)
- Coming-soon listing needs a teaser campaign
- Investor wants to advertise a portfolio of similar properties

## Inputs you need

- **MLS data** (or property detail sheet): address, price, beds/baths/sqft, year, lot size, photos
- **The story** of the home: why is it special? Who's it for?
- **Comparable sales** in the area (helps with positioning)
- **Days on market** (changes the copy strategy)
- **Compliance:** Fair Housing language, agent license, broker info

## Process

### 1. Pick the angle

Each listing has 1-2 dominant angles. Pick before writing:

| Angle | Best for | Hook |
|---|---|---|
| **Lifestyle** | Family homes, lifestyle properties | "Where Saturdays Slow Down" |
| **Investment** | Multifamily, vacation rentals, BRRRR-friendly | "$X cash flow projection on this Phoenix duplex" |
| **First-time buyer** | Starter homes under FHA/VA limit | "Your first home for $X/mo (FHA-eligible)" |
| **Luxury / exclusive** | Premium properties | "Two minutes from [landmark]. One showing left this week." |
| **Flip-able** | Properties needing work | "Equity in the dirt: $X under comp" |
| **Downsize** | Empty-nester homes | "Less house, more living" |

### 2. Write headlines per platform

Different platforms = different headline grammar.

**Meta Ads (carousel + single image)**
- Lead headline: 25-40 chars, outcome-led
- Examples:
  - "$485K, walk to the park, move-in May"
  - "Your Phoenix family home (4 bed / pool)"
  - "Backyard you'll never want to leave"

**Google Display / Performance Max**
- 30-char headlines (multiple)
- 90-char descriptions
- Lead with neighborhood + price range

**Zillow Premier Agent**
- Use Zillow's standard fields; supplement with custom Q&A copy if available

**YouTube (15-30s pre-roll)**
- First 3 seconds: visual hook (drone shot, key feature)
- Voiceover beat 1: address + price range
- Voiceover beat 2: 2 unique features (specific, not generic)
- Voiceover beat 3: CTA ("Tour this Saturday — link below")

### 3. Image / video strategy

This is where most listing ads fail. The MLS hero image is rarely the best ad image.

**Hero image rules:**
- Lifestyle shot > exterior architecture shot (most ads need a person's life implied)
- Daytime > twilight unless property is luxury
- Ground-level > drone for first impression (drone for #2 in carousel)
- Avoid wide-angle distortion that makes rooms look "Instagram-fake"

**Carousel sequencing (Meta):**
1. Hook image (lifestyle / outcome)
2. Wide exterior
3. Kitchen (always — kitchens sell homes)
4. Primary bedroom
5. Outdoor space / unique feature
6. Floor plan (this card has 30%+ engagement)
7. CTA card with address + agent contact

**Video clip order (Reels / Shorts):**
- 0-1s: outcome shot (kid in pool, dog on porch, car in driveway)
- 1-3s: best 1-2 interior beats
- 3-7s: "what makes this home different" specific feature
- 7-12s: address + price + CTA

### 4. Compliance lock-in

Real estate ads are heavily regulated. Always include:

- **Fair Housing logo** (or "Equal Housing Opportunity" text)
- **Agent name + license #** (state-dependent format)
- **Brokerage name + address**
- **No demographic targeting language** ("perfect for young families" is a Fair Housing violation; "perfect for families" can also be flagged)
- Meta requires "Special Ad Category: Housing" toggle ON

### 5. Ad set targeting per angle

| Angle | Targeting framework |
|---|---|
| Lifestyle / family | Geo + age 28-45 + life events (married, kids) |
| Investment | Geo (broader — investors travel) + interest in real-estate-investing + income $100K+ |
| First-time buyer | Geo + age 22-35 + renter detection (Meta + custom audience) |
| Luxury | Geo (tight, higher-income zips) + interest in luxury indicators |
| Downsize | Geo + age 55-72 + "newly retired" or "empty nester" segments |

## Output format

```
# Listing Ad Set: <address>

## Strategic summary
- Angle: <lifestyle | investment | first-time | luxury | flip | downsize>
- Target audience: <persona>
- Recommended platforms: Meta carousel + Google PMax + (optional) Reels
- Budget recommendation: $X/day (typically $20-50 for solo listing)

## Meta carousel (7 cards)
[Per-card image direction + caption + headline]

## Meta single-image variants (3)
[3 alternate creative directions for testing]

## Google PMax assets
- Headlines (15)
- Descriptions (5)
- Logo / image specs

## Reels / Shorts script (15s)
[Beat-by-beat script with B-roll directions]

## Ad set targeting
[Full Meta + Google targeting]

## Compliance checklist
- [ ] Fair Housing language present
- [ ] Agent license # included
- [ ] Brokerage info included
- [ ] No demographic targeting language
- [ ] Meta Special Ad Category: Housing → ON

## Phase plan
- Day 1-3: launch all 3 single-image variants + carousel
- Day 4-7: kill bottom CTR variant; double winning variant
- Day 8+: refresh creative if engagement drops 30%+
```

## Common mistakes

1. **Using the MLS description verbatim.** It's written for other agents, not buyers. Rewrite.
2. **Listing every spec ("3 bed, 2 bath, hardwood, granite, SS appliances").** Buyers' eyes glaze over. Pick 2-3 specifics.
3. **No CTA in the ad.** "See more photos" is not enough. Use "Tour this Saturday" or "Get full info".
4. **Same creative for all platforms.** Different aspect ratios + different intent. Customize.
5. **Running ads with no Fair Housing toggle.** Meta will eventually flag and disable the ad account.
6. **Over-photoshopped images.** Wide-angle distortion + HDR grass kills trust. Buyers can tell.

## Compliance (real-estate ads)

- **Fair Housing Act:** no protected-class targeting or language. "Family-friendly" is risky; "near elementary school" is fine.
- **State licensing:** every ad must include agent + brokerage license info
- **Truth in advertising:** features described must be present. No "potential" without disclosure.
- **NAR rules:** use the Realtor® mark only if you're a member

## Leverage with other skills

- Run with `real-estate-lead-gen-architect` for the broader audience-build context
- Use `high-intent-buyer-persona-mapper` if you're targeting one specific persona for a portfolio of listings

## MCP integration

With `meta-ads` MCP: `Generate the carousel ads, single-image variants, and Reels script for the listing at [address]. Apply Special Ad Category: Housing. Schedule launch at $30/day for 7 days.`
