---
name: testing-gravity-inversion
description: >-
  Choose the lowest test layer that can detect a failure and prevent duplicated
  domain coverage in integration suites. Use when planning or adding tests,
  reviewing test placement, repairing slow or brittle suites, or documenting
  test ownership across core logic, APIs, application shells, and OS boundaries.
---

# Testing Gravity Inversion

Read the whole essay below before choosing test placement. Its explanation is
part of the skill: carry the causal reasoning into plans, reviews, comments, and
handoffs wherever future work needs it. A checklist alone does not explain why
locally convenient test choices gradually damage a suite.

## The essay

What you are diagnosing is a classic failure mode of localized agentic work:
**Testing Gravity Inversion**. Because an agent’s context window is usually
anchored to the task at hand—say, wiring up a CLI subcommand or a SwiftUI
view—it defaults to verifying its work at the exact altitude where the prompt
entered the system. Combine that with the economic reality of agent tokens
(appending a new test at the top of the stack is vastly cheaper than auditing
existing lower-level suites), and you inevitably end up with an inverted
pyramid: bloated, brittle, slow integration tests trying to brute-force
combinatorics that belong in pure logic functions.

### Testing Altitude & The Law of Lowest-Level Verification

#### The Core Problem: Local Context Bias in Agentic Testing

When building software in isolated tasks, there is a strong gravitational pull
to write tests at the exact layer where a feature was requested or wired up. It
is also locally cheaper in the short term to append a new end-to-end test than
to search the codebase to see where a behavior is already verified.

Over time, this creates two severe forms of test suite decay:

1. **Horizontal Duplication:** The same underlying behavior is asserted
   repeatedly across scattered test files because each task added its own
   localized verification without auditing existing coverage.
2. **Altitude Creep (Testing Too High):** Domain invariants, edge cases, and
   input permutations get tested through high-level interfaces (CLI invocations,
   FFI bridges, GUI harnesses, or OS integrations) rather than at the pure logic
   layer where the behavior actually lives.

#### The Testing Ladder

Every application—whether a local CLI, a native GUI application, or a server—is
structured as a ladder of increasing integration and diffusion:

- **Rung 1: Pure Core Logic (e.g., internal library functions).** Pure
  computation and data transformation. Zero I/O, zero system dependencies, tiny
  code touch, deterministic execution in microseconds.
- **Rung 2: Internal Composition & Module Boundaries.** Functions that
  orchestrate two or three pure primitives to fulfill a domain operation. Still
  fast, narrow in scope, and isolated from external state.
- **Rung 3: Public API & FFI Entry Points.** The boundary of the core engine.
  Its job is translating external requests into internal calls, managing state
  lifecycles, and marshaling types across boundaries.
- **Rung 4: Application Shell (CLI Parsers, UI View Models, State Stores).** The
  presentation and interaction layer (e.g., SwiftUI views, command-line argument
  routing). High surface area, heavy framework involvement.
- **Rung 5: System & OS Integration.** The outermost boundary—launching
  binaries, file-system watchers, IPC, dragging documents from the OS file
  manager onto an application icon. Maximum diffusion, heavy third-party and OS
  involvement, slow setup and teardown.

As you climb this ladder, three things compound exponentially: **execution
time**, **setup cost**, and **structural brittleness**. Worse, the combinatorial
state space explodes. If function $A$ has 5 edge cases and function $B$ has 5
edge cases, testing them together at Rung 4 requires accounting for 25
interactions—all while paying the tax of spinning up an application shell.

### The Four Laws of Testing Altitude

#### 1. Push Verification Down to the Lowest Possible Rung

Every behavior, invariant, and edge case must be tested at the lowest level
where that logic exists. If a bug can be caught by calling a pure function in
memory, it is an architectural error to catch it by spawning a CLI process or
driving a UI view. Exhaustive parameter sweeps, malformed inputs, and boundary
invariants belong exclusively at Rungs 1 and 2.

#### 2. Upper Layers Test Only the "Glue" (Contract & Dispatch)

Once a piece of logic is thoroughly tested at Rung 1, **never re-test its
internal correctness at Rung 2, 3, or 4.** When writing tests at a higher layer,
treat the lower layer as an already-proven black box. A test at the API or UI
boundary has only three responsibilities:

- Did this layer parse or receive the input correctly?
- Did it dispatch the right lower-level function with the expected parameters?
- Did it handle the return value or error type and map it to the right output
  state?

Use mocks, stubs, or lightweight fixtures at upper layers to verify that the
_wiring_ works without re-running the combinatorial logic underneath.

#### 3. Never Skip Lower Tests to "Cover It in Integration"

Higher-level tests are not a substitute for lower-level unit tests; they are a
poor approximation of them. Because high-level tests are slow to run and
expensive to write, testing functionality only at the top guarantees you will
only test the "happy path" and miss the edge cases. Grind the edge cases and
invariants at the bottom where execution is free; keep upper-level tests thin.

#### 4. Audit Before You Append

Before writing a new test, search the test suite down the ladder. Ask two
questions:

- _Is this behavior already tested at a lower rung?_ If so, do not duplicate the
  logic test—only test the new wiring if a new boundary was introduced.
- _Does a test fixture for this module already exist?_ Extend existing
  parameterized tests or property suites at the core level rather than creating
  a new standalone test file at the feature level.

### Practical Heuristic: The "Why Am I Here?" Check

Before committing a test at the CLI, API, UI, or OS level, apply this filter:

- **If the test varies domain inputs to check different domain outputs:** It is
  at the wrong altitude. Move the test down into the core logic module.
- **If the test spins up the app shell more than once or twice per feature:**
  Ask whether you are testing the shell or using the shell as an expensive test
  runner for core code.
- **At the GUI / OS integration level:** Restrict tests strictly to smoke tests
  (verifying the binary boots and layers are connected) and contract checks for
  OS-specific mechanics (e.g., verifying that a file-drop event extracts a path
  URL and hands it to the API boundary—not what the core engine does with the
  file contents afterward).

## Applying the laws

Interpret “lowest possible” as **the lowest layer capable of detecting the
actual failure**. The ladder describes responsibilities; map those to the
repository's modules before choosing a harness. A public pure function can be
tested as core logic even though it is also an API. The essay's cost language
describes the pressure toward expensive suites, not a measured exponential law;
actual execution costs depend on the implementation.

### Establish ownership before adding coverage

Trace the requested behavior from the entry point to its implementation. Search
existing tests, fixtures, parameterized cases, and property suites by behavior
and implementing symbol. Read the assertions: a matching test name does not
establish coverage.

For each behavior, identify the owning function or module, the lowest test that
can expose its failure, and any separate boundary obligation. In a small change,
a few sentences suffice. For a larger change, use a table of behavior, owner,
existing coverage, and missing coverage. Cite actual paths and test names so the
next agent can resume the audit.

Extend the owning suite for missing domain cases. If logic is embedded in a
handler, extract a focused pure operation when that fits the requested change.
Do not turn a narrow fix into an unrelated architecture rewrite. When moving
existing coverage down, establish equivalent assertions below before removing
the redundant cases above; retain tests that catch distinct integration
failures.

### Preserve each boundary's own correctness

The prohibition on repeated domain permutations does not remove a boundary's own
input space. CLI syntax, FFI lifetimes, serialization, cancellation,
concurrency, and OS event delivery can introduce failures that pure core tests
cannot detect. Test those at the lowest layer that actually exercises the
mechanism. Malformed domain values belong with domain validation; malformed
transport bytes belong with the decoder that receives them.

Use a stub to induce a return value or error when testing a caller's mapping.
Use real collaborating components when their interaction is the subject of the
test. Do not mock away the boundary being verified or assert incidental private
call sequences. “Already proven” means lower-level tests own the domain
assertions; it does not mean those tests prove that deployed components connect
correctly.

Five cases in each of two functions do not automatically require 25 composed
tests. Test each function's cases independently, then test interactions that
introduce an additional failure mode. Keep a small real end-to-end check where
it proves assembly or delivery that narrower tests cannot. One or two shell
launches is a prompt to inspect test purpose, not a numerical quota.

For example, a CLI that accepts a range needs core cases for range arithmetic,
parser cases for its syntax, and a focused handler check for argument and error
mapping. A process test may verify exit status and stdout delivery. Repeating
every range-arithmetic case through the process adds no new ownership.

### Carry the reasoning into the next task

When preparing a plan, review, PR description, or handoff, explain the local
cause and consequence: where the behavior lives, why that suite owns its
permutations, and what distinct failure the higher test detects. Include
relevant test paths, validation performed, and remaining gaps. “Unit tests
added” or “keep tests low” loses the reasoning the next agent needs.

For example, adapt this explanation to the actual code and name its tests:

> Range validation belongs to the core, so its parameterized suite covers empty,
> reversed, and out-of-bounds ranges without starting the CLI. The handler test
> checks that parsed endpoints reach that operation and that its error becomes
> the documented exit status. New range rules belong in the core suite; new CLI
> syntax belongs in parser tests. Repeating the range matrix through the
> executable would add process setup without detecting a different failure.

Put a durable explanation beside a suite when its scope would otherwise be easy
to misread. Put repository-wide ownership in the existing testing guide or agent
instructions when that documentation is within scope. Preserve the reasoning in
handoffs and task context, including after context compaction; link this skill
and require its full reading when the next task makes test placement decisions.
Explain the project's concrete ownership locally rather than copying the entire
essay into every comment.

Run the focused suites and the repository's required checks. Report what they
demonstrate and what remains unverified. A smaller suite is an improvement only
when it preserves the distinct failures the project needs to catch.
