---
name: interface-first
description:
  Decide whether a feature's interface should land as its own workstream ahead
  of the implementation, and how to build one when it does. Use when slicing a
  spec into an epic and workstreams; whenever a decomposition introduces a new
  data model, schema, API, or contact surface between repos, teams, or parallel
  workstreams; whenever several workstreams would build against the same new
  interface at once; whenever a plan proposes contract, stub, or scaffold
  phases; when implementing a workstream whose job is shapes rather than
  behavior; and before adding filesystem, network, clock, or environment access
  to core logic. Read it also to decide when NOT to slice a feature this way —
  vertical slices remain the default and this is the exception.
---

# Interface-First

An interface workstream is one pull request holding the feature's types, schemas
and public signatures with every function body stubbed, merged before any pull
request that holds a body. Section "10. Decomposition" of
`docs/430-handbook-planning.lex` in the edward-legacy repository (lines 128-132)
sizes a workstream as one reviewable pull request built as a vertical slice,
makes the walking skeleton the first workstream, and, when the interface is the
risk, merges the interface first in its own workstream with every body stubbed,
then the skeleton, then the slices. Section "7. Across Repos" of the same
repository's `docs/440-handbook-epics.lex` (lines 59-73) covers an interface
shared by two repos.

A reviewer of a diff that holds only types and signatures reads the data model,
the signatures and the module layout, because the diff holds nothing else.
Workstreams that start after that diff merges build against one set of types;
line 136 of the 430 handbook gives the reason: "Whatever they share is what they
drift on."

## When to create an interface workstream

1. **Trigger:** any one of the three conditions in the 430 handbook, lines
   134-138: several workstreams build against the same new interface at once,
   the interface is built by two independent parties (different repos, teams, or
   a provider and a consumer), or the data model is the decision whose reversal
   reworks everything downstream. **Action:** create the interface workstream.
2. **Trigger:** the feature is one workstream, or a few that share nothing.
   **Action:** no interface workstream; build vertical slices.
3. **Trigger:** nobody has implemented anything behind the interface yet.
   **Action:** prototype, discard it, then write the interface from what the
   prototype taught (430 handbook, line 140).
4. **Trigger:** the interface is one function, or one struct with about three
   fields. **Action:** put it in the first vertical slice.
5. **Trigger:** none of rules 1-4 matches. **Action:** apply the counter-test at
   line 140 of the 430 handbook: would a reviewer of the interface alone have
   anything to argue with? If only one shape fits the problem, the reviewer has
   nothing to argue with, and the interface goes into the first vertical slice
   as in rule 4.

   Not yet decided: which rule applies when a struct of about three fields is
   also the decision whose reversal reworks everything downstream.

6. **Trigger:** the interface crosses repos. **Action:** classify the dependency
   per the 440 handbook, section 7, lines 63-72. Sequencing (one side needs
   something the other has shipped) only orders the workstreams. Integration
   (new endpoints, data structures or message formats between the repos) has the
   provider merge endpoints, types and schemas with no behavior behind them
   before either side implements.

## Scoping the workstream

The interface workstream contains:

- Data types, schemas, enums and error types.
- Public signatures for every module the feature touches, including the I/O
  modules, so the file layout exists and is named.
- Doc comments on each public type and signature stating its invariants,
  ordering constraints and error modes (the codebase-design skill's definition
  of interface).
- Tests on the data types only: construction, defaults, serialization
  round-trips, validation.

It contains no behavior. Every function body that will later hold logic is a
stub.

The ticket's acceptance criteria:

- The package compiles or type-checks and the existing test suite passes.
- Every logic-bearing body raises a loud stub; none returns a silent default.
- Data-type tests pass; no test asserts behavior that does not exist.
- The PR description lists the decisions a reviewer should push back on before
  anything is built against them.

A walking skeleton is the thinnest working path end to end and answers "does one
request pass through every module". An interface workstream is every type and
signature with no body working and answers "is this the right shape". An epic
that needs both answers takes the interface first, the skeleton as the first
slice through it, then the remaining workstreams in parallel (430 handbook,
lines 130-132).

The `contract-phase` eval in `evals/evals.json` (lines 4-21) shows the scope for
a feed digest: entry, per-feed group, digest and settings defined as types; the
window and the per-feed cap passed in as configuration values, not read from the
environment; every function that will hold logic raising `NotImplementedError`;
no `httpx`, `open()`, `os.environ` or `datetime.now()` in the new modules.

## The rest of the graph

Each workstream after the interface is a vertical slice that replaces stubs in
every module it touches and is demoable on its own. Line 142 of the 430 handbook
refuses the alternative: "A core-logic workstream followed by an I/O workstream
is a horizontal decomposition, and it defers every integration error to the
end." Line 72 of the 440 handbook names the cross-repo form: all of the server,
then all of the client, then integrate.

Not yet decided: whether a `contract-phase`, then a `core-phase` with `cli.py`
and `config.py` stubbed, then an edges phase (the sequence `evals/evals.json`
rewards) is the horizontal decomposition the 430 handbook's line 142 refuses.

## Implementing an interface workstream

1. **Trigger:** the implementer knows how to write a body. **Action:** leave the
   stub. A written body puts implementation into the diff the reviewer reads for
   shape only.
2. **Trigger:** a function will hold logic later. **Action:** give it a loud
   stub.

   | Language     | Loud stub                                   |
   | ------------ | ------------------------------------------- |
   | Rust         | `todo!()`                                   |
   | Python       | `raise NotImplementedError`                 |
   | TypeScript   | `throw new Error("not implemented")`        |
   | Go           | `panic("not implemented")`                  |
   | Java, Kotlin | `throw new UnsupportedOperationException()` |

3. **Trigger:** a body returns `nil`, `""`, `[]`, or is a bare `pass`.
   **Action:** replace it with a loud stub. A silent default type-checks, passes
   any test that does not assert on the value, and after merge reads as a bug
   (`evals/evals.json` line 12 rejects it).
4. **Trigger:** the implementer sees work that belongs to a later workstream.
   **Action:** record it, either as a `TODO` comment beside the signature naming
   that workstream or as a filed follow-up issue; do not do it.
5. **Trigger:** the PR is about to open. **Action:** read the diff for any body
   holding real logic and any call that performs I/O, and stub both.

## Core logic takes its inputs as arguments either way

1. **Trigger:** a function holds core logic, with or without an interface
   workstream. **Action:** it takes everything it needs as arguments: no
   environment variables, no filesystem, no network, no clock, no ambient state.
   The edge modules (CLI, HTTP client, on-disk cache, config loader) construct
   those values and pass them in. This is rule 1, "Accept dependencies, don't
   create them", in the codebase-design skill.
2. **Trigger:** a core function needs something from outside. **Action:** add a
   parameter. A test of a function that calls `os.Getenv` or `open(path)` has to
   set that variable or write that file before it runs. With a parameter, the
   test passes the value directly.

The `core-phase` eval in `evals/evals.json` (lines 22-38) shows the argument
rule: `digest.py` reaches nothing outside its arguments and takes the current
time from its `now` parameter, while `cli.py` and `config.py` touch the outside.
If the feature later gets an interface workstream, the signatures it merges for
`digest.py` are these parameter lists, and `cli.py` and `config.py` are the
modules that call the outside.

## When the interface turns out to be wrong

1. **Trigger:** the merged interface is wrong. **Action:** change it in one
   edit, state the change in the PR description, and do not work around it
   locally. Parallel workstreams can only adjust to a change they can see; an
   edit that stays inside one workstream is the drift the move prevents.
2. **Trigger:** the interface changes a second time in one epic. **Action:** say
   in the PR that the review came before anyone understood the interface, and
   consider having the remaining workstreams change the shape themselves instead
   of a third revision.

---

The 430 handbook, section "10. Decomposition" (lines 128 and 146-148), sizes
workstreams and orders their publication; the same repository's
`docs/440-handbook-epics.lex` describes how a workstream is executed.
