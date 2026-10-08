import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { Fleet } from '../types'

const PANE = 'fleet'
const fleet = atom({ plugin: 'fleet-pane', key: 'fleet' } as const, null)
const SCRIPT = '/Users/dillonmohr/code/claude-skills-repo/mods/fleet-pane/fleet.py'
// Claude Code's ultracode rainbow, red to violet
const RB = ['#EB5F57', '#F58B57', '#FAC35F', '#91C882', '#82AADC', '#9B82C8', '#C882B4']
const dotColor = (s: string) =>
  s === 'up' || s === 'running' ? '#91C882' : s === 'down' || s === 'failed' ? '#EB5F57' : '#9AA0A8'

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'fleet', description: 'Live pane: services, launchd jobs, tmux' })
    // read-only snapshot every 15s; fleet.py caches and uses 1s timeouts, never blocks the prompt
    $.clock.every(15000, async () => {
      const r = await $.process.run(['python3', SCRIPT, '--json'])
      if (r.exitCode === 0) await update($, fleet, () => JSON.parse(r.stdout) as Fleet)
    })
    return next(e)
  })

  on('command.run', { command: 'fleet' }, async $ => {
    const r = await $.process.run(['python3', SCRIPT, '--json'])
    if (r.exitCode === 0) await update($, fleet, () => JSON.parse(r.stdout) as Fleet)
    await $.ui.open({ id: PANE, title: 'Fleet' })
    return { text: 'Fleet pane opened.' }
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    const f = await read($, fleet)
    if (!f) return <Text dimColor>Loading...</Text>
    const room = Math.max(4, (e.viewport?.rows ?? 24) - 8)

    return (
      <Box flexDirection="column">
        <Text bold color={RB[0]}>SERVICES</Text>
        {f.services.map(s => (
          <Text>
            <Text color={dotColor(s.state)}>●</Text> <Text color={RB[1]}>{s.port}</Text> {s.name}
          </Text>
        ))}
        <Text bold color={RB[2]}>LAUNCHD</Text>
        {f.jobs.slice(0, room).map(j => (
          <Text>
            <Text color={dotColor(j.state)}>●</Text> <Text color={RB[3]}>{j.name}</Text>{' '}
            <Text dimColor>{j.state}</Text>
          </Text>
        ))}
        <Text bold color={RB[4]}>TMUX</Text>
        {f.tmux.map((t, i) => (
          <Text>
            <Text color={RB[5]}>●</Text> {t}
          </Text>
        ))}
      </Box>
    )
  })
}
