# InsightSocial skills agent instructions

This repository publishes customer-facing agent skills for the InsightSocial API. The source of
truth for every fact in them is the live API and its docs, not this repository:

- Endpoints, parameters and prices: `GET https://api.insightsocial.app/v1/endpoints`.
- Behaviour (auth, envelope, credits, pagination, errors, rate limits):
  https://www.insightsocial.app/docs/llms-full.txt.

When the API changes, update the docs first, deploy them, then sync `skills/insightsocial/`.
Never write a path, parameter, price or limit into a skill that the catalogue or docs do not
state today. Never name an upstream data provider.

When a skill's content changes, bump the version in all five places together:
`.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.cursor-plugin/plugin.json`,
`gemini-extension.json`, and `metadata.version` in each `SKILL.md`.

Run `bash scripts/check.sh` before handing off changes. It checks the manifests agree, and that
every `/v1/...` path and every insightsocial.app link a skill names is live today.
