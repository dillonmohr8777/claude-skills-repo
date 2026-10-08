import type { EngineInterface, Register } from 'claude-code'

import { buildRows, counts, doingOf, elapsed, isFailed, isLive, summary, type Row, type Seen } from './model'

const PANE = 'swarm-map'
// Lavender Ultracode family: accent, bright, muted, white for emphasis, red only for failures.
const ACCENT = '#A99BF5'
const BRIGHT = '#D6CFFF'
const MUTED = '#8A84A8'
const FAIL = '#EB5F57'

let rows: Row[] = []
let seen: Record<string, Seen> = {}
let sig = ''

async function poll($: EngineInterface) {
  const now = await $.clock.now()
  const list = await $.agent.list()
  for (const a of list) seen[a.id] ??= { firstAt: now, tools: 0 }
  rows = buildRows(list, seen, now)
  const live = counts(rows).live
  $.ui.status(live > 0 ? `swarm ${live} live` : undefined)
  // Redraw only when something visible moved; elapsed times tick with each change.
  const next = JSON.stringify(rows.map(r => [r.id, r.status, r.tools, r.doing]))
  if (next !== sig) {
    sig = next
    $.ui.invalidate('ui.render')
  }
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    rows = []
    seen = {}
    sig = ''
    await $.command.register({ name: 'swarm', description: 'Live tree of subagents: who spawned whom, status, tool calls, what each is doing' })
    $.clock.every(3000, () => void poll($).catch(() => undefined))
    return next(e)
  })

  on('command.run', { command: 'swarm' }, async $ => {
    await $.ui.open({ id: PANE, title: 'Swarm' })
    await poll($).catch(() => undefined)
    return { text: rows.length ? `Swarm: ${summary(rows)}` : 'Swarm open. No subagents this session yet.' }
  })

  // Each subagent's loop reports its own tool calls (agentId); the main loop has none.
  on('tool.call', async ($, e, next) => {
    if (e.agentId) {
      const now = await $.clock.now()
      const s = (seen[e.agentId] ??= { firstAt: now, tools: 0 })
      s.tools += 1
      s.doing = doingOf(e.tool, e as unknown as Record<string, unknown>)
    }
    return next(e)
  })

  on('agent.spawn', async ($, e, next) => {
    const r = await next(e)
    void poll($).catch(() => undefined)
    return r
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    if (rows.length === 0) return <Text color={MUTED}>No subagents yet.</Text>
    const room = Math.max(3, (e.viewport?.rows ?? 24) - 5)
    return (
      <Box flexDirection="column">
        <Text color={ACCENT} bold>
          {summary(rows)}
        </Text>
        {rows.slice(0, room).map(r => (
          <Box key={r.id} flexDirection="column">
            <Text wrap="truncate-end">
              {'  '.repeat(r.depth)}
              <Text color={isLive(r.status) ? BRIGHT : isFailed(r.status) ? FAIL : MUTED}>{isLive(r.status) ? '●' : isFailed(r.status) ? '✗' : '✓'} </Text>
              <Text color="#FFFFFF" bold={isLive(r.status)}>
                {r.label}
              </Text>
              <Text color={MUTED}>
                {' '}
                {r.type} · {r.tools} calls · {elapsed(r.ageMs)}
              </Text>
            </Text>
            {r.doing ? (
              <Text color={MUTED} wrap="truncate-end">
                {'  '.repeat(r.depth)}  {r.doing}
              </Text>
            ) : null}
          </Box>
        ))}
        {rows.length > room ? <Text color={MUTED}>+ {rows.length - room} more</Text> : null}
      </Box>
    )
  })
}
