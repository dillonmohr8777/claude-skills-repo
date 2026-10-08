import { test, expect } from 'claude-code/testing'

// Dillon change: a headless run (claude -p, launchd loops) has nobody to press Proceed,
// so a risky command passes straight through instead of stalling for the 3 minute hold.
test('headless session lets rm -rf through without holding it', async ($, on) => {
  on('session.start', (_$, e) => ({ cwd: e.cwd }))
  on('tool.call', () => ({ result: { stdout: 'ran', stderr: '', interrupted: false } }) as never)
  await $.session.start({ cwd: '/tmp', surface: null, isInteractive: false })
  const ran = await $.tool.call({ tool: 'Bash', command: 'rm -rf build', tool_use_id: 't1' } as never)
  expect(ran.deny).toBeUndefined()
})

// Dillon change 2026-10-07: `blast-approve 2h` writes a future unix-seconds expiry to
// ~/.claude/blast-radius-approve. While it is in the future an interactive session runs
// risky commands with a toast instead of a hold.
test('standing approval file lets rm -rf through in an interactive session', async ($, on) => {
  on('session.start', (_$, e) => ({ cwd: e.cwd }))
  on('tool.call', () => ({ result: { stdout: 'ran', stderr: '', interrupted: false } }) as never)
  on('process.run', (_$, e) => {
    const argv = (e as { argv?: string[] }).argv ?? []
    if (argv[0] === 'bash' && String(argv[2]).includes('blast-radius-approve')) {
      return { value: { exitCode: 0, stdout: String(Math.floor(Date.now() / 1000) + 3600), stderr: '', isStdoutTruncated: false, isStderrTruncated: false } } as never
    }
    return { value: { exitCode: 0, stdout: '', stderr: '', isStdoutTruncated: false, isStderrTruncated: false } } as never
  })
  await $.session.start({ cwd: '/tmp', surface: null, isInteractive: true })
  const ran = await $.tool.call({ tool: 'Bash', command: 'rm -rf build', tool_use_id: 't2' } as never)
  expect(ran.deny).toBeUndefined()
})

test('expired approval file does not count', async ($, on) => {
  on('session.start', (_$, e) => ({ cwd: e.cwd }))
  on('process.run', (_$, e) => {
    const argv = (e as { argv?: string[] }).argv ?? []
    if (argv[0] === 'bash' && String(argv[2]).includes('blast-radius-approve')) {
      return { value: { exitCode: 0, stdout: String(Math.floor(Date.now() / 1000) - 60), stderr: '', isStdoutTruncated: false, isStderrTruncated: false } } as never
    }
    return { value: { exitCode: 0, stdout: '', stderr: '', isStdoutTruncated: false, isStderrTruncated: false } } as never
  })
  await $.session.start({ cwd: '/tmp', surface: null, isInteractive: true })
  const ran = await $.tool.call({ tool: 'Bash', command: 'rm -rf build', tool_use_id: 't3' } as never)
  expect(String(ran.deny ?? '')).toContain('Blast Radius held this command')
})

for (const invalid of ['', '9999999999junk', 'Infinity', '999999999999999999', '9999999999', String(Math.floor(Date.now() / 1000) + 12 * 3600 + 60)]) {
  test(`malformed approval ${invalid} does not count`, async ($, on) => {
    on('session.start', (_$, e) => ({ cwd: e.cwd }))
    on('process.run', (_$, e) => {
      const argv = (e as { argv?: string[] }).argv ?? []
      const stdout = argv[0] === 'bash' && String(argv[2]).includes('blast-radius-approve') ? invalid : ''
      return { value: { exitCode: 0, stdout, stderr: '', isStdoutTruncated: false, isStderrTruncated: false } } as never
    })
    await $.session.start({ cwd: '/tmp', surface: null, isInteractive: true })
    const ran = await $.tool.call({ tool: 'Bash', command: 'rm -rf build', tool_use_id: 'invalid' } as never)
    expect(String(ran.deny ?? '')).toContain('Blast Radius held this command')
  })
}
