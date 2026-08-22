# Fixing a corpus

How to run a session that repairs an existing set of documents, rather than
writing one. Read this when someone asks you to clean up a doc set, a spec tree,
a handbook, or a wiki — not when you are writing a single document.

The short version: the writing is the visible problem and the missing decisions
are the real one. Plan for the second from the start.

## Do not blanket-rewrite

Score first. A corpus that reads uniformly bad is usually not uniformly bad, and
rewriting sound documents damages them. Score every document, then rewrite only
what scores badly. On one 25-document corpus the sectional flags covered about
17% of sections; a blanket pass would have degraded eleven documents to fix
twenty-one sections.

## Do not tell the scorers what you expect

The single largest error available to you. If you have read some of the corpus
and formed impressions, keep them out of the briefs. Priming a scorer with
"document X is largely sound, be sceptical of your impulse to flag it" reliably
produces a pass. On the corpus above, eleven documents passed a primed first
round; re-scored with neutral briefs, **all eleven failed**, two badly enough to
need full rewrites. Your impressions are a hypothesis, not a prior to hand out.

## Two signals, and expect them to disagree

Run a cheap deterministic pass (grep for the vocabulary you distrust) alongside
the judgment pass. Do not trust the cheap one. Measured on that corpus, lexical
tell-density was **anti-correlated** with the defect: documents scoring worst on
word-level measures were judged sound, and the cleanest document by word counts
needed the most work.

The reason is worth knowing. Dense, confident, aphoristic prose co-occurs with
having actually thought something through. Documents that score low on jargon
often score low because they assert nothing — there is no metaphor to flag
because there is no claim. Word-level tools cannot find that.

## Separate the reader from the writer

The disease is in-context imitation: an agent that reads a page of bad prose and
is then asked to write will match its register, because matching the surrounding
style is what models do best and one instruction is weak against a page of
counter-examples.

So the agent that writes should see as little of the original prose as possible.
Structure it as:

1. **Interrogate** — reads the document, its siblings, and the code. Emits a
   fact sheet, not a critique.
2. **Rewrite** — reads the fact sheet, the standard, an approved exemplar, and
   the document's heading skeleton. Not the original body prose.
3. **Check style** — sees only the rewrite.
4. **Check fidelity** — sees the rewrite and the fact sheet, and asks only
   whether anything is asserted that the sheet does not support.

Split style and fidelity. An agent asked both will trade one against the other.

## The intermediate must be a fact sheet, not a critique

If the analyst emits criticism ("this paragraph asserts a verdict"), the
rewriter has to read the original to apply it, and the contamination is back. If
it emits **answers** — terse `Q / A / SRC file:line` fragments, or `TBD` — the
rewriter can work without ever reading the bad prose.

Force the schema hard. A bullet of actor/verb/constraint/source cannot carry
verdict prose. If your analyst starts writing beautiful paragraphs, the pipeline
is already reinfected.

## Look for the facts before concluding they are missing

Design corpora usually have a second tier — research notes, ADRs, decision logs,
scratch documents — where the concrete reasoning was written down before being
compressed away. Check it before marking anything undecided.

One example from that corpus: a design doc said a data stream was authoritative
"because it is the vendor's own machine contract", which is circular. The
research note one directory away gave the real reason: a named telemetry
convention had moved to a separate repository at a specific version so that it
could change freely, so the stable choice was to parse the vendor's own output.
Dated, versioned, checkable — and lost in compression. Most of what looks
undecided is recoverable.

## Never invent a mechanism

The rule that protects everything else. A rewriter told "be concrete", with a
gap in front of it, will produce something plausible and wrong.

- Anything undecided gets an explicit marker in the text, never smoothed over.
- Mark it wrong and you cost the author ten seconds. Resolve it wrong and you
  put a decision they never made into their design documents.
- When unsure which it is, mark it.

Watch yourself here too. When illustrating what good prose would look like, it
is easy to supply a concrete detail that feels obviously right and is not in the
corpus at all.

## Two kinds of contradiction

- **Corpus-resolvable** — one statement is checkably wrong, or one word is doing
  two jobs and the documents supply both meanings. Fix these; say which you did.
- **Decision-requiring** — the author has not chosen. Mark both sides with
  file:line, and leave the surrounding prose so it assumes neither.

Do not resolve the second kind, including by picking the version that appears
more often or reads better.

## Everything goes to files

Agent return values are a bad channel: they get lost, they are unverifiable
later, and they fill the orchestrator's context. Have every stage write to disk
and report one summary line.

```text
.rewrite/
  triage.tsv
  facts/<doc>.facts.txt
  drafts/<doc>
  decisions.txt
  DECISIONS-NEEDED.txt
```

This also makes the campaign resumable and lets the author inspect any stage.

## Verify mechanically, not by impression

Every correction you send should rest on a measurement:

- **Scope** — flagged sections rewritten, everything else byte-identical. Diff
  proves it. Beware naive section-detection when nested headings are indented.
- **Growth** — count words with marker text subtracted, so you can tell added
  facts from added padding.
- **Format** — whatever linter the corpus uses, as a gate on every draft.
- **Vocabulary** — grep the banned list against the result, not against your
  memory of the result.

## Expect expansion, and give a number

Every rule in the writing standard pushes toward adding; nothing pushes back.
Expect every agent to over-expand, and put the limit in the brief up front: **if
a section grows by more than about half again, something other than precision is
happening.** Stating this in advance cut the over-expansion rate from seven
agents out of seven to zero.

The usual cause is not padding but misplacement — correct facts, correctly
sourced, in a document that should have cross-referenced their owner.

## Batch questions for the author, and record the answers

The author is the only source for genuinely undecided things, and their time is
the scarce resource. Collect markers into one list with file:line and hand it
over as a single document.

When they answer, write the answers to a decisions file and pass **that** to the
agents as authoritative input. Do not relay decisions conversationally; they get
softened. Number them so a later brief can say "apply D8 only".

Expect answers to arrive as explanations rather than rulings, and expect a good
answer to generate a new, sharper question — that is the sign it was specific
enough to be useful.

## When a decision deletes a claim, fix its citers

A corrected claim with stale citers is a new contradiction you just made. After
any deletion, grep for documents citing the deleted statement. They will be
citing the document you just fixed, as authority for something it no longer
says.

## Let agents refuse you

Brief them so that the standard outranks your instruction, and expect the good
ones to decline. On that corpus, two agents refused parts of a decision I passed
down: one because asserting it would contradict a closed enumeration in a
sibling document, one because the statement belonged to a different document
under the ownership test. Both were right and I was not. An agent that applies
everything you say uncritically will introduce contradictions at your speed.

## What the campaign actually produces

Two artifacts, and the second is usually worth more:

1. The rewritten corpus.
2. **A list of decisions that were never made.** Vague prose conceals absent
   decisions — a sentence that asserts nothing checkable cannot be noticed as
   missing an answer. Expect this list to be long, expect it to include things
   the author will not recognise as ever having been decided, and expect to work
   it with them rather than closing it yourself.
