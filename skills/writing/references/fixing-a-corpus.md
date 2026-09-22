# Fixing a corpus

An orchestrator asked to repair a doc set, a spec tree, a handbook or a wiki
runs a campaign over the corpus, the documents plus code comments, docstrings,
CLI help strings, READMEs, commit templates and skill files, with agents:
scorers score every file, stage 1 writes a fact sheet per flagged file, stage 2
rewrites from the sheet, stages 3 and 4 check, and the orchestrator hands the
author `DECISIONS-NEEDED.txt`. Not yet decided: whether the scorers score code
files as well as documents.

## Two modes

Pipeline mode
([Separate the reader from the writer](#separate-the-reader-from-the-writer)):
the author is absent or slow, the corpus is large or mixed-voice, and the rule
set does not change while a sweep runs. Not yet decided: whether a rule added to
`decisions.txt` from an answer re-runs the sweep on files already swept, or
applies only to files not yet swept.

Calibration-sample mode: the author is present, the corpus is one voice, the
rule set is not yet fixed.

1. Pick one document.
2. Hand the author findings, not edits: `QUOTE` / `DEFECT` / `REPLACE WITH`.
3. Take their corrections over one or two rounds.
4. Write each correction into `decisions.txt` as a numbered rule before opening
   a second document. An agent started after the correction reads
   `decisions.txt`, not the conversation it was given in; relayed in
   conversation, a correction softens and the sweep drifts back to the first
   calibration.
5. Sweep the rest of the corpus with that rule set.

The orchestrator can run calibration and then the pipeline in one campaign:
`decisions.txt` holds the calibration's rules first, then the rules for the
pipeline sweep, in one numbered list.

Not yet decided: which file is the rule set, `writing/SKILL.md` alone, SKILL.md
plus `decisions.txt`, or a per-campaign brief.

## Do not blanket-rewrite

The scorers score every file; only a document scored `rewrite` goes through
stages 1 to 4, where stage 2 replaces every sentence from the fact sheet and the
text grows toward the half-again limit.

- Reads: every file.
- Writes: `triage.tsv`, one row per file, and `score/<group>/<doc>.findings.md`:
  per finding `FILE`, `SECTION`, `QUOTE` (at most three lines), `DEFECT` (at
  most ten words), `REPLACE WITH` (a fact with file:line, or `TBD: <question>`);
  last line
  `SCORE: <score>  FLAGGED: <n>  TERMS: <coined terms with sense counts>`. Not
  yet decided: whether the scores are two, sound and rewrite, or three, with a
  patch outcome whose findings are applied in place.
- Must not: edit outside the score directory, write paragraphs, judge style in
  general.

## Do not tell the scorers what you expect

A scoring brief names the tests, SKILL.md's
[Three tests](../SKILL.md#three-tests) onward, and no file. Do not write into
the brief which documents you expect to pass or fail; the scores test that
expectation as a hypothesis.

## Two signals, and expect them to disagree

Run a grep for the words you distrust beside the scorers' pass and write the
counts per file to `.rewrite/`. Not yet decided: the counts file's name. The
grep does not decide what gets rewritten: a document that asserts nothing has no
metaphor to flag, and a document with a high count can score `sound`, because
dense confident prose co-occurs with an author who has thought the thing
through.

## Separate the reader from the writer

An agent that reads a page of prose and then writes imitates it; one instruction
does not outweigh a page of counter-examples. The writer never reads the
original body.

| Stage            | Reads                                                                      | Writes                                     | Must not                                         |
| ---------------- | -------------------------------------------------------------------------- | ------------------------------------------ | ------------------------------------------------ |
| 1 Interrogate    | document, findings, `decisions.txt`, the code and data described, siblings | `facts/<doc>.facts.txt`                    | criticise; write paragraphs                      |
| 2 Rewrite        | fact sheet, rule set, approved exemplar, heading skeleton                  | `drafts/<doc>`                             | open the original, its history or earlier drafts |
| 3 Check style    | rewrite only                                                               | style findings                             | read the fact sheet                              |
| 4 Check fidelity | rewrite and fact sheet                                                     | every assertion the sheet does not support | read the original                                |

One agent cannot run stages 3 and 4: asked for both, it trades one against the
other.

Not yet decided: who approves the exemplar, and at what path under `.rewrite/`
it is stored.

## The intermediate must be a fact sheet, not a critique

Stage 1 emits `Q` / `A` / `SRC file:line` fragments, or `TBD`, and no criticism,
under `DOC`, `READER`, `HEADINGS`, `FACTS`, `TERMS`, `CONFLICT`, `TBD`,
`OWNED ELSEWHERE`. A line such as "this paragraph asserts a verdict" makes the
rewriter open the original to apply it and copy its prose. Paragraphs in the
fact sheet mean stage 1 has failed; one actor, verb, constraint and source per
line keeps verdicts out.

## Look for the facts before concluding they are missing

Before stage 1 marks a claim `TBD`, it reads the research notes, ADRs, decision
logs and scratch documents, where the reasoning sits before the main documents
compress it away. Most of what looks undecided is recoverable there.

## Never invent a mechanism

Where the facts leave a gap, stage 2 writes a `TBD` marker at that point in the
draft, and `DECISIONS-NEEDED.txt` gets an entry with file:line and the one
question a human must answer. Not yet decided: whether stage 2 itself appends
that entry. When unsure, mark: a wrong marker costs the author ten seconds; a
wrong resolution puts a decision they never made into their documents. An
illustration of what good prose would look like invents too: a detail that feels
right is not in the corpus.

## Two kinds of contradiction

Stage 1 writes a contradiction the corpus resolves, one statement checkably
wrong or one word with two stated meanings, as a `Q` / `A` / `SRC file:line`
line; stage 2 writes the answer, so the wrong statement does not survive. The
tests are SKILL.md's
[Two more tests](../SKILL.md#two-more-tests-once-the-document-has-neighbours)
and [Coined terms](../SKILL.md#coined-terms). Not yet decided: where the fix is
reported and by which stage. Stage 1 writes a contradiction the author has not
decided as a `CONFLICT` line,
`<document line>: says <x>; code/table at <src> does <y>`; stage 2 leaves the
surrounding prose assuming neither side and never resolves it, not even by
picking the more frequent or better-reading version.

## Everything goes to files

Each stage writes to disk and returns one summary line: `SCORE` lines from
scoring, counts from stage 1. A return value exists only in the orchestrator's
context and cannot be verified later; a file on disk is read by the next agent,
survives a restart of the campaign, and lets the author inspect any stage.
`.rewrite/` holds:

| File                              | Format                                                                                                                     |
| --------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `triage.tsv`                      | one row per file. Not yet decided: whether the columns are group, source, score, flagged, owner, findings.                 |
| `score/<group>/<doc>.findings.md` | findings, as under [Do not blanket-rewrite](#do-not-blanket-rewrite)                                                       |
| `facts/<doc>.facts.txt`           | the fact sheet                                                                                                             |
| `drafts/<doc>`                    | the rewrite                                                                                                                |
| `decisions.txt`                   | `D<n>. <rule>`, so a brief can say "apply D8 only"                                                                         |
| `DECISIONS-NEEDED.txt`            | file:line plus the question. Not yet decided: whether the line is `<source path>:<line>  <question>  "<quoted sentence>"`. |

## Verify mechanically, not by impression

Four measurements check each draft before it is sent. Not yet decided: which
stage or script runs them.

1. Scope: a diff shows only the flagged sections changed, every other byte
   identical. Naive section detection breaks when nested headings are indented.
   Not yet decided: which script finds the section boundaries. Not yet decided:
   whether this applies only to documents patched in place, or how a draft
   written from the fact sheet keeps unflagged sections identical.
2. Growth: the draft's word count minus `TBD` marker text, against the original,
   at most one and a half times the original.
3. Format: the corpus linter on every draft; a failing draft is not sent.
4. Vocabulary: dejargon's
   [The banned words](../../dejargon/SKILL.md#the-banned-words) and
   [The watchlist](../../dejargon/SKILL.md#the-watchlist), grepped against the
   result file, not memory of it.

## Expect expansion, and give a number

The rewrite brief states the limit up front: at most one and a half times the
original word count. SKILL.md's [Calibration](../SKILL.md#calibration) and
[Whose fact is it?](../SKILL.md#whose-fact-is-it) state the limit and why
rewrites grow.

## Batch questions for the author, and record the answers

Hand the author `DECISIONS-NEEDED.txt`, every entry with file:line in one
document; the author is the only source for undecided things, and their time is
the scarce input. Write the answers into `decisions.txt`, numbered, and pass
that file to the agents ("Apply D1, D2, D6 and D9"). An answer arrives as an
explanation; write the rule it implies into `decisions.txt` as `D<n>`, and put
any question the explanation leaves open back into `DECISIONS-NEEDED.txt`. Never
relay an answer in conversation, where it softens.

## When a decision deletes a claim, fix its citers

After a decision deletes or corrects a claim, grep the corpus for documents that
cite the old statement, and fix them. SKILL.md's
[Before you finish](../SKILL.md#before-you-finish), step 8, states the rule.

## The corpus is everything agents ingest

The sweep covers every file in the corpus, code included; the next agent
imitates whatever it reads, so a swept doc set is reinfected from any text left
unswept. slop-clean's
[Surfaces and their editing regimes](../../slop-clean/SKILL.md#surfaces-and-their-editing-regimes)
states the editable span per file kind; identifier and file renames are code
changes run through the test suite. A term the project's code prints is not
exempt: SKILL.md's [Coined terms](../SKILL.md#coined-terms) overrules dejargon's
project-vocabulary rule.

## Let agents refuse you

The rule set outranks the orchestrator's instruction. An agent declines one that
would contradict a closed enumeration in a sibling document, or place a fact in
a document that does not own it under
[Whose fact is it?](../SKILL.md#whose-fact-is-it). An agent that applies every
instruction uncritically introduces contradictions at the orchestrator's speed.

## What the campaign actually produces

The campaign produces the rewritten corpus and `DECISIONS-NEEDED.txt`. The
orchestrator works `DECISIONS-NEEDED.txt` with the author entry by entry, since
an entry may name a choice the author did not know they had made; the author
answers each one.
