# skills

Personal agent skills in the [Agent Skills](https://agentskills.io) format.

```bash
npx skills add arthur-debert/skills
```

[![skills.sh](https://skills.sh/b/arthur-debert/skills)](https://skills.sh/arthur-debert/skills)

The catalog lives in [`skills/`](skills/). Each skill is a directory whose name
matches the `name` field in `SKILL.md`.

## Skills

| Skill                                                | What it does                                                                                                     |
| ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| [`dejargon`](skills/dejargon/SKILL.md)               | Replace vague mechanical-metaphor jargon with the concrete actor, mechanism, and consequence.                    |
| [`interface-first`](skills/interface-first/SKILL.md) | Decide whether a feature's interface should land as its own workstream, and how to build one when it does.       |
| [`slop-clean`](skills/slop-clean/SKILL.md)           | Remove session sediment from persisted comments, docs, scripts, and config without changing executable behavior. |

## Install

User-level (available in every project):

```bash
npx skills add arthur-debert/skills -g
```

Project-level (committed with the repo):

```bash
npx skills add arthur-debert/skills
```

Install one skill:

```bash
npx skills add arthur-debert/skills --skill dejargon
```

The CLI discovers every `SKILL.md` under `skills/`. A typical global install
puts the canonical copy in `~/.agents/skills/` and symlinks it into
`~/.claude/skills/`.

## Checks

lefthook runs on every commit:

1. A docs warner reports word deltas and slop tells on staged markdown (warn
   only).
2. Prettier `--check` on tracked markdown, JSON, and YAML.
3. markdownlint on tracked markdown.

Both format and lint run against the whole tree so an unstaged edit cannot hide
from the check.

```bash
prettier --write '**/*.{md,json,yml,yaml}'
markdownlint '**/*.md'
```

Requires [lefthook](https://github.com/evilmartians/lefthook), Prettier, and
markdownlint on `PATH`. After clone: `lefthook install`.

## License

MIT
