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

The agent loads this skill before writing prose that outlives the conversation
(a design doc, spec, ADR, PR description, review reply, docstring, issue
comment, commit message, plan or status report) and when asked to rewrite or
critique text. The reader is a competent stranger who took no part in the
conversation that produced the text. The agent writes so that stranger can build
the thing, check the reasoning, and point at the sentence they think is wrong.
Anything the text assumes but does not say, that reader loses.

## The failure: a verdict where a description belongs

A verdict is a judgment about the thing. A description says what exists: the
actor, the mechanism, the constraint. The failure is a verdict with no fact
beside it.

Two answers to "what is the film like?":

> Tarkovsky post-Godard in a Tarantino-ized post-Marvel world.
>
> Typical save-the-universe multiverse plot. Gratuitous violence played as
> banal, with the characters discussing burgers in the middle of it. Long
> panoramic shots and very slow camera, but the editing is chopped up.

The first is not a compressed form of the second. A reader spots a software
verdict less easily than the film verdict: "schema-versioned jsonl" and "the
vendor's own machine contract" sound rigorous.

### Before

> Capture is the session's own result stream: minsky parses the backend's
> structured output — turns, tool calls, spawns, token spend, the terminal
> result — into the one session shape. The harnesses' native otel export runs
> beside it as a second copy, minsky's identity in resource attributes. The
> stream is the source of truth because it is the vendor's own machine contract;
> the export is the projection outward, so records reach other tools without the
> internal model tracking a convention that moves. The store is schema-versioned
> jsonl in the machine-data bucket, with duckdb as a rebuildable index.

A reader can neither check, build from, nor argue with any sentence in it.

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

The After is the same length as the Before; the difference is facts in place of
verdicts, not padding. Every sentence in the After states something the reader
can act on or dispute.

## Three tests

The agent runs these on its drafts and on documents it reviews.

1. **Disagreement test.** Trigger: any paragraph. Action: ask whether a reader
   who thinks the text is wrong could quote the sentence they would fight. If
   not, the text has no claims. "The stream is the source of truth because it is
   the vendor's own machine contract" fails. "We write one object per session
   because GCS has no atomic append" passes.
2. **Build test.** Trigger: any description of a system. Action: ask whether a
   competent stranger could build, draw or call the thing from this text alone.
3. **Cold-reader test.** Trigger: any draft written inside a conversation.
   Action: ask whether the text decompresses for someone absent from that
   conversation. Text that reads as tight while written and as empty a week
   later fails.

## Two more tests, once the document has neighbours

Tests 4 and 5 compare a passage with its neighbours; a passage read alone cannot
fail them. A document **owns** a fact when it is the place that fact is stated;
every other document cites it there.

- **Test 4, which-document.** Trigger: a section in a document with siblings.
  Action: ask whether it states facts another document owns, or omits facts it
  owns because it assumed the reader knows them. To answer while writing, read
  the heading and ask what a reader who opened this document came for.
- **Test 5, self-consistency.** Trigger: any claim of the form "exactly N",
  "only these", "never", "the one X". Action: read it against every other
  statement about the same thing in this document and its siblings. One word
  used for two objects with the distinction never drawn is the same failure
  (`writing-documentation/SKILL.md`, Define terms where the reader meets them).

A sentence that asserts nothing checkable does not collide with the sentence
contradicting it, so both survive. When two vague statements contradict, the
agent does not pick a winner; it looks for the distinction neither sentence
draws.

## The shape that works

A design section, in this order:

1. The goal and what bounds it.
2. The pick, named specifically: GCS, DuckDB, not "cloud-native storage".
3. Why the constraints force it.
4. What it costs and what is deferred, stated as deferred: "no persistent index
   until query time gets slow".

The agent writes the constraints before the pick because a reader given the
problem understands the answer; a reader given the answer alone memorizes it.

## Whose fact is it?

Every test except the which-document test adds a fact; that one is the only
check that removes. An agent running only the adding tests lengthens every
document until an overview explains a cache its component document describes.

Before adding a fact, the agent asks whether this document owns it. When the
mechanism lives elsewhere, the agent writes the cross-reference, which is the
concrete answer, not a vaguer one (`writing-documentation/SKILL.md`, Detail
flows down, decisions don't flow up; `slop-clean/SKILL.md`, Pass 2).

Which document states which fact:

- An overview names what is optimized and points at the document for each
  mechanism.
- A command reference says what each verb does. When to use the verb belongs to
  the document that describes the system's conceptual model.
- A stack or build-vs-buy document argues the choice. The shape of the data
  belongs to the data-model document.

To choose between stating and citing, the agent reads the heading and asks what
a reader who opened this document came for. It states those facts and cites the
ones they would go elsewhere for.

A judgment stays when the fact that earns it is on the page beside it: "slow
editing" once the text has said the shots are long.

## Sentence mechanics

- **Abstract subject.** Make an actor the subject: a program, a person, a file,
  a command, a request. Bad: "Capture is the session's own result stream." Good:
  "minsky, the capture program in the Before exemplar, reads the backend's
  stdout and writes one JSON record per session."
- **"The store", "the query layer", "the projection outward".** Write the real
  thing: `gcs`, `DuckDB`, `session.jsonl`, `parse_turns()`, HTTP 429.
- **"Robust", "principled", "clean", "first-class", "rich".** Delete the
  adjective, or state the fact that would make a reader say it unprompted
  (`dejargon/SKILL.md`, The watchlist).
- **Several claims in one sentence.** One claim per sentence, or cut to the one
  that matters. "Evals gate a harness change and draw on that same pool, so
  evaluation competes with development and suite size is a design constraint" is
  four claims and no picture.
- **Category nouns (pool, surface, layer, model, constraint, competition).**
  Name the thing.
- **A property attributed to an entity in the system's model.** Name the
  concrete thing that provides the property.
- **A rule stated as a prohibition.** State what the rule buys alongside what it
  forbids. Bad: "Github never computes." Good: "A workflow calls a task that
  runs the same on your laptop, so a CI change is tested before it is pushed."
  `writing-documentation/SKILL.md`, No task residue, states the same rule.
- **"Cheap", "expensive", "doesn't scale", "costs a serializer".** Say how much
  of what, measured or estimated how.

Not every sentence argues. A goals list states goals; a command reference says
what a verb does. The reason for a choice goes in the design doc; a goals list
that states the reason sits at a different level of detail than its heading.

## Coined terms

A coined term is a project-private word coined for one apt use (mint for issuing
an identifier, fold for a typed merge). It spreads because reusing the word is
always cheaper than naming the actual operation, until its meaning is the union
of its uses and empty. Coinages then compose ("the fold mints build identities")
and one sentence needs two private decoders.
`writing/references/fixing-a-corpus.md`, Separate the reader from the writer,
says why the drift does not stop.

The agent keeps a recurring term when either holds:

- It is a real external term: APIs, commands or other people's docs reference
  it.
- It is defined where the reader meets it: the defining clause is on the page,
  or the use glosses itself ("the rate allowance — the one subscription pool
  every session draws on").

A term the project's own CLI prints keeps the printed spelling, and each use
says which thing it names at that site ("the `runtime` container", "the
extracted runtime installation"): `dejargon/SKILL.md`, Boundaries, "clarify the
prose around it". The decode test below still applies to the prose around it.

**Decode test.** Trigger: a term that recurs across a document or corpus.
Action: replace it at every site with what it concretely means there and count
the distinct words needed. One or two: it is a name; keep it. Two decoded
meanings are a name only when the text draws the distinction between them;
otherwise the term is one word for two objects. Three or more: replace it at
every site with the meaning at that site.

## Tells

| Tell                                                                                                            | Action                                                                                                                                    |
| --------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Verdict noun: "source of truth", "the real contract", "the one shape", "the projection"                         | State the mechanism the verdict is about.                                                                                                 |
| Abstract subject: "Capture is...", "Adoption would...", "The export is..."                                      | Find the actor and make it the subject.                                                                                                   |
| The same "A is X because Y; B is Z, so W" shape repeated in a paragraph                                         | Leave it when both halves state facts. Not yet decided: how many repetitions in one paragraph trigger a rewrite, and what the rewrite is. |
| Unpriced tradeoff: "costs a serializer", "doesn't scale"                                                        | Give the number, or the mechanism that produces it.                                                                                       |
| Unearned adjective: robust, first-class, ergonomic, principled                                                  | Delete it, or add beside it the fact that earns it.                                                                                       |
| Orphan instance: one specific record type dropped into a general section                                        | Move it to where instances belong, or label it.                                                                                           |
| What the writer considered, in the order considered                                                             | Keep the conclusion and the reason; drop the search.                                                                                      |
| A paragraph at a different level of detail than its heading: a section titled "Stack" arguing design philosophy | Read the heading, then the paragraph; check they match.                                                                                   |

A word-level cleanup does not catch a narrated search or a paragraph at the
wrong level of detail, so the agent reads each heading against its paragraph,
cuts the search by hand, and writes in the order the reader needs, not the order
the agent figured it out.

## What the reader needs, per medium

The agent asks who reads this and what they will do with it.

- **Design doc or ADR.** Goal, constraints, the concrete choice, why the
  constraints force it, what is deferred. Not a defense: the reader is deciding
  whether to agree, or building.
- **Product spec.** The problem and for whom, the solution in plain English, the
  common behavior and its error classes, the interaction (commands, config,
  flow). The constraint-forced choice belongs to the design doc;
  `writing-documentation/SKILL.md`, Specs, states shape, size and non-goals.
- **PR description.** What changed in the code, what problem it fixes, what to
  look at hardest, how to verify it. Not "improves ergonomics of the retry
  path".
- **Rustdoc or docstring.** What it does, what it takes, what it returns, when
  it fails or panics, ordering and edge behavior, one example. Not "a robust
  abstraction over the session store".
- **Issue reply or review comment.** Answer, then evidence, then next action.
- **Commit message.** What changed and why, usable by someone running `git log`
  in a year.
- **Status report.** What is done, what is not, what is blocked and on whom.
  "Solid progress" and "mostly there" say nothing.

## Before you finish

The agent runs nine steps on the finished draft:

1. Look at each sentence's subject. If it is not a program, a person, a file, a
   command, a request, rewrite it.
2. Mark each claim as fact or verdict. Every verdict needs an adjacent fact.
3. Find the constraints. If the text says the choice but not what forced it, add
   what forced it.
4. Read each heading, then its paragraph, and check they are at the same level
   of detail (`writing-documentation/SKILL.md`, Three questions, not three
   files).
5. For each fact added, ask whether this document owns it. If another document
   does, replace the explanation with a cross-reference.
6. Run the dejargon word check as a separate pass; every test here passes
   sentences built on metaphor.
7. Grep the draft's absolutes ("exactly", "only", "never", "the one") and read
   each against everything else said about the same thing here and in the
   siblings.
8. After deleting or correcting a claim, grep for the documents that cite it
   (`writing/references/fixing-a-corpus.md`, When a decision deletes a claim,
   fix its citers).
9. Run the disagreement test on the whole piece.

## Calibration

- The agent aims for the same length as the original; a section that grows past
  about half again is taking on facts a neighbouring document owns
  (`writing/references/fixing-a-corpus.md`, Expect expansion, and give a
  number).
- The agent names the actual thing; it does not explain what an object store is
  to people who ship them.
- The agent keeps a project term when it is an external term or defined where
  the reader meets it.
- A short sentence is fine when the reader can expand it from what is on the
  page; it fails when expanding it needs the conversation the reader took no
  part in.
- The agent does not rewrite the user's own words back at them; it answers the
  question and applies this skill to its own prose (`dejargon/SKILL.md`,
  Boundaries).

## Repairing an existing corpus

When the task is a doc set, a spec tree, a handbook or a wiki, the agent reads
`writing/references/fixing-a-corpus.md` first. It covers scoring without priming
the scorers, keeping the rewriting agent away from the prose it replaces,
marking what is undecided instead of inventing it, and handing the author the
decisions the vague prose concealed.

## Related skills

- **dejargon** works at the word level: it swaps vague mechanical metaphors
  (gate, leg, pin, load-bearing, surface, mint, ride) for the concrete actor and
  mechanism (`dejargon/SKILL.md`, The banned words and The watchlist).
- **Both skills run.** Text can pass dejargon and be pure verdict; text can pass
  every test here and be built on metaphor.
- **Words that pass both:** abstract verbs, adjectives and nouns that name a
  change or quality without naming what changed or what provides it (converge,
  materialize, reconcile, durable, doctrine). The agent watches for them.
- **slop-clean** removes dates, provenance and verification narration from text
  under source control (`slop-clean/SKILL.md`, Pass 1).
