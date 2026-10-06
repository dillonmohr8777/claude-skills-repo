import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

const frame = atom({ plugin: 'clawd-buddy', key: 'frame' } as const, 0)

const HANDS = ['  ▘▘ ▝▝', '  ▝▝ ▘▘']
const DOTS = ['●○○', '○●○', '○○●', '○●○']

// One frame of Clawd: idle types at a third of the working speed.
export function sprite(tick: number, working: boolean) {
  const t = working ? tick : Math.floor(tick / 3)
  return { hands: HANDS[t % HANDS.length], dots: DOTS[t % DOTS.length], caption: working ? 'typing' : 'vibing' }
}

export const register: Register = on => {
  on('session.start', ($, e, next) => {
    $.clock.every(450, () => void update($, frame, f => (f + 1) % 1200))
    return next(e)
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey || e.props.maxRows < 3) return next(e)
    const { Box, Text } = $.ui.resolve(e)
    const s = sprite(await read($, frame), e.props.isWorking)
    return (
      <Box flexDirection="column">
        <Text color="claude"> ▐▛███▜▌</Text>
        <Text>
          <Text color="claude">▝▜█████▛▘ </Text>
          <Text color="#A99BF5">{s.dots}</Text>
          <Text dimColor> clawd is {s.caption}</Text>
        </Text>
        <Text color="claude">{s.hands}</Text>
      </Box>
    )
  })
}
