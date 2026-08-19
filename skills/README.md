# Catalog

Installable agent skills in the [Agent Skills](https://agentskills.io) format.

```bash
npx skills add arthur-debert/skills
```

| Skill                                         | What it does                                                                                                     |
| --------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| [`dejargon`](dejargon/SKILL.md)               | Replace vague mechanical-metaphor jargon with the concrete actor, mechanism, and consequence.                    |
| [`interface-first`](interface-first/SKILL.md) | Decide whether a feature's interface should land as its own workstream, and how to build one when it does.       |
| [`slop-clean`](slop-clean/SKILL.md)           | Remove session sediment from persisted comments, docs, scripts, and config without changing executable behavior. |

Each skill is self-contained: a `SKILL.md` plus any reference files the
instructions point at. The directory name matches the `name` frontmatter field.
