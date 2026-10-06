export type Frame = number

declare module 'claude-code' {
  interface PluginState {
    'clawd-buddy': { frame: Frame }
  }
}
