"""
Builds the chibi "Kyle" character from the hero illustration and exports it as
model/kyle.glb for the website.

Run (from the repo root):
    /Applications/Blender.app/Contents/MacOS/Blender -b -P blender/build_kyle.py
Optional preview render (no export):
    ... -P blender/build_kyle.py -- --render blender/preview.png [--laugh] [--yaw 35] --no-export

Base: big mochi head (~55% of the height), small pear torso, stubby legs and
short arms. Hair is built from tapered clumps that hug the skull.

Conventions (Blender is Z-up, the character faces -Y; glTF export converts to
Y-up facing +Z). Animatable pivots are empties named:
    Root > Hips > Torso > Head
                        > ShoulderR > ElbowR      (waving arm, viewer's left)
                        > ShoulderL > ElbowL
                > LegR, LegL
Two face groups live under Head: FaceHappy (default) and FaceLaugh (hidden).
Object names ending in "_noline" get no toon outline on the web.
"""
import bpy
import bmesh
import math
import os
import random
import sys
from mathutils import Vector

random.seed(11)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_GLB = os.path.join(ROOT_DIR, "model", "kyle.glb")

# --------------------------------------------------------------------------- #
# Scene + helpers
# --------------------------------------------------------------------------- #
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def srgb(hexstr):
    h = hexstr.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


_mats = {}


def mat(name, hexstr, rough=0.85):
    if name in _mats:
        return _mats[name]
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except Exception:
        pass
    col = (*srgb(hexstr), 1.0)
    m.diffuse_color = col
    nt = m.node_tree
    if nt:
        bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if bsdf is None:
            out = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"), None) \
                or nt.nodes.new("ShaderNodeOutputMaterial")
            bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
            nt.links.new(bsdf.outputs[0], out.inputs[0])
        bsdf.inputs["Base Color"].default_value = col
        bsdf.inputs["Roughness"].default_value = rough
    _mats[name] = m
    return m


SKIN = mat("Skin", "#f6d2b4")
HAIR = mat("Hair", "#272934")
HAIR_HI = mat("HairHighlight", "#5d6076")
SHIRT = mat("Shirt", "#3b3a44")
SHIRT_DARK = mat("ShirtCollar", "#2a2a33")
PANTS = mat("Pants", "#1f2029")
SHOE = mat("Shoes", "#18181f")
PRINT = mat("Print", "#4a74ad")
PRINT_INK = mat("PrintInk", "#24324a")
LINE = mat("Line", "#3a1d16")
FRAME = mat("Frame", "#4b2219")
TEETH = mat("Teeth", "#ffffff")
MOUTH = mat("Mouth", "#8f2f2f")
TONGUE = mat("Tongue", "#e9827a")
BLUSH = mat("Blush", "#f3a79c")
BLUSH_HOT = mat("BlushHot", "#ef7f78")
SWEAT = mat("Sweat", "#9fd4ee")
BUD = mat("Earbud", "#22232b")


def empty(name, loc, parent=None):
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 0.08
    scene.collection.objects.link(e)
    e.location = loc
    if parent is not None:
        set_parent(e, parent)
    return e


def set_parent(child, parent):
    bpy.context.view_layer.update()
    mw = child.matrix_world.copy()
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()
    child.matrix_world = mw


def finish(obj, name, material, parent=None, smooth=True):
    obj.name = name
    if obj.type == "MESH":
        obj.data.name = name
        obj.data.materials.clear()
        obj.data.materials.append(material)
        if smooth:
            for p in obj.data.polygons:
                p.use_smooth = True
    if parent is not None:
        set_parent(obj, parent)
    return obj


def apply_xform(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


def sphere(name, loc, scale, material, parent=None, seg=32, rings=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, radius=1, location=loc)
    o = bpy.context.active_object
    o.scale = scale
    apply_xform(o)
    return finish(o, name, material, parent)


def cyl(name, a, b, r1, r2, material, parent=None, verts=24, caps=True):
    a, b = Vector(a), Vector(b)
    d = b - a
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=d.length,
                                    location=(a + b) / 2,
                                    end_fill_type="NGON" if caps else "NOTHING")
    o = bpy.context.active_object
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    apply_xform(o)
    return finish(o, name, material, parent)


def join(objs, name, material=None, parent=None):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    o = bpy.context.active_object
    o.name = name
    o.data.name = name
    if material is not None:
        o.data.materials.clear()
        o.data.materials.append(material)
    if parent is not None:
        set_parent(o, parent)
    return o


def capsule(name, a, b, r, material, parent=None, r2=None):
    r2 = r if r2 is None else r2
    parts = [cyl(name + "_c", a, b, r, r2, material, verts=16, caps=False),
             sphere(name + "_a", a, (r, r, r), material, seg=16, rings=8),
             sphere(name + "_b", b, (r2, r2, r2), material, seg=16, rings=8)]
    return join(parts, name, material, parent)


def tube(name, pts, radius, material, parent=None, poly=False, radii=None, res=10, bevel_res=3):
    """Bevelled curve through pts (optionally tapered with per-point radii), as a mesh."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = radius
    cu.bevel_resolution = bevel_res
    cu.use_fill_caps = True
    cu.resolution_u = res
    radii = radii or [1.0] * len(pts)
    if poly:
        sp = cu.splines.new("POLY")
        sp.points.add(len(pts) - 1)
        for p, co, r in zip(sp.points, pts, radii):
            p.co = (*co, 1)
            p.radius = r
    else:
        sp = cu.splines.new("BEZIER")
        sp.bezier_points.add(len(pts) - 1)
        for p, co, r in zip(sp.bezier_points, pts, radii):
            p.co = co
            p.radius = r
            p.handle_left_type = p.handle_right_type = "AUTO"
    o = bpy.data.objects.new(name, cu)
    scene.collection.objects.link(o)
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.convert(target="MESH")
    o = bpy.context.active_object
    return finish(o, name, material, parent)


def lathe(name, profile, material, parent=None, yscale=1.0, cx=0.0, seg=32):
    """Surface of revolution around the Z axis. profile = [(z, r), ...] bottom→top;
    r == 0 at either end closes the shape with a pole."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    rings = []
    for z, r in profile:
        if r <= 1e-6:
            rings.append([bm.verts.new((cx, 0, z))])
        else:
            rings.append([bm.verts.new((cx + math.cos(a) * r, math.sin(a) * r * yscale, z))
                          for a in (2 * math.pi * i / seg for i in range(seg))])
    for lo, hi in zip(rings, rings[1:]):
        if len(lo) == 1:
            for i in range(seg):
                bm.faces.new((lo[0], hi[(i + 1) % seg], hi[i]))
        elif len(hi) == 1:
            for i in range(seg):
                bm.faces.new((lo[i], lo[(i + 1) % seg], hi[0]))
        else:
            for i in range(seg):
                bm.faces.new((lo[i], lo[(i + 1) % seg], hi[(i + 1) % seg], hi[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    scene.collection.objects.link(o)
    return finish(o, name, material, parent)


def profile_r(profile, z):
    for (z0, r0), (z1, r1) in zip(profile, profile[1:]):
        if z0 <= z <= z1:
            return r0 + (r1 - r0) * (z - z0) / max(z1 - z0, 1e-6)
    return 0.0


def flat_shape(name, outline_xz, y, material, parent=None, thickness=0.006):
    """Thin extruded polygon facing -Y (decals: mouths, prints). `y` is a number or
    a function y(x, z) so the decal can hug a curved surface."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    yf = y if callable(y) else (lambda _x, _z: y)
    vs = [bm.verts.new((x, yf(x, z), z)) for x, z in outline_xz]
    f = bm.faces.new(vs)
    ext = bmesh.ops.extrude_face_region(bm, geom=[f])
    moved = [e for e in ext["geom"] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=moved, vec=(0, thickness, 0))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    scene.collection.objects.link(o)
    return finish(o, name, material, parent, smooth=False)


# --------------------------------------------------------------------------- #
# Proportions (chibi base)
# --------------------------------------------------------------------------- #
HEAD_C = Vector((0, 0, 1.42))
RX, RY, RZ = 0.48, 0.44, 0.56


def head_shape(n):
    """Mochi head: a slightly squared-off ellipsoid, narrower and flatter toward the chin.
    n is a direction; returns the surface point relative to HEAD_C."""
    n = Vector(n).normalized()
    s = (n.x ** 4 + n.y ** 4 + n.z ** 4) ** -0.25
    p = n * (1 + 0.28 * (s - 1))
    p = Vector((p.x * RX, p.y * RY, p.z * RZ))
    if p.z < 0:
        t = -p.z / RZ
        p.x *= 1 - 0.16 * t * t
        p.y *= 1 - 0.06 * t
        p.z *= 1 - 0.08 * t
    return p


def sph_dir(theta, phi):
    """theta from the crown (0 = top), phi around the head (0 = front/-Y, +pi/2 = +X)."""
    return Vector((math.sin(theta) * math.sin(phi), -math.sin(theta) * math.cos(phi), math.cos(theta)))


# --------------------------------------------------------------------------- #
# Rig pivots
# --------------------------------------------------------------------------- #
root = empty("Root", (0, 0, 0))
hips = empty("Hips", (0, 0, 0.36), root)
torso = empty("Torso", (0, 0, 0.4), hips)
head = empty("Head", (0, 0, 0.86), torso)
sh_r = empty("ShoulderR", (-0.175, 0, 0.77), torso)   # waving arm (viewer's left)
sh_l = empty("ShoulderL", (0.175, 0, 0.77), torso)
leg_r = empty("LegR", (-0.1, 0, 0.36), hips)
leg_l = empty("LegL", (0.1, 0, 0.36), hips)

# --------------------------------------------------------------------------- #
# Legs: short stubby lathed legs + rounded shoes
# --------------------------------------------------------------------------- #
LEG = [(0.0, 0.0), (0.015, 0.06), (0.05, 0.082), (0.15, 0.09), (0.27, 0.098), (0.36, 0.105), (0.4, 0.09), (0.42, 0.0)]
for side, leg in ((-1, leg_r), (1, leg_l)):
    tag = "R" if side < 0 else "L"
    lathe(f"Pant{tag}", LEG, PANTS, leg, cx=0.1 * side, seg=24)
    sphere(f"Shoe{tag}", (0.1 * side, -0.035, 0.055), (0.095, 0.13, 0.068), SHOE, leg, seg=24, rings=12)

# --------------------------------------------------------------------------- #
# Torso: pear-shaped body — pants on the hips, tee on top
# --------------------------------------------------------------------------- #
lathe("Hip", [(0.27, 0.0), (0.29, 0.12), (0.33, 0.185), (0.4, 0.21), (0.47, 0.205), (0.48, 0.0)],
      PANTS, torso, yscale=0.8)
SHIRT_P = [(0.41, 0.0), (0.412, 0.2), (0.43, 0.228), (0.5, 0.222), (0.62, 0.205), (0.72, 0.19),
           (0.79, 0.17), (0.84, 0.13), (0.87, 0.06), (0.875, 0.0)]
lathe("Shirt", SHIRT_P, SHIRT, torso, yscale=0.8)
bpy.ops.mesh.primitive_torus_add(major_radius=0.07, minor_radius=0.018, location=(0, -0.005, 0.86))
finish(bpy.context.active_object, "Collar", SHIRT_DARK, torso)
cyl("Neck", (0, 0, 0.82), (0, 0, 0.96), 0.06, 0.058, SKIN, torso)


def shirt_y(_x, z, off=0.006):
    return -profile_r(SHIRT_P, z) * 0.8 - off


# Print: blue square with a dark figure (arms spread, headphones)
PC, PH = 0.61, 0.085                     # print centre z, half size


def pm(x, z):                            # map the original print design into the square
    return (x * PH / 0.12, PC + (z - 0.825) * PH / 0.125)


flat_shape("ShirtPrint_noline", [pm(-0.12, 0.7), pm(0.12, 0.7), pm(0.12, 0.95), pm(-0.12, 0.95)],
           shirt_y, PRINT, torso, 0.004)
flat_shape("PrintFigure_noline",
           [pm(*p) for p in ((-0.1, 0.84), (-0.03, 0.835), (-0.04, 0.70), (0.04, 0.70), (0.03, 0.835), (0.1, 0.85),
                             (0.1, 0.835), (0.03, 0.81), (0.035, 0.80), (-0.035, 0.80), (-0.03, 0.81), (-0.1, 0.825))],
           lambda x, z: shirt_y(x, z, 0.009), PRINT_INK, torso, 0.002)
hx, hz = pm(0, 0.875)
sphere("PrintHead_noline", (hx, shirt_y(0, hz, 0.009), hz), (0.024, 0.004, 0.026), PRINT_INK, torso, seg=16, rings=8)

# --------------------------------------------------------------------------- #
# Arms (short, built hanging straight down; posed on the pivots below)
# --------------------------------------------------------------------------- #


def build_arm(tag, shoulder, side):
    s = shoulder.matrix_world.translation.copy()
    cyl(f"Sleeve{tag}", s + Vector((0, 0, 0.035)), s + Vector((0.012 * side, 0, -0.11)), 0.075, 0.068, SHIRT, shoulder)
    elbow_pos = s + Vector((0.012 * side, 0, -0.155))
    capsule(f"UpperArm{tag}", s + Vector((0.006 * side, 0, -0.06)), elbow_pos, 0.042, SKIN, shoulder)
    elbow = empty(f"Elbow{tag}", elbow_pos, shoulder)
    wrist = elbow_pos + Vector((0, 0, -0.13))
    capsule(f"Forearm{tag}", elbow_pos, wrist, 0.041, SKIN, elbow, r2=0.036)
    # Small chibi hand: palm faces forward (-Y), fingers point down the arm.
    palm_c = wrist + Vector((0, 0, -0.045))
    parts = [sphere(f"Palm{tag}", palm_c, (0.054, 0.03, 0.054), SKIN, seg=20, rings=12)]
    for i, fx in enumerate((-0.033, -0.011, 0.011, 0.033)):
        length = (0.04, 0.05, 0.048, 0.037)[i]
        a = palm_c + Vector((fx, 0, -0.032))
        b = a + Vector((fx * 0.35, 0, -length))
        parts.append(capsule(f"Finger{tag}{i}", a, b, 0.0135, SKIN, r2=0.012))
    th_a = palm_c + Vector((0.034 * side, -0.006, 0.008))
    parts.append(capsule(f"Thumb{tag}", th_a, th_a + Vector((0.03 * side, -0.008, -0.022)), 0.012, SKIN))
    join(parts, f"Hand{tag}", SKIN, elbow)
    return elbow


elbow_r = build_arm("R", sh_r, -1)
elbow_l = build_arm("L", sh_l, 1)

# --------------------------------------------------------------------------- #
# Head
# --------------------------------------------------------------------------- #
bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=1, location=HEAD_C)
skull = bpy.context.active_object
for v in skull.data.vertices:
    v.co = head_shape(v.co)
finish(skull, "HeadSkin", SKIN, head)
bpy.context.view_layer.update()


def face_y(x, z, off=0.0):
    """World Y of the front of the head at (x, z) (ray cast), pushed `off` outward."""
    inv = skull.matrix_world.inverted()
    org = inv @ Vector((x, -3.0, z))
    d = (inv.to_3x3() @ Vector((0, 1, 0))).normalized()
    hit, loc, _n, _i = skull.ray_cast(org, d)
    if not hit:
        return -0.3 - off
    return (skull.matrix_world @ loc).y - off


EAR_Z = 1.24
for side in (-1, 1):
    tag = "R" if side < 0 else "L"
    ex = head_shape(sph_dir(math.acos(-0.32), side * math.pi / 2)).x
    sphere(f"Ear{tag}", (ex + 0.005 * side, 0.0, EAR_Z), (0.055, 0.04, 0.08), SKIN, head, seg=20, rings=10)
    sphere(f"Earbud{tag}", (ex + 0.03 * side, -0.03, EAR_Z - 0.02), (0.028, 0.028, 0.028), BUD, head, seg=16, rings=8)

# --- Hair ------------------------------------------------------------------ #
# Cap: a slightly inflated copy of the skull with the face and ears cut out.
bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=1, location=HEAD_C)
cap = bpy.context.active_object
bm = bmesh.new()
bm.from_mesh(cap.data)
kill = []
for v in bm.verts:
    n = v.co.normalized()
    face = n.y < -0.18 and n.z < 0.42
    neck = n.z < -0.8
    jaw = n.z < -0.25 and n.y < -0.05
    ears = abs(n.x) > 0.78 and -0.6 < n.z < 0.0 and abs(n.y) < 0.4
    if face or neck or jaw or ears:
        kill.append(v)
    else:
        v.co = head_shape(n) * 1.05
bmesh.ops.delete(bm, geom=kill, context="VERTS")
bm.to_mesh(cap.data)
bm.free()
finish(cap, "HairCap", HAIR, head)
cap.modifiers.new("solid", "SOLIDIFY").thickness = 0.015

hair = []


def strand(theta0, theta1, phi0, phi1, r0, lift1, lift0=0.0, n=7):
    """A tapered hair clump lying on the skull from (theta0, phi0) to (theta1, phi1).
    `lift` pushes the clump off the surface (ease-in, so tips flick outward)."""
    pts, radii = [], []
    for i in range(n):
        u = i / (n - 1)
        th = theta0 + (theta1 - theta0) * u
        ph = phi0 + (phi1 - phi0) * (u * u)
        lift = lift0 + (lift1 - lift0) * (u ** 2.2)
        pts.append(tuple(HEAD_C + head_shape(sph_dir(th, ph)) * (1.035 + lift)))
        radii.append(max(1.0 - u, 0.0) ** 0.75)
    hair.append(tube(f"Strand{len(hair)}", pts, r0, HAIR, radii=radii, res=6, bevel_res=2))


def jit(a):
    return random.uniform(-a, a)


# Fringe: chunky pointed bangs over the forehead, alternating lengths, sweeping inward.
for i, phi in enumerate([-0.95 + 0.19 * k for k in range(11)]):
    long = i % 2 == 0
    strand(0.18 + jit(0.06), (1.52 if long else 1.36) + jit(0.05), phi, phi * 0.8 + jit(0.12),
           0.09 + jit(0.012), 0.05 + jit(0.03), lift0=0.03)
# Side locks in front of the ears.
for s in (-1, 1):
    for phi, th1 in ((0.98, 1.85), (1.12, 2.02), (1.27, 1.9)):
        strand(0.4, th1 + jit(0.05), s * phi, s * (phi + 0.04), 0.085, 0.1, lift0=0.03)
# Messy spikes sticking out above the ears (like the drawing).
for s in (-1, 1):
    for phi, th1, lift in ((1.45, 1.42, 0.22), (1.75, 1.55, 0.26), (2.05, 1.5, 0.2)):
        strand(0.55, th1 + jit(0.06), s * phi, s * (phi + jit(0.08)), 0.08, lift)
# Back: long clumps down to the nape, tips flicking out.
for phi in [1.95 + (2 * math.pi - 3.9) * k / 11 for k in range(12)]:
    strand(0.3, 2.5 + jit(0.1), phi, phi + jit(0.15), 0.1, 0.2 + jit(0.08), lift0=0.03)
# Crown fill: medium clumps radiating from the top so the cap never reads as a helmet.
for k in range(12):
    phi = 2 * math.pi * k / 12 + jit(0.15)
    strand(0.05, 0.95 + jit(0.15), phi, phi + jit(0.2), 0.11, 0.08, lift0=0.04)
# Messy tufts on top.
for phi, th0 in ((2.4, 0.15), (-2.3, 0.2), (1.2, 0.35), (-1.1, 0.3), (3.1, 0.25), (0.6, 0.3), (-0.5, 0.35)):
    strand(th0, th0 + 0.5 + jit(0.08), phi, phi + jit(0.25), 0.075, 0.24 + jit(0.05))
# Spiky silhouette: clumps around the upper head whose tips kick outward.
for k in range(18):
    phi = 0.85 + (2 * math.pi - 1.7) * k / 17 + jit(0.08)
    th0 = random.uniform(0.45, 0.8)
    strand(th0, th0 + random.uniform(0.45, 0.65), phi, phi + jit(0.2), random.uniform(0.07, 0.09),
           random.uniform(0.28, 0.45), lift0=0.03)
# Taller messy spikes on top.
for phi, th0, lift in ((2.6, 0.1, 0.5), (-2.5, 0.15, 0.45), (1.6, 0.3, 0.42), (-1.5, 0.28, 0.48),
                       (0.9, 0.35, 0.36), (-0.8, 0.32, 0.4), (3.14, 0.2, 0.42), (0.1, 0.4, 0.3)):
    strand(th0, th0 + 0.55, phi, phi + jit(0.3), 0.075, lift, lift0=0.04)
# Cowlick: one clump sweeping up and over the top.
strand(0.45, -0.25, math.pi, math.pi, 0.07, 0.3)
join(hair, "HairStrands", HAIR, head)

# Highlight streaks on top.
for i, phi in enumerate((-0.45, 0.4)):
    pts = [tuple(HEAD_C + head_shape(sph_dir(th, phi + d)) * 1.075) for th, d in ((0.62, -0.1), (0.66, 0.0), (0.62, 0.1))]
    tube(f"HairShine{i}_noline", pts, 0.012, HAIR_HI, head)

# --- Glasses ---------------------------------------------------------------- #
E_Z = 1.28                    # eye line (chibi: below the centre of the head)
G_W, G_H = 0.22, 0.145
for side in (-1, 1):
    tag = "R" if side < 0 else "L"
    cx = 0.175 * side
    y = face_y(cx, E_Z, 0.032)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(cx, y, E_Z), rotation=(math.pi / 2, 0, 0))
    lens = bpy.context.active_object
    lens.scale = (G_W, G_H, 1)
    lens.rotation_euler.z = -0.22 * side
    apply_xform(lens)
    w = lens.modifiers.new("frame", "WIREFRAME")
    w.thickness = 0.017
    w.use_even_offset = True
    finish(lens, f"Glasses{tag}_noline", FRAME, head, smooth=False)
    outer = Vector((cx + G_W / 2 * side * 0.97, y + 0.025, E_Z + 0.035))
    tube(f"Temple{tag}_noline", [tuple(outer), (0.47 * side, -0.02, EAR_Z + 0.06)], 0.007, FRAME, head, poly=True)
tube("GlassesBridge_noline",
     [(-0.065, face_y(0.065, E_Z, 0.055), E_Z + 0.025), (0, face_y(0, E_Z, 0.06), E_Z + 0.035),
      (0.065, face_y(0.065, E_Z, 0.055), E_Z + 0.025)], 0.008, FRAME, head)

# --------------------------------------------------------------------------- #
# Faces
# --------------------------------------------------------------------------- #
face_happy = empty("FaceHappy", (0, 0, 0.86), head)
face_laugh = empty("FaceLaugh", (0, 0, 0.86), head)


def arc_pts(cx, cz, w, h, n=7, off=0.012):
    out = []
    for i in range(n):
        t = i / (n - 1)
        x = cx + (t - 0.5) * w
        z = cz + math.sin(t * math.pi) * h
        out.append((x, face_y(x, z, off), z))
    return out


def ellipse_half(cx, cz, w, h, top, n=16):
    pts = [(cx - w, cz + top)]
    for i in range(n + 1):
        a = math.pi + math.pi * i / n
        pts.append((cx + math.cos(a) * w, cz + math.sin(a) * h))
    pts.append((cx + w, cz + top))
    return pts


def on_face(off):
    return lambda x, z: face_y(x, z, off)


M_Z = 1.1
# Happy: ^ ^ eyes, eyebrows, big toothy grin, soft blush.
for side in (-1, 1):
    tag = "R" if side < 0 else "L"
    cx = 0.175 * side
    tube(f"EyeHappy{tag}_noline", arc_pts(cx, E_Z - 0.022, 0.095, 0.036), 0.012, LINE, face_happy, poly=True)
    tube(f"Brow{tag}_noline", arc_pts(cx + 0.01 * side, 1.415, 0.11, 0.014, off=0.02), 0.012, HAIR, head, poly=True)
    bx = 0.26 * side
    sphere(f"BlushHappy{tag}_noline", (bx, face_y(bx, 1.18, 0.004), 1.18),
           (0.06, 0.012, 0.034), BLUSH, face_happy, seg=20, rings=10)
    bpy.data.objects[f"BlushHappy{tag}_noline"].rotation_euler.z = -0.35 * side

flat_shape("GrinLine_noline", ellipse_half(0, M_Z + 0.015, 0.095, 0.068, 0.013), on_face(0.003), LINE, face_happy)
flat_shape("GrinTeeth_noline", ellipse_half(0, M_Z + 0.015, 0.08, 0.055, 0.004), on_face(0.008), TEETH, face_happy)
tube("GrinTeethLine_noline", [(x, face_y(x, M_Z - 0.008, 0.012), M_Z - 0.008) for x in (-0.065, 0, 0.065)],
     0.0035, LINE, face_happy, poly=True)

# Laugh: > < eyes, open mouth, hot blush, sweat drops.
for side in (-1, 1):
    tag = "R" if side < 0 else "L"
    cx = 0.175 * side
    inner, outer = cx - 0.038 * side, cx + 0.05 * side
    pts = [(outer, E_Z + 0.038), (inner, E_Z), (outer, E_Z - 0.038)]
    tube(f"EyeLaugh{tag}_noline", [(x, face_y(x, z, 0.012), z) for x, z in pts], 0.013, LINE, face_laugh, poly=True)
    bx = 0.24 * side
    sphere(f"BlushLaugh{tag}_noline", (bx, face_y(bx, 1.18, 0.005), 1.18),
           (0.1, 0.012, 0.05), BLUSH_HOT, face_laugh, seg=20, rings=10)
    bpy.data.objects[f"BlushLaugh{tag}_noline"].rotation_euler.z = -0.35 * side

flat_shape("LaughMouth_noline", ellipse_half(0, M_Z + 0.03, 0.092, 0.11, 0.011), on_face(0.003), LINE, face_laugh)
flat_shape("LaughInside_noline", ellipse_half(0, M_Z + 0.03, 0.078, 0.095, 0.002), on_face(0.007), MOUTH, face_laugh)
flat_shape("LaughTongue_noline", ellipse_half(0, M_Z - 0.035, 0.055, 0.033, 0.022), on_face(0.01), TONGUE, face_laugh)
flat_shape("LaughTeeth_noline", [(-0.074, M_Z + 0.032), (0.074, M_Z + 0.032), (0.066, M_Z + 0.01), (-0.066, M_Z + 0.01)],
           on_face(0.01), TEETH, face_laugh)

for i, (x, z, s) in enumerate(((-0.66, 1.62, 1.0), (-0.7, 1.44, 0.7), (0.66, 1.66, 1.0), (0.7, 1.48, 0.75), (0.3, 1.1, 0.6))):
    y = -0.25 if abs(x) > 0.5 else face_y(x, z, 0.012)
    sphere(f"Sweat{i}_noline", (x, y, z), (0.032 * s, 0.022 * s, 0.048 * s), SWEAT, face_laugh, seg=16, rings=8)

# --------------------------------------------------------------------------- #
# Earphone cable: buds -> past the jaw -> splitter on chest -> down to the pocket.
# --------------------------------------------------------------------------- #
bpy.context.view_layer.update()
budR = bpy.data.objects["EarbudR"].matrix_world.translation + Vector((0, -0.02, -0.025))
budL = bpy.data.objects["EarbudL"].matrix_world.translation + Vector((0, -0.02, -0.025))
chest = shirt_y(0, 0.7, 0.03)
split = (0.02, shirt_y(0, 0.62, 0.035), 0.64)
for tag, bud, s in (("R", budR, -1), ("L", budL, 1)):
    tube(f"Cable{tag}_noline",
         [tuple(bud), (bud.x * 0.76, -0.2, 1.02), (0.24 * s, -0.24, 0.9), (0.08 * s, chest, 0.74), split],
         0.005, BUD, torso)
tube("CableDown_noline", [split, (0.1, shirt_y(0.1, 0.52, 0.03), 0.52), (0.19, -0.15, 0.43)], 0.005, BUD, torso)
sphere("CableMic_noline", split, (0.014, 0.011, 0.026), BUD, torso, seg=12, rings=6)

# --------------------------------------------------------------------------- #
# Default pose: right hand up waving by the cheek, left hand relaxed.
# --------------------------------------------------------------------------- #
sh_r.rotation_euler = (0, math.radians(100), 0)     # upper arm out to the side (-X)
elbow_r.rotation_euler = (0, math.radians(55), 0)   # forearm up
sh_l.rotation_euler = (0, math.radians(-24), 0)
elbow_l.rotation_euler = (0, math.radians(-10), 0)

# --------------------------------------------------------------------------- #
# Optional preview render
# --------------------------------------------------------------------------- #
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if "--render" in argv:
    out = os.path.abspath(argv[argv.index("--render") + 1])
    laugh = "--laugh" in argv
    for o in face_laugh.children:
        o.hide_render = not laugh
    for o in face_happy.children:
        o.hide_render = laugh
    cam_data = bpy.data.cameras.new("Cam")
    cam_data.lens = 70
    cam = bpy.data.objects.new("Cam", cam_data)
    scene.collection.objects.link(cam)
    yaw = float(argv[argv.index("--yaw") + 1]) if "--yaw" in argv else 0.0
    r = 6.6
    cam.location = (math.sin(math.radians(yaw)) * r, -math.cos(math.radians(yaw)) * r, 1.05)
    cam.rotation_euler = (math.radians(90), 0, math.radians(yaw))
    scene.camera = cam
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.data.energy = 3.5
    sun.rotation_euler = (math.radians(50), 0, math.radians(-30))
    scene.collection.objects.link(sun)
    world = bpy.data.worlds.new("W")
    scene.world = world
    try:
        world.use_nodes = True
        world.node_tree.nodes["Background"].inputs[0].default_value = (0.95, 0.95, 0.95, 1)
        world.node_tree.nodes["Background"].inputs[1].default_value = 0.9
    except Exception:
        pass
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 800
    scene.render.resolution_y = 1000
    scene.render.filepath = out
    bpy.ops.render.render(write_still=True)
    print("rendered", out)

# --------------------------------------------------------------------------- #
# Export
# --------------------------------------------------------------------------- #
if "--no-export" not in argv:
    os.makedirs(os.path.dirname(OUT_GLB), exist_ok=True)
    for o in scene.objects:
        o.hide_render = False
    bpy.ops.export_scene.gltf(filepath=OUT_GLB, export_format="GLB", export_apply=True,
                              export_yup=True, export_cameras=False, export_lights=False,
                              use_selection=False)
    print("exported", OUT_GLB, os.path.getsize(OUT_GLB), "bytes")
