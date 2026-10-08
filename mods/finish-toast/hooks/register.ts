import type { Register } from 'claude-code'

// Toasts are plain text (no ANSI), so color rides on the emoji marker.
const MIN_MS = 45_000 // short turns stay silent; the person is still looking

// Pure, so it can be dry-run without the engine.
export const toastText = (e: { durationMs: number; answer: string; reason: string }): string | null => {
  if (e.durationMs < MIN_MS || e.reason === 'aborted') return null
  const s = Math.round(e.durationMs / 1000)
  const t = s >= 60 ? `${Math.floor(s / 60)}m ${s % 60}s` : `${s}s`
  const asks = e.answer.trim().endsWith('?')
  return asks ? `🟡 Needs your input (after ${t})` : `🟢 Finished in ${t}`
}

export const register: Register = on => {
  on('turn.complete', ($, e, next) => {
    const text = toastText(e)
    if (text) $.ui.toast(text)
    return next(e)
  })
}
