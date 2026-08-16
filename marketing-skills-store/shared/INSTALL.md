# Install Guide

Get a skill running in under 10 minutes. Tested on Windows 11 (PowerShell 7) and macOS.

## What you'll need

- Claude Code CLI (free, install below)
- An Anthropic API key OR a Claude Pro/Team account (the skill works with either)
- Tool-specific credentials for whichever skill you're running:
  - **HubSpot skills** → a HubSpot Private App access token
  - **SEMrush skills** → a SEMrush API key
  - **Google Ads skills** → Google Ads Developer Token + OAuth refresh token
  - **Meta Ads skills** → Meta Marketing API access token
  - **GA4 skills** → Google Cloud service account JSON

You only need the credential for the skill you're running — not all of them.

## Step 1 — Install Claude Code

### Windows (PowerShell — exactly how I run it)

```powershell
# In an elevated PowerShell window:
winget install Anthropic.ClaudeCode

# Verify
claude --version
```

If `winget` isn't available, grab the installer from `claude.ai/download` and run it.

### macOS / Linux

```bash
curl -fsSL https://claude.ai/install.sh | sh
claude --version
```

## Step 2 — Drop the skill into Claude Code's skills folder

Each skill in this bundle is a folder with a `SKILL.md` inside it. You install a skill by copying the folder into your local skills directory.

### Per-user (works across all projects)

```powershell
# Windows
$skillsDir = "$env:USERPROFILE\.claude\skills"
New-Item -ItemType Directory -Force -Path $skillsDir
Copy-Item -Recurse .\skills\* $skillsDir
```

```bash
# macOS / Linux
mkdir -p ~/.claude/skills
cp -r ./skills/* ~/.claude/skills/
```

### Per-project (only this project sees the skill)

```bash
mkdir -p .claude/skills
cp -r ./skills/* .claude/skills/
```

Either works. Per-user is simpler if you're a solo operator.

## Step 3 — Wire up the MCP server (only for skills that need one)

Skills that read/write to HubSpot, SEMrush, Google Ads, Meta Ads, or GA4 talk to those platforms via MCP servers. Add the relevant entry to your `claude_mcp_settings.json` (Claude Code reads this on startup).

### HubSpot MCP — exactly how I run mine

I use a **HubSpot Private App** (legacy app key style) for full read/write autonomy on the portal. In HubSpot:

1. Settings → Integrations → Private Apps → Create a private app
2. Set scopes: `crm.objects.contacts.read/write`, `crm.objects.companies.read/write`, `crm.objects.deals.read/write`, `content`, `automation`, `forms`, `tickets.read/write` (toggle whichever the skill needs)
3. Copy the access token — it starts with `pat-na1-...` or `pat-eu1-...`

Then add to `~/.claude/claude_mcp_settings.json`:

```json
{
  "mcpServers": {
    "hubspot": {
      "command": "npx",
      "args": ["-y", "@hubspot/mcp-server"],
      "env": {
        "HUBSPOT_ACCESS_TOKEN": "pat-na1-YOUR-TOKEN-HERE"
      }
    }
  }
}
```

Restart Claude Code. You should see `hubspot` listed under MCP servers (`/mcp` slash command).

### SEMrush MCP

```json
{
  "mcpServers": {
    "semrush": {
      "command": "npx",
      "args": ["-y", "@semrush/mcp-server"],
      "env": {
        "SEMRUSH_API_KEY": "YOUR-API-KEY-HERE"
      }
    }
  }
}
```

### Google Ads MCP

Google Ads requires an OAuth refresh-token dance the first time. The MCP server handles it; just have your Developer Token + Customer ID ready:

```json
{
  "mcpServers": {
    "google-ads": {
      "command": "npx",
      "args": ["-y", "@google-ads/mcp-server"],
      "env": {
        "GOOGLE_ADS_DEVELOPER_TOKEN": "YOUR-TOKEN",
        "GOOGLE_ADS_CUSTOMER_ID": "123-456-7890"
      }
    }
  }
}
```

### Meta Ads MCP

```json
{
  "mcpServers": {
    "meta-ads": {
      "command": "npx",
      "args": ["-y", "@meta/marketing-api-mcp"],
      "env": {
        "META_ACCESS_TOKEN": "YOUR-TOKEN",
        "META_AD_ACCOUNT_ID": "act_123456789"
      }
    }
  }
}
```

### GA4 MCP

```json
{
  "mcpServers": {
    "ga4": {
      "command": "npx",
      "args": ["-y", "@google-analytics/data-mcp"],
      "env": {
        "GA4_PROPERTY_ID": "123456789",
        "GOOGLE_APPLICATION_CREDENTIALS": "/absolute/path/to/service-account.json"
      }
    }
  }
}
```

## Step 4 — Run the skill

In Claude Code, just describe what you want:

```
> Run the HubSpot blog optimizer on the last 25 posts published to my blog and surface the 5 highest-impact rewrites.
```

Claude will recognize the skill from your installed library, ask for confirmation before write actions, and execute. You can also invoke a skill explicitly:

```
> /skill hubspot-blog-optimizer
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| "Skill not found" | Confirm the folder is in `~/.claude/skills/<skill-name>/SKILL.md` (not nested). Restart Claude Code. |
| "MCP server not responding" | Run `claude mcp list` to see status. Re-check token. Some MCP packages need Node 20+. |
| "Insufficient HubSpot scopes" | Open the Private App in HubSpot, edit scopes, regenerate token, update `claude_mcp_settings.json`. |
| Rate limits on SEMrush | The skill has built-in throttling. If you hit it, wait 60 seconds. Consider upgrading SEMrush plan. |
| Skill works but output looks off | Ask Claude `Explain how you decided that` — usually surfaces a missing input you forgot to provide. |

## Security note

**Never paste API keys into chat with Claude.** They go in `claude_mcp_settings.json` (or `.env`), period. The skills never ask for keys at runtime — they assume the MCP server already has them.

## Need help?

Message me through Gumroad. I respond within 24 hours.
