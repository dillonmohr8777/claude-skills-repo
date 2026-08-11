# Microsoft Foundry MCP for Claude

This repository enables Microsoft's hosted Foundry MCP Server for Claude Code.
The project configuration exposes the server's complete advertised tool set and
pre-authorizes all of its tools in Claude Code.

## One-time sign-in

1. Open Claude Code from this repository.
2. Run `/mcp`.
3. Select `microsoft_foundry` and complete the Microsoft Entra sign-in.
4. Approve the requested access using the Azure identity that has access to the
   intended Foundry account and projects.

Tokens are stored by Claude Code's OAuth credential store. Do not commit tokens,
client secrets, subscription exports, or copied Azure credentials to this repo.

## Verify access

After authentication, ask Claude:

```text
Use microsoft_foundry to list the Foundry agents I can access. Then invoke one
non-destructively with a short test message and report the exact project, agent,
tool call, and result.
```

The Foundry MCP Server currently includes read and write tools, including agent
creation, update, invocation, container control, and deletion. This repository
does not restrict that tool surface. Effective access is determined by the Entra
identity and Azure RBAC roles used during sign-in.

## Claude.ai

The same endpoint can be added to Claude.ai under **Customize > Connectors > Add
custom connector**:

```text
https://mcp.ai.azure.com
```

Claude.ai connector installation is account-level UI state and cannot be applied
by a Git commit. Complete its Microsoft sign-in in the browser after adding it.

## Sources

- Microsoft Foundry MCP setup: <https://learn.microsoft.com/en-us/azure/foundry/mcp/get-started>
- Foundry MCP tools: <https://learn.microsoft.com/en-us/azure/foundry/mcp/available-tools>
- Claude Code MCP configuration: <https://docs.anthropic.com/en/docs/claude-code/mcp>
