import { test, expect } from 'claude-code/testing'

// Dillon change: a headless run (claude -p, launchd loops) has nobody to press Proceed,
// so a risky command passes straight through instead of stalling for the 10 minute hold.
test('headless session lets rm -rf through without holding it', async ($, on) => {
  on('session.start', (_$, e) => ({ cwd: e.cwd }))
  on('tool.call', () => ({ result: { stdout: 'ran', stderr: '', interrupted: false } }) as never)
  await $.session.start({ cwd: '/tmp', surface: null, isInteractive: false })
  const ran = await $.tool.call({ tool: 'Bash', command: 'rm -rf build', tool_use_id: 't1' } as never)
  expect(ran.deny).toBeUndefined()
})
