import { test, expect } from 'claude-code/testing'
import { buildRows, counts, doingOf, elapsed, summary } from './model'

const a = (id: string, status: string, parentId?: string) => ({ id, description: `task ${id}`, type: 'general-purpose', status, ...(parentId ? { parentId } : {}) })

test('tree puts children under their parent, orphans and cycles at the root', () => {
  const rows = buildRows([a('p', 'running'), a('c', 'completed', 'p'), a('o', 'failed', 'gone'), a('x', 'running', 'x')], { p: { firstAt: 0, tools: 3, doing: 'reading a.ts' } }, 5000)
  expect(rows.map(r => [r.id, r.depth])).toEqual([['p', 0], ['c', 1], ['o', 0], ['x', 0]])
  expect(rows[0]!.doing).toBe('reading a.ts')
  expect(rows[1]!.doing).toBeUndefined()
  expect(counts(rows)).toEqual({ live: 2, failed: 1, done: 1 })
  expect(summary(rows)).toBe('2 live · 1 done · 1 failed')
})

test('plain words for tool calls and times', () => {
  expect(doingOf('Edit', { file_path: '/a/b/c.ts' })).toBe('editing c.ts')
  expect(doingOf('mcp__x__do_thing', {})).toBe('do_thing')
  expect(elapsed(75_000)).toBe('1m 15s')
})

test('pane draws the tree on terminal and desktop', async ($, on) => {
  on('agent.list', () => [a('p', 'running')] as never)
  for (const surface of ['terminal', 'desktop'] as const) {
    await $.command.run({ command: 'swarm', args: '' } as never).catch(() => undefined)
    const ui = await $.ui.mount({ plugin: 'swarm-map', surface, component: 'Pane', requestId: 'swarm-map', props: {} as never } as never)
    expect(await ui.find({ type: 'Text' })).toBeDefined()
    await ui.unmount()
  }
})
