# InsightSocial agent skills

Official [Agent Skills](https://agentskills.io) for the [InsightSocial API](https://www.insightsocial.app/docs) -
public data from nine social platforms through one key: Instagram, TikTok, Facebook, LinkedIn,
X/Twitter, Threads, YouTube, Reddit and Pinterest. Profiles, posts, comments, followers, search,
ads and transcripts as clean JSON, **one key, one credit balance, priced per call, failed calls free.**

The skill teaches your agent the InsightSocial workflow (read the free catalogue -> price ->
call -> page, cost discipline, error handling), so it uses real paths and parameters instead of
guessing them, and stops to ask before it spends.

## Install

Any agent that supports Agent Skills (Claude Code, Codex, Cursor, Copilot, and others):

```bash
npx skills add insightsocial/skills
```

Claude Code, as a plugin:

```bash
claude plugin marketplace add insightsocial/skills
claude plugin install insightsocial@insightsocial
```

Gemini CLI:

```bash
gemini extensions install https://github.com/insightsocial/skills
```

Manual: copy `skills/insightsocial/` into your agent's skills directory
(`.agents/skills/`, `~/.agents/skills/`, or `.claude/skills/`).

## Setup

Create a key at [insightsocial.app/portal/api/keys](https://www.insightsocial.app/portal/api/keys)
and expose it only as an environment variable:

```bash
export INSIGHTSOCIAL_API_KEY=isk_live_...
```

Every new account gets 10 free calls. Then ask your agent for what you need, for example
*"find 20 fitness creators on TikTok with over 50k followers"* or *"what are people saying
under this YouTube video?"*.

## Skills

| Skill | What it does |
|---|---|
| [`insightsocial`](skills/insightsocial/SKILL.md) | Find, price, and call any endpoint in the catalogue; pagination, errors and credit discipline |

Application-integration guidance (Python, Node, a ready-made agent tool) is in
[`references/rest.md`](skills/insightsocial/references/rest.md).

## Docs

- [insightsocial.app/docs](https://www.insightsocial.app/docs) - quickstart, authentication, API reference
- [api-reference.md](https://www.insightsocial.app/docs/api-reference.md) - every endpoint, as Markdown
- [`GET /v1/endpoints`](https://api.insightsocial.app/v1/endpoints) - machine-readable catalogue with prices, free and keyless
- [llms-full.txt](https://www.insightsocial.app/docs/llms-full.txt) - the full docs in one file

## Support

Questions, problems, or a platform you want covered: support@insightsocial.app
