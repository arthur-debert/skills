---
name: writing-documentation
description: >-
  Structure a project's documentation — README, architecture docs, component
  docs, specs — as why/what/how roles scaled to the project's actual size. Use
  when writing or reorganizing a README or doc set, when deciding whether a
  document should be split or merged, or when reviewing docs that open by
  describing themselves instead of the system. Documentation fails structurally
  when every project gets three mandatory doc levels regardless of size, when a
  doc's first paragraph is about the document, when a component doc re-litigates
  architecture, or when the task prompt leaks into the text as negations of
  things nobody proposed. Sentence-level prose failure is the `writing` skill;
  run both.
---

# Writing Documentation

_Which documents a project has, which facts each one states, and the order a
reader meets them in. The sentence level is the `writing` skill; run both._

## Three questions, not three files

Every documentation set answers three questions:

- **Why, and for whom.** What problem the system solves, who uses it, what it
  refuses to do. The reader is deciding whether this project is relevant to them
  at all.
- **What.** The architecture: the parts, what each part is responsible for, and
  how they communicate. The reader is picturing the parts and their connections
  before touching code.
- **How.** The internals of one part: file formats, schemas, algorithms, exact
  command behavior. The reader is implementing or debugging that part right now.

The _what_ role includes how the parts relate to each other — a document that
exhaustively lists what each part is responsible for and never says how they
connect has answered half its question. The _why_ role for a runnable system
includes the reader's first action. And the reader's questions are the
organizing scheme: a doc organized entirely as a charter — owns, does not own,
vocabulary — serves the maintainer's boundary disputes; a scope section can live
inside a reader-organized doc, but cannot replace the usage and relations the
reader came for.

These are **roles a document plays, not a required file count.** The number of
documents follows from how much material the project actually has:

- **A few kloc** (a CLI tool, a shell script collection): one README plays all
  three roles in three or four sections. Creating an `architecture.md` here
  produces a file with two paragraphs in it and a reader who opened two files to
  learn one thing.
- **Tens to low hundreds of kloc** — the common case: a README that answers
  _why_ and _what_, plus one doc per subsystem that has earned it. A subsystem
  earns a doc when its internals outgrow a section, not because the taxonomy has
  a slot for it.
- **Only a genuinely large system** needs the full recursive tree — a root doc,
  per-subsystem architecture docs, per-component design docs — and even there
  the tree only propagates as deep as the material does. A leaf component with a
  page of internals gets a page, not a directory.

The trigger to split is always the same: **a document outgrew one sitting
(around 200 lines), so extract the deepest material into a child and leave a
summary and a link.** Split by pushing detail down, never by cloning a level of
the tree. The inverse rule holds too: a document that would be under a screenful
is a section of its parent, not a file.

When a correctly-sized document carries material that is too deep for its role —
store-transport internals in a README — and no child doc exists to receive it,
the fix is to cut the depth down to its one-line summary, not to open a child.
The detail sat a level below its heading; it becomes a child doc only when there
is a screenful of it.

## Open with the system, not the document

The opening block — everything before the first section heading — tells a
stranger what the system is, what it does, and for whom, with at least one
concrete, named thing in it: a command, a config file, an input and its output.
If the system is runnable, the opening also shows the reader's first action: the
command they type or the file they write. No sentence in the opening block is
about the _document_, because the reader came to learn about the system and does
not yet care how its documentation is organized. Burying the self-description in
paragraph three instead of paragraph one does not satisfy this rule.

### Before — a real README opening

> This file is the charter: what missio owns, what it does not, and the words it
> defines. A fact that fits none of the three does not belong in this repo.

Every noun here is about the file. A reader who does not know what missio is —
the only reader a README opening exists for — finishes the paragraph still not
knowing. Worse, agents ingest this register and re-emit it, so the style
propagates.

### After

> Missio is a terminal application that fully provisions sandboxed containers —
> OS-level dependencies, secrets, configuration injection — driven by a
> declarative config file in the user's repo.
>
> In missio.toml, a repo declares blocks: reusable, composable infrastructure
> components missio knows how to handle. The rust block, for example, tells
> missio to install the Rust toolchain, that code lives under crates/, and that
> cargo test and cargo build are the test and build commands.

Same length. The difference is the subject: the system doing things, not the
document classifying things.

The ban is not confined to the opening. Anywhere in the document, a sentence
whose subject is the file, its sections, or its words — "each entry states a
contract," "these words mean here what this repo says they mean" — is talking
about the document instead of the system, and goes. The two exceptions: the
scoping subtitle, and a prerequisite link at the top.

A deeper doc (a subsystem or component doc) does state its own scope — but as
the one-line subtitle under the title, never as the opening prose.

## Self-evident headlines

Every document starts with a title and a one-to-two sentence subtitle that
scopes it. A reader scanning the docs directory decides from the subtitle alone
whether to open the file.

- Bad: `Data_Format.md`
- Good: `Plaintext_Markup_Grammar.md` — _the AST structure and parsing rules for
  the custom document format._

For the root README, the first sentence of the opening block _is_ the subtitle —
"Missio is a terminal application that fully provisions sandboxed containers…"
scopes the document by scoping the system, and a separate subtitle would repeat
it. The subtitle-as-its-own-slot rule is for the documents a reader scans in a
directory.

## Detail flows down, decisions don't flow up

A document inherits the decisions of the level above it and never restates or
overrides them:

- A component doc describes its internals _within_ the architecture. If the
  architecture doc says stages chain through a store, the store-transport doc
  does not introduce an event bus — and if writing the component doc convinces
  you the architecture is wrong, change the architecture doc, don't fork it
  locally.
- The same rule points up: the README does not carry schemas, and the
  architecture doc does not carry parsing grammars. When a fact belongs to a
  deeper doc, the cross-reference _is_ the correct sentence — see `writing` on
  which document states a fact.

## Define terms where the reader meets them

The reader starts at the top of the doc set and reads downward; nothing may
require a forward jump. Concretely:

- Every project-coined term is defined at first use, in the sentence that uses
  it or the one before. "The contract defines the seams" is unreadable when
  neither _contract_ nor _seam_ has been given a meaning in this project — two
  abstractions multiplying, not explaining.
- If a document requires another document first, it says so in its subtitle
  ("assumes the architecture overview") — one link at the top, not scattered
  prerequisites.
- A glossary does not license undefined use. A term defined only in a glossary
  the reader hasn't opened is an undefined term. The `writing` skill's
  coined-terms decode test applies to every recurring one.
- A glossary entry is a definition or it is deleted. A vocabulary section that
  lists bare words — "stage, store, key, transport" — defines nothing; it claims
  fourteen terms as the project's vocabulary while leaving all fourteen
  undefined.

## No task residue

Documentation describes what the system **is**. The session that produced the
text — its instructions, its rejected alternatives, its chain of thought — must
not be recoverable from it.

The telltale is the unmotivated negation: the task said "do not use X," and the
doc now says "foo is not X" — "signing is never a stage," "a workflow computes
nothing," "never a container a job archives." A negative claim earns its place
only when a reader would plausibly assume the alternative _and_ the doc says
what the reader gets instead: "workflows only call commands, so every CI step
can be run and tested locally" documents a property; "a workflow computes
nothing" documents an instruction someone once gave the author.

A scope section — "what this project does not do" — is legitimate; the why-role
includes refusals. The license covers the section, not its sentences: each entry
still owes the reader which project or component handles the refused thing, or
what the reader gets instead. "Update resolves; fetch never does" passes — it
prices a plausible assumption and pairs the negation with the positive half.
"Declared nowhere" alone does not.

Two calibrations. A negation sharing its sentence with the positive half it
prices passes; a negation that only restates the previous clause in negative
form ("nothing in its model sits above the repo," after the clause already said
it resolves everything from the checkout in front of it) is redundancy — cut it
as repetition, not as a leaked instruction. And a sentence arguing why the
document breaks one of these rules ("none of them names who is on the other
side, because…") is itself a trace of the authoring session: the rationale
documents the authoring policy, and does not waive the rule.

Even a licensed negation is rationed, because negations carry a cost specific to
the reader that is an agent: the words stick to context, and over a long session
"never watches the filesystem" keeps _watching the filesystem_ in the agent's
attention — a NOT can steer generation toward the thing it bans. There is also
an infinite supply of true ones. State the few non-goals a reader would
plausibly assume, and stop.

The same applies to options listed in the order they were considered, and to
dates, provenance and verification narration: see `writing` and `slop-clean`.

## Specs

A spec is the why and the what for one feature: the problem or opportunity, for
whom, and how the system will behave to that user. It is also what the finished
work is checked against — the standing answer to "did we build the right thing"
— and that acceptance role, not description of a built system, is what gives it
its own rules.

**Shape.** The problem or opportunity first: what the user cannot do today, or
does painfully. Then the solution in plain English — "lets the user choose the
model that runs the session instead of one static universal choice" — before any
mechanism. Then the interaction: the commands with their main arguments and
outputs, the config file, the GUI flow; a feature often has several, which is
fine. Limitations and assumptions where relevant, priced. Touch points with the
rest of the system named and deferred: "requires an authenticated account" is
the whole sentence — login has its own doc.

**Behavior by class, not enumeration.** The full behavior under every condition
is literally what the finished code is, and the spec is not that. Describe the
common behavior, then the _classes_ of errors and limitations. Enumerate
individual variants only when the set is small — around three; past that,
enumeration is waste pretending to be rigor.

**Not exhaustive, still authoritative.** The spec does not contain all the
answers; it contains the ideas later answers are derived from and judged
against. Implementation internals — which cloud provider, which encryption
algorithm — belong to an implementation overview, not here. For developer tools
the user is a developer, so commands, APIs, and file formats _are_ the user
experience: the border is what the user touches, not how technical the fact is.

**Size.** Around 100 lines of prose; 300 is far too much. This is stricter than
the general ~200-line split trigger, and the remedy differs too: an oversized
spec is usually several features wearing one name — split it into multiple specs
(you don't write one spec for a spreadsheet), never into a level of child docs.

**Non-goals** follow the negation rules above, including the ration: name the
assumptions a reader would actually make, and stop.

**A meta channel for the agent.** Context about the spec itself — "this is a
sample," "this extends the questionnaire feature," guidance for the implementing
agent — goes in marked comments (in Lex, `:: note ::` lines), never in the body.
The meta channel is the designated home for exactly the material that otherwise
leaks into the text as residue.

## When writing a document

1. **Place it.** Which of the three questions does it answer, and what is its
   parent? If the answer is "all three," check the size — that usually means
   it's the README of a small project, which is fine.
2. **Open with the system.** First paragraph: what it is, does, for whom, with a
   named concrete thing in it.
3. **Headline it.** Title plus scoping subtitle.
4. **Check the borders.** Nothing in the draft overrides its parent; nothing in
   it belongs to a child. Cross-reference instead of restating.
5. **Split on overflow only.** Past ~200 lines, push the deepest section down
   into a child doc with a summary and link left behind. Never open a child doc
   for less than a screenful.
6. **Reread for negations and undefined terms.** Every negation must price a
   real alternative; no term used before it's defined.
7. **Then run `writing`'s final pass** on the prose itself.

## Related skills

- `writing` — the sentence level: descriptions not verdicts, actors as subjects,
  coined terms, which document states each fact, and self-consistency across a
  doc set. Always run alongside this skill.
- `dejargon` — the word level: mechanical metaphors swapped for concrete actors
  and mechanisms.
- `slop-clean` — removing session sediment from text already committed.
- `lex-primer` — when the target file is `.lex`, load it for syntax; Lex is not
  Markdown.
