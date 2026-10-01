# TechDraw objects and properties (FreeCAD 1.1)

Objects are created with `doc.addObject(type, name)` and attached to a page with
`page.addView(obj)`. Lengths are millimetres; page positions are measured from
the sheet's bottom-left corner.

## Page and template

| Object                      | Property         | Meaning                                          |
| --------------------------- | ---------------- | ------------------------------------------------ |
| `TechDraw::DrawPage`        | `Template`       | the `DrawSVGTemplate`                            |
|                             | `Scale`          | page scale; views with `ScaleType = Page` use it |
|                             | `ProjectionType` | `First angle` (ISO) or `Third angle` (ASME)      |
| `TechDraw::DrawSVGTemplate` | `Template`       | path to the `.svg`                               |
|                             | `EditableTexts`  | dict of title block fields; assign a whole dict  |
|                             | `Width`/`Height` | sheet size                                       |

Stock templates are under `App.getResourceDir() + "Mod/TechDraw/Templates/"`, in
`ISO/` (A0–A4, `ISO5457_advanced` with a full title block, `_minimal`, `_blank`)
and `ASME/`.

## Views

`TechDraw::DrawViewPart`:

| Property                                     | Meaning                                                  |
| -------------------------------------------- | -------------------------------------------------------- |
| `Source`                                     | list of objects to project                               |
| `Direction`                                  | view direction, from the part towards the viewer         |
| `XDirection`                                 | model direction that points right on the sheet           |
| `X`, `Y`                                     | view centre on the sheet                                 |
| `ScaleType`, `Scale`                         | `Page`, `Automatic` or `Custom`; `Scale` only for Custom |
| `Rotation`                                   | rotate the view on the sheet, degrees                    |
| `HardHidden`, `SmoothVisible`, `SeamVisible` | which edge classes to draw                               |
| `Caption`                                    | text under the view                                      |

Standard directions with Z up in the model: front `(0, -1, 0)`, top `(0, 0, 1)`,
right `(1, 0, 0)`, left `(-1, 0, 0)`, isometric `(1, -1, 1)` with
`XDirection (1, 1, 0)`, rear (the second face of a plate) `(0, 0, -1)` with
`XDirection (-1, 0, 0)`.

View object (`view.ViewObject`) properties: `LineWidth`, `HiddenWidth`,
`IsoWidth`, `ArcCenterMarks`, `CenterScale`, `HorizCenterLine`,
`VertCenterLine`, `ShowSectionLine`, `SectionLineStyle`.

Geometry queries, valid only after the view has finished projecting:

- `getEdgeByIndex(i)`, `getVertexByIndex(i)`: `Part.Edge` / `Part.Vertex` in the
  view's 2D frame, model units, centred on the view origin.
- `getVisibleEdges()`, `getHiddenEdges()`.

Cosmetic geometry (drawn on the view, not in the model):

- `makeCosmeticCircle3d(center, r)`,
  `makeCosmeticCircleArc3d(center, r, start_deg, end_deg)`,
  `makeCosmeticLine3D(p1, p2)`: model coordinates; return a tag.
- `getCosmeticEdge(tag).Format` is a dict `{style, weight, color, visible}`;
  read it, change keys, assign it back. Style 1 is continuous, 2 dashed, 4
  dash-dot (centre line).

`TechDraw::DrawViewSection` adds `BaseView`, `SectionNormal`, `SectionOrigin`
(model point the plane passes through), `SectionSymbol`.

`TechDraw::DrawViewDetail` adds `BaseView`, `AnchorPoint` (view 2D frame),
`Radius`, `Reference` (letter), and takes its own `Scale`.

## Dimensions

`TechDraw::DrawViewDimension`:

| Property                                            | Meaning                                                                         |
| --------------------------------------------------- | ------------------------------------------------------------------------------- |
| `Type`                                              | `Distance`, `DistanceX`, `DistanceY`, `Radius`, `Diameter`, `Angle`, `Angle3Pt` |
| `References2D`                                      | `[(view, "Edge3")]` or `[(view, "Vertex1"), (view, "Vertex4")]`                 |
| `X`, `Y`                                            | label offset from the view centre, page mm, +Y up                               |
| `FormatSpec`                                        | label text; `%.1f` style placeholders take the measured value                   |
| `Arbitrary`                                         | `True` when the label is fixed text with no measured value                      |
| `OverTolerance`, `UnderTolerance`, `EqualTolerance` | tolerance values                                                                |
| `TheoreticalExact`                                  | boxed basic dimension                                                           |

`getRawValue()` returns the measured value in model units.

Symbols for labels: `⌀` diameter, `↧` depth, `□` square, `±`, `×`.

## Annotations

`TechDraw::DrawViewAnnotation`: `Text` (list of lines), `TextSize`, `Font`, `X`,
`Y`.

`TechDraw::DrawViewBalloon`: `SourceView`, `Text`, `OriginX`, `OriginY` (for
assembly drawings).

## Export (GUI only)

`TechDrawGui.exportPageAsPdf(page, path)` and
`TechDrawGui.exportPageAsSvg(page, path)` render the open page's scene; open the
page first with `Gui.getDocument(doc.Name).getObject(page.Name).doubleClicked()`
and let the event loop run.
