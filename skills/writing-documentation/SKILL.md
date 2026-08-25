**Core Philosophy:** Documentation must follow a strict "General to Specific"
hierarchy. Massive, monolithic files destroy usability. Systems must be
documented in hierarchical layers where reader context is carefully preserved.

## 1. The Hierarchical Levels

Agents must classify any documentation task into one of three structural levels.

### Level 1: System Context & Product Spec (The Root)

- **Scope:** What the system does, who uses it, and its external boundaries.
- **Content:** Business requirements, user flows, feature constraints, and root
  architectural paradigms (e.g., "This is a node-based pipeline," or "This is a
  CLI tool").
- **Audience:** Product managers, stakeholders, and engineers needing a
  high-level mental model.
- **Constraint:** Zero implementation details, database schemas, or specific
  algorithms.

### Level 2: Sub-systems & Architecture (The Containers)

- **Scope:** How the root system is divided into functional blocks and how they
  communicate.
- **Content:** High-level engineering decisions, data storage strategies,
  concurrency models, and network topology.
- **Audience:** Software architects and technical leads.
- **Constraint:** Acknowledges Level 1 business rules but focuses entirely on
  the structural strategy to achieve them.

### Level 3: Component Design (The Leaf Nodes)

- **Scope:** The internal mechanics of a specific container or module.
- **Content:** Internal file structures, parsing grammar rules, API
  specifications, and exact data schemas.
- **Audience:** The developer implementing or debugging that exact component.
- **Constraint:** Focuses strictly on local execution and implementation.

---

## 2. The Unbreakable Rules of Documentation

When generating or reviewing documentation, agents must enforce the following
rules:

### Rule 1: The Law of Downward Dependency

A document at Level `N` can never define, alter, or overturn a structural
concept that belongs at Level `N-1`.

- **Correct:** The Level 2 architecture defines a sequential execution pipeline.
  The Level 3 document for a specific diffuser node positioned at the start of
  the output phase describes its local image caching logic.
- **Violation:** The Level 3 document for the diffuser node declares that the
  system will use an asynchronous event-bus instead of the sequential pipeline
  defined in Level 2.

### Rule 2: The Self-Evident Headline

Every document or topic block must begin with a title and a 1-2 sentence
subtitle that perfectly scopes the contents. A reader scanning a directory must
know immediately if they need to read it.

- **Bad:** `Data_Format.md`
- **Good:** `Plaintext_Markup_Grammar.md` — _Defines the AST structure and
  parsing rules for the custom document format._

### Rule 3: The Linear Context Guarantee

A reader must never be forced to jump forward to understand the current
paragraph.

- If a concept relies on prerequisite knowledge, that knowledge must either be
  summarized earlier in the same document or explicitly linked at the very top
  as a required read.
- Assume the reader starts at the top and reads downward.

### Rule 4: The Cognitive Threshold (Chunking)

If a document or section exceeds a reasonable cognitive load (approximately 200
lines), it is too detailed for its current level.

- **Action:** The agent must summarize the remaining concepts, spawn a new Level
  3 document for the deeper technical details, and link to it from the parent
  document.

---

## 3. Operational Directives for Agents

When invoked to write documentation, agents must follow this execution loop:

1. **Assess Level:** Determine if the requested documentation is Level 1, Level
   2, or Level 3.
2. **Verify Upward Constraints:** If writing at Level 2 or 3, identify the
   parent document (Level 1 or 2). Ensure no decisions in the draft override the
   parent.
3. **Apply Headlines:** Generate a strict, self-evident headline and scope
   description.
4. **Enforce Thresholds:** If the output grows too large, recursively split the
   document downwards, leaving a summary and a link in the parent.
