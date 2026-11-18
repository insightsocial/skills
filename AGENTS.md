# InsightSocial skills agent instructions

This repository publishes customer-facing agent skills for the InsightSocial API. The source of
truth for every fact in them is the live API and its docs, not this repository:

- Endpoints, parameters and prices: `GET https://api.insightsocial.app/v1/endpoints`.
- Behaviour (auth, envelope, credits, pagination, errors, rate limits):
  https://www.insightsocial.app/docs/llms-full.txt.

`skills/insightsocial/` is also bundled, byte for byte, in the CLI package
([insightsocial/cli](https://github.com/insightsocial/cli)), which installs it on `insightsocial init`.
Edit it here, then copy it into the CLI and release both; the check fails while they differ.

The Claude plugin ships a different skill, `claude/skills/insightsocial/`: the same workflow through
the hosted MCP tools only. The Claude directory holds a plugin whose skill reads a credential from the
user's machine, so this one must never mention an API key, an environment variable, the CLI or a
local file. When the shared skill changes, carry the change into it by hand.

When the API changes, update the docs first, deploy them, then sync `skills/insightsocial/`.
Never write a path, parameter, price or limit into a skill that the catalogue or docs do not
state today. Never name an upstream data provider.

When a skill's content changes, bump the version in the four manifests together:
`.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.cursor-plugin/plugin.json` and
`gemini-extension.json`, plus `metadata.version` in the `SKILL.md` that changed. The check requires
the plugin's skill to carry the manifest version; the shared skill's version moves with the CLI copy.

Run the check before handing off changes. It checks the manifests agree, and that every `/v1/...`
path and every insightsocial.app link a skill names is live today. It lives inline in
`.github/workflows/check.yml`, because the Claude directory refuses script files in this repository
(we are not a Verified organization). Run it locally from the repository root:

    sed -n "/python3 - <<'PY'/,/^ *PY$/{//!p;}" .github/workflows/check.yml | sed 's/^          //' | python3 -

Keep this repository free of scripts, `allowed-tools` lines and other non-Markdown/JSON/YAML files,
or the Claude directory refuses the plugin.
