# Momentum 360 Agents — live AI app

A **working** chat app (not a mockup): prospects and clients can **type anything**
about growing their business and get real answers, grounded in a deep Momentum 360
knowledge base, streamed live. Optional specialist "agents" (Google Ads, SEO, 3D
Virtual Tours, Pinterest, Reviews, …) reshape the assistant for a specific job.

Built on the **Claude API** using **Fable 5**, with an automatic server-side
fallback to **Opus 4.8** on refusals.

## Run it

```bash
npm install
cp .env.example .env.local        # then paste your ANTHROPIC_API_KEY
npm run dev                       # http://localhost:3000
```

You need an Anthropic API key from https://console.anthropic.com. That's the
only credential required.

## Deploy

Any Node host works. Easiest is Vercel: import the repo, set `ANTHROPIC_API_KEY`
as an environment variable, deploy. (This folder is the project root.)

## How it works

- `app/page.tsx` — the chat UI (free-text input + an agent grid), Momentum 360
  navy/gold brand. Streams responses token-by-token.
- `app/api/chat/route.ts` — the backend. Calls Claude (`claude-fable-5`,
  `effort: "low"` for snappy replies) with the knowledge base as a cached system
  prompt, streams text back, and opts into a server-side fallback to
  `claude-opus-4-8` if a request is refused.
- `lib/knowledge.ts` — **the knowledge base.** Everything the assistant knows
  about Momentum 360. Edit this to change what it can speak to.
- `lib/agents.ts` — the specialist presets. Each adds a system instruction and a
  starter prompt. Add an agent by adding one object to the array.

## Make it yours

- **Sharper answers, slower:** raise `output_config.effort` to `"medium"` or
  `"high"` in `app/api/chat/route.ts`.
- **New knowledge:** paste it into `lib/knowledge.ts`. For large or frequently
  changing content, move to retrieval (RAG) instead of stuffing the prompt.
- **Real logo:** drop `logo.png` into a `public/` folder and swap the text
  wordmark in `app/page.tsx` for an `<img>`.
- **Guardrails / lead capture / auth:** add them in the API route before the
  model call.

## Notes

- Illustrative numbers in answers are examples, not guaranteed results — the
  system prompt tells the model to say so if asked.
- The knowledge base is sourced from momentumvirtualtours.com; keep it factual.
