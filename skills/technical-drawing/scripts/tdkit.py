"""Helpers for building TechDraw pages from a script running inside FreeCAD.

Import from a drawing script that fc_run.py executes:

    import sys, importlib
    sys.path.insert(0, "/abs/path/to/skills/technical-drawing/scripts")
    import tdkit; importlib.reload(tdkit)

Coordinates: view X/Y and dimension X/Y are page millimetres. A view's X/Y is
its centre measured from the sheet's bottom-left corner. A dimension's X/Y is
the label position measured from its view's centre, +Y up. Edge geometry from
edges() is in model units in the view's own 2D frame (centred on the view,
unscaled), so multiply by the view scale to get page millimetres.
"""
import collections
import math
import os
import subprocess
import time

import FreeCAD as App
import FreeCADGui as Gui
import TechDraw  # noqa: F401  registers the TechDraw document types
import TechDrawGui
from PySide import QtGui

TEMPLATES = os.path.join(App.getResourceDir(), "Mod", "TechDraw", "Templates")


def pump(seconds=0.5):
    """Run the Qt event loop so TechDraw's worker threads can deliver results."""
    end = time.time() + seconds
    while time.time() < end:
        QtGui.QApplication.processEvents()
        time.sleep(0.02)


def settle(views, timeout=60):
    """Recompute and wait until every view has finished hidden-line removal.

    TechDraw projects geometry on a worker thread; right after recompute() a
    view reports zero edges and any dimension built on it has no references.
    """
    doc = views[0].Document
    doc.recompute()
    end = time.time() + timeout
    while time.time() < end:
        QtGui.QApplication.processEvents()
        ready = all(v.getVisibleEdges() for v in views)
        if ready and not any("Touched" in v.State for v in views):
            pump(0.2)
            return
        time.sleep(0.05)
    raise TimeoutError("TechDraw views did not finish projecting: "
                       + ", ".join(v.Name for v in views if not v.getVisibleEdges()))


def new_document(name, path=None):
    """Return a fresh, empty document called `name`.

    An open document of that name is closed when it is unsaved (a previous
    run's) or saved at `path` (the file this script writes). Any other saved
    document of that name may be someone else's work in a shared FreeCAD, so
    it is left open and this raises; pick a name specific to the task.
    """
    target = os.path.abspath(path) if path else None
    for open_name, d in list(App.listDocuments().items()):
        if open_name != name:
            continue
        if d.FileName and os.path.abspath(d.FileName) != target:
            raise RuntimeError(f"document {name!r} is open and saved at {d.FileName}; "
                               "use a different document name")
        App.closeDocument(open_name)
    return App.newDocument(name)


def list_documents():
    """Print the open documents (name, label, file) before touching any."""
    for name, d in App.listDocuments().items():
        print(f"{name}  label={d.Label!r}  file={d.FileName or '(unsaved)'}")


def reopen(model_path, drawing_path):
    """Open the saved model and save it at once as the drawing document.

    The drawing script starts from the model file, which holds no page, so a
    re-run never has to delete the previous run's TechDraw objects: removing a
    page with its views in a loop segfaults FreeCAD 1.1 in
    DrawPage::unsetupObject. Any open copy of either file is closed first.
    """
    targets = {os.path.abspath(model_path), os.path.abspath(drawing_path)}
    for name, d in list(App.listDocuments().items()):
        if d.FileName and os.path.abspath(d.FileName) in targets:
            App.closeDocument(name)
    doc = App.openDocument(model_path)
    doc.saveAs(drawing_path)
    return doc


def new_page(doc, template="ISO/A3_Landscape_ISO5457_advanced.svg", scale=1.0,
             projection="First angle", name="Page"):
    """Create a page on a stock template. Views default to the page scale."""
    page = doc.addObject("TechDraw::DrawPage", name)
    tpl = doc.addObject("TechDraw::DrawSVGTemplate", name + "Template")
    tpl.Template = os.path.join(TEMPLATES, template)
    page.Template = tpl
    page.Scale = scale
    page.ProjectionType = projection
    return page


def fill_title(page, **fields):
    """Set title block fields; all others are blanked. Unknown keys raise."""
    tpl = page.Template
    texts = dict(tpl.EditableTexts)
    unknown = set(fields) - set(texts)
    if unknown:
        raise KeyError(f"template has no fields {sorted(unknown)}; it has {sorted(texts)}")
    # Template placeholders (ST1, A. Nemesis, AAA...) print as real data, so
    # every field not given is blanked rather than left at its sample value.
    texts = {k: "" for k in texts}
    texts.update({k: str(v) for k, v in fields.items()})
    tpl.EditableTexts = texts


def add_view(page, source, direction, x, y, xdir=None, name=None, scale=None):
    """Add a projected view of `source` (list of objects) at page point (x, y)."""
    doc = page.Document
    v = doc.addObject("TechDraw::DrawViewPart", name or "View")
    page.addView(v)
    v.Source = source
    v.Direction = App.Vector(*direction)
    if xdir is not None:
        v.XDirection = App.Vector(*xdir)
    if scale is not None:
        v.ScaleType = "Custom"
        v.Scale = scale
    v.X, v.Y = x, y
    return v


def add_section(page, base, source, normal, origin, x, y, symbol="A", name=None, xdir=None):
    """Add a section view cut through `origin` with plane normal `normal`.

    The arrows on the base view point along -normal (the viewing direction).
    """
    doc = page.Document
    s = doc.addObject("TechDraw::DrawViewSection", name or f"Section{symbol}")
    page.addView(s)
    s.BaseView = base
    s.Source = source
    s.ScaleType = base.ScaleType
    s.Scale = base.Scale
    s.SectionNormal = App.Vector(*normal)
    s.Direction = App.Vector(*normal)
    s.SectionOrigin = App.Vector(*origin)
    if xdir is not None:
        s.XDirection = App.Vector(*xdir)
    s.SectionSymbol = symbol
    s.X, s.Y = x, y
    return s


def add_detail(page, base, anchor, radius, scale, x, y, ref="D", name=None):
    """Add a detail view magnifying a circle of `radius` around `anchor`.

    anchor is in the base view's frame (as describe() prints). The detail's
    own edges come back in that frame minus the anchor, unscaled. A detail of
    a section view loses its hatching in FreeCAD 1.1.
    """
    d = page.Document.addObject("TechDraw::DrawViewDetail", name or f"Detail{ref}")
    page.addView(d)
    d.BaseView = base
    d.Source = base.Source
    d.Direction = base.Direction
    d.XDirection = base.XDirection
    d.AnchorPoint = App.Vector(anchor[0], anchor[1], 0)
    d.Radius = radius
    d.ScaleType = "Custom"
    d.Scale = scale
    d.Reference = ref
    d.X, d.Y = x, y
    return d


def frame(view):
    """Print a view's 2D frame: edge bounding box and scale, in one line.

    Cheaper than describe() for mapping model points into the view: compare
    the box with the model's known extents to get the offset.
    """
    bb = None
    for _, e in edges(view):
        bb = e.BoundBox if bb is None else bb.united(e.BoundBox)
    print(f"{view.Name}: x[{bb.XMin:.2f}, {bb.XMax:.2f}] y[{bb.YMin:.2f}, {bb.YMax:.2f}] "
          f"scale {view.getScale()}")
    return bb


def edges(view):
    """All projected edges of a view as (name, edge) pairs, e.g. ("Edge7", e).

    The name is what dimension References2D expects. Visible and hidden edges
    share one index space, so use these names, not positions in
    getVisibleEdges().
    """
    out, i = [], 0
    while True:
        try:
            e = view.getEdgeByIndex(i)
        except Exception:
            break
        if e is None:
            break
        out.append((f"Edge{i}", e))
        i += 1
    return out


def vertices(view):
    out, i = [], 0
    while True:
        try:
            p = view.getVertexByIndex(i)
        except Exception:
            break
        if p is None:
            break
        out.append((f"Vertex{i}", p))
        i += 1
    return out


def describe(view, limit=400):
    """Print every edge so the right reference can be picked by geometry."""
    for name, e in edges(view)[:limit]:
        c, bb = e.Curve, e.BoundBox
        kind = type(c).__name__
        extra = ""
        if hasattr(c, "Radius"):
            extra = f" r={c.Radius:.3f} c=({c.Center.x:.2f},{c.Center.y:.2f})"
        print(f"{view.Name}.{name} {kind} "
              f"x[{bb.XMin:.2f},{bb.XMax:.2f}] y[{bb.YMin:.2f},{bb.YMax:.2f}]{extra}")


def find_circle(view, radius, center=None, tol=0.05):
    """Name of the circle/arc edge with this radius, nearest `center` if given."""
    best = None
    for name, e in edges(view):
        c = e.Curve
        if not hasattr(c, "Radius") or abs(c.Radius - radius) > tol:
            continue
        d = 0 if center is None else math.hypot(c.Center.x - center[0], c.Center.y - center[1])
        if best is None or d < best[0]:
            best = (d, name)
    if best is None:
        raise LookupError(f"{view.Name}: no circle of radius {radius}")
    return best[1]


def find_line(view, p1, p2, tol=0.1):
    """Name of the straight edge whose end points are p1 and p2 (either order)."""
    for name, e in edges(view):
        if type(e.Curve).__name__ not in ("Line", "LineSegment"):
            continue
        a, b = e.Vertexes[0].Point, e.Vertexes[-1].Point
        for q1, q2 in ((a, b), (b, a)):
            if (math.hypot(q1.x - p1[0], q1.y - p1[1]) < tol
                    and math.hypot(q2.x - p2[0], q2.y - p2[1]) < tol):
                return name
    raise LookupError(f"{view.Name}: no line {p1} -> {p2}")


def find_vertex(view, p, tol=0.1):
    for name, v in vertices(view):
        if math.hypot(v.Point.x - p[0], v.Point.y - p[1]) < tol:
            return name
    raise LookupError(f"{view.Name}: no vertex at {p}")


def cosmetic_vertex(view, p):
    """Add a vertex at view-frame point p = (x, y) and return its name.

    Use it for dimensions that end on an arc extreme or a tangent point, which
    are not vertices of the projection. Takes view coordinates (as describe()
    prints them): makeCosmeticVertex3d mirrors Y in FreeCAD 1.1, so a
    dimension built on it measures to the wrong point without any error.
    """
    tag = view.makeCosmeticVertex(App.Vector(p[0], p[1], 0))
    view.Document.recompute()
    # The recompute re-projects the view on TechDraw's worker thread; the
    # new vertex is listed only once that finishes.
    end = time.time() + 30
    while time.time() < end:
        for name, v in vertices(view):
            if math.hypot(v.Point.x - p[0], v.Point.y - p[1]) < 1e-6:
                return name
        pump(0.1)
    raise LookupError(f"{view.Name}: cosmetic vertex {tag} at {p} not found")


def dim(page, view, kind, refs, x, y, text=None, name=None, size=3.5):
    """Add a dimension.

    kind: Distance, DistanceX, DistanceY, Radius, Diameter, Angle.
    refs: one edge name, or two vertex/edge names.
    x, y: label position in page mm from the view centre, +Y up.
    text: label text. "%.1f" style specifiers are filled with the measured
          value here, with a decimal point whatever the system locale;
          FreeCAD's own formatting follows the locale and can print a
          comma. Fixed text replaces FreeCAD's tolerance display, so write
          any tolerance into the text ("⌀109 +0.1/0").
    size: lettering height in mm (ISO 3098: 3.5 on A3/A2, 5 on A1/A0).
    The view must have settled (settle()) before this is called.
    """
    doc = page.Document
    d = doc.addObject("TechDraw::DrawViewDimension", name or "Dim")
    d.Type = kind
    refs = [refs] if isinstance(refs, str) else list(refs)
    d.References2D = [(view, r) for r in refs]
    page.addView(d)
    d.X, d.Y = x, y
    d.ViewObject.Fontsize = size
    d.ViewObject.LineWidth = 0.25          # ISO 128 thin line
    if kind in ("Diameter", "Radius"):
        # The default draws a line across the whole circle through its centre,
        # so every callout on concentric features crosses at the centre.
        # Referencing puts horizontal text on a shoulder, and Confined starts
        # the leader at the circle and runs it outwards.
        d.ViewObject.StandardAndStyle = "ISO Referencing"
        d.ViewObject.RenderingExtent = "Confined"
    if text is not None:
        if "%" in text:
            doc.recompute()
            text = text % d.getRawValue()
        d.FormatSpec = text
        d.Arbitrary = True
    return d


def note(page, lines, x, y, size=3.5, name=None):
    """Free text block centred on page point (x, y)."""
    a = page.Document.addObject("TechDraw::DrawViewAnnotation", name or "Note")
    page.addView(a)
    a.Text = list(lines)
    a.TextSize = size
    a.X, a.Y = x, y
    return a


def _chain(view, tag):
    edge = view.getCosmeticEdge(tag)
    fmt = edge.Format
    fmt.update(style=4, weight=0.25, color=(0.0, 0.0, 0.0, 1.0))   # thin dash-dot
    edge.Format = fmt
    return tag


def center_mark(view, center, radius, overshoot=2.0):
    """Cross of thin chain lines through a hole centre, in view coordinates.

    Use this on holes and bores instead of ArcCenterMarks, which also marks
    every fillet and corner arc. Lines run 2 mm (page) past the circle.
    """
    x, y = center
    r = radius + overshoot / view.getScale()
    return [_chain(view, view.makeCosmeticLine(App.Vector(x - r, y, 0), App.Vector(x + r, y, 0))),
            _chain(view, view.makeCosmeticLine(App.Vector(x, y - r, 0), App.Vector(x, y + r, 0)))]


def center_line(view, p1, p2):
    """Thin chain line between two view-coordinate points (symmetry axes)."""
    return _chain(view, view.makeCosmeticLine(App.Vector(p1[0], p1[1], 0), App.Vector(p2[0], p2[1], 0)))


def pitch_circle(view, center, radius):
    """Thin chain circle for a bolt circle, in view coordinates."""
    return _chain(view, view.makeCosmeticCircle(App.Vector(center[0], center[1], 0), radius))


def thread_circle(view, center, major_diameter):
    """Draw an internal thread's major diameter as a thin 3/4 circle (ISO 6410).

    `center` is the hole axis point in model coordinates (x, y, z). The bore
    at the tap-drill (minor) diameter must exist as real geometry; the thread
    itself is never modelled.
    """
    tag = view.makeCosmeticCircleArc3d(App.Vector(*center), major_diameter / 2, 0, 270)
    edge = view.getCosmeticEdge(tag)
    fmt = edge.Format
    fmt.update(style=1, weight=0.25)   # continuous thin line
    edge.Format = fmt
    return tag


def report_dims(page):
    """Print each dimension's measured value and label so mismatches show up."""
    for o in page.Views:
        if o.TypeId != "TechDraw::DrawViewDimension":
            continue
        try:
            raw = o.getRawValue()
        except Exception as ex:  # a dimension whose reference vanished
            raw = f"ERROR {ex}"
        refs = [sub for _, subs in o.References2D for sub in subs]
        print(f"{o.Name}: {o.Type} raw={raw} spec={o.FormatSpec!r} refs={refs} at ({o.X}, {o.Y})")


def _label_box(d):
    """Centre, unit direction and half sizes of a dimension label, page mm."""
    v = d.References2D[0][0]
    fs = d.ViewObject.Fontsize.Value
    text = d.getText()
    c = (v.X.Value + d.X.Value, v.Y.Value + d.Y.Value)
    u = (1.0, 0.0)
    try:
        a1, a2 = d.getArrowPositions()
        dx, dy = a2.x - a1.x, a2.y - a1.y
        n = math.hypot(dx, dy)
        if n > 1e-6:
            u = (dx / n, dy / n)
            if u[0] < -1e-9 or (abs(u[0]) < 1e-9 and u[1] < 0):
                u = (-u[0], -u[1])
    except Exception:
        pass
    # ISO lettering: character width about 0.6 of the height, plus margin.
    return c, u, (0.6 * fs * max(len(text), 1) + 1.0) / 2, 0.65 * fs, text


def _to_local(p, c, u):
    x, y = p[0] - c[0], p[1] - c[1]
    return (x * u[0] + y * u[1], -x * u[1] + y * u[0])


def _seg_hits_box(p, q, c, u, hw, hh):
    """Liang-Barsky clip of segment pq against the label's rotated box."""
    (x0, y0), (x1, y1) = _to_local(p, c, u), _to_local(q, c, u)
    t0, t1, dx, dy = 0.0, 1.0, x1 - x0, y1 - y0
    for pp, qq in ((-dx, x0 + hw), (dx, hw - x0), (-dy, y0 + hh), (dy, hh - y0)):
        if abs(pp) < 1e-12:
            if qq < 0:
                return False
        else:
            t = qq / pp
            if pp < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
            if t0 > t1:
                return False
    return True


def _boxes_overlap(b1, b2):
    """Separating-axis test for two rotated label boxes."""
    def corners(c, u, hw, hh):
        n = (-u[1], u[0])
        return [(c[0] + sx * hw * u[0] + sy * hh * n[0],
                 c[1] + sx * hw * u[1] + sy * hh * n[1])
                for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    k1, k2 = corners(*b1[:4]), corners(*b2[:4])
    for c, u, *_ in (b1, b2):
        for ax in (u, (-u[1], u[0])):
            p1 = [x * ax[0] + y * ax[1] for x, y in k1]
            p2 = [x * ax[0] + y * ax[1] for x, y in k2]
            if max(p1) < min(p2) or max(p2) < min(p1):
                return False
    return True


def layout_report(page):
    """Print every dimension label that overlaps drawn geometry, another
    dimension's line, or another label, and any label off the sheet frame.
    Returns the number of problems.

    Label boxes are estimated from position, text length, font size and
    the dimension line's direction, so a hit within about 1 mm can be a
    near miss; anything listed is worth a look on a crop. Run it before
    reading the PNG: it names every overlap at once, with page mm
    coordinates measured from the sheet's bottom-left corner.
    """
    dims = [o for o in page.Views if o.TypeId == "TechDraw::DrawViewDimension"]
    views = [o for o in page.Views if o.isDerivedFrom("TechDraw::DrawViewPart")]
    boxes = {d.Name: _label_box(d) for d in dims}

    def to_page(v, p):
        s = v.getScale()
        return (v.X.Value + p.x * s, v.Y.Value + p.y * s)

    geometry = []
    for v in views:
        for _, e in edges(v):
            pts = [to_page(v, p) for p in e.discretize(Distance=1.0)] \
                if not type(e.Curve).__name__.startswith("Line") else \
                [to_page(v, e.Vertexes[0].Point), to_page(v, e.Vertexes[-1].Point)]
            geometry.append((v.Name, pts))
    dim_lines, ext_lines = {}, {}
    for d in dims:
        v = d.References2D[0][0]
        try:
            a1, a2 = d.getArrowPositions()
        except Exception:
            continue
        dim_lines[d.Name] = (to_page(v, a1), to_page(v, a2))
        if d.Type in ("Distance", "DistanceX", "DistanceY"):
            # getLinearPoints() reports Y negated relative to the view frame and
            # multiplied by the view scale; getArrowPositions() is unscaled.
            s = v.getScale()
            p1, p2 = (App.Vector(p.x / s, -p.y / s, 0) for p in d.getLinearPoints())
            if (p1 - a1).Length + (p2 - a2).Length > (p1 - a2).Length + (p2 - a1).Length:
                p1, p2 = p2, p1
            ext_lines[d.Name] = [(to_page(v, p1), to_page(v, a1)),
                                 (to_page(v, p2), to_page(v, a2))]

    w, h = page.Template.Width.Value, page.Template.Height.Value
    problems = 0
    for d in dims:
        c, u, hw, hh, text = boxes[d.Name]
        hits = []
        for vname, pts in geometry:
            if any(_seg_hits_box(p, q, c, u, hw, hh) for p, q in zip(pts, pts[1:])):
                hits.append(f"geometry of {vname}")
        own = dim_lines.get(d.Name)
        # ISO puts the text above its own line, so the line may graze the
        # box edge but must not run through the middle of the text.
        if own and _seg_hits_box(own[0], own[1], c, u, hw * 0.8, hh * 0.4):
            hits.append("its own dimension line runs through it")
        for p, q in ext_lines.get(d.Name, []):
            if _seg_hits_box(p, q, c, u, hw * 0.8, hh * 0.6):
                hits.append("its own extension line runs through it")
        for other, (p, q) in dim_lines.items():
            if other != d.Name and _seg_hits_box(p, q, c, u, hw, hh):
                hits.append(f"line of {other} {boxes[other][4]!r}")
        for other, segs in ext_lines.items():
            if other != d.Name and any(_seg_hits_box(p, q, c, u, hw, hh) for p, q in segs):
                hits.append(f"extension line of {other} {boxes[other][4]!r}")
        for other, b in boxes.items():
            if other != d.Name and _boxes_overlap(boxes[d.Name], b):
                hits.append(f"label of {other} {b[4]!r}")
        if not (20 < c[0] < w - 10 and 10 < c[1] < h - 10):
            hits.append("outside the drawing frame")
        if hits:
            problems += 1
            print(f"OVERLAP {d.Name} {text!r} at ({c[0]:.0f}, {c[1]:.0f}): "
                  + "; ".join(sorted(set(hits))))
    print(f"{len(dims)} labels checked, {problems} with problems")
    return problems


def export(page, out_base, dpi=150):
    """Open the page in the GUI, then write <out_base>.pdf, .svg and .png.

    Export renders the GUI scene, which exists and refreshes only while the
    page is open; exporting a page that was never opened drops the template
    and uses stale view geometry.
    """
    Gui.getDocument(page.Document.Name).getObject(page.Name).doubleClicked()
    pump(1.5)
    TechDrawGui.exportPageAsPdf(page, out_base + ".pdf")
    TechDrawGui.exportPageAsSvg(page, out_base + ".svg")
    w = int(dpi / 25.4 * page.Template.Width.Value)
    subprocess.run(["rsvg-convert", "-w", str(w), "-b", "white",
                    out_base + ".svg", "-o", out_base + ".png"], check=True)
    print("exported", out_base + ".{pdf,svg,png}")


def add_lights(av):
    """Put a key, a fill and an under light at the top of a 3D view's scene graph.

    Some FreeCAD builds render every face near-black (the headlight has no
    effect even with EnableHeadlight set), which hides all shading in
    screenshots. The lights go into this view only and are added once.
    """
    from pivy import coin
    sg = av.getSceneGraph()
    if any(sg.getChild(i).getName() == "tdkit_lights" for i in range(sg.getNumChildren())):
        return
    grp = coin.SoGroup()
    grp.setName("tdkit_lights")
    for direction, intensity in (((-0.4, 0.5, -1.0), 0.85), ((0.6, -0.3, -0.6), 0.35),
                                  ((0.3, 0.4, 1.0), 0.7)):
        light = coin.SoDirectionalLight()
        light.direction.setValue(*direction)
        light.intensity.setValue(intensity)
        grp.addChild(light)
    sg.insertChild(grp, 0)


def screenshot_3d(doc, out_png, view="Isometric", size=(1400, 1000)):
    """Save a shaded 3D screenshot of the document from a standard direction.

    view: Isometric, Front, Top, Right, Rear, Bottom, Left, Axonometric.
    """
    av = Gui.getDocument(doc.Name).mdiViewsOfType("Gui::View3DInventor")[0]
    add_lights(av)
    getattr(av, "view" + view)()
    av.fitAll()
    pump(0.3)
    # On macOS a 3D view hidden behind the page tab saves a blank frame unless
    # the framing is re-issued synchronously right before saveImage().
    av.fitAll()
    av.saveImage(out_png, size[0], size[1], "White")
    # fitAll leaves wide margins; trim to the part plus a small border.
    subprocess.run(["magick", out_png, "-trim", "+repage", "-bordercolor", "white",
                    "-border", "30", out_png], check=True)
    print("saved", out_png)
