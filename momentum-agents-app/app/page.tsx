"use client";

import { useRef, useState, useEffect } from "react";
import { AGENTS, GROUPS, type Agent } from "@/lib/agents";

type Msg = { role: "user" | "assistant"; content: string };

export default function Page() {
  const [agent, setAgent] = useState<Agent | null>(null);
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const threadRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    threadRef.current?.scrollTo({ top: threadRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, busy]);

  function openAgent(a: Agent) {
    setAgent(a);
    setMessages([]);
    setInput(a.starter);
  }

  function reset() {
    setAgent(null);
    setMessages([]);
    setInput("");
  }

  async function send(text: string) {
    const content = text.trim();
    if (!content || busy) return;
    const next: Msg[] = [...messages, { role: "user", content }];
    setMessages(next);
    setInput("");
    setBusy(true);
    setMessages((m) => [...m, { role: "assistant", content: "" }]);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: next, agentId: agent?.id }),
      });
      if (!res.body) throw new Error("No response stream");
      const reader = res.body.getReader();
      const dec = new TextDecoder();
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        const chunk = dec.decode(value, { stream: true });
        setMessages((m) => {
          const copy = [...m];
          copy[copy.length - 1] = { role: "assistant", content: copy[copy.length - 1].content + chunk };
          return copy;
        });
      }
    } catch (e) {
      setMessages((m) => {
        const copy = [...m];
        copy[copy.length - 1] = { role: "assistant", content: `[Error: ${(e as Error).message}]` };
        return copy;
      });
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="wrap">
      <header className="top">
        <button className="brand" onClick={reset} aria-label="Momentum 360 home">
          <span className="mk">Momentum</span> <span className="ag">360</span>
          <span className="tag">Agents</span>
        </button>
        <span className="fable">Fable 5 · type anything</span>
      </header>

      {!agent && messages.length === 0 ? (
        <section className="home">
          <h1>Your marketing team, on tap.</h1>
          <p className="sub">
            Ask anything about growing your business — or pick a specialist to start. Powered by Momentum 360&apos;s
            playbooks and Fable&nbsp;5.
          </p>
          <div className="ask">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && send(input)}
              placeholder="e.g. How do I get more customers from Google?"
              autoFocus
            />
            <button onClick={() => send(input)} disabled={busy}>Ask</button>
          </div>
          {GROUPS.map((g) => (
            <div key={g.key} className="group">
              <p className="glabel">{g.label}</p>
              <div className="grid">
                {AGENTS.filter((a) => a.group === g.key).map((a) => (
                  <button key={a.id} className="tile" onClick={() => openAgent(a)}>
                    <span className="tname">{a.name}</span>
                    <span className="ttag">{a.tag}</span>
                  </button>
                ))}
              </div>
            </div>
          ))}
        </section>
      ) : (
        <section className="chat">
          {agent && (
            <div className="agentbar">
              <button className="back" onClick={reset}>&larr;</button>
              <div>
                <div className="an">{agent.name}</div>
                <div className="at">{agent.tag}</div>
              </div>
            </div>
          )}
          <div className="thread" ref={threadRef}>
            {messages.map((m, i) => (
              <div key={i} className={`bubble ${m.role}`}>
                {m.content || (busy && i === messages.length - 1 ? <span className="dots"><i /><i /><i /></span> : "")}
              </div>
            ))}
          </div>
          <div className="composer">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  send(input);
                }
              }}
              placeholder="Ask a follow-up…"
              rows={1}
            />
            <button onClick={() => send(input)} disabled={busy}>Send</button>
          </div>
        </section>
      )}
    </main>
  );
}
