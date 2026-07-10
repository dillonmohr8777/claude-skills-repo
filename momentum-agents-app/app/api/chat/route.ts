import Anthropic from "@anthropic-ai/sdk";
import { KNOWLEDGE_BASE } from "@/lib/knowledge";
import { AGENTS } from "@/lib/agents";

export const runtime = "nodejs";
export const maxDuration = 60;

const client = new Anthropic(); // reads ANTHROPIC_API_KEY from the environment

const BASE_SYSTEM = `You are the Momentum 360 AI assistant — a done-for-you marketing partner for local businesses and real estate pros. You speak for Momentum 360.

Rules:
- Be concrete, warm, and results-first. Talk in leads, calls, bookings, rankings, and cost-per-lead — not vanity metrics.
- Lead with the answer, then the supporting detail. Keep it tight and skimmable; use short markdown (headings, bold, bullets) when it helps.
- Ground every answer in what Momentum 360 actually offers (see the knowledge base). If something is outside our services, say so and point to what we can do instead.
- Any numbers you give are realistic illustrations, not guarantees — say so if a prospect asks for guaranteed results.
- Never produce generic, AI-sounding filler. If you need a detail to be useful (industry, city, budget), ask one sharp question.`;

type Msg = { role: "user" | "assistant"; content: string };

export async function POST(req: Request) {
  let body: { messages?: Msg[]; agentId?: string };
  try {
    body = await req.json();
  } catch {
    return new Response("Bad request", { status: 400 });
  }

  const messages = (body.messages ?? []).filter(
    (m) => (m.role === "user" || m.role === "assistant") && typeof m.content === "string" && m.content.trim(),
  );
  if (!messages.length) return new Response("No messages", { status: 400 });

  const agent = AGENTS.find((a) => a.id === body.agentId);

  // Stable prefix (base + knowledge base) is cached; the volatile agent
  // instruction goes after the cache breakpoint.
  const system: Anthropic.Beta.BetaTextBlockParam[] = [
    {
      type: "text",
      text: `${BASE_SYSTEM}\n\n${KNOWLEDGE_BASE}`,
      cache_control: { type: "ephemeral" },
    },
  ];
  if (agent) system.push({ type: "text", text: `Active specialist: ${agent.name}. ${agent.system}` });

  const encoder = new TextEncoder();
  const stream = new ReadableStream<Uint8Array>({
    async start(controller) {
      try {
        const run = client.beta.messages.stream({
          model: "claude-fable-5",
          max_tokens: 4096,
          // Fable 5's thinking is always on; keep effort low for snappy,
          // sales-demo-speed replies. Raise to "medium"/"high" for depth.
          output_config: { effort: "low" },
          // Opt into server-side fallback so a safety refusal is transparently
          // re-served by Opus 4.8 in the same call (recommended for Fable 5).
          betas: ["server-side-fallback-2026-06-01"],
          fallbacks: [{ model: "claude-opus-4-8" }],
          system,
          messages: messages.map((m) => ({ role: m.role, content: m.content })),
        });

        run.on("text", (delta) => controller.enqueue(encoder.encode(delta)));
        const final = await run.finalMessage();
        if (final.stop_reason === "refusal") {
          controller.enqueue(
            encoder.encode(
              "\n\nI can't help with that one — let's keep it to growing your business. Ask me about ads, SEO, virtual tours, content, or reviews.",
            ),
          );
        }
      } catch (err) {
        controller.enqueue(
          encoder.encode(`\n\n[Something went wrong: ${(err as Error).message}]`),
        );
      } finally {
        controller.close();
      }
    },
  });

  return new Response(stream, {
    headers: { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "no-store" },
  });
}
