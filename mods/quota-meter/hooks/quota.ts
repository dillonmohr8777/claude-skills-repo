import type { SessionRateLimit } from 'claude-code'

// Pure helpers: no `$`, so the tests drive them directly. The only data source is the
// engine's own rate-limit windows (the same figures the status line gets). No window,
// no text: a missing reading is never drawn as zero.

export const WEEK_MS = 7 * 24 * 60 * 60 * 1000

export type Level = 'ok' | 'near' | 'over'
export type Pace = 'ahead' | 'on' | 'unknown'

export const levelOf = (used: number, cap: number): Level => (used >= cap ? 'over' : used >= cap * 0.8 ? 'near' : 'ok')

/** How far into the 7-day window we are, 0 to 1; undefined without a reset time. */
export const elapsedFrac = (resetsAt: string | undefined, nowMs: number): number | undefined => {
  const t = resetsAt === undefined ? NaN : Date.parse(resetsAt)
  if (!Number.isFinite(t)) return undefined
  return Math.min(1, Math.max(0, 1 - (t - nowMs) / WEEK_MS))
}

// ponytail: straight-line budget (cap * elapsed share) with 25% slack; no burn-rate model.
export const paceOf = (used: number, cap: number, frac: number | undefined): Pace => {
  if (frac === undefined || frac < 0.05) return 'unknown'
  return used > cap * frac * 1.25 + 0.5 ? 'ahead' : 'on'
}

export const countdown = (resetsAt: string | undefined, nowMs: number): string => {
  const t = resetsAt === undefined ? NaN : Date.parse(resetsAt)
  if (!Number.isFinite(t) || t <= nowMs) return ''
  const m = Math.floor((t - nowMs) / 60000)
  const d = Math.floor(m / 1440)
  const h = Math.floor((m % 1440) / 60)
  if (d > 0) return `${d}d ${h}h`
  return h > 0 ? `${h}h ${m % 60}m` : `${m}m`
}

const pct = (n: number) => `${+n.toFixed(1)}%`

export const bar = (used: number, cap: number, cells = 10): string => {
  const on = Math.round(Math.min(1, used / cap) * cells)
  return '▰'.repeat(on) + '▱'.repeat(cells - on)
}

/** The pinned line, or undefined when the engine has no 7-day reading. */
export const meterText = (limits: readonly SessionRateLimit[], nowMs: number, cap: number): string | undefined => {
  const week = limits.find(l => l.kind === 'seven_day')
  if (!week) return undefined
  const five = limits.find(l => l.kind === 'five_hour')
  const level = levelOf(week.percentUsed, cap)
  const pace = paceOf(week.percentUsed, cap, elapsedFrac(week.resetsAt, nowMs))
  const resets = countdown(week.resetsAt, nowMs)
  const parts = [
    `${level === 'over' ? 'OVER CAP ' : ''}weekly ${pct(week.percentUsed)} of ${cap}% cap ${bar(week.percentUsed, cap)}`,
    pace === 'unknown' ? '' : pace === 'ahead' ? 'ahead of pace' : 'on pace',
    five ? `5h ${pct(five.percentUsed)}` : '',
    resets ? `resets ${resets}` : '',
  ]
  return parts.filter(Boolean).join(' · ')
}
