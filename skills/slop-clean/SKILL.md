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

The agent removes from committed files the text recording the session that
produced the code: dates, tracker tags, who requested or reviewed a change, what
ran to verify it, implementation chronology, and rationale repeated where one
site with a pointer serves. Executable behavior does not change. Text explaining
purpose, design, trade-offs, usage, or behavior the code does not make obvious
stays.

## File kinds and what may change in each

- Source or test file: language-recognized comments, documentation comments,
  docstrings. Never executable code.
- Prose document (markdown, lex, rst, README): the whole file. Delete dates, "as
  of", "currently", "previously", "we decided/verified", surveys, verification
  runs and chronology; rewrite the remainder in present tense.
- Script or config file: comments only. Never commands, values, or keys.

A survey, inventory, verification run, or chronology anywhere is deleted; its
conclusion stays as a present-tense fact.

## 1. Set scope and invariants

1. Scope: the path the user named; else maintained source and tests, minus
   generated, vendored, and third-party files.
2. First read the repository's instructions; learn its languages, comment
   syntaxes, validation commands, version-control state, and delivery workflow.
3. Never edit identifiers, types, signatures, executable code, test logic,
   string literals, or documentation inside strings; embedded source in a string
   literal changes only when the user separately authorizes that. In source,
   test, script and config files, text not classifiable as a comment stays.
4. Legal, license, attribution, and compliance text stays.
5. A comment feeding generated documentation, a package, a source map, or a
   schema: before editing, write down what must stay true of that output. Not
   yet decided: which properties, recorded where.
6. A formatter or bulk rewrite may not change non-comment text.
7. Metaphor words in kept text: `dejargon`.

## 2. Survey and partition the work

Read the repository's tracker and tag naming and search with those terms for:
issue, pull-request, milestone, workstream, and ticket references; agent or
prompt narration and implementation-history play-by-play; TODOs with tracking
metadata; repeated distinctive explanations; comments paraphrasing the adjacent
declaration, branch, validation, or error; comment-heavy files.

Comment density only orders inspection; read every match in context first.
`rustloc count --by-file --ordering docs` ranks files by comment volume (the
other flags and the `tokei`, `cloc`, and `wc -l` fallbacks: `loc-refactor`).

Several agents: non-overlapping paths, one branch, one PR. Each worker gets an
exclusive path scope, this SKILL.md, and the repository's instructions; touches
nothing outside it; stages and commits nothing; reports files inspected
(including unchanged), removed, and kept. One coordinator reads the assembled
diff, validates, and commits; whether a PR is opened follows the repository's
delivery workflow. Repository instructions requiring separate worktrees,
branches, or PRs win.

## 3. Pass 1: remove the record of the session

Delete text whose only content is who requested, implemented, reviewed, or
tracked a change:

- Tracking tag: delete, repair punctuation.
- Ticket bookkeeping on a TODO: delete the bookkeeping; the TODO stays.
- Agent reasoning, prompt narration, build-history commentary: delete.
- Implementation chronology whose constraint applies to the code: one
  present-tense sentence stating the constraint.
- In prose, dates, "as of", "currently", "previously", "we decided/verified":
  delete; a remainder stating a constraint the code depends on becomes present
  tense, undated.

Keep decision records, specifications, standards, stable API references, and
documentation links. A tracker link that alone explains a non-obvious constraint
stays. Not yet decided: which reference kinds may replace it.

For text narrating the session that produced the code, apply the
`writing-documentation` section "No task residue"; for text recording
deliberation, apply the `writing` section "Tells".

Then reread the diff, rerun the step 2 searches; every remaining match is on the
keep list (decision records, specifications, standards, stable API references,
documentation links). Not yet decided: whether matches outside it may stay.

## 4. Pass 2: one site for each explanation

Merge only explanations with the same meaning, grouped by idea, not wording.

- Full rationale: at the defining type, function, module, subsystem overview, or
  design document.
- Other sites: local information plus, when readers need the full explanation, a
  pointer (intra-doc link, documentation symbol reference, `@see`, stable
  document link). No `@see` where the doc tool will not resolve it.
- No lasting site, and the explanation needed at each decision point: it stays
  at each.
- Pointer farther from the reader than the duplicated sentence: the duplicate
  stays. Not yet decided: the distance (file, module, crate, repository) that
  counts as farther.

Example: `crop` and `resize` each have the docstring "Coordinates use a top-left
origin." After: one module docstring "Image operations use a top-left coordinate
origin." and no per-function docstring.

Prose cross-references: `writing` ("Whose fact is it?"), `writing-documentation`
("Detail flows down, decisions don't flow up").

## 5. Pass 3: remove self-evident narration

Novelty test: if the code, identifier, type, signature, or the adjacent control
flow says the same thing, delete the comment.

Delete: comments restating a field's type or a parameter's name; prose versions
of the next if, loop, allocation, conversion, or error return; states the type
system excludes; test comments narrating setup, action, assertion; error-variant
prose repeating the variant name and fields.

Keep: why a check exists, why a tempting alternative is wrong, a rule callers
must follow that the signature does not show, a numerical or concurrency hazard,
wire-format compatibility, a platform quirk, a subtle edge case.

Examples (full text in examples/comment-quality.md):

- Two comment lines saying
  `if band.image.color.width != band.full_width { return Err(...) }` avoids an
  out-of-bounds: deleted.
- Three doc lines on `ZeroDimension` about later methods assuming non-zero size:
  `/// Zero is not a valid width or height.` One enum doc line when every
  variant has the same defensive reason.
- `/** The unique user ID as a string. */` on `userId: string`: deleted; a
  replacement would say what the type cannot (stability across reconnects).
- A Go comment above `registry.Unlock()` then `compiler.Compile(input)` giving
  the re-entrancy reason for the order: kept.
- A `//` line inside `const SHADER: &str = r#"..."#` is WGSL source, not a
  comment: untouched unless the user authorizes edits to the embedded source.

## 6. Review what each module's documentation covers

Apply to every substantial comment left after pass 3 (not yet decided: which
comments count as substantial):

- A module's documentation describes its own purpose and the rules callers must
  follow, never its parent.
- It lists siblings or children only as a short map of one small group (an
  `operations` overview may list `add` and `remove`, without internals) and
  stops once the map needs its own guide. Not yet decided: the child count past
  which listing stops.
- A repository- or subsystem-wide convention is written once at that level, not
  beside each function following it.
- A leaf may point to the full explanation, not repeat it.
- Public API docs explain usage and rules the signature and types do not show.

Documentation worth keeping:

- architectural responsibility, design rationale and trade-offs;
- a high-level overview of a module, subsystem, or public API;
- usage constraints not evident from the signature;
- tricky behavior, edge cases, safety conditions, interoperability details.

Prose: `writing-documentation` ("Detail flows down, decisions don't flow up").
Hard cases: examples/comment-quality.md.

## 7. Verify and deliver

1. Run the scope's build, lint, documentation, and test commands. Formatting
   runs check-only; a formatter that must write has every non-comment change
   removed.
2. Confirm on the final diff that steps 1 to 6 hold: only editable spans
   changed, strings and embedded languages untouched, generated outputs as
   recorded, behavior unchanged.
3. Report intended changes to rendered or distributed documentation. If a
   comments-only edit cannot keep a generated output as recorded, stop and
   report.
4. If a check cannot run, state which.
5. A single agent commits once per pass when that helps review; a coordinator
   commits the assembled diff. No forced empty commits. Follow the repository's
   delivery workflow; assume no hosting system, delegation model, or permission
   to publish.
