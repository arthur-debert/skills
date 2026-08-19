---
name: slop-clean
description:
  Remove session sediment from anything persisted under source control — code
  comments, docstrings, prose docs, scripts, config — without changing
  executable behavior. Use when persisted text contains development history,
  provenance, dates, duplicated rationale, self-evident narration, or
  disproportionate volume; optionally limit cleanup to a requested path.
---

# Slop Clean

Perform a cleanup in three passes, followed by an information-boundary review.
Preserve text that explains purpose, design, trade-offs, usage, or genuinely
non-obvious behavior.

## Surfaces and their editing regimes

The disease is one — session scaffolding persisted as if it were the design —
but the editable span depends on the surface:

- Code files (source, tests): language-recognized comments, documentation
  comments, and docstrings only. Never executable code.
- Prose documents (markdown, lex, rst, standalone docs, READMEs): the whole file
  is editable. Apply timeless register: present tense, no dates, no "as of /
  currently / previously", no process or session narration, no verification
  story. Only the model survives.
- Scripts and config: comments only; never commands, values, or keys.

The universal law: session evidence — surveys, inventories, verification runs,
chronology — is never persisted under source control. Only its consequences are,
stated as present-tense facts.

## Establish scope and invariants

1. Use the user's path or component as the scope. Otherwise cover maintained
   source and tests, excluding generated, vendored, and third-party files.
2. Read repository instructions before editing. Discover the languages, comment
   syntaxes, validation commands, version-control state, and delivery workflow
   from the repository itself.
3. Treat only language-recognized comments, documentation comments, and
   docstrings as editable. Do not edit identifiers, types, signatures,
   executable code, test logic, string literals, or documentation embedded in
   strings. If unsure whether text is a comment, leave it unchanged.
4. Preserve legal, license, attribution, and compliance text.
5. Determine whether comments feed generated documentation, packaged artifacts,
   source maps, schemas, or other distributed output. Establish those output
   invariants before editing.
6. Preserve unrelated work. Do not let a formatter or bulk rewrite modify
   non-comment text.

The completion criterion is strict: every changed span sits inside its surface's
editable regime, every retained comment or sentence has a clear informational
job, and the repository's relevant checks pass.

## Survey and partition the work

Derive the repository's actual process vocabulary instead of assuming one
tracker or tag format. Search for:

- issue, pull-request, milestone, workstream, and ticket provenance;
- agent or prompt narration and implementation-history play-by-play;
- TODOs coupled to tracking metadata;
- repeated distinctive explanations;
- comments that paraphrase the adjacent declaration, branch, validation, or
  error;
- unusually comment-heavy files and modules.

Inspect matches in context before editing. Comment density is triage evidence,
not proof of bloat. Use language-aware tools where available; otherwise combine
text search with manual review.

When `rustloc` supports the repository's language, its `--by-file`,
`--by-module`, `--ordering docs`, `--top`, and `--output json` options can help
prioritize inspection. It is optional and does not replace judgment.

If the scope warrants parallel work and delegation is authorized, partition it
by non-overlapping files or directories on one integration branch and PR:

1. Assign one coordinator to own the combined diff, validation, commit, and PR.
2. Give each agent an exclusive path scope plus this rubric and the repository
   guardrails.
3. Forbid agents from formatting unrelated files, staging, committing, or
   editing outside their scope.
4. Have each agent report files inspected, including intentionally unchanged
   files, and summarize what it removed and preserved.
5. Independently audit the assembled diff before delivery.

Avoid overlapping scopes and concurrent repository-wide formatters. If
repository instructions require isolated trees, branches, or PRs, follow them
instead of forcing the shared-PR pattern.

## Pass 1: remove process sediment

Remove metadata whose only value is recording who requested, implemented,
reviewed, or tracked a change:

- delete tracking tags and repair punctuation;
- keep a useful TODO but remove its ticket bookkeeping;
- replace implementation chronology with a present-tense constraint only when
  the constraint remains useful;
- remove agent reasoning, prompt narration, and build-history commentary;
- in prose docs, remove temporal and provenance language (dates, "as of",
  "currently", "previously", "we decided/verified"), rewriting any load-bearing
  remainder as a timeless statement.

Preserve decision records, specifications, standards, stable API references, and
documentation links. If a tracker link is the only source for a non-obvious
constraint, keep it or replace it with a canonical durable reference.

Review the diff and rerun the candidate searches. Every remaining process-like
match must be intentionally durable.

## Pass 2: establish one owner for each explanation

Consolidate only explanations that carry the same meaning:

1. Group near-duplicates by idea, not merely by similar wording.
2. Choose the defining type, function, module, subsystem overview, or design
   document as the canonical source.
3. Keep the complete rationale there.
4. At other sites, retain only local information. Add a short,
   language-appropriate pointer when readers genuinely need the canonical
   explanation.
5. If no durable target exists and the explanation is necessary at each decision
   point, keep it.

Use the ecosystem's normal reference mechanism: an intra-doc link, documentation
symbol reference, `@see`, or stable document link. Do not introduce `@see` where
the language's documentation system will not resolve or render it.

Review each consolidation while its context is fresh. A pointer is not useful if
it sends the reader farther away than the duplicated sentence would.

## Pass 3: remove self-evident narration

Apply the **novelty test**: if the code, identifier, type, signature, or
immediately adjacent control flow already says the same thing, delete the
comment.

Typical removals include:

- comments that restate a field's type or a parameter's name;
- prose versions of the next `if`, loop, allocation, conversion, or error
  return;
- documentation that explains an impossible state already excluded by the type
  system or type hints;
- test comments that narrate setup, action, and assertion without adding intent;
- verbose error-variant prose whose only message is the variant name and fields.

Do not confuse brevity with clarity. Keep information the code does not carry:
why a check exists, why a tempting alternative is wrong, a surprising contract,
a numerical or concurrency hazard, wire-format compatibility, a platform quirk,
or a subtle edge case.

## Review information boundaries

Apply the **ownership test** to every substantial surviving comment:

- A module documents its own purpose and contract, never its parent.
- It documents siblings or children only as a compact map of one small, cohesive
  logical unit. Larger components own their own documentation.
- A repository- or subsystem-wide convention belongs at that boundary, not
  beside every variable or function that follows it.
- A leaf may point to the canonical explanation but must not repeat it.
- Public API documentation should explain caller-visible usage and contracts
  that signatures and types do not express.

Examples of worthwhile documentation:

- architectural responsibility, design rationale, and trade-offs;
- a high-level overview of a module, subsystem, or public API;
- usage constraints not evident from the signature;
- tricky behavior, edge cases, safety conditions, and interoperability details.

If a classification is ambiguous or calibration would help, read
[examples/comment-quality.md](examples/comment-quality.md). The examples are
diagnostic contrasts, not text templates.

## Verify and deliver

Run the build, lint, documentation, and test commands relevant to the scope.
Prefer check-only formatting commands; if formatting is required, audit and
exclude every non-comment change it produces.

Independently inspect the final diff and confirm:

- only comments or docstrings changed;
- comments inside strings, templates, generated code, and embedded languages
  remain untouched;
- every process-noise search result is intentionally durable;
- every shared explanation has one canonical owner and only useful pointers
  elsewhere;
- every surviving comment passes the novelty and ownership tests;
- generated and distributed outputs satisfy the established invariants;
- executable behavior is unchanged.

Report intentional changes to rendered or distributed documentation. If a
comments-only edit cannot satisfy an output invariant, stop and report the
conflict instead of widening scope.

If checks are unavailable, state exactly what could not run. Keep coherent
passes separate in commits when that aids review, but do not force empty or
artificial commits. Follow the repository's delivery workflow; do not assume a
hosting system, delegation model, or permission to publish.
