---
name: dejargon
description: >-
  Replace vague mechanical-metaphor jargon — gate, leg, pin, load-bearing, wire
  up, plumb through, surface — with the concrete actor, mechanism, and
  consequence. Use this whenever writing prose that persists or reaches humans
  (commit messages, PR titles and bodies, docs, specs, ADRs, plans, code
  comments, review replies, reports), whenever a draft already contains one of
  these words, and whenever asked to de-jargon, sweep, or clean the jargon out
  of a file, diff, or document. These words feel technical but each one
  collapses several distinct concepts into a single metaphor, so text full of
  them reads as precise while communicating almost nothing.
---

# Dejargon

## The problem

A small set of mechanical metaphors — _gate_, _leg_, _pin_, _load-bearing_ —
gets applied to so many different things that each word ends up meaning only "a
thing that matters". The result is prose (and reasoning) like "the gate gated
the commit": grammatically fine, informationally empty. Worse, the metaphor
hides real distinctions, so different mechanisms with different consequences,
code paths, and risks all get filed under one word and start being reasoned
about as if they were the same thing.

## The rule

A word from the list may stand in a sentence that already names the program,
file or command and what it does; it may not stand in for them. "A check in the
CI job runs the linter in case the local pre-commit hook skipped it; this gate
..." names the job, the check and the hook, and "gate" is decoration. "Lint
gates commits" names nothing a reader can open. The test for every occurrence:
**delete the word; does the sentence still say which thing does what?** If yes,
keep or drop the word. If no, write the specific noun or verb in its place. A
rewrite that swaps one vague word for another ("gate" → "blocker") has fixed
nothing.

## Tool, policy, enforcement — keep them separate

Most "gate" usage confounds three different ideas:

- **The check** — a tool that examines something and reports a result: a linter,
  a test suite, a changelog validator. Running `foo lint` in a terminal blocks
  nothing; it is just a quality check.
- **The policy** — a requirement about what must be true: "a PR needs an
  approving review before it can be marked ready", "commits must pass lint".
- **The enforcement point** — the mechanism that applies the policy at a moment
  in time: a pre-commit hook, a required CI status, branch protection, a release
  script that refuses to proceed.

Calling all three "the gate" makes them indistinguishable. Naming them
separately makes sentences strictly richer:

- Bad: "the gate gated the commit"
- Good: "the pre-commit hook aborted the commit because the lint check failed"

That sentence names the enforcement point (pre-commit hook), the check (lint),
and the consequence (commit aborted). Aim for that shape.

## The banned words

### gate / gating / gated

Ask which of the three ideas above is meant, and say that one:

| Instead of                           | Write                                                                              |
| ------------------------------------ | ---------------------------------------------------------------------------------- |
| "lint is a gate"                     | "lint is a quality check; the pre-commit hook blocks commits when it fails"        |
| "the PR is gated on review"          | "the PR can't be marked ready until it has an approving review"                    |
| "CI gates the merge"                 | "the merge is blocked until the required CI checks pass"                           |
| "e2e tests are gated on GPU runners" | "the e2e workflows run only on GPU runners" (a scheduling condition, not blocking) |
| "the release gate"                   | "the release script refuses to proceed while changelog entries are missing"        |

### leg

Means "a part" or "a step" of something. Say which part of what: a task step, a
project phase, a workstream, a deliverable, a request hop, a stage of a journey.
"The second leg" → "the second phase (the migration)".

### pin / pinned

Means "held fixed" — but by what, and why? The one established sense that is
fine is dependency versions ("pin `requests` to 2.31"). Everything else, spell
out: "the snapshot test records the expected output", "the config sets the value
explicitly so upgrades don't change it", "the session keeps reusing the same
worker".

### load-bearing

Means "something depends on this". The metaphor asserts importance without
evidence; naming the dependent is both shorter and checkable: "the deploy script
parses this filename" instead of "this filename is load-bearing".

## The watchlist

The same disease, milder symptoms. Prefer the concrete alternative whenever one
exists: **wire up** (connect, register, pass X to Y), **plumb / thread through**
(pass the parameter down through A and B), **surface** as a verb (show, report,
return), **story** ("the testing story" → "how this is tested"), **guardrail**
(name the specific check or limit), **blast radius** (what breaks if this
fails), **first-class / battle-tested / robust** (say what it actually does or
survived), **mint / ride / hydrate** (create, use the same path as, populate).

## Boundaries

- **Existing identifiers stay.** If code, a vendor API, or a tool already names
  something `Gate`, `feature_gate`, or `--pin`, quote the identifier as-is in
  backticks. But don't let the identifier's metaphor leak into the surrounding
  prose — describe what the code does in concrete terms.
- **A project's own vocabulary stays — even banned words.** A word from the
  banned list or watchlist can be a product's established name for a concept: a
  tool whose docs define "gate dirs" or "the five surfaces" is using those words
  as _names_, not as vague metaphors, and renaming them makes the docs
  contradict the glossary, the CLI's printed output, and every other doc that
  uses the name. Before rewriting a recurring term in project material, check
  whether the project treats it as vocabulary: look for it in a glossary or
  terms reference, grep the source for it in printed strings (`gated out`, help
  text), and look for it in config keys. If it's defined or printed anywhere,
  it's a name — keep it everywhere it's used as that name, clarify the prose
  _around_ it, and list a rename as a candidate for a separate decision.
  Checking one term this way and not the others is the common failure: apply the
  same check to every recurring term you're about to rewrite, not just the most
  prominent one.
- **Don't rewrite the user's own words back at them.** If they say "gate",
  answer the question; use precise terms in your own text.
- **Precision, not word-policing.** The goal is that every sentence survives the
  question "concretely, what happened / what is required / what enforces it?" A
  banned word that appears inside an accurate, concrete sentence is a smaller
  sin than a vague sentence with no banned words.

## Search and rewrite a target

When invoked explicitly on a target (a file, directory, or diff — e.g.
`/dejargon docs/` or "de-jargon this PR description"):

1. Search the target's prose — docs, comments, docstrings, commit message
   drafts, PR body text — for the banned words and watchlist terms.
2. For each recurring hit, first decide: metaphor or name? Run the project-
   vocabulary check from Boundaries (glossary, printed strings, config keys) on
   _every_ recurring term, not just the headline one. Names stay.
3. Rewrite the metaphors so each names the concrete actor, mechanism, or
   consequence. Read enough context to know what the word actually refers to;
   never guess a concrete meaning you can't verify from the surrounding code or
   doc.
4. Leave code identifiers and project vocabulary unrenamed, but list them at the
   end as rename candidates — renaming is a change that ripples into code, CLI
   output, and other docs, so it deserves its own decision.
5. Report what changed in your reply as a short before → after list, with the
   rename candidates from step 4 at the end.
