"""Shared helpers: materials, collections, mesh construction (sweeps, tubes,
quad spheres) and small math utilities. Blender is Z-up; the character faces -Y."""
import math

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


# --------------------------------------------------------------------------- #
# Math
# --------------------------------------------------------------------------- #
def clamp(x, lo=0.0, hi=1.0):
    return lo if x < lo else hi if x > hi else x


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def lerp(a, b, t):
    return a + (b - a) * t


def catmull(points, n):
    """Resample a Catmull-Rom spline through `points` to `n` evenly spaced (in t) points."""
    pts = [Vector(p) for p in points]
    if len(pts) == 2:
        return [pts[0].lerp(pts[1], i / (n - 1)) for i in range(n)]
    ext = [pts[0] * 2 - pts[1]] + pts + [pts[-1] * 2 - pts[-2]]
    out = []
    segs = len(pts) - 1
    for i in range(n):
        u = i / (n - 1) * segs
        k = min(int(u), segs - 1)
        t = u - k
        p0, p1, p2, p3 = ext[k], ext[k + 1], ext[k + 2], ext[k + 3]
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                          + (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t))
    return out


# --------------------------------------------------------------------------- #
# Colours / materials
# --------------------------------------------------------------------------- #
def srgb(hexstr):
    h = hexstr.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


_mats = {}


def material(name, hexstr, rough=0.6, metal=0.0, spec=0.5, alpha=None, image=None, sheen=0.0,
             coat=0.0, emission=0.0):
    """Principled material. `image` (bpy image) drives Base Color (+ alpha when `alpha` == 'tex')."""
    if name in _mats:
        return _mats[name]
    m = bpy.data.materials.new(name)
    col = (*srgb(hexstr), 1.0)
    m.diffuse_color = col
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = col
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    bsdf.inputs["Specular IOR Level"].default_value = spec
    if sheen:
        bsdf.inputs["Sheen Weight"].default_value = sheen
        bsdf.inputs["Sheen Roughness"].default_value = 0.5
    if coat:
        bsdf.inputs["Coat Weight"].default_value = coat
        bsdf.inputs["Coat Roughness"].default_value = 0.25
    if emission:
        bsdf.inputs["Emission Color"].default_value = col
        bsdf.inputs["Emission Strength"].default_value = emission
    if image is not None:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = image
        tex.location = (-400, 200)
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        if alpha == "tex":
            nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
    if alpha is not None:
        if alpha != "tex":
            bsdf.inputs["Alpha"].default_value = alpha
        try:
            m.surface_render_method = "BLENDED"
        except Exception:
            m.blend_method = "BLEND"
        m.use_backface_culling = False
    _mats[name] = m
    return m


def image_from_pixels(name, w, h, rgba):
    """rgba: flat float list (linear-agnostic, stored as sRGB PNG) of length w*h*4, row 0 = bottom."""
    img = bpy.data.images.new(name, w, h, alpha=True)
    img.pixels.foreach_set(rgba)
    img.file_format = "PNG"
    img.pack()
    return img


# --------------------------------------------------------------------------- #
# Collections / objects
# --------------------------------------------------------------------------- #
def collection(name, parent=None):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    par = parent or bpy.context.scene.collection
    if c.name not in par.children:
        par.children.link(c)
    return c


def new_object(name, verts, faces, coll, mats, smooth_shade=True, mat_index=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.validate(clean_customdata=False)
    me.update()
    mats = mats if isinstance(mats, (list, tuple)) else [mats]
    for m in mats:
        me.materials.append(m)
    if mat_index is not None:
        for p, mi in zip(me.polygons, mat_index):
            p.material_index = mi
    for p in me.polygons:
        p.use_smooth = smooth_shade
    o = bpy.data.objects.new(name, me)
    coll.objects.link(o)
    return o


def activate(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def apply_modifiers(obj):
    activate(obj)
    for m in list(obj.modifiers):
        bpy.ops.object.modifier_apply(modifier=m.name)


def join(objs, name):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    o = bpy.context.active_object
    o.name = name
    o.data.name = name
    return o


def bvh_of(obj):
    me = obj.data
    mw = obj.matrix_world
    return BVHTree.FromPolygons([mw @ v.co for v in me.vertices], [tuple(p.vertices) for p in me.polygons])


# --------------------------------------------------------------------------- #
# Geometry builders (return verts, faces so callers can merge into one mesh)
# --------------------------------------------------------------------------- #
class Geo:
    """Accumulates verts/faces (+ per-face material index) for one mesh."""

    def __init__(self):
        self.verts, self.faces, self.mat = [], [], []

    def add(self, verts, faces, mat=0):
        off = len(self.verts)
        self.verts.extend(Vector(v) for v in verts)
        self.faces.extend(tuple(i + off for i in f) for f in faces)
        self.mat.extend([mat] * len(faces))
        return range(off, off + len(verts))

    def build(self, name, coll, mats, smooth_shade=True):
        return new_object(name, self.verts, self.faces, coll, mats, smooth_shade, self.mat)


def frames_along(path, up_hint):
    """Parallel-transport-ish frames: returns list of (T, B, N). up_hint: Vector or callable(i, P)."""
    out = []
    n = len(path)
    for i, p in enumerate(path):
        a = path[max(i - 1, 0)]
        b = path[min(i + 1, n - 1)]
        t = (b - a).normalized()
        u = up_hint(i, p) if callable(up_hint) else Vector(up_hint)
        bn = t.cross(u)
        if bn.length < 1e-6:
            bn = t.orthogonal()
        bn.normalize()
        nn = bn.cross(t).normalized()
        out.append((t, bn, nn))
    return out


def sweep(path, profile, sx, sy, up_hint=(0, 0, 1), closed_profile=True, cap_start=True, cap_end=True,
          closed_path=False):
    """Sweep a 2D profile [(px, py)] along `path`. At point i the profile is scaled by (sx[i], sy[i])
    in the (B, N) frame. A ring whose scale is 0 collapses into a single vertex (pointed tip)."""
    path = [Vector(p) for p in path]
    fr = frames_along(path, up_hint)
    verts, faces, rings = [], [], []
    m = len(profile)
    for i, p in enumerate(path):
        _t, b, nn = fr[i]
        if sx[i] < 1e-7 and sy[i] < 1e-7:
            rings.append([len(verts)])
            verts.append(p.copy())
            continue
        ring = []
        for px, py in profile:
            ring.append(len(verts))
            verts.append(p + b * (px * sx[i]) + nn * (py * sy[i]))
        rings.append(ring)
    seq = list(range(len(rings)))
    pairs = list(zip(seq, seq[1:])) + ([(seq[-1], seq[0])] if closed_path else [])
    for ia, ib in pairs:
        ra, rb = rings[ia], rings[ib]
        if len(ra) == 1 and len(rb) == 1:
            continue
        if len(ra) == 1:
            for k in range(m if closed_profile else m - 1):
                faces.append((ra[0], rb[k], rb[(k + 1) % m]))
        elif len(rb) == 1:
            for k in range(m if closed_profile else m - 1):
                faces.append((ra[k], ra[(k + 1) % m], rb[0]))
        else:
            for k in range(m if closed_profile else m - 1):
                k2 = (k + 1) % m
                faces.append((ra[k], ra[k2], rb[k2], rb[k]))
    if not closed_path and closed_profile:
        if cap_start and len(rings[0]) > 1:
            faces.append(tuple(reversed(rings[0])))
        if cap_end and len(rings[-1]) > 1:
            faces.append(tuple(rings[-1]))
    return verts, faces


def circle_profile(m=12):
    return [(math.cos(2 * math.pi * k / m), math.sin(2 * math.pi * k / m)) for k in range(m)]


def tube(points, radii, m=12, n=None, rounded=(True, True), up_hint=(0, 0, 1)):
    """Smooth round tube through `points` (Catmull-Rom resampled to n) with per-control radii,
    optional hemispherical end caps. Returns verts, faces."""
    n = n or max(6, len(points) * 4)
    path = catmull(points, n)
    rs = [r.x for r in catmull([Vector((r, 0, 0)) for r in radii], n)]
    k = 5
    if rounded[1]:
        d = (path[-1] - path[-2]).normalized()
        r_end, tip = rs[-1], path[-1]
        for j in range(1, k + 1):
            a = j / k * math.pi / 2
            path.append(tip + d * math.sin(a) * r_end)
            rs.append(math.cos(a) * r_end if j < k else 0.0)
    if rounded[0]:
        d = (path[0] - path[1]).normalized()
        r0, tip = rs[0], path[0]
        for j in range(1, k + 1):
            a = j / k * math.pi / 2
            path.insert(0, tip + d * math.sin(a) * r0)
            rs.insert(0, math.cos(a) * r0 if j < k else 0.0)
    return sweep(path, circle_profile(m), rs, rs, up_hint=up_hint)


def quad_sphere(cuts=16):
    """Unit cube-sphere (all quads, no poles). Returns verts (unit dirs), faces."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=2.0)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=cuts, use_grid_fill=True)
    verts = [v.co.normalized() for v in bm.verts]
    faces = [tuple(v.index for v in f.verts) for f in bm.faces]
    bm.free()
    return verts, faces


def uv_ellipsoid(center, radii, seg=24, rings=12, shape=None):
    """UV ellipsoid; `shape(dir)->Vector` may replace the radii scaling."""
    c = Vector(center)
    verts, faces = [], []
    verts.append(c + Vector((0, 0, -radii[2])) if shape is None else c + shape(Vector((0, 0, -1))))
    for r in range(1, rings):
        th = math.pi * r / rings - math.pi / 2
        for s in range(seg):
            ph = 2 * math.pi * s / seg
            d = Vector((math.cos(th) * math.cos(ph), math.cos(th) * math.sin(ph), math.sin(th)))
            verts.append(c + (shape(d) if shape else Vector((d.x * radii[0], d.y * radii[1], d.z * radii[2]))))
    verts.append(c + Vector((0, 0, radii[2])) if shape is None else c + shape(Vector((0, 0, 1))))
    top = len(verts) - 1
    for s in range(seg):
        faces.append((0, 1 + (s + 1) % seg, 1 + s))
    for r in range(rings - 2):
        a, b = 1 + r * seg, 1 + (r + 1) * seg
        for s in range(seg):
            s2 = (s + 1) % seg
            faces.append((a + s, a + s2, b + s2, b + s))
    last = 1 + (rings - 2) * seg
    for s in range(seg):
        faces.append((last + s, last + (s + 1) % seg, top))
    return verts, faces


def disc(points_2d, to3d, center_2d=None):
    """Fan-triangulated flat polygon. points_2d: loop of (x, z); to3d(x, z)->Vector."""
    cx = sum(p[0] for p in points_2d) / len(points_2d) if center_2d is None else center_2d[0]
    cz = sum(p[1] for p in points_2d) / len(points_2d) if center_2d is None else center_2d[1]
    verts = [to3d(cx, cz)] + [to3d(x, z) for x, z in points_2d]
    n = len(points_2d)
    faces = [(0, 1 + i, 1 + (i + 1) % n) for i in range(n)]
    return verts, faces
