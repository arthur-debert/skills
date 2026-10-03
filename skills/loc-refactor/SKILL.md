---
name: loc-refactor
description: >-
  Split oversized source and test files into cohesive modules without changing
  behavior. Use when the user invokes /loc-refactor, asks for a periodic file
  split, wants rustloc-guided modularization, or needs large files made easier
  for humans and agents to navigate. File counts identify candidates; they do
  not determine the design.
---

# LOC Refactor

Use file LOC as a maintenance signal, not a score. Runtime behavior does not
improve when code moves between files, but people, agents, diff tools, and test
runners all use files as working units. The result should make each file easier
to understand and change while preserving behavior and public APIs.

Module organization is fractal. A broad domain can remain one file while it is
small. As it grows, themes that were once sections become child modules; those
modules may split again later. A threshold prompts inspection. It never proves
that a file should split or that two adjacent line counts deserve different
treatment.

## Establish the comparison

1. Read the repository instructions and inspect version-control status. Preserve
   unrelated work and generated or vendored files.
2. Use the scope, thresholds, and languages the user supplied. Without explicit
   thresholds, start inspection around 500 production lines or 800 total lines.
   Treat these as guidelines.
3. Identify the repository's focused tests and full quality command. Run the
   focused tests for likely candidates before editing so pre-existing failures
   are distinguishable from regressions.
4. Record the relevant `rustloc` commands and rows. The comparison is complete
   when production code, tests, and total LOC have been ranked separately.

When `rustloc` is available, prefer its language-aware counts. Adapt the
languages and path to the repository:

```sh
rustloc path/to/scope --lang rust,python,typescript --by-file --ordering code --top 20
rustloc path/to/scope --lang rust,python,typescript --by-file --ordering tests --top 20
rustloc path/to/scope --lang rust,python,typescript --by-file --ordering total --top 20
rustloc path/to/scope --lang rust,python,typescript --by-module --ordering code --top 20
```

Use `--output json` when another agent or a script will consume the results.
Filters such as `--code-gte 500` and `--total-gte 800` can narrow a large
repository after the initial ranking.

If `rustloc` is unavailable, continue with `tokei`, `cloc`, or `wc -l`. State
that code and test classification may be approximate. Do not make installing a
counter a prerequisite for the refactor.

## Choose candidates by size and theme

Inspect the largest production files and the largest test files independently.
Read each candidate in full, then inspect its callers, siblings, and tests.

Prioritize a file when its size combines with one or more concrete split
opportunities:

- unrelated domains or change reasons share the file;
- one broad, central feature contains concepts that its adapters, callers, or
  tests already treat as separate domains;
- distinct parsing, normalization, persistence, transport, or orchestration
  responsibilities can own separate names and tests;
- a long sequence of types and helpers forms recognizable subdomains;
- test scenarios for several domains share one file;
- repeated test setup obscures the scenario and can become a small fixture or
  builder without hiding assertions.

Leave a large file intact when its contents remain cohesive, splitting would
create arbitrary names or circular dependencies, or most lines are generated
data, tables, or inherently verbose test cases. Test code is usually more
verbose than production code; 600 test lines alone are not evidence of a
problem.

Unless the user requests a repository-wide pass, select one justified hotspot or
one small set of independent hotspots. The selection is complete when every
chosen file has a proposed thematic split and every skipped outlier has a short
reason.

## Compare independent split proposals

When subagents are available, have two or three agents independently inspect the
same candidate read-only. Give each the file, nearby modules, test layout, LOC
rows, repository instructions, and the invariants that must remain true. Do not
show them one another's proposals.

Ask each proposal to name:

- each proposed file and the responsibility it owns;
- which types, functions, and tests move there;
- dependency direction and required visibility;
- public paths, serialization, error behavior, and test discovery that must not
  change;
- splits considered but rejected.

Compare the proposals against the code rather than voting by majority. Combine
ideas only when each resulting file still has a one-sentence responsibility and
no file merely receives leftover code. If delegation is not available, perform
the same analysis directly.

The design is ready when every new file has a one-sentence responsibility, no
new file merely receives leftover code, and the proposed dependency direction
does not require widening public visibility solely to make the split compile.

## Move one responsibility at a time

Keep the refactor behavior-preserving. Move one coherent group, fix its imports
and visibility, and run its focused checks before moving the next group. Prefer
the narrowest language-supported visibility and preserve existing public import
paths with module declarations or re-exports when callers depend on them.

Treat an item's attributes and documentation as part of the item when selecting
text to move. After a mechanical extraction, compare the before-and-after
documentation inventory; a successful compile cannot detect a comment dropped at
a cut boundary.

Move same-file tests with the code they exercise. For dedicated test files, keep
scenarios organized by the production responsibility they verify. Extract shared
fixtures only when they remove genuinely repeated setup; do not hide scenario
inputs or assertions merely to reduce LOC.

Moving tests into child modules can change their fully qualified runner names
even when every test function keeps its name. Search repository scripts and CI
for exact selectors before accepting that change, and report new prefixes when
they are observable to developers.

Avoid splits that only move lines:

- forwarding wrappers whose only purpose is making the original file shorter;
- `utils`, `common`, or `misc` collections with no specific responsibility;
- one large replacement file that recreates the original hotspot;
- compressed formatting, deleted documentation, or deleted tests;
- opportunistic behavior changes mixed into the move.

For parallel implementation, assign fresh agents exclusive existing files or
module trees. Two agents must not edit the same original file or create files
under the same new module tree concurrently. A single agent owns all extractions
from one large source file; parallel agents can handle other independent
hotspots. The coordinator reviews the combined diff and resolves cross-file
imports.

## Verify the result

Run focused tests after each extraction, then the repository's formatter,
linters, documentation build, and full relevant test suite. A documentation
inventory proves that text moved; it cannot prove that links still resolve from
the new module. When supported, make broken documentation links fail the build.
For Rust, use a repository-specific equivalent of:

```sh
RUSTDOCFLAGS="-D warnings" cargo doc --workspace --no-deps
```

Rerun the same `rustloc` rankings used for the baseline and inspect the
working-tree change when useful:

```sh
rustloc diff --path path/to/repository --by-file --ordering total
```

The refactor is complete when:

- focused and repository-level checks pass, apart from failures recorded before
  editing;
- test function names and counts, rendered documentation, and embedded protocol
  or configuration strings match the baseline unless an intentional change was
  separately approved;
- public paths and externally observable behavior remain unchanged;
- each new file owns a recognizable theme and its relevant tests;
- the original hotspot is smaller without creating an equivalent replacement;
- no production code, tests, or documentation were removed just to lower a
  count.

Report the before-and-after LOC rows, the responsibility of each new file, the
checks run, and any large files deliberately left intact. Net LOC may stay flat
or grow slightly because module declarations and explicit interfaces have a
cost. Do not commit or publish unless the user asks.
