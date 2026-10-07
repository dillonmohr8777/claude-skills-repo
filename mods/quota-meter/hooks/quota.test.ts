import { test, expect, mock } from 'claude-code/testing'
import { bar, countdown, levelOf, meterText, paceOf } from './quota'

const NOW = Date.parse('2026-10-06T12:00:00Z')
const day = (n: number) => new Date(NOW + n * 86_400_000).toISOString()

test('levels step at 80% of the cap and at the cap', () => {
  expect(levelOf(15.9, 20)).toBe('ok')
  expect(levelOf(16, 20)).toBe('near')
  expect(levelOf(20, 20)).toBe('over')
})

test('pace compares use against a straight-line budget', () => {
  expect(paceOf(5, 20, 0.5)).toBe('on')
  expect(paceOf(15, 20, 0.5)).toBe('ahead')
  expect(paceOf(5, 20, 0.01)).toBe('unknown')
  expect(paceOf(5, 20, undefined)).toBe('unknown')
})

test('countdown and bar', () => {
  expect(countdown(day(3.5), NOW)).toBe('3d 12h')
  expect(countdown(new Date(NOW + 90 * 60000).toISOString(), NOW)).toBe('1h 30m')
  expect(countdown(day(-1), NOW)).toBe('')
  expect(bar(10, 20)).toBe('▰▰▰▰▰▱▱▱▱▱')
  expect(bar(40, 20)).toBe('▰▰▰▰▰▰▰▰▰▰')
})

test('no seven_day window means no text, never zero', () => {
  expect(meterText([], NOW, 20)).toBeUndefined()
  expect(meterText([{ kind: 'five_hour', percentUsed: 40 }], NOW, 20)).toBeUndefined()
})

test('line carries usage, cap, pace, 5h and reset', () => {
  const t = meterText([{ kind: 'seven_day', percentUsed: 9.5, resetsAt: day(3.5) }, { kind: 'five_hour', percentUsed: 31 }], NOW, 20)
  expect(t).toBe('weekly 9.5% of 20% cap ▰▰▰▰▰▱▱▱▱▱ · on pace · 5h 31% · resets 3d 12h')
  expect(meterText([{ kind: 'seven_day', percentUsed: 21 }], NOW, 20)).toContain('OVER CAP')
})

test('a rate-limit measurement pins the line and toasts once on crossing the cap', async ($, on) => {
  const status: Array<string | undefined> = []
  const toasts: string[] = []
  on('ui.status', ($$, e) => (status.push(e.text), undefined as never))
  on('ui.toast', ($$, e) => (toasts.push(e.text), undefined as never))
  mock.clock(on, { now: NOW })
  on('session.measure', ($$, e) => ({ changed: e.changed }))
  const context = { window: 200000 } as never
  await $.session.measure({ context, rateLimits: [{ kind: 'seven_day', percentUsed: 21, resetsAt: day(3) }], changed: ['rateLimits'] })
  await $.session.measure({ context, rateLimits: [{ kind: 'seven_day', percentUsed: 22, resetsAt: day(3) }], changed: ['rateLimits'] })
  expect(status.length).toBe(2)
  expect(status[1]).toContain('OVER CAP')
  expect(toasts.length).toBe(1)
})
