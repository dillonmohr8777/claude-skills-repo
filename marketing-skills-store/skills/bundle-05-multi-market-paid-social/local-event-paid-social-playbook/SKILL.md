---
name: "local-event-paid-social-playbook"
description: "Designs paid-social ad campaigns for local events — bar crawls, festivals, food tours, concerts, ticketed experiences — with multi-market launch logic, urgency-based ad rotation, and conversion-API setup. Built from the system that sold 3,100 tickets across Bar Crawl USA's multi-city Taco & Tequila campaigns in a 14-day window. Use when 'sell tickets to my event', 'launch ads for a local event', 'bar crawl marketing', 'festival ad strategy', or 'multi-city event campaign'."
license: proprietary
metadata:
  version: 1.0.0
  author: Dillon Mohr
  category: marketing/paid-social
  domain: events
  updated: 2026-04-26
  mcp_servers: ["meta-ads"]
  receipts: "3,100 tickets sold across multi-city Bar Crawl USA Taco & Tequila campaigns (April 11-25)"
---

# Local Event Paid Social Playbook

You design paid-social campaigns for local ticketed events. The receipt: **3,100 tickets sold across multi-city Bar Crawl USA Taco & Tequila campaigns in a 14-day window** (April 11-25). Most event marketers run a single Meta campaign with one creative and call it a day. This playbook is the system that scales across 5+ markets simultaneously.

## When to use

- Single-event launch (festival, bar crawl, food tour, concert)
- Multi-city / multi-date series (same event in 5 cities)
- Late-stage ticket push (event in 7-14 days, need to fill remaining seats)
- Re-launch after slow initial push

## Inputs you need

- **Event details:** name, theme, date(s), location(s), price tier(s), ticket URL
- **Target attendee profile:** age range, interest stack, lifestyle indicators
- **Total tickets to sell + already sold**
- **Time to event:** affects urgency framing
- **Photo / video assets:** previous event footage, venue shots, theme imagery

## The 3-phase ticket sale curve

Every event ticket sale has 3 phases. Most under-perform because all phases get the same treatment.

### Phase 1: Awareness + Early-Bird (T-30 to T-14 days)

**Audience:** broad — interest-based + 1% lookalikes of past event attendees
**Creative:** lifestyle, "this is going to be the best Saturday of your year" emotional
**Offer:** early-bird pricing, limited quantity
**Optimization:** Reach + Add-to-Cart (NOT Purchase yet — you want learning data)
**Budget:** 30-40% of total

### Phase 2: Conversion (T-14 to T-3 days)

**Audience:** retargeting (cart abandoners, page visitors, video viewers >50%) + warm lookalikes (LAL of recent purchasers)
**Creative:** social proof — last year's footage, specific testimonials, "selling fast" messaging
**Offer:** standard ticket pricing, FOMO triggers ("87% sold")
**Optimization:** Purchase + tCPA
**Budget:** 50-60% of total — this is where most tickets sell

### Phase 3: Urgency Push (T-3 to T-1 days)

**Audience:** all retargeting + broad + "engaged with event in last 7 days"
**Creative:** pure urgency — "tickets at the door $15 more", countdown timer in ad copy
**Offer:** last-call price (no discount, but framing creates urgency)
**Optimization:** Purchase
**Budget:** 10-20% of total — small spend, high CPM tolerance

**Bar Crawl USA learning:** Phase 3 produced 22% of total tickets despite only 12% of budget. Don't underspend it.

## Multi-market scaling

When running the same event template in 5+ cities, structure campaigns at the city level, NOT the campaign level:

```
Campaign 1: Taco & Tequila Crawl Campaign
├── Ad Set: Phoenix (geo: Phoenix DMA, audience: 21-40 + nightlife interests)
├── Ad Set: Tucson (same shape)
├── Ad Set: Denver
├── Ad Set: Las Vegas
├── Ad Set: Albuquerque
└── Each ad set has 3 creative variants
```

This lets Meta optimize budget across cities based on which cities convert. Lower-performing cities can have budget drained automatically into higher-performing ones if you use **Campaign Budget Optimization (CBO)**.

**CBO ON for multi-market campaigns. CBO OFF for single-market.** This is the rule.

## Creative strategy

Each city gets 3 creative variants. Mix:

### Variant A: Lifestyle / FOMO

15-30 second video. Crowd footage from past event. People dancing, laughing, signature drinks, themed costumes. Music with energy. Captions: "Saturday April 27 / Phoenix / 2-7 PM". CTA: "Get Your Wristband".

### Variant B: Specificity / Social Proof

Static image with overlay: "10 venues. 1 wristband. $25 includes drinks at all stops." Plus a 3-line testimonial from a past attendee.

### Variant C: Behind-the-Scenes / Personality

Short selfie-style video from the event organizer or local promoter. "Hey Phoenix — wanna know what makes our crawl different?" 30-45 seconds, ends on the CTA.

**For Bar Crawl USA, Variant A drove 60%+ of conversions, Variant B drove 25%, Variant C drove 15%.** Run all three so Meta finds the winner per market.

## Pixel + CAPI

For event ticketing, **CAPI (Conversion API) is non-optional.** Without it, you'll see 30-50% under-attribution and Meta's algorithm will optimize toward bad audiences.

Set up:
- Meta Pixel installed on ticketing platform (Eventbrite, Tixr, Ticketleap)
- Conversion API via the platform's Meta integration (most have it built-in now)
- Test events: confirm Purchase event fires correctly with order value

## Output format

```
# Event Paid Social Plan: <event name>

## Strategic summary
- Cities: N
- Total tickets to sell: X
- Total budget: $Y
- Phase 1 budget: $Z (Awareness, T-30 to T-14)
- Phase 2 budget: $A (Conversion, T-14 to T-3)
- Phase 3 budget: $B (Urgency, T-3 to T-1)
- Optimization goal evolution: Reach → Purchase

## City-level campaign structure (one campaign, N ad sets)

### Ad Set: Phoenix
- Geo: Phoenix DMA + 25mi radius around venue cluster
- Audience: 21-40 + interests (nightlife, cocktail bars, brunch, food festivals) + 1% LAL of past Phoenix event attendees
- Daily budget: $X (scales via CBO)
- Bid strategy: Lowest cost, then tCPA $X after 50 conversions

[Variant A creative spec]
[Variant B creative spec]
[Variant C creative spec]

### Ad Set: Tucson
[Same shape]

### ... 5 more cities

## Phase rotation calendar

| Date (relative to event) | Phase | Ad sets active | Creative | Daily budget | Optimization |
|---|---|---|---|---|---|
| T-30 to T-14 | 1 — Awareness | All cities, all variants | Variant A primary | $X total | Reach + Add-to-Cart |
| T-14 to T-3 | 2 — Conversion | All + retargeting layer | Variant B + C primary | $Y total | Purchase + tCPA |
| T-3 to T-1 | 3 — Urgency | All + retargeting + broad | Variant urgency-rewrite | $Z total | Purchase |

## Pixel + CAPI checklist
- [ ] Meta Pixel on ticketing site
- [ ] CAPI enabled via [platform name]
- [ ] Test events firing in Meta Events Manager
- [ ] Custom audience: cart abandoners (180-day)
- [ ] Custom audience: purchasers (365-day; for next event LAL)

## KPIs to track per city
- CPP (cost per purchase): target $4-12 depending on ticket price
- ROAS: target 4-8x for $25 tickets, 6-15x for $50+ tickets
- Tickets sold per day vs goal pace
- Sell-through %

## Decision rules
- City running 80% of avg ROAS at day 7: shift 20% of its budget to top performer
- Creative variant CTR < 50% of leader: kill, replace with new test
- Phase 3 should always burn full budget by event date (no leftover)
```

## Common mistakes

1. **Single campaign across all cities.** Meta can't optimize properly. Always one ad set per city.
2. **Skipping Phase 3.** Last-72-hour push drives 20%+ of total sales. Don't let the campaign rest.
3. **No CAPI.** Mobile-iOS attribution is broken without it.
4. **Same creative for all phases.** Phase 1 is awareness; Phase 3 is urgency. Different ads.
5. **Over-optimizing on Day 1.** Each ad set needs 50+ conversions before tCPA reliably works. Don't switch optimization strategies on day 3.
6. **Single creative variant.** No A/B = no learning. Always 3 variants per ad set minimum.

## Compliance / Meta policy

- Alcohol-themed events: must restrict audience to 21+ AND target only states/regions where age is legal
- Promotional pricing: don't say "free" if there's a fee
- Drug references / 420 events: extra Meta scrutiny — keep creative wholesome

## Leverage with other skills

- Pair with `multi-market-meta-campaign-launcher` for the build-out across cities
- Pair with `event-ticketing-funnel-builder` for the post-click experience
- Pair with `instagram-reels-promo-script-writer` for the Variant A creative
- Pair with `tiktok-ads-strategist` if extending to TikTok

## MCP integration

With `meta-ads` MCP: `Build the campaign structure as specified for the [event name] across [N cities]. Set up CBO at $X daily, all ad sets active. Enable CAPI integration with [ticketing platform]. Save as paused; activate after I review.`
