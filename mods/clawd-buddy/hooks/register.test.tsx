import { test, expect } from 'claude-code/testing'
import { sprite } from './register'

test('types fast while working, slow while idle', () => {
  expect(sprite(1, true).hands).not.toBe(sprite(0, true).hands)
  expect(sprite(1, false).hands).toBe(sprite(0, false).hands)
  expect(sprite(3, false).hands).not.toBe(sprite(0, false).hands)
  expect(sprite(0, true).caption).toBe('typing')
})

test('draws above the prompt on terminal and desktop', async $ => {
  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount({ plugin: 'clawd-buddy', surface, component: 'AbovePrompt', props: { hasSurvey: false, isWorking: true, maxRows: 20, columns: 100 } as never })
    expect(await ui.find({ type: 'Text', text: /clawd is typing/ })).toBeDefined()
    await ui.unmount()
  }
})
