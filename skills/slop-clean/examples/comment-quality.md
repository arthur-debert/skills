# Comment Quality Calibration

Use these contrasts to classify comments during cleanup. They are examples of
the tests in `SKILL.md`, not templates to copy.

## Narrating an obvious validation

Before:

```rust
// Validate the band before allocating. A mismatched width would be out
// of bounds, so this public adapter returns Err instead of panicking.
if band.image.color.width != band.full_width {
    return Err(format!("incorrect band width"));
}
```

After:

```rust
if band.image.color.width != band.full_width {
    return Err(format!("incorrect band width"));
}
```

The condition and result already communicate the behavior. Retain a comment only
if the validation protects a non-obvious invariant that the names and types do
not reveal.

## Error variants

Before:

```rust
/// `width` or `height` is zero. A zero-sized image is degenerate and
/// several methods assume non-zero dimensions, so rejecting it here
/// prevents a later panic.
ZeroDimension { width: u32, height: u32 },
```

After:

```rust
/// Zero is not a valid width or height.
ZeroDimension { width: u32, height: u32 },
```

If every variant serves the same defensive purpose, put that purpose once on the
error type:

```rust
/// Malformed inputs rejected at the boundary before they reach the evaluator.
enum DecodeError {
    ZeroDimension { width: u32, height: u32 },
    TrailingBytes { expected: usize, actual: usize },
}
```

Document a variant separately only when its semantics, recovery, or trigger are
surprising.

## Restating the type system

Before:

```typescript
interface Session {
  /** The unique user ID as a string. */
  userId: string;
}
```

After:

```typescript
interface Session {
  userId: string;
}
```

A useful replacement would explain something the type cannot, such as stability
across reconnects or whether the value is safe to expose.

## One owner for a subsystem convention

Before:

```python
def crop(...):
    """Coordinates use a top-left origin."""

def resize(...):
    """Coordinates use a top-left origin."""
```

After, at the subsystem boundary:

```python
"""Image operations use a top-left coordinate origin."""
```

Leaf documentation should mention the convention only when omission would make
that API misleading. If readers need navigation, use the language's resolvable
documentation reference instead of copying the explanation.

## A small umbrella is allowed

```text
operations/
  add
  remove
```

An `operations` overview may list `add` and `remove` when they are tiny parts of
one cohesive unit. It should not explain their internals, and it should stop
listing them once the map becomes substantial enough to need its own guide.

## A design comment worth keeping

```go
// Release the registry lock before invoking the compiler. Compilation can
// synchronously request another registry entry, so holding it would deadlock.
registry.Unlock()
result := compiler.Compile(input)
```

This survives the novelty test: the code shows _what_ happens, while the comment
records the re-entrancy constraint and the consequence of changing the order.

## Strings are not comments

```rust
const SHADER: &str = r#"
// This is WGSL source consumed at runtime.
fn main() {}
"#;
```

The `//` text belongs to an embedded language inside a string literal. A
comments-only cleanup must not edit it unless the user separately authorizes
changes to that embedded source.
