import type { EngineInterface, Register, SessionRateLimit } from 'claude-code'

import { levelOf, meterText, type Level } from './quota'

// Status text is plain (the engine's status pin takes no color), so the meter uses block
// characters. A toast fires when the level steps up: near (80% of the cap) or over.
let cap = 20
let last: Level | undefined

async function show($: EngineInterface, limits: readonly SessionRateLimit[]) {
  $.ui.status(meterText(limits, await $.clock.now(), cap))
  const week = limits.find(l => l.kind === 'seven_day')
  if (!week) return
  const level = levelOf(week.percentUsed, cap)
  if (level !== last && level !== 'ok') {
    const used = +week.percentUsed.toFixed(1)
    $.ui.toast(level === 'over' ? `Weekly plan usage ${used}% is past your ${cap}% cap` : `Weekly plan usage ${used}%, close to your ${cap}% cap`, { timeoutMs: 10000 })
  }
  last = level
}

export const register: Register = (on, options) => {
  const asked = Number(options.weeklyCapPercent)
  cap = asked > 0 ? asked : 20
  last = undefined

  on('session.start', async ($, e, next) => {
    const r = await next(e)
    try {
      await show($, (await $.session.usage()).rateLimits)
    } catch {
      // no reading yet; the next measurement draws it
    }
    return r
  })

  on('session.measure', async ($, e, next) => {
    if (e.changed.includes('rateLimits')) await show($, e.rateLimits)
    return next(e)
  })
}
