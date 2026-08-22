---
name: writing
description: >-
  Write descriptions, not meta-analysis. Use whenever producing prose a human or
  another agent will read later — design docs, specs and ADRs, PR descriptions
  and review replies, rustdoc and docstrings, GitHub issue comments, commit
  messages, plans, and status reports — and whenever asked to rewrite, tighten,
  or critique someone else's writing. Prose fails when it states verdicts about
  a design ("the source of truth", "the real contract", "the projection
  outward") instead of naming the actors, mechanisms, and constraints. It reads
  as precise and leaves the reader unable to build the thing or disagree with
  it.
---

# Writing

The reader was not in the conversation that produced this text. Everything the
text assumes and does not say is lost to them. Write so that a competent
stranger can build the thing, check the reasoning, and point at the sentence
they think is wrong.

## The failure: a verdict where a description belongs

Two ways to answer "how was the movie?"

> Tarkovsky post-Godard in a Tarantino-ized post-Marvel world.
>
> Typical save-the-universe multiverse plot. Gratuitous violence played as
> banal, with the characters discussing burgers in the middle of it. Long
> panoramic shots and very slow camera, but the editing is chopped up.

The first is not a compressed version of the second. It is a different act: an
_analysis of_ the movie, not a description of it. It decompresses only for
someone who already shares years of prior — and then it is wonderful, nine words
doing the work of an essay. For everyone else there is nothing in it to unpack,
because the description was never in there to begin with.

Technical prose fails the same way, and the failure hides better because the
vocabulary sounds rigorous.

### Before

> Capture is the session's own result stream: minsky parses the backend's
> structured output — turns, tool calls, spawns, token spend, the terminal
> result — into the one session shape. The harnesses' native otel export runs
> beside it as a second copy, minsky's identity in resource attributes. The
> stream is the source of truth because it is the vendor's own machine contract;
> the export is the projection outward, so records reach other tools without the
> internal model tracking a convention that moves. The store is schema-versioned
> jsonl in the machine-data bucket, with duckdb as a rebuildable index.

Nothing here is checkable. "Source of truth", "machine contract", "the
projection outward", "a convention that moves" are all judgments about a design
whose mechanics were never stated. A reader cannot build this, and a reader who
thinks it is wrong has no sentence to argue with.

### After

> The project runs with no server component, but sessions do not run locally
> either, so the store has to be reachable from anywhere and operated by nobody.
> We use cloud object storage — GCS here; S3 would work the same way.
>
> Object stores have no cheap append and no locking worth relying on. So nothing
> is ever appended or edited: each session writes new objects into the bucket
> and never touches an existing one. Writers only create.
>
> For querying we use DuckDB. It runs entirely in the client, so there is still
> no server to operate, and it reads JSON records directly, which is what our
> records are. It builds indexes at query time, so there is no index to maintain
> or keep in sync. If that gets too slow at our record counts, we add a
> persistent index layer then.

Same length. The difference is not verbosity — it is that every sentence now
carries a fact you could act on or dispute.

## Three tests

Apply these to your own drafts and to documents you are reviewing.

- **The disagreement test.** Could a reader who thinks you are wrong quote the
  sentence they would fight? If not, the text contains no claims — only
  atmosphere. "The stream is the source of truth because it is the vendor's own
  machine contract" cannot be argued with. "We write one object per session
  because GCS has no atomic append" can.
- **The build test.** Could a competent stranger build it, draw it, or call it
  from this alone? A description says what exists. A verdict says how to feel
  about what exists.
- **The cold-reader test.** Does this still decompress for someone who was not
  in the session that produced it? You share an enormous prior with the
  conversation you are in and the reader shares none of it. Text that reads as
  tight while you write it and as empty a week later failed this one.

## Two more tests, once the document has neighbours

The three tests above judge a passage on its own. A document in a set can pass
all three and still be wrong, because both failures below need two places read
together.

- **The ownership test.** Does this section carry facts another document owns,
  or omit facts it owes because it assumed the reader already knew? See
  [Whose fact is it?](#whose-fact-is-it) for how to answer it while writing.
- **The self-consistency test.** Does the document contradict itself, or a
  sibling? Read every claim of the form "exactly N", "only these", "never", "the
  one X" against every other statement about the same thing. Check the glossary
  case too: one word used for two objects with the distinction never drawn is
  the same defect wearing a disguise.

The second test matters more than it sounds. Verdict prose _hides_
contradictions: when a sentence asserts nothing checkable, the sentence
contradicting it does not collide with anything, so both survive. Measured on
one corpus, a re-read that added just these two tests overturned every one of
eleven documents that had passed the first three — including a document
asserting "Kent is stateless" and "kent owns state" eight lines apart, in a
section titled "State".

**A contradiction between two vague statements is usually a missing distinction,
not a disagreement.** When the author of that corpus went through the
contradictions this test found, not once was one side right and the other wrong.
"State" turned out to be three things — data held elsewhere, a config file never
mutated, and one small mutable thing. "Artifact" was one object with two roles.
"Path-pure, no network" was a garbled way of saying "runs on your laptop". Both
halves were true and about different things, and the abstraction had hidden
that. So when you find one, do not pick a winner: look for the distinction
neither sentence draws.

What that pass found, almost entirely, was flat factual contradiction: "exactly
two workflow files" against "a further generated caller per trigger"; "one build
yields many artifacts" against "artifacts exist only on the release side"; two
commands each documented as doing the same setup step; a document claiming to
own a model it never states. None of it is a matter of taste, and none of it is
visible one sentence at a time.

## The shape that works

Goal and constraints, then the concrete choice, then what it costs and what it
defers.

1. **What are we trying to do, and what bounds it.** No server. Not local
   either. Reachable from anywhere.
2. **What we picked, named specifically.** GCS. DuckDB. Not "cloud-native
   storage" or "a client-side query layer".
3. **Why the constraints force it,** so the reader can disagree with the link
   rather than the conclusion.
4. **What it costs, and what is deferred,** stated as deferred: "no persistent
   index until query time gets slow".

Constraints first is what builds the mental model. Give people the problem
before the answer and the answer explains itself; give them the answer alone and
they memorize it without understanding it.

## Whose fact is it?

Concreteness has a direction, and it will run away with you. Every rule above
pushes toward adding — name the mechanism, price the tradeoff, state the
constraint. Nothing above pushes back, so a rewrite guided only by those rules
grows without limit and drifts upward in detail until an overview is explaining
a cache layer.

The governor is ownership. **Before adding a fact, ask whether this document
owns it, or defers to one that does.** When the mechanism lives elsewhere, the
cross-reference _is_ the concrete answer — a pointer to the owner is not a
vaguer sentence, it is the correct one.

- An overview is navigated from, not built from. It names what is optimized and
  points at the doc that owns each mechanism.
- A command reference says what each verb does. The policy about when to reach
  for that verb belongs to the doc that owns the model.
- A stack or build-vs-buy doc argues the choice. The shape of the data flowing
  through it belongs to the data-model doc.

The test that catches this: read the heading, then ask what a reader who opened
_this_ document came for. Facts they came for, state. Facts they would go
elsewhere for, cite.

Judgments are welcome — after the description, next to the fact that earns them.
"Slow editing" is a fine thing to say once you have said the shots are long.
Judgment instead of description is the failure; judgment on top of it is the
point.

## Sentence mechanics

**Give every sentence an actor and a verb.** The subject should be a program, a
person, a file, a command, a request — something that does things. Abstract
subjects are where descriptions go to die.

- Bad: "Capture is the session's own result stream."
- Good: "minsky reads the backend's stdout and writes one JSON record per
  session."

**Name real things.** `gcs`, `DuckDB`, `session.jsonl`, `parse_turns()`, HTTP
429 — not "the store", "the query layer", "the projection outward".

**Every adjective needs a fact behind it.** "Robust", "principled", "clean",
"first-class", "rich" assert quality without evidence. Either delete them or
state the fact that would make a reader say it unprompted.

**One claim per sentence.** Three claims packed into one sentence read as dense
and land as none. "Evals gate a harness change and draw on that same pool, so
evaluation competes with development and suite size is a design constraint" is
four claims and no picture. Split it, or cut to the one that matters.

**Name the thing, not its category.** _Pool, surface, layer, model, constraint,
competition_ are categories. A sentence whose every noun is a category has
nothing in it to see. "Evaluation competes with development" names no actor and
no resource; "running the suite spends the tokens the fleet is developing on"
names both.

**Give the property to the thing that has it.** "A session is the durable unit"
attributes durability to an entity in a model; what is actually durable is the
mounted disk the session writes to. The session dies with its container. Ask
which concrete thing provides the property, and say that instead — the entity
usually turns out not to have it.

**State what a rule buys, not only what it forbids.** "Github never computes"
tells a reader what does not happen and leaves the benefit to be inferred. "A
workflow calls a task that runs the same on your laptop, so a CI change is
tested before it is pushed" gives the rule and its reason together. Prohibitions
are cheap to write and leave the reader to reconstruct the point.

**Not every sentence is an argument.** A goals list states goals. A command
reference says what a verb does. Compressing an argument into a goal statement
is altitude drift wearing the costume of rigor — the argument belongs to the doc
that owns it, and the goal should just be stated plainly.

**Price every tradeoff.** "Cheap", "expensive", "doesn't scale", "costs a
serializer" are gestures at an argument. Say how much of what, measured or
estimated how.

## Tells

Recognizable patterns. Each one has a mechanical fix.

| Tell                     | Looks like                                                        | Fix                                                   |
| ------------------------ | ----------------------------------------------------------------- | ----------------------------------------------------- |
| **The verdict noun**     | source of truth, the real contract, the one shape, the projection | State the mechanism the verdict is about              |
| **The abstract subject** | "Capture is…", "Adoption would…", "The export is…"                | Find the actor; make it the subject                   |
| **Balanced antithesis**  | "A is X because Y; B is Z, so W" — three times in a paragraph     | Fine when both halves carry facts; suspicious in bulk |
| **Unpriced tradeoff**    | "costs a serializer", "doesn't scale"                             | Give the number, or the mechanism that produces it    |
| **Unearned adjective**   | robust, first-class, ergonomic, principled                        | Delete, or replace with the fact                      |
| **Orphan instance**      | one specific record type dropped into a general section           | Move it to where instances belong, or label it        |
| **Deliberation residue** | what you considered, in the order you considered it               | Keep the conclusion and the reason; drop the search   |
| **Altitude drift**       | section titled "Stack" arguing design philosophy                  | Read the heading, then the paragraph — same level?    |

Deliberation residue and altitude drift are the two that survive every
word-level cleanup, so check them explicitly. Write in the order the reader
needs, not the order you figured it out in.

## What the reader needs, per medium

Ask first: who reads this, and what are they about to do with it?

- **Design doc / spec / ADR.** The reader is deciding whether to agree, or
  building from it. Goal, constraints, the concrete choice, why the constraints
  force it, what is deferred. Not a defense of the choice.
- **PR description.** The reader is reviewing. What changed in the code, what
  problem it fixes, what to look at hardest, how to verify it. Not "improves
  ergonomics of the retry path".
- **rustdoc / docstring.** The reader is calling this function right now. What
  it does, what it takes, what it returns, when it fails or panics, ordering and
  edge behavior, one example. Not "a robust abstraction over the session store".
- **Issue reply / review comment.** The reader wants an answer. The answer, the
  evidence for it, the next action. Lead with the answer.
- **Commit message.** What changed and why, in terms the person running
  `git log` in a year can use.
- **Status report.** What is done, what is not, what is blocked and on whom.
  Progress adjectives ("solid progress", "mostly there") say nothing.

## Before you finish

A five-step pass over any draft:

1. Look at each sentence's subject. Not a person, program, file, or command?
   Rewrite it.
2. Mark each claim as fact or verdict. Every verdict needs an adjacent fact.
3. Find the constraints. If the text says what you chose but not what forced it,
   add it.
4. Read each heading, then its paragraph. Same altitude?
5. For each fact you added, ask whether this document owns it. If another doc
   does, replace the explanation with a cross-reference.
6. Run the word check — see `dejargon` below. Every test above passes sentences
   built on metaphor, so this is a separate pass, not a side effect.
7. Grep your own absolutes — "exactly", "only", "never", "the one" — and read
   each against everything else said about the same thing, in this document and
   its siblings.
8. If you deleted or corrected a claim, grep for the documents that cite it. A
   corrected claim with stale citers is a new contradiction you just made.
9. Run the disagreement test on the whole piece.

## Calibration

**Concrete is not longer.** The rewrite above is the same length as the
original. You are replacing verdicts with facts, not padding. If a section grows
by more than about half again, something other than precision is happening —
usually facts that belong to a neighbouring document.

**Concrete is not remedial.** Specific means naming the actual thing, not
explaining what an object store is to people who ship them.

**Shared vocabulary is allowed once it is defined.** A term the doc set defines,
or a name printed by the tool itself, is a name and not a metaphor. Use it. The
failure is compression against a prior the reader does not have — not
compression as such.

**Do not rewrite the user's own words back at them.** Answer what they asked;
apply this to your own prose.

## Repairing an existing corpus

Everything above is about writing a document. Repairing a set of documents
someone else already wrote is a different job with its own failure modes —
scoring without priming the scorers, keeping the rewriting agent away from the
prose it is replacing, marking what is undecided instead of inventing it, and
handing the author the decisions the vague prose was concealing.

Read [references/fixing-a-corpus.md](references/fixing-a-corpus.md) when the
task is a doc set, a spec tree, a handbook or a wiki rather than one document.
Not needed for ordinary writing; skip it unless you are repairing at scale.

## Related skills

- `dejargon` — the word level: vague mechanical metaphors (gate, leg, pin,
  load-bearing, surface, mint, ride) swapped for the concrete actor and
  mechanism. Its list does not cover abstract **verbs and adjectives** that name
  a change or a quality without naming what changed or what provides it —
  _converge, materialize, reconcile, durable, doctrine_. Those pass both skills:
  the sentence has an actor and a verb, and the word is not a mechanical
  metaphor. Watch for them yourself. **The two skills do not substitute for each
  other in either direction, and you must run both.** Text passes dejargon
  cleanly and is still pure verdict; text passes every test in this skill —
  naming actors, arguable, buildable-from — and is still built on metaphor.
  Measured on one corpus: a rewrite done to this standard alone left 60 banned
  and watchlist words standing across 14 documents, 7 of them `gate`, some in
  sentences written during that very rewrite.
- `slop-clean` — removing session sediment (dates, provenance, verification
  narration) from text already committed.
