# Free-Resource Playbook (checked 2026-10-23)

Add-on to [`docs/AGENT-TEAM-PROTOCOL.md`](../AGENT-TEAM-PROTOCOL.md) → "Resource rule". Goal: keep Western Heart work moving 24/7 at $0 while the owner's paid credits (Claude Code, etc.) are reserved for work that needs them. Quotas change; re-check the source link before relying on a number.

## CI (checks)
| Option | Cost | Notes | Source |
|---|---|---|---|
| GitHub Actions on **public** repos | Free, unlimited standard runners | Making a repo public removes the minutes problem. | https://docs.github.com/en/billing/managing-billing-for-your-products/managing-billing-for-github-actions/about-billing-for-github-actions |
| Actions on **private** repos (Free plan) | 2,000 min/month, then blocked at $0 spending limit | **mhvnsnt/agent-ops is out of minutes: its checks have failed since Oct 14** (jobs never start). Fix: raise the Actions spending limit / payment method at https://github.com/settings/billing, make it public, or use a self-hosted runner. | same |
| **Self-hosted runner** on the shared box | Free (no minutes billed) | `runs-on: self-hosted`. Only for repos we trust (never run untrusted fork PRs on it). | https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/about-self-hosted-runners |

## Hosting
- **GitHub Pages**: free for public repos (private repos need a paid plan); 1 GB site, ~100 GB/month bandwidth soft limit. Western Heart already deploys here (`gh-pages`). https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits

## AI coding agents / IDEs, free tiers
| Tool | Free allowance (2026) | Best use | Source |
|---|---|---|---|
| **Jules** (Google) | 15 tasks / rolling 24h, 3 concurrent; opens PRs from a Google cloud VM | Well-scoped TASKBOARD items that end in a PR | https://jules.google/docs/usage-limits/ |
| **Gemini CLI** | **No longer free for personal accounts since 2026-06-18** (replaced by Antigravity CLI). Unpaid Gemini API key tier listed at 250 req/day Flash-only, verify with one real call. | Scripted reviews if a key works | https://geminicli.com/docs/resources/quota-and-pricing/ , https://developers.googleblog.com/en/an-important-update-transitioning-gemini-cli-to-antigravity-cli/ |
| **Antigravity** (desktop + CLI) | $0 Individual plan, basic weekly rate limits | Replacement for free Gemini CLI | https://antigravity.google/pricing |
| **GitHub Copilot Free** | 2,000 completions/month + limited chat/agent (auto model only) | Small edits, PR review in VS Code | https://docs.github.com/en/copilot/concepts/billing/individual-plans |
| **Cursor Hobby** | Free, no card; "limited" Agent + Tab (no published number) | Extra IDE seat when others are capped | https://cursor.com/pricing |
| **OpenAI Codex** | Included with ChatGPT plans; free-plan access is limited/promotional, check your account | Cloud tasks that open PRs | https://developers.openai.com/codex/pricing |
| **Cline / Roo + OpenRouter `:free` models** | 50 req/day, 20/min (1,000/day after a one-time $10 credit purchase) | Cheap bulk edits, docs, triage | https://openrouter.ai/docs/api_reference/limits |
| **Kaggle notebooks** | ~30 GPU-hours/week (T4/P100), 12h sessions | Mocap retargeting, batch Blender renders, ML | https://www.kaggle.com/docs/efficient-gpu-usage |
| **Google Colab free** | T4 GPU when available, no guaranteed quota, ~12h max | Same as Kaggle, overflow | https://research.google.com/colaboratory/faq.html |
| **Grok Bot agents on the shared box** | Running already; the box is free compute | Long jobs, extraction, CI-like local checks, deploy builds | — |

## 24/7 rotation at $0
1. **Box + Grok Bot agents** are the always-on base: extraction, builds, local test runs, merges (after green checks).
2. **Jules** gets up to 15 queued TASKBOARD items/day (tag them `jules-ok`); review its PRs like anyone else's.
3. **Claude Code** (paid, session cap, e.g. reset 6 PM CT) gets the hardest items: rigs, deploy fixes. It must push early (autosave hook). When it caps, its branch is picked up per the handoff steps in [`HANDOFF.md`](HANDOFF.md).
4. **Muse** keeps its coordinator lanes; when idle it pulls from TASKBOARD.
5. **Copilot Free / Cursor Hobby / Antigravity / Cline+OpenRouter free** are overflow seats: when one caps, switch to the next. Log which tool did what in the PR body.
6. **Kaggle → Colab** for GPU work; save outputs to the repo/release, never only in the notebook.
7. CI: keep western-heart checks running; for agent-ops either fund Actions, go public, or register the box as a self-hosted runner.
