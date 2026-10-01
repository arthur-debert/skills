---
name: technical-drawing
description: >-
  Model a part in FreeCAD and produce a manufacturing drawing of it (ISO title
  block, orthographic views, section, isometric, dimensions, hole and thread
  callouts, tolerances, notes) as PDF, SVG and PNG, driving the running FreeCAD
  GUI through the freecad-mcp addon. Use when asked to model a part from a
  datasheet, manual figure, photo or sketch; to make, redo or check a technical,
  engineering, dimension or shop drawing; to turn a vendor drawing into CAD; or
  to produce isometric renders of a modelled part. A drawing fails when it looks
  finished but a machinist cannot make the part from it alone: dimensions
  missing or duplicated, labels on top of geometry, estimated sizes passed off
  as given, threads drawn wrong, or a title block still holding the template's
  sample text.
---

# Technical drawing with FreeCAD

The agent builds the part as a Python script, checks the solid against the
source numerically and visually, then lays out a TechDraw page from a second
script, exports it, and looks at the rendered PNG before calling it done. Both
scripts live in files the agent edits and re-runs; nothing is clicked in the
GUI, so every result can be rebuilt from scratch after a change or a crash.

The finished drawing has to answer one question: could a machinist who has never
seen the part make it from this sheet alone? Every rule below serves that.

## Tools

FreeCAD runs as a GUI app with the FreeCADMCP addon, which serves XML-RPC on
`localhost:9875`. Two clients reach it:

- The `freecad` MCP server (`freecad-mcp`), when registered, gives tools such as
  `execute_code`, `get_view`, `get_objects` and `list_documents`.
- `scripts/fc_run.py` sends a file to the same server and prints its output and
  traceback. Use it for the model and drawing scripts, so the code lives in a
  file rather than a tool argument:

  ```bash
  scripts/fc_run.py --ping                          # can FreeCAD run code now?
  scripts/fc_run.py --headless work/model.py        # geometry in a throwaway process
  scripts/fc_run.py work/model.py work/drawing.py   # run in the GUI, stop on error
  ```

  Each file runs in a fresh namespace with `__file__` set, so a script can find
  its siblings.

`scripts/tdkit.py` holds the TechDraw helpers. Import it at the top of a drawing
script (the path is absolute because the code runs inside FreeCAD):

```python
import sys, importlib
sys.path.insert(0, "/abs/path/to/technical-drawing/scripts")
import tdkit; importlib.reload(tdkit)
```

`references/techdraw-api.md` lists the TechDraw objects and properties the
helpers set, for anything the helpers do not cover.

`scripts/figure_runs.py` measures a raster source figure (see Stage 1).

Rasterising needs `rsvg-convert` (librsvg) and `magick` (ImageMagick).

## Stage 1: a spec table before any geometry

Read the source (PDF text and figures, photos, notes) and write `work/spec.md`:
one row per feature with its value and where the value came from.

| Feature          | Value | Source                                                |
| ---------------- | ----- | ----------------------------------------------------- |
| Flange thickness | 12    | given: side view "12", datasheet p.3                  |
| Bore             | ⌀40   | given: "⌀40 H7"                                       |
| Bolt circle      | ⌀70   | derived: hole centres at ±35 given in top view        |
| Bolt holes       | 6× ⌀6 | estimated: ⌀6.2 ±0.3 px-scaled against ⌀90, 6 counted |

Three kinds of source, and the drawing treats them differently:

- **given**: printed on the source. Dimension it exactly.
- **derived**: computed from given values. Write the arithmetic in the row.
- **estimated**: measured off a figure by scaling against a given dimension, or
  inferred from a photo or a standard. Give the uncertainty. These go into the
  drawing as reference dimensions in parentheses, `(100)`, and the final report
  lists them so a human can confirm them.

To estimate from a raster figure, measure in pixels against the longest given
dimension in the same view, not a short one; the error scales with the
reference. Measure rather than eyeball:
`scripts/figure_runs.py fig.png --row 480` prints the dark-pixel runs along one
pixel row (or `--col`), so the gaps between drawn lines come out to about one
pixel. Crop and zoom the figure (`magick in.png -crop WxH+X+Y`) before reading
small features. Count repeated features (holes, slots) on the zoomed crop and
record the count. Test the numbers for structure the designer likely used: equal
distances from the bore axis to each flank, a bolt circle at a round diameter,
equal angular spacing.

Work out each source view's viewing direction before reading features off it.
Vendor drawings mix conventions, and a side view placed below the face view is
seen from below in third-angle layout but from above in first-angle. Settle it
with a feature visible from one side only (a connector, a notch), and check it
numerically with tangent edges: a rounded corner seen edge-on shows lines at its
tangent points (R·cos θ from the corner centre), and they appear only on the
side the corner faces. Write the direction in the spec. Reading it the wrong way
round mirrors the part, which no numeric check catches.

## Stage 2: the model script

Write `work/model.py` so it runs both ways. The geometry part imports `FreeCAD`
and `Part` only, builds the solids and prints the verification block; the
document, colours, save and screenshots sit under `if App.GuiUp:`. Develop it
with `fc_run.py --headless work/model.py` until the verification passes: an
OpenCascade segfault there kills a helper process, while the same segfault in
the GUI kills FreeCAD with every open document, the user's included. Run it in
the GUI (`fc_run.py work/model.py`) only once it passes headless.

Rules for the geometry:

- All dimensions are named constants at the top, each with its spec row in a
  comment. No number appears twice.
- Build with `Part` primitives and booleans or a sketch extruded with
  `Part.Face(Part.Wire(...)).extrude(...)`. Model the features a machinist
  makes, in the order they make them: outline, pockets and recesses, through
  bores, then hole patterns.
- Check every 2D profile before extruding, filleting or chamfering it:
  `wire.isClosed()`, `Part.Face(wire).isValid()`, and its bounding box against
  the spec. An arc built the long way round makes the wire cross itself, and
  `makeChamfer` or `makeFillet` on a solid from such a profile segfaults
  OpenCascade. Build arcs from three points (`Part.Arc(p1, mid, p2)`) so the
  middle point fixes the direction, and mirror with `Shape.mirror()`;
  `transformGeometry` turns arcs into B-splines.
- Model threaded holes at the tap-drill (minor) diameter: M3 at ⌀2.5, M92×1 at
  ⌀91. The thread itself is never modelled; the drawing shows it with a thin
  circle and a callout.
- Print a verification block: bounding box, volume, number of faces, and a
  measured value for every given dimension (distance between faces, hole radii
  from `Face.Surface.Radius`, hole counts by radius). Compare each against the
  spec table and fix the model until they agree.

In `model.py`, run `tdkit.list_documents()` first, then create the document with
`tdkit.new_document(name, path)` under a name specific to the task, where `path`
is the `.FCStd` the script saves to. It closes a previous run of that name
(unsaved, or saved at `path`) and refuses to touch any other saved document. Add
one `Part::Feature` per machined piece (two stacked plates are two features),
set `ViewObject.ShapeColor` to a light grey such as `(0.80, 0.80, 0.83)`, and
save the `.FCStd` next to the scripts. The model file never holds a drawing
page.

Then take 3D screenshots with `tdkit.screenshot_3d(doc, path, view)` for
`Isometric`, `Top`, `Front` and `Bottom`. It adds its own lights to the scene,
because this FreeCAD build renders faces near-black with the default headlight.
Set each screenshot and set each beside the source figure. Check outline shape,
feature count and position, and which side each recess or connector is on. A
wrong-handed part (mirrored, a feature on the wrong face) passes every numeric
check and is only caught by looking.

## Stage 3: the drawing script

Write `work/drawing.py`. It starts with
`doc = tdkit.reopen("work/part.FCStd", "work/part_drawing.FCStd")`, which opens
the saved model and saves it straight away as a separate drawing document, then
builds the page and exports. Every run starts from the model file, so there is
never an old page to delete. Never remove TechDraw objects in a loop to rebuild
a page: deleting a page together with its views segfaults FreeCAD 1.1.

A part made of several pieces gets one sheet that shows how they stack, through
a section cutting all of them, plus a view of each piece's own outer face.
Dimension each piece's outline and features on its own view, and the second
piece's position against a datum on the first (the shared bore axis).

### Sheet and scale

Use an ISO template, `ISO/A3_Landscape_ISO5457_advanced.svg` unless the part
needs more room, and first-angle projection
(`page.ProjectionType = "First angle"`, the default in `tdkit.new_page`). Pick
the page scale from the ISO series (1:1, 1:2, 1:5, 2:1, 5:1) so the smallest
dimensioned feature is still at least about 2 mm on the sheet; then pick the
sheet size (A3, A2, A1) that holds all views at that scale with room for
dimensions. Shrinking the scale to fit a smaller sheet leaves 3 mm holes under
3.5 mm text. Lettering follows ISO 3098: dimension text 3.5 mm on A3 and A2, 5
mm on A1 and A0 (`tdkit.dim(..., size=)`); notes 3.5 mm. Views take the page
scale; set a custom scale only on the isometric or a detail view, and write that
scale under the view.

### Views

- **Main view**: the face that shows the most features, usually the face with
  the hole pattern. Place it top left in first-angle layout.
- **Other primary views**: only those that show something the main view does
  not, usually one side view for thicknesses and steps. First angle puts the
  view seen from the left on the right of the main view, and the view from above
  below it.
- **Section**: one through every recess, counterbore, step or blind feature
  whose depth would otherwise be a hidden line. Cut through hole centres.
  `tdkit.add_section` places the cutting line, arrows and letter.
- **Rear view**: when the second face carries its own features, a view from
  behind with direction `(0, 0, -1)` and x-direction `(-1, 0, 0)` keeps the part
  upright. Caption it with its letter and the face name.
- **Detail view**:
  `tdkit.add_detail(page, base, anchor, radius, scale, x, y, ref)`, for features
  too small to dimension at sheet scale (chamfers, grooves, a connector
  cut-out), magnified 2:1 to 5:1. A detail taken from a section view loses the
  hatching in FreeCAD 1.1; take details from a primary view where the feature
  shows, or note the omission.
- **Isometric**: always, in the largest free area of the sheet (top right when
  the projection layout leaves it free), direction `(1, -1, 1)` with x-direction
  `(1, 1, 0)`, no dimensions on it.

Leave at least 15 mm between views for dimensions. Hidden lines are off by
default; turn them on in a view only when no section shows the feature.

### Centre lines

Every hole and bore gets a centre mark, every bolt circle a chain circle, and
every symmetric part a symmetry line: `tdkit.center_mark(view, (x, y), r)`,
`tdkit.pitch_circle(view, (x, y), r)` and `tdkit.center_line(view, p1, p2)`, all
in view coordinates, all thin black chain lines. Leave
`ViewObject.ArcCenterMarks`, `HorizCenterLine` and `VertCenterLine` off: the
first marks every fillet and corner arc too, and the other two draw in the
preference colour, red on a default install.

### Dimensions

Pick edges by geometry, never by guessed index: run `tdkit.describe(view)` once,
then `tdkit.find_circle(view, r, center)`, `tdkit.find_line(view, p1, p2)` or
`tdkit.find_vertex(view, p)`. Coordinates are in the view's own 2D frame in
model units, and that frame is centred on the bounding box of the projection,
not on the model origin: a bore at the model origin of an asymmetric part sits
off-centre in the view. `tdkit.frame(view)` prints the frame's extent in one
line; compare it with the model's bounding box to get the offset, or locate one
known feature with `find_circle`. `describe()` lists every edge, hundreds of
lines for a plate with many holes.

An overall size often ends on an arc extreme or a tangent point (the tip and
widest points of a rounded outline), which is not a vertex of the projection.
Add one with `tdkit.cosmetic_vertex(view, (x, y))` in view coordinates and
dimension between the vertex names it returns. Do not use
`makeCosmeticVertex3d`: it mirrors Y, and the dimension measures to the wrong
point without any error.

Rules, each tied to a failure the reader would otherwise hit:

- **Every feature once.** Each size and position appears exactly once, on the
  view that shows the feature's true shape. Duplicates disagree after the first
  edit.
- **From datums.** Choose datums the part is made and measured from (the bore
  axis, a machined face) and dimension positions from them, not chained from
  feature to feature; chained tolerances add up.
- **Overall sizes**: length, width, thickness, always.
- **Patterns by count**: one callout for identical features,
  `12× M3 ↧5 EQ SP on ⌀100`, not twelve dimensions.
- **Hole and thread callouts** carry size, depth and count: `M92×1 ↧7`,
  `⌀109 ↧2.5`, `4× ⌀5.5 THRU`. Set the text with `tdkit.dim(..., text=...)`;
  `%.1f` in the text is filled with the measured value, always with a decimal
  point. Fixed text hides FreeCAD's tolerance fields, so a toleranced callout
  carries its tolerance in the text (`⌀109 +0.1/0 ↧2.5`).
- **Placement**: labels sit outside the part outline, in the gap between views,
  with larger dimensions further out so lines do not cross. A callout may sit
  inside a large empty bore when its leader stays clear of other leaders. A
  label on top of geometry, another label, or another dimension's line is a
  defect. Dimension X/Y are page millimetres from the view centre, +Y up.
- **Leaders into one feature**: when several callouts point at concentric
  features (bore, seat, thread, bolt circle), spread their leaders to different
  angles so no two cross. `tdkit.dim` draws diameters and radii ISO-referencing
  style (arrow on the circle, leader outwards, text on a shoulder); FreeCAD's
  default runs a line through the centre for every one.
- **Diameters vs radii**: full circles get ⌀, arcs up to a semicircle get R.
- **Estimated values** appear in parentheses as reference dimensions.

After building them, `tdkit.report_dims(page)` prints each dimension's measured
value. Every value must match the spec table; a mismatch means the dimension
picked the wrong edge.

### Threads (ISO 6410)

In the end view an internal thread is a thick circle at the minor diameter (the
modelled bore) and a thin three-quarter circle at the major diameter:
`tdkit.thread_circle(view, (x, y, z), 92)`. In section, the thread is thin lines
at the major diameter to the thread depth.

### Tolerances

The title block's general tolerance, ISO 2768-m, covers every dimension without
its own tolerance. Add explicit tolerances only where function needs them:
mating diameters, bearing seats, thread depth limits. A tolerance tighter than
±0.05 mm raises cost; add one only with a reason.

### Title block and notes

`tdkit.fill_title(page, ...)` blanks every field it is not given, so no sample
text ("ST1", "A. Nemesis", "AAA") survives. Fill at least: `title`,
`drawing_number`, `part_material`, `scale`, `general_tolerances`, `creator`,
`date_of_issue`, `revision_index`, `sheet_number` ("1 / 1"), `document_type`.
Print `page.Template.EditableTexts` to see the template's keys. Fields are short
(the title cell holds about 30 characters at 5 mm); longer text runs into the
next cell without an error, so check the title block on a crop.

Notes go above the title block with `tdkit.note`:

```text
1. ALL DIMENSIONS IN MILLIMETRES.
2. GENERAL TOLERANCES ISO 2768-m.
3. REMOVE ALL BURRS AND SHARP EDGES.
4. SURFACE FINISH Ra 3.2 UNLESS OTHERWISE STATED.
5. DIMENSIONS IN ( ) ARE REFERENCE, ESTIMATED FROM <source>.
```

Material and finish go in the title block (e.g. `EN AW-6061-T6, anodised`).

## Stage 4: export and inspect

Each round is: edit `drawing.py`, run it alone (the model is already saved),
read the reports it prints, then look at images.

1. `tdkit.report_dims(page)`: every measured value matches the spec table. A
   mismatch means a dimension picked the wrong edge.
2. `tdkit.export(page, "work/out/name")` writes `.pdf`, `.svg` and `.png`.
3. `tdkit.layout_report(page)`, after the export: every label that overlaps
   geometry, another label, another dimension's line, or its own extension line,
   with its page position. Move those labels and re-run until it reports none.
   It estimates label boxes from the text, so a hit within a millimetre can be a
   near miss; check those on a crop. "Geometry" includes cosmetic lines, so a
   label on a centre line or pitch circle is reported too.
4. Read the sheet scaled to 2000 px wide
   (`magick name.png -resize 2000x review.png`), once per round. Then crop only
   the regions you changed or that the report named
   (`magick name.png -crop WxH+X+Y +repage crop.png`) at full resolution. Every
   image read stays in the context for the rest of the task, so a full-size
   sheet per round is the most expensive habit in this loop.

On the images, check in this order:

1. Every view shows the right geometry, and the section hatches only cut
   material.
2. Nothing the layout report cannot see collides: captions, notes, the title
   block, the cutting-plane letters.
3. Every row of the spec table appears on the sheet exactly once, or is covered
   by a pattern callout.
4. Centre marks on every hole, bolt circles drawn, no marks on fillets.
5. Title block and notes complete, scale matches the page scale.
6. The machinist question: anything they would have to guess?

Fix in the script and run the next round. Plan the layout before the first run
(view positions from the view sizes, a gap for each dimension tier) so the
rounds fix details, not the arrangement.

Also save renders of the solid for the report:
`tdkit.screenshot_3d(doc, path, view)` for `Isometric`, `Axonometric`, and the
side that shows what the isometric hides. The helper trims the margins.

## FreeCAD behaviour that breaks scripts

- **Views project on a worker thread.** Right after `recompute()` a view has
  zero edges, and a dimension built then has no references. Call
  `tdkit.settle(views)` after adding or changing views, before reading edges.
- **Export renders the GUI page.** A page never opened in the GUI exports
  without its template and with stale geometry. `tdkit.export` opens it first.
- **Views follow the page scale.** `ScaleType` defaults to `Page`; setting
  `view.Scale` alone does nothing. Set `page.Scale`, or pass `scale=` to
  `tdkit.add_view`, which sets `ScaleType = "Custom"`.
- **Edge names are indices** into visible and hidden edges together; a change in
  the model renumbers them. Look edges up by geometry on every run.
- **The FreeCAD instance may be shared** with the user or other agents. Close
  and recreate only documents the script created; list documents before starting
  and leave the others alone. `saveAs` renames a document's Label to the file
  name while its Name stays, so match open documents by `FileName`, as
  `tdkit.reopen` does.
- **FreeCAD on macOS crashes when accessibility clients walk its widgets**
  (`QAccessibleCache` / `QMacAccessibilityElement` in the crash report). Do not
  inspect FreeCAD with AppleScript UI scripting or other accessibility tools.
  After a crash, `fc_run.py` gets "connection refused"; relaunch with
  `open -a FreeCAD` and run `fc_run.py --ping`. A Document Recovery dialog
  blocks every call until it is closed, and the ping then fails with "a modal
  dialog is open". List the documents it offers with
  `find ~/Library/Caches/FreeCAD/v1-1/Cache -name fc_recovery_file.xml -exec grep -H '<Label>' {} +`
  (a plain `ls` glob aborts in zsh when the cache is empty). If every label is a
  document this task created, quit FreeCAD, move those `FreeCAD_Doc_*`
  directories into the work directory, and relaunch. If any other label is
  listed, stop and ask the user: it may be their unsaved work.
- **Heavy booleans, fillets and chamfers can crash OCCT.** Develop geometry with
  `fc_run.py --headless`. Fuse hole tools into one compound and cut once, rather
  than cutting in a loop.
- **Crash report names are local time**
  (`~/Library/Logs/DiagnosticReports/freecad-YYYY-MM-DD-HHMMSS.ips`), not UTC.
  Before concluding that FreeCAD was quit rather than crashed, compare against
  `date` in local time and read the newest report's stack.

## Report

End with: the PDF and PNG paths, the isometric renders, the spec table with the
estimated rows called out, and anything the source left ambiguous (features seen
in one view only, conflicting numbers).
