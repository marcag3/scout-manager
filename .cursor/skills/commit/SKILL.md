---
name: commit
description: >-
  Commit staged and unstaged changes with a gitmoji-prefixed message. Use when
  the user asks to commit, says /commit, or wants changes committed with gitmoji.
disable-model-invocation: true
---

# /commit

Commit your changes using [gitmoji](https://gitmoji.dev).

## When to run

Only commit when the user explicitly asks (e.g. `/commit`, "commit this", "commit your changes"). If scope is unclear, ask first.

## Workflow

### 1. Inspect (run in parallel)

```bash
git status
git diff
git diff --staged
git log -5 --oneline
```

### 2. Stage and draft message

- Stage only files that belong to this change. Never stage secrets (`.env`, credentials, keys).
- Pick **one** leading gitmoji that best matches the change.
- Write a concise subject (≤72 chars after the emoji): `EMOJI verb specific change`
- Add an optional body (1–2 sentences) explaining **why**, separated by a blank line.

### 3. Commit

```bash
git add <paths>
git commit -m "$(cat <<'EOF'
EMOJI subject line

Optional body explaining why.

EOF
)"
git status
```

### 4. On failure

If a pre-commit hook fails or rejects the commit: fix the issue and create a **new** commit. Do **not** amend unless all amend rules below are met.

## Git safety

- Never update git config
- Never run destructive git commands (`push --force`, `hard reset`, etc.) unless explicitly requested
- Never skip hooks (`--no-verify`, `--no-gpg-sign`, etc.) unless explicitly requested
- Never force-push to `main`/`master`; warn the user if they request it
- Do not push unless the user explicitly asks
- Do not create empty commits

### Amend only when ALL are true

1. User explicitly requested amend, **or** commit succeeded but a hook auto-modified files that must be included
2. HEAD commit was created by you in this conversation (`git log -1 --format='%an %ae'`)
3. Commit has **not** been pushed (`git status` shows branch ahead, not synced with remote)

If commit **failed** or was **rejected** by a hook → never amend; fix and make a new commit.

## Gitmoji picker

| Change type | Emoji | When to use |
|-------------|-------|-------------|
| New feature | ✨ `:sparkles:` | New capability, page, endpoint, or user-facing behavior |
| Bug fix | 🐛 `:bug:` | Something broken now works |
| Docs | 📝 `:memo:` | README, comments, design docs only |
| Style | 🎨 `:art:` | Formatting, structure, UI polish (no logic change) |
| Refactor | ♻️ `:recycle:` | Restructure without changing behavior |
| Perf | ⚡ `:zap:` | Performance improvement |
| Tests | ✅ `:white_check_mark:` | Add or update tests |
| Chore / config | 🔧 `:wrench:` | Tooling, CI, deps, config, scripts |
| Remove | 🔥 `:fire:` | Delete code or files |
| Deprecate | ⚰️ `:coffin:` | Deprecate feature or API |
| Security | 🔒 `:lock:` | Security fix or hardening |
| Breaking | 💥 `:boom:` | Breaking change |
| WIP | 🚧 `:construction:` | Incomplete work (avoid unless user asks) |
| Release | 🚀 `:rocket:` | Deploy or release cut |
| Init | 🎉 `:tada:` | Initial commit or major milestone |

When multiple apply, prefer the **most specific** emoji for the primary intent (e.g. 🐛 for a fix even if you refactored while fixing).

## Examples

```
✨ add Accounts Payable to treasurer workspace doc

Document features used in v15 and group them for the future workspace.
```

```
🐛 fix bank import duplicate detection on re-upload

Skip rows already linked to a Bank Transaction for the same account.
```

```
📝 document used ERPNext features by workspace card
```

```
♻️ extract party alias lookup into shared helper
```

## Output

After a successful commit, tell the user:

- The gitmoji subject line used
- Short summary of what was included
- `git status` result (clean working tree or remaining changes)
