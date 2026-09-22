# Documentation Audit

For the target document, report:

**Role:** [why-for-whom / what / how — one or several] **Parent:** [the document
it inherits decisions from, or "root"] **Coverage:** [what the role owes that
the doc never answers — how the parts relate, the first action, who it is for]
**Overall:** [PASS / NEEDS REVISION]

## 1. The system as subject

- **Status:** [Pass / Fail]
- **Critique:** [Examine the opening block — everything before the first section
  heading. Is any sentence in it about the document rather than the system? Does
  it contain at least one named concrete thing — a command, file, input/output —
  and, for a runnable system, the reader's first action? Then quote any sentence
  *anywhere* in the document whose subject is the file, its sections, or its
  words. Also flag when the whole organizing scheme is the document's own
  taxonomy — owns / does not own / vocabulary — rather than the reader's
  questions.]

## 2. Headline

- **Status:** [Pass / Fail]
- **Critique:** [Title plus one-to-two sentence subtitle that lets a reader
  scanning the directory decide whether to open it. For a root README, the first
  sentence of the opening block counts as the subtitle.]

## 3. Borders

- **Status:** [Pass / Fail]
- **Critique:** [Quote any sentence that overrides a decision made in the
  parent, and any material too deep for this document's role. Where a child doc
  exists, the displaced fact moves there behind a cross-reference; where none
  exists, the fix is cutting the depth to its one-line summary — recommend a new
  doc only for a screenful or more of displaced material.]

## 4. Terms defined before use

- **Status:** [Pass / Fail]
- **Critique:** [List every project-coined term used before it is defined on the
  page. A glossary elsewhere does not count, and a glossary entry that is a bare
  word with no definition is itself a finding.]

## 5. Task residue

- **Status:** [Pass / Fail]
- **Critique:** [Quote every unmotivated negation — "X is never Y", "X does
  nothing" — that prices no real alternative, any options listed in the order
  they were considered, and any survey, inventory, verification run or
  chronology from the session. A scope section ("what it does not do") is
  licensed as a section; each entry inside it still owes which project or
  component handles the refused thing or what the reader gets instead. A
  negation paired in-sentence with its positive half passes; one restating the
  prior clause negatively is redundancy. A stated rationale for breaking a rule
  is itself a trace of the authoring session, not a waiver.]

## 6. Size

- **Status:** [Pass / Fail]
- **Critique:** [Past ~200 lines: name the deepest section to extract into a
  child doc. Under a screenful: name the parent it should be a section of. Do
  NOT recommend new documents for material that fits here. For a product spec
  the ceiling is stricter — ~100 lines of prose, 300 far too much — and the
  remedy is splitting into multiple specs, never child docs. Also for specs:
  flag exhaustive variant enumeration where classes would do.]

## Remediation

[Two to four explicit, bulleted instructions, each pointing at quoted text.]

Then run the `writing` skill's review on the prose itself; this audit covers
structure only.
