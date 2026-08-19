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

**Vertical slices are the default.** A workstream is a thin, complete path
through every layer, demoable on its own, and the epic opens with a walking
skeleton. That rule holds; this skill is the one exception to it.

The exception: **when the interface is the risk, it lands first, in its own
workstream, stubbed** — the types, the schemas, the public signatures, with no
behavior behind them. The implementation follows in the vertical slices after
it.

Two payoffs, and both are lost if the interface arrives mixed into an
implementation:

- **The design gets an undivided review.** A reviewer reading an interface-only
  diff evaluates the data model, the signatures, and the module layout, with
  nothing else competing for attention. Mix in implementation and the reviewer
  reads the implementation — the shape gets waved through, and the shape is the
  expensive thing to reverse.
- **Parallel workstreams stop drifting.** Once the interface is merged, the
  workstreams that build against it proceed at once without colliding, because
  the thing they would have collided over is already fixed and shared.

Where a repo's own handbooks state this rule, they are authoritative and this
skill only carries the how. In `edward`, that home is
`docs/430-handbook-planning.lex` §10, with `440-handbook-epics.lex` §7 covering
the cross-repo case.

## When to mint an interface workstream

Any one of these is enough:

- **Several workstreams will build against the same new interface at once.**
  Whatever they share is what they will conflict over and drift from. Fix it
  first.
- **The contact surface crosses a boundary** — repos, teams, or a
  provider/consumer split where the two sides are built independently.
- **The data model is the expensive decision in the feature.** If getting the
  shape wrong means reworking everything downstream, buy the focused review.

Do not mint one when:

- The feature is one workstream, or a handful that barely touch each other.
  There is nothing to synchronize, and you would be adding a review cycle to buy
  a property you already have.
- The shape is genuinely unknown. An interface reviewed before anyone has tried
  to implement behind it is a guess with a merge commit. Prototype first, throw
  the prototype away, then write the interface from what you learned.
- The interface is small and obvious — one function, one struct with three
  fields. Put it in the first vertical slice.

The counter-test, applied honestly: **would a reviewer of this interface have
anything to argue with?** If the shape is forced by the problem, there is no
review to buy, and the workstream is ceremony.

## Scoping the workstream

**In scope:** data models, types, schemas, enums, error types. Public interfaces
across every layer the feature touches — including the edge modules, so the
layout is visible and named. Doc comments recording what each interface
promises: invariants, ordering, error modes. Tests on the data models themselves
— construction, defaults, serialization round-trips, validation.

**Out of scope:** all behavior. Every body that will eventually hold logic stays
a stub.

**Acceptance criteria to write into the ticket:**

- Compiles and type-checks; the existing suite still passes.
- Every logic-bearing body raises a loud stub; none returns a silent default.
- Data-model tests pass; no test asserts behavior that does not exist yet.
- The PR description names the decisions worth arguing with now — the ones a
  reviewer should push back on before anything is built against them.

**It is not a walking skeleton.** A skeleton is the thinnest _working_ thread
end to end; an interface workstream is all the shapes with nothing working. They
answer different questions — "is this the right shape" versus "is this wired
together" — and an epic usually wants both answers. Take them in that order: the
interface first, the skeleton as the first slice through it, then the parallel
fan-out. That costs one serial cycle before the fan-out, and buys the shape
review undivided.

## The rest of the graph

Everything after the interface workstream stays a vertical slice: a narrow but
complete path that replaces stubs across every layer it touches and is demoable
on its own. Do not follow an interface workstream with a "core logic" workstream
and an "I/O" workstream — that is a horizontal decomposition, and it defers
every integration error to the end, which is the failure `440` §7 names.

The interface workstream buys the shared shape once. It does not license slicing
the rest by layer.

## Implementing an interface workstream

You will know how to implement the thing while you are stubbing it, and writing
it costs almost nothing in the moment. That is the trap: it costs the review.
Leave the stub.

A stub must be impossible to mistake for working code:

| Language    | Stub                                        |
| ----------- | ------------------------------------------- |
| Rust        | `todo!()`                                   |
| Python      | `raise NotImplementedError`                 |
| TypeScript  | `throw new Error("not implemented")`        |
| Go          | `panic("not implemented")`                  |
| Java/Kotlin | `throw new UnsupportedOperationException()` |

Never stub with a silent default — `return nil`, `return ""`, `return []`, a
bare `pass`. A silent stub type-checks, survives any test that does not assert
hard on the value, and merges looking finished. Later it reads as a bug rather
than as unfinished work.

Work you notice that belongs to a later workstream gets recorded, not done: a
`TODO(WSnn)` beside the signature, or a filed follow-up. Before opening the PR,
read your own diff and ask whether any body contains real logic and whether
anything performs I/O.

## The layering holds either way

Whether or not the interface gets its own workstream, keep the layering inside
whatever you build: **core logic takes everything it needs as arguments** — no
environment variables, no filesystem, no network, no clock, no ambient state —
and the edge modules construct those values and pass them in.

This is the cheap half of the benefit and it costs nothing. It makes the core
testable without mocks, and it means that if the feature later grows enough to
need an interface workstream, the seam is already where it belongs.

When a core function needs something from outside, add a parameter. Reaching for
`os.Getenv` or `open(path)` mid-function is a two-second edit that costs the
isolation everything else depends on.

## When the interface turns out to be wrong

It will sometimes. Change it — but in one deliberate edit, and say so plainly in
the PR, rather than working around it locally. An interface that mutates quietly
while several workstreams are being built against it is the drift this whole
move exists to prevent. Making the change visible is what lets the parallel work
react to it.

Two of these in the same epic is a signal, not bad luck: the interface was
reviewed before it was understood. Say so, and consider whether the remaining
workstreams should absorb the shape rather than a third revision.

---

For the vocabulary of what makes an interface worth reviewing — depth, seams,
leverage — see the `codebase-design` skill. For how workstreams are sized,
published, and executed, see `to-tickets` and `440-handbook-epics.lex`. For
building test-first inside a slice once the shapes exist, see `tdd` — the
interface workstream splits review units, never the red-green cycle.
