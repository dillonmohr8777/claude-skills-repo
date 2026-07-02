# Mohr Agents — prototype

An interactive, single-file prototype of **Mohr Agents**: an iOS-style home
screen where every "app" is a pre-built marketing agent for local business
owners. Tap any icon to open a canned agent flow that shows the request, a
brief "thinking" beat, and a formatted result — with a live Fable 5 latency chip.

Open `index.html` in any browser. No build step, no dependencies.

## Concept

Mohr Media already runs Google Ads, SEO, and content for local service
businesses (HVAC, landscaping, bridal, cleaning, etc.). This packages those
exact workflows as tappable agents so an owner who can't afford a $3–5k/mo
retainer gets the same playbook in their pocket. The moat is the curated
agents, not the model; users never see the prompt.

## Brand

Palette, logo colors, and type are pulled from **mohrmedia.com**:

- Green `#2F9E36` (MOHR) · Blue `#1F5AA6` (MEDIA) · signature Orange `#FF6600`
- Deep blue `#004784`, steel `#4F7383` (supporting)
- Georgia serif headlines + Tahoma/Helvetica UI (echoes the site's
  "New Technologies, Old-School Journalism" tagline)
- Tri-color swoosh (green → orange → blue) rebuilt as inline SVG

## The 11 agents

**Get found** — Google Ads · SEO Ranker · Google Business · Landing Pages
**Win customers** — Ad Writer · Lead Reviver · Review Reply · Content Engine
**Run it** — Report Card · Website Fixes · Quote Builder

Each agent is defined as one object in the `AGENTS` array in `index.html`
(`id`, `name`, `tag`, `icon`, `tint`, `lat`, `group`, `user`, `render`).
Adding an agent = adding one object.

## If building the real app

This is a design/UX reference, not production code. A real build would likely be:

- **Client**: SwiftUI iOS app — agent grid, voice + attachment input, streaming responses
- **Backend**: thin proxy so system prompts never touch the device; per-user usage metering; Claude API on Fable 5
- **Agents as config**: each agent = a prompt + tools + example I/O file, so new agents ship without an App Store update
