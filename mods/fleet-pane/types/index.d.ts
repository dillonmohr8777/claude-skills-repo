export type Fleet = {
  jobs: { name: string; state: string }[]
  tmux: string[]
  services: { port: number; name: string; state: string }[]
}

declare module 'claude-code' {
  interface PluginState {
    'fleet-pane': { fleet: Fleet | null }
  }
}
