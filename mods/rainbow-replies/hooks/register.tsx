import type { Register } from 'claude-code'

// Ultracode rainbow, same hex as the status line.
const COLOR: Record<string, string> = {
  '🟢': '#91C882',
  '🟡': '#FAC35F',
  '🔴': '#EB5F57',
  '🔵': '#82AADC',
  '🟣': '#C882B4',
}
const MARKER = /^\s*(🟢|🟡|🔴|🔵|🟣)/u
const BULLET = /^\s*[-*] (.*)$/
// [label](url) | bare url | `code` | **bold**
const INLINE = /\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)|(https?:\/\/[^\s)]+)|`([^`]+)`|\*\*([^*]+)\*\*/g

type Row = { kind: 'color'; text: string; color: string; bullet: boolean } | { kind: 'md'; text: string }

export function rows(text: string): Row[] {
  const out: Row[] = []
  let color: string | null = null
  let fenced = false
  for (const line of text.split('\n')) {
    if (line.trimStart().startsWith('```')) fenced = !fenced
    const m = fenced ? null : MARKER.exec(line)
    const b = fenced ? null : BULLET.exec(line)
    if (m) {
      color = COLOR[m[1]]
      out.push({ kind: 'color', text: line.trim(), color, bullet: false })
    } else if (b && color) {
      out.push({ kind: 'color', text: b[1], color, bullet: true })
    } else {
      if (line.trim()) color = null // blank lines keep the color for the bullets below
      const last = out[out.length - 1]
      if (last?.kind === 'md') last.text += '\n' + line
      else out.push({ kind: 'md', text: line })
    }
  }
  return out.filter(r => r.kind === 'color' || r.text.trim())
}

export const register: Register = on => {
  on('ui.render', { component: 'AssistantMessage' }, ($, e, next) => {
    if (!MARKER.test(e.props.text) && !/\n\s*(🟢|🟡|🔴|🔵|🟣)/u.test(e.props.text)) return next(e)
    const { Box, Text, Link, Markdown } = $.ui.resolve(e)

    const inline = (s: string, key: string) => {
      const parts: unknown[] = []
      let last = 0
      let i = 0
      for (const m of s.matchAll(INLINE)) {
        if (m.index! > last) parts.push(s.slice(last, m.index))
        const k = `${key}-${i++}`
        if (m[2]) parts.push(<Link key={k} href={m[2]} label={m[1]} />)
        else if (m[3]) parts.push(<Link key={k} href={m[3]} />)
        else parts.push(<Text key={k} bold>{m[4] ?? m[5]}</Text>)
        last = m.index! + m[0].length
      }
      if (last < s.length) parts.push(s.slice(last))
      return parts
    }

    return (
      <Box flexDirection="column">
        {rows(e.props.text).map((r, n) =>
          r.kind === 'md' ? (
            <Markdown key={`md-${n}`} text={r.text} />
          ) : (
            <Text key={`line-${n}`} color={r.color}>
              {r.bullet ? '  • ' : ''}
              {inline(r.text, `line-${n}`)}
            </Text>
          ),
        )}
      </Box>
    )
  })
}
