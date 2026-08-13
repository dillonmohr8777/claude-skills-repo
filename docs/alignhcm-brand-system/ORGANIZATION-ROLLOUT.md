# Align HCM Claude skill organization rollout

The plugin is hosted in the public `dillonmohr8777/claude-skills-repo`
marketplace and requires no repository credentials.

## Individual installation

Run these commands inside Claude Code:

```text
/plugin marketplace add https://github.com/dillonmohr8777/claude-skills-repo.git
/plugin install alignhcm-brand-system@alignhcm-tools
/reload-plugins
```

Invoke the skill with:

```text
/alignhcm-brand-system:alignhcm-brand-system
```

## Organization-wide forced enablement

Claude Team or Enterprise administrators should add the contents of
`organization-managed-settings.json` to the organization's server-managed
Claude Code settings. This declares the public marketplace, enables automatic
marketplace updates, and force-enables the plugin for organization users.

For endpoint-managed Windows installations, merge the same keys into:

```text
C:\Program Files\ClaudeCode\managed-settings.json
```

Do not overwrite unrelated managed settings. If `strictKnownMarketplaces` is
already configured, the administrator must also allow the exact Git source
used here. Managed settings have the highest precedence and cannot be changed
by an ordinary user.

## Repository collaborators

This repository also declares the marketplace and enabled plugin in
`.claude/settings.json`. Claude prompts collaborators to install it when they
trust the checkout. That project-level prompt does not replace the managed
settings step for organization-wide forced enablement.
