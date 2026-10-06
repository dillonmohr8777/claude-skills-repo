import { test, expect } from 'claude-code/testing'
import { rows } from './register'

const REPLY = '🟢 Done and **verified**: https://example.com/a\n- first bullet\n- second\nplain `code` line\n```\n🔴 inside a fence\n```\n🔴 Broke'

test('marker lines and their bullets get the marker color', () => {
  const r = rows(REPLY)
  expect(r[0]).toMatchObject({ kind: 'color', color: '#91C882', bullet: false })
  expect(r[1]).toMatchObject({ kind: 'color', color: '#91C882', bullet: true, text: 'first bullet' })
  expect(r[3]).toMatchObject({ kind: 'md' })
  expect(r[3].text).toContain('🔴 inside a fence')
  expect(r[4]).toMatchObject({ kind: 'color', color: '#EB5F57' })
})

test('draws on terminal and desktop without refusal', async $ => {
  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount({ plugin: 'rainbow-replies', surface, component: 'AssistantMessage', props: { text: REPLY, isFirstOfReply: true } })
    expect(await ui.drawn()).toMatchObject({ type: 'Box' })
    expect(await ui.find({ type: 'Text', text: /Done and/ })).toBeDefined()
    await ui.unmount()
  }
})

test('replies without markers keep the default drawing', async ($, on) => {
  on('ui.render', { component: 'AssistantMessage' }, ($, e) => {
    const { Text } = $.ui.resolve(e)
    return <Text>engine drawing</Text>
  })
  const ui = await $.ui.mount({ plugin: 'rainbow-replies', surface: 'terminal', component: 'AssistantMessage', props: { text: 'just text', isFirstOfReply: true } })
  expect(await ui.find({ type: 'Text', text: /engine drawing/ })).toBeDefined()
  await ui.unmount()
})
