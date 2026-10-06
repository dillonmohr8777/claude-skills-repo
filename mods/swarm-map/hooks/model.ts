import type { AgentInfo } from 'claude-code'

// Pure model: no `$`, so the tests drive it directly. Our own small take on a subagent map;
// it only reads what the engine reports (`$.agent.list()` and each loop's `tool.call`).

export type Seen = { firstAt: number; tools: number; doing?: string }
export type Row = { id: string; depth: number; label: string; type: string; status: string; tools: number; doing?: string; ageMs: number }

export const isLive = (s: string) => s === 'running' || s === 'pending' || s === 'starting'
export const isFailed = (s: string) => s === 'failed' || s === 'killed' || s === 'error'

const base = (p: unknown) => (typeof p === 'string' ? (p.split('/').filter(Boolean).pop() ?? p) : '')
const clip = (s: string, n: number) => (s.length > n ? `${s.slice(0, n - 1)}…` : s)

/** A tool call in a few plain words. */
export const doingOf = (tool: string, input: Record<string, unknown>): string => {
  const s = (k: string) => (typeof input[k] === 'string' ? (input[k] as string) : '')
  switch (tool) {
    case 'Bash':
      return `running ${clip(s('description') || s('command').split('\n')[0]!, 50)}`
    case 'Read':
      return `reading ${base(input.file_path)}`
    case 'Write':
    case 'Edit':
    case 'MultiEdit':
      return `editing ${base(input.file_path)}`
    case 'Grep':
    case 'Glob':
      return `searching ${clip(s('pattern'), 36)}`
    case 'WebFetch':
    case 'WebSearch':
      return 'on the web'
    default:
      return clip(tool.startsWith('mcp__') ? (tool.split('__').pop() ?? tool) : tool, 40)
  }
}

/** The spawn tree, depth first, siblings in the order the engine listed them. An unknown parent counts as the root. */
export const buildRows = (list: readonly AgentInfo[], seen: Readonly<Record<string, Seen>>, now: number): Row[] => {
  const ids = new Set(list.map(a => a.id))
  const kids = new Map<string, AgentInfo[]>()
  for (const a of list) {
    const p = a.parentId && ids.has(a.parentId) && a.parentId !== a.id ? a.parentId : ''
    kids.set(p, [...(kids.get(p) ?? []), a])
  }
  const rows: Row[] = []
  const done = new Set<string>()
  const walk = (parent: string, depth: number) => {
    for (const a of kids.get(parent) ?? []) {
      if (done.has(a.id)) continue // a parent cycle must not loop
      done.add(a.id)
      const s = seen[a.id]
      rows.push({
        id: a.id,
        depth,
        label: a.name || a.description || a.type,
        type: a.type,
        status: a.status,
        tools: s?.tools ?? 0,
        doing: isLive(a.status) ? s?.doing : undefined,
        ageMs: s ? now - s.firstAt : 0,
      })
      walk(a.id, depth + 1)
    }
  }
  walk('', 0)
  return rows
}

export const counts = (rows: readonly Row[]) => ({
  live: rows.filter(r => isLive(r.status)).length,
  failed: rows.filter(r => isFailed(r.status)).length,
  done: rows.filter(r => !isLive(r.status) && !isFailed(r.status)).length,
})

export const summary = (rows: readonly Row[]): string => {
  const c = counts(rows)
  return `${c.live} live · ${c.done} done${c.failed ? ` · ${c.failed} failed` : ''}`
}

export const elapsed = (ms: number): string => {
  const s = Math.max(0, Math.round(ms / 1000))
  if (s < 60) return `${s}s`
  const m = Math.floor(s / 60)
  return m < 60 ? `${m}m ${String(s % 60).padStart(2, '0')}s` : `${Math.floor(m / 60)}h ${String(m % 60).padStart(2, '0')}m`
}
