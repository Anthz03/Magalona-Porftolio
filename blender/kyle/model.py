"""Kyle's body geometry, built in *design units* (about 2.1 tall). The build scales
everything x0.5 to metres once rigging is done.

Every part is created as its own object named `part_<Name>` so the rig can weight
it with the right function; the rig module then joins parts into the final GEO_*
meshes."""
import math

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

from . import util as U

# --------------------------------------------------------------------------- #
# Proportions (design units)
# --------------------------------------------------------------------------- #
HEAD_C = Vector((0, 0, 1.53))
RX, RY, RZT, RZB = 0.385, 0.355, 0.40, 0.385
E_Z = 1.45          # eye line (chibi: below the head centre)
EYE_X = 0.152
M_Z = 1.262         # mouth centre
BLUSH_Z = 1.372
EAR_Z = 1.425
ARM_ANGLE = math.radians(50)       # rest pose: A-pose, arms 50 deg from vertical
UPPER, FORE, PALM = 0.2, 0.185, 0.072

# Joint positions, filled by build(); the rig reads these.
J = {}

PAL = {
    "skin": "#f6c9a9", "hair": "#1d2030", "hair_hi": "#454b66", "shirt": "#393a45",
    "collar": "#2b2c35", "pants": "#25262f", "shoe": "#1f2029", "sole": "#3a3c4a",
    "frame": "#3f2018", "lens": "#cfe3ff", "bud": "#1c1d24", "print": "#4f7bb8",
}


def side_tag(s):
    return "L" if s > 0 else "R"


# --------------------------------------------------------------------------- #
# Head
# --------------------------------------------------------------------------- #
def head_shape(n):
    """Surface point (relative to HEAD_C) of the head in direction n."""
    n = Vector(n).normalized()
    s = (n.x ** 4 + n.y ** 4 + n.z ** 4) ** -0.25          # 1 (axes) .. 1.32 (diagonals)
    p = n * (1 + 0.1 * (s - 1))
    p = Vector((p.x * RX, p.y * RY, p.z * (RZT if p.z > 0 else RZB)))
    if p.z < 0:                                           # jaw narrows toward the chin
        t = -p.z / RZB
        p.x *= 1 - 0.2 * t * t
        p.y *= 1 - 0.06 * t * t
    if n.y < 0:                                           # slightly flatter face plane
        p.y *= 1 - 0.06 * (-n.y) ** 3
    for sx in (-1, 1):                                    # full, soft cheeks
        c = Vector((0.6 * sx, -0.62, -0.38)).normalized()
        p += n * 0.032 * math.exp(-(n - c).length_squared / 0.07)
    c = Vector((0, -0.42, -0.9)).normalized()             # soft chin
    p += Vector((0, -0.7, -0.4)).normalized() * 0.012 * math.exp(-(n - c).length_squared / 0.04)
    c = Vector((0, -1, -0.2)).normalized()                # tiny button nose
    p.y -= 0.011 * math.exp(-(n - c).length_squared / 0.0035)
    return p


def sph_dir(theta, phi):
    """theta from the crown (0 = top), phi around the head (0 = front/-Y, +pi/2 = +X / his left)."""
    return Vector((math.sin(theta) * math.sin(phi), -math.sin(theta) * math.cos(phi), math.cos(theta)))


def head_point(theta, phi, inflate=1.0):
    return HEAD_C + head_shape(sph_dir(theta, phi)) * inflate


def build_head(coll, mats):
    dirs, faces = U.quad_sphere(16)
    verts = [HEAD_C + head_shape(d) for d in dirs]
    head = U.new_object("part_Head", verts, faces, coll, mats["skin"])

    # Ears: flattened ovals with a scooped bowl, tilted to face slightly forward.
    for s in (-1, 1):
        th = math.acos(max(-1, min(1, (EAR_Z - HEAD_C.z) / RZB)))
        base = head_point(th + 0.05, s * math.radians(96))
        rx, ry, rz = 0.034, 0.056, 0.078

        def ear_shape(d, s=s):
            p = Vector((d.x * rx, d.y * ry, d.z * rz))
            if d.x > 0:                                    # outer face: scoop a bowl
                p.x -= rx * 1.25 * math.exp(-(d.y * d.y + d.z * d.z) / 0.45) * d.x
            return p
        v, f = U.uv_ellipsoid((0, 0, 0), (rx, ry, rz), seg=20, rings=12, shape=ear_shape)
        mw = Matrix.Translation(base + Vector((s * 0.012, 0.0, 0.0))) @ \
            Matrix.Rotation(math.radians(-14 * s), 4, "Z") @ Matrix.Rotation(math.radians(8), 4, "X")
        if s < 0:
            mw = mw @ Matrix.Scale(-1, 4, Vector((1, 0, 0)))
        v = [mw @ x for x in v]
        if s < 0:
            f = [tuple(reversed(ff)) for ff in f]
        U.new_object(f"part_Ear{side_tag(s)}", v, f, coll, mats["skin"])
        J[f"ear{side_tag(s)}"] = base + Vector((s * 0.05, -0.012, -0.012))

    v, f = U.tube([(0, 0.012, 1.02), (0, 0.012, 1.14), (0, 0.02, 1.26)], [0.072, 0.07, 0.072], m=16,
                  rounded=(False, True))
    U.new_object("part_Neck", v, f, coll, mats["skin"])
    return head


# --------------------------------------------------------------------------- #
# Torso / clothes
# --------------------------------------------------------------------------- #
def superellipse(hw, hd, e, m=40, yoff=0.0):
    out = []
    for k in range(m):
        a = 2 * math.pi * k / m
        c, s = math.cos(a), math.sin(a)
        out.append((math.copysign(abs(c) ** (2 / e), c) * hw, math.copysign(abs(s) ** (2 / e), s) * hd + yoff))
    return out


def lofted(levels, m=40, e=2.6):
    """levels: [(z, hw, hd)] bottom->top, closed with poles at both ends."""
    verts, faces = [], []
    rings = []
    for z, hw, hd in levels:
        if hw < 1e-6:
            rings.append([len(verts)])
            verts.append(Vector((0, 0, z)))
            continue
        ring = []
        for x, y in superellipse(hw, hd, e, m):
            ring.append(len(verts))
            verts.append(Vector((x, y, z)))
        rings.append(ring)
    for ra, rb in zip(rings, rings[1:]):
        if len(ra) == 1:
            faces += [(ra[0], rb[(k + 1) % m], rb[k]) for k in range(m)]
        elif len(rb) == 1:
            faces += [(ra[k], ra[(k + 1) % m], rb[0]) for k in range(m)]
        else:
            faces += [(ra[k], ra[(k + 1) % m], rb[(k + 1) % m], rb[k]) for k in range(m)]
    if len(rings[0]) > 1:
        faces.append(tuple(reversed(rings[0])))
    if len(rings[-1]) > 1:
        faces.append(tuple(rings[-1]))
    return verts, faces


def remesh(obj, voxel, smooth_iters=4, smooth_fac=0.5):
    U.activate(obj)
    obj.data.remesh_voxel_size = voxel
    bpy.ops.object.voxel_remesh()
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for _ in range(smooth_iters):
        bmesh.ops.smooth_vert(bm, verts=bm.verts[:], factor=smooth_fac, use_axis_x=True, use_axis_y=True,
                              use_axis_z=True)
    bm.to_mesh(obj.data)
    bm.free()
    for p in obj.data.polygons:
        p.use_smooth = True


def bisect(obj, co, no, where):
    """Cut `obj` with the plane (co, no), deleting the + side, only among faces whose
    verts all satisfy where(v)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    faces = [f for f in bm.faces if all(where(v.co) for v in f.verts)]
    geom = list({e for f in faces for e in f.edges}) + faces + list({v for f in faces for v in f.verts})
    bmesh.ops.bisect_plane(bm, geom=geom, plane_co=co, plane_no=no, clear_outer=True)
    bm.to_mesh(obj.data)
    bm.free()


def displace(obj, fn):
    """Move every vertex along its normal by fn(co, normal)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.normal_update()
    moves = [(v, v.normal * fn(v.co, v.normal)) for v in bm.verts]
    for v, d in moves:
        v.co += d
    bm.to_mesh(obj.data)
    bm.free()


def seg_dist(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))
    return (p - (a + ab * t)).length, t


def arm_dir(s):
    return Vector((math.sin(ARM_ANGLE) * s, 0, -math.cos(ARM_ANGLE)))


def build_shirt(coll, mats):
    levels = [(0.455, 0.262, 0.192), (0.5, 0.26, 0.19), (0.62, 0.252, 0.186), (0.78, 0.248, 0.181),
              (0.9, 0.244, 0.176), (0.965, 0.232, 0.168), (1.02, 0.2, 0.152), (1.058, 0.15, 0.12),
              (1.082, 0.1, 0.09), (1.094, 0.0, 0.0)]
    v, f = lofted(levels)
    g = U.Geo()
    g.add(v, f)
    for s in (-1, 1):
        S, d = J[f"shoulder{side_tag(s)}"], arm_dir(s)
        v, f = U.tube([S - d * 0.06 + Vector((-0.02 * s, 0, -0.02)), S + d * 0.06, S + d * 0.17],
                      [0.08, 0.088, 0.086], m=20, rounded=(True, False))
        g.add(v, f)
    shirt = g.build("part_Shirt", coll, mats["shirt"])
    remesh(shirt, 0.019, smooth_iters=5)

    # Openings: hem, sleeve ends, neck.
    bisect(shirt, Vector((0, 0, 0.462)), Vector((0, 0, -1)), lambda c: c.z < 0.56)
    for s in (-1, 1):
        S, d = J[f"shoulder{side_tag(s)}"], arm_dir(s)
        def near_sleeve(c, S=S, d=d):
            t = (c - S).dot(d)
            return t > 0.06 and (c - S - d * t).length < 0.105 and c.x * d.x > 0.16
        bisect(shirt, S + d * 0.155, d, near_sleeve)
    bm = bmesh.new()
    bm.from_mesh(shirt.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z > 1.0 and math.hypot(v.co.x, v.co.y - 0.004) < 0.094],
                     context="VERTS")
    bm.to_mesh(shirt.data)
    bm.free()

    # Fabric: gentle hem wave, armpit drag folds, a soft crease across the belly.
    folds = []
    for s in (-1, 1):
        S = J[f"shoulder{side_tag(s)}"]
        folds += [(S + Vector((-0.05 * s, -0.12, -0.12)), Vector((0.06 * s, -0.19, 0.74)), 0.006, 0.02),
                  (S + Vector((-0.06 * s, 0.12, -0.1)), Vector((0.08 * s, 0.18, 0.72)), 0.005, 0.02),
                  (Vector((0.24 * s, -0.12, 0.6)), Vector((0.2 * s, -0.17, 0.5)), 0.004, 0.018)]
    folds += [(Vector((-0.12, -0.2, 0.56)), Vector((0.1, -0.2, 0.585)), 0.003, 0.016)]

    def fabric(c, _n):
        out = 0.0
        if c.z < 0.62:
            a = math.atan2(c.y, c.x)
            out += 0.006 * math.sin(a * 6 + 0.7) * (1 - U.smooth((c.z - 0.46) / 0.16))
        for a, b, depth, w in folds:
            dd, _t = seg_dist(c, a, b)
            out -= depth * math.exp(-(dd / w) ** 2)
        return out
    displace(shirt, fabric)
    sol = shirt.modifiers.new("thickness", "SOLIDIFY")
    sol.thickness = 0.012
    sol.offset = -1
    sol.use_even_offset = True
    sol.use_rim_only = True
    U.apply_modifiers(shirt)

    # Ribbed crew-neck collar.
    path = [Vector((math.cos(a) * 0.097, math.sin(a) * 0.088 + 0.004, 1.07 + 0.008 * math.cos(a) ** 2))
            for a in (2 * math.pi * k / 40 for k in range(40))]
    v, f = U.sweep(path, U.circle_profile(10), [0.016] * 40, [0.02] * 40, up_hint=(0, 0, 1), closed_path=True)
    U.new_object("part_Collar", v, f, coll, mats["collar"])
    return shirt


def print_image():
    """Chest graphic: blue square with a dark silhouette (arms out, headphones on)."""
    n, ss = 256, 4
    N = n * ss
    y, x = np.mgrid[0:N, 0:N]
    x = (x + 0.5) / N
    y = (y + 0.5) / N                         # y up (row 0 = bottom)

    def cap(ax, ay, bx, by, r):
        abx, aby = bx - ax, by - ay
        t = np.clip(((x - ax) * abx + (y - ay) * aby) / (abx * abx + aby * aby), 0, 1)
        return (x - ax - abx * t) ** 2 + (y - ay - aby * t) ** 2 < r * r

    fig = (x - 0.5) ** 2 + ((y - 0.6) / 1.08) ** 2 < 0.082 ** 2          # head
    fig |= cap(0.5, 0.5, 0.5, 0.56, 0.045)                                 # neck
    torso = (y < 0.5) & (y > -0.1) & (np.abs(x - 0.5) < 0.16 + (0.5 - y) * -0.1)
    fig |= torso | cap(0.38, 0.45, 0.62, 0.45, 0.06)                       # shoulders
    fig |= cap(0.38, 0.45, 0.13, 0.34, 0.045) | cap(0.62, 0.45, 0.88, 0.39, 0.045)   # arms out
    fig |= cap(0.13, 0.34, 0.08, 0.36, 0.03) | cap(0.88, 0.39, 0.93, 0.42, 0.03)     # hands
    r = np.hypot(x - 0.5, (y - 0.61) / 1.05)
    band = (np.abs(r - 0.112) < 0.014) & (y > 0.6)                         # headphone band
    cups = ((x - 0.39) ** 2 / 0.026 ** 2 + (y - 0.6) ** 2 / 0.045 ** 2 < 1) | \
           ((x - 0.61) ** 2 / 0.026 ** 2 + (y - 0.6) ** 2 / 0.045 ** 2 < 1)
    fig |= band | cups
    glow = np.exp(-((x - 0.62) ** 2 + (y - 0.82) ** 2) / 0.08)             # soft light top-right
    edge = np.minimum.reduce([x, 1 - x, y, 1 - y])
    border = edge < 0.012

    bg = np.array([0.31, 0.48, 0.72])
    hi = np.array([0.52, 0.68, 0.9])
    ink = np.array([0.12, 0.17, 0.27])
    col = bg[None, None, :] * (1 - glow[..., None] * 0.6) + hi[None, None, :] * glow[..., None] * 0.6
    col = np.where(fig[..., None], ink[None, None, :], col)
    col = np.where(border[..., None], bg * 0.75, col)
    col = col.reshape(n, ss, n, ss, 3).mean(axis=(1, 3))
    rgba = np.concatenate([col, np.ones((n, n, 1))], axis=2).astype(np.float32)
    return U.image_from_pixels("TEX_ShirtPrint", n, n, rgba.ravel())


def build_print(coll, mats, shirt):
    bvh = U.bvh_of(shirt)
    nx, nz = 12, 12
    x0, x1, z0, z1 = -0.13, 0.13, 0.64, 0.92
    verts, faces, uvs = [], [], []
    for j in range(nz + 1):
        for i in range(nx + 1):
            x, z = U.lerp(x0, x1, i / nx), U.lerp(z0, z1, j / nz)
            loc, nrm, _i, _d = bvh.ray_cast(Vector((x, -1.0, z)), Vector((0, 1, 0)))
            verts.append(loc + nrm * 0.0035)
            uvs.append((i / nx, j / nz))
    for j in range(nz):
        for i in range(nx):
            a = j * (nx + 1) + i
            faces.append((a, a + 1, a + nx + 2, a + nx + 1))
    o = U.new_object("part_Print", verts, faces, coll, mats["print"])
    uv = o.data.uv_layers.new(name="UVMap")
    for loop in o.data.loops:
        uv.data[loop.index].uv = uvs[loop.vertex_index]
    return o


def build_pants(coll, mats):
    g = U.Geo()
    v, f = U.uv_ellipsoid((0, 0.004, 0.6), (0.218, 0.168, 0.15), seg=32, rings=16)
    g.add(v, f)
    for s in (-1, 1):
        t = side_tag(s)
        v, f = U.tube([J[f"hip{t}"] + Vector((0, 0, 0.08)), J[f"hip{t}"], J[f"knee{t}"], J[f"ankle{t}"]],
                      [0.104, 0.104, 0.095, 0.098], m=24, rounded=(False, False))
        g.add(v, f)
    pants = g.build("part_Pants", coll, mats["pants"])
    remesh(pants, 0.02, smooth_iters=5)

    def fabric(c, _n):
        out = 0.0
        for s in (-1, 1):
            k = J[f"knee{side_tag(s)}"]
            # soft horizontal creases behind the knee + bunching above the shoe
            if abs(c.x - k.x) < 0.12:
                out -= 0.003 * math.exp(-((c.z - k.z - 0.02) / 0.015) ** 2) * U.smooth((c.y - 0.0) / 0.08)
                out -= 0.0015 * math.exp(-((c.z - 0.2) / 0.015) ** 2) * U.smooth((-c.y) / 0.06)
        return out
    displace(pants, fabric)
    return pants


def build_shoes(coll, mats):
    for s in (-1, 1):
        t = side_tag(s)
        a = J[f"ankle{t}"]
        c = Vector((a.x, -0.035, 0.068))

        def shoe(d):
            ry = 0.142 if d.y < 0 else 0.11
            p = Vector((d.x * 0.08, d.y * ry, d.z * 0.072))
            if d.y < 0:                                    # rounder, fuller toe box
                p.z += 0.012 * (-d.y) * max(d.z, 0)
                p.x *= 1 + 0.08 * (-d.y)
            p.z = max(p.z, -0.056)                         # flat sole
            return p
        v, f = U.uv_ellipsoid(c, (0.08, 0.13, 0.07), seg=28, rings=14, shape=shoe)
        U.new_object(f"part_Shoe{t}", v, f, coll, mats["shoe"])
        # Sole: a slightly wider rounded slab.
        outline = []
        for k in range(32):
            ang = 2 * math.pi * k / 32
            cx, cy = math.cos(ang), math.sin(ang)
            ry = 0.148 if cy < 0 else 0.116
            outline.append((c.x + math.copysign(abs(cx) ** 0.8, cx) * 0.086, c.y + math.copysign(abs(cy) ** 0.8, cy) * ry))
        path = [Vector((x, y, 0.0)) for x, y in outline]
        verts, faces = [], []
        for z in (0.0, 0.024):
            verts += [Vector((x, y, z)) for x, y in outline]
        n = len(outline)
        faces += [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
        faces.append(tuple(reversed(range(n))))
        faces.append(tuple(range(n, 2 * n)))
        del path
        U.new_object(f"part_Sole{t}", verts, faces, coll, mats["sole"], smooth_shade=False)


# --------------------------------------------------------------------------- #
# Arms + hands
# --------------------------------------------------------------------------- #
FINGERS = (("index", 0.0285, 0.05, 6), ("middle", 0.0095, 0.056, 1), ("ring", -0.0095, 0.052, -4),
           ("pinky", -0.0275, 0.042, -10))


def hand_frame(s):
    f = arm_dir(s)
    w = Vector((0, -1, 0))                    # thumb side faces forward
    p = f.cross(w) * s                        # palm normal: toward the body / down
    return f, w, p.normalized()


def build_arms(coll, mats):
    for s in (-1, 1):
        t = side_tag(s)
        S, E, W = J[f"shoulder{t}"], J[f"elbow{t}"], J[f"wrist{t}"]
        d = arm_dir(s)
        v, f = U.tube([S + d * 0.02, S + d * 0.1, E, E + d * 0.09, W + d * 0.012],
                      [0.05, 0.049, 0.045, 0.042, 0.037], m=16, n=22)
        U.new_object(f"part_Arm{t}", v, f, coll, mats["skin"])

        f_, w_, p_ = hand_frame(s)
        g = U.Geo()
        pc = W + f_ * 0.036

        def palm(dd):
            e = 2.6
            q = Vector([math.copysign(abs(c) ** (2 / e), c) for c in dd])
            return f_ * (q.x * 0.04) + w_ * (q.y * 0.041) + p_ * (q.z * (0.019 if q.z > 0 else 0.023))
        v, fc = U.uv_ellipsoid((0, 0, 0), (1, 1, 1), seg=20, rings=12, shape=palm)
        g.add([pc + x for x in v], fc)
        for name, off, length, spread in FINGERS:
            base = W + f_ * 0.062 + w_ * off - p_ * 0.002
            fd = (Matrix.Rotation(math.radians(spread), 3, p_) @ f_).normalized()
            pts, cur, dirv = [base], base, fd
            for seg_len, curl in zip((0.42, 0.32, 0.26), (8, 10, 8)):
                dirv = (Matrix.Rotation(math.radians(curl), 3, w_ * s) @ dirv).normalized()
                cur = cur + dirv * length * seg_len
                pts.append(cur)
            J[f"{name}{t}"] = pts
            v, fc = U.tube([base - fd * 0.01] + pts[1:], [0.0118, 0.0112, 0.0104, 0.0096], m=10, n=12,
                           rounded=(False, True))
            g.add(v, fc)
        tb = W + f_ * 0.016 + w_ * 0.024 + p_ * 0.01
        td = (f_ * 0.5 + w_ * 0.72 + p_ * 0.42).normalized()
        tpts = [tb, tb + td * 0.026]
        td2 = (td + f_ * 0.35 + p_ * 0.1).normalized()
        tpts += [tpts[-1] + td2 * 0.022, tpts[-1] + td2 * 0.04]
        J[f"thumb{t}"] = tpts
        v, fc = U.tube(tpts, [0.016, 0.0135, 0.0122, 0.011], m=10, n=12, rounded=(False, True))
        g.add(v, fc)
        g.build(f"part_Hand{t}", coll, mats["skin"])


# --------------------------------------------------------------------------- #
# Glasses + earphones
# --------------------------------------------------------------------------- #
def rounded_rect(w, h, r, n_corner=6):
    pts = []
    for cx, cy, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180),
                       (w / 2 - r, -h / 2 + r, 270)):
        for k in range(n_corner + 1):
            a = math.radians(a0 + 90 * k / n_corner)
            pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    return pts


def build_glasses(coll, mats, head_bvh):
    G_W, G_H = 0.228, 0.146
    g = U.Geo()
    corners = {}
    for s in (-1, 1):
        cx = EYE_X * s
        # Sit the lens just in front of the most forward part of the face behind it.
        front = min(head_bvh.ray_cast(Vector((cx + dx, -1, E_Z + dz)), Vector((0, 1, 0)))[0].y
                    for dx in (-0.1, 0, 0.1) for dz in (-0.07, 0, 0.07))
        yaw = math.radians(13) * s
        mw = Matrix.Translation((cx, front - 0.034, E_Z + 0.004)) @ Matrix.Rotation(yaw, 4, "Z")

        def to3(x, z, mw=mw):
            return mw @ Vector((x, 0, z))
        loop = [to3(x, z) for x, z in rounded_rect(G_W, G_H, 0.03)]
        prof = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        nrm = (mw.to_3x3() @ Vector((0, -1, 0))).normalized()
        v, f = U.sweep(loop, prof, [0.0065] * len(loop), [0.0065] * len(loop),
                       up_hint=lambda i, p, nrm=nrm: nrm, closed_path=True)
        g.add(v, f, 0)
        corners[s] = (to3(G_W / 2 * s, G_H / 2 - 0.022), to3(-G_W / 2 * s, G_H / 2 - 0.03))
    # Bridge: a gentle arch between the inner top corners.
    a, b = corners[-1][1], corners[1][1]
    mid = (a + b) / 2 + Vector((0, -0.01, 0.012))
    v, f = U.tube([a, mid, b], [0.0075] * 3, m=8, n=10, rounded=(False, False))
    g.add(v, f, 0)
    # Temples back to the ears, hooking down behind them.
    for s in (-1, 1):
        o = corners[s][0]
        ear = J[f"ear{side_tag(s)}"]
        pts = [o, o + Vector((0.025 * s, 0.03, 0)), Vector((ear.x + 0.004 * s, ear.y - 0.02, ear.z + 0.07)),
               Vector((ear.x - 0.012 * s, ear.y + 0.05, ear.z + 0.055)), Vector((ear.x - 0.02 * s, ear.y + 0.075, ear.z))]
        v, f = U.sweep(U.catmull(pts, 16), [(-1, -1), (1, -1), (1, 1), (-1, 1)], [0.0045] * 16, [0.008] * 16,
                       up_hint=(0, 0, 1))
        g.add(v, f, 0)
    return g.build("part_Glasses", coll, mats["frame"])


def build_earphones(coll, mats, shirt_bvh):
    g = U.Geo()
    buds = {}
    for s in (-1, 1):
        e = J[f"ear{side_tag(s)}"] + Vector((-0.012 * s, -0.004, -0.006))
        v, f = U.uv_ellipsoid(e, (0.022, 0.022, 0.024), seg=14, rings=8)
        g.add(v, f)
        stem_end = e + Vector((0.004 * s, -0.012, -0.045))
        v, f = U.tube([e, stem_end], [0.009, 0.007], m=8, n=6)
        g.add(v, f)
        buds[s] = stem_end

    def on_shirt(x, z, off=0.012):
        loc, nrm, _i, _d = shirt_bvh.ray_cast(Vector((x, -1.0, z)), Vector((0, 1, 0)))
        return loc + nrm * off
    split = on_shirt(0.0, 0.9, 0.016)
    for s in (-1, 1):
        b = buds[s]
        pts = [b, b + Vector((-0.02 * s, -0.04, -0.12)), Vector((0.24 * s, -0.16, 1.05)),
               on_shirt(0.13 * s, 1.0, 0.014), on_shirt(0.05 * s, 0.95, 0.016), split]
        v, f = U.tube(pts, [0.0055] * len(pts), m=6, n=30)
        g.add(v, f)
    pts = [split, on_shirt(0.03, 0.8, 0.014), on_shirt(0.1, 0.62, 0.012), on_shirt(0.17, 0.5, 0.012),
           Vector((0.21, -0.2, 0.44))]
    v, f = U.tube(pts, [0.0055] * len(pts), m=6, n=28)
    g.add(v, f)
    v, f = U.uv_ellipsoid(split, (0.012, 0.012, 0.022), seg=10, rings=6)       # inline mic / splitter
    g.add(v, f)
    return g.build("part_Earphones", coll, mats["bud"])


# --------------------------------------------------------------------------- #
def joints():
    """Joint positions shared by the mesh builders and the rig."""
    J["root"] = Vector((0, 0, 0))
    J["hips"], J["spine"], J["chest"], J["neck"], J["head"] = (Vector((0, 0.01, z)) for z in (0.56, 0.68, 0.86, 1.03, 1.16))
    J["head_top"] = Vector((0, 0.01, 1.78))
    for s in (-1, 1):
        t = side_tag(s)
        S = Vector((0.212 * s, 0.004, 0.982))
        d = arm_dir(s)
        J[f"clavicle{t}"] = Vector((0.04 * s, 0.0, 1.0))
        J[f"shoulder{t}"] = S
        J[f"elbow{t}"] = S + d * UPPER
        J[f"wrist{t}"] = S + d * (UPPER + FORE)
        J[f"palm{t}"] = S + d * (UPPER + FORE + PALM)
        J[f"hip{t}"] = Vector((0.108 * s, 0.0, 0.54))
        J[f"knee{t}"] = Vector((0.114 * s, -0.012, 0.3))
        J[f"ankle{t}"] = Vector((0.12 * s, 0.0, 0.1))
        J[f"ball{t}"] = Vector((0.12 * s, -0.11, 0.03))
        J[f"toe{t}"] = Vector((0.12 * s, -0.175, 0.03))
        J[f"eye{t}"] = Vector((EYE_X * s, -0.3, E_Z))


HEAD_PARTS = ("part_Head", "part_EarL", "part_EarR", "part_Hair", "part_Glasses", "part_Face")


def lower_head(dz):
    """Shorten the neck: move everything on the head down by dz (design units). The earphone
    cable bends: its top follows fully, fading out toward the chest."""
    for name in HEAD_PARTS:
        me = bpy.data.objects[name].data
        for v in me.vertices:
            v.co.z -= dz
        if me.shape_keys:
            for kb in me.shape_keys.key_blocks:
                for d in kb.data:
                    d.co.z -= dz
    for v in bpy.data.objects["part_Earphones"].data.vertices:
        v.co.z -= dz * U.smooth((v.co.z - 0.98) / 0.2)
    for v in bpy.data.objects["part_Neck"].data.vertices:
        v.co.z -= dz * U.smooth((v.co.z - 1.08) / 0.1)
    for k in ("head", "head_top", "eyeL", "eyeR", "earL", "earR"):
        J[k] = J[k] - Vector((0, 0, dz)) if k != "head" else J[k] - Vector((0, 0, dz * 0.5))


def materials():
    print_img = print_image()
    return {
        "skin": U.material("MAT_Skin", PAL["skin"], rough=0.55, spec=0.35, sheen=0.15),
        "shirt": U.material("MAT_Shirt", PAL["shirt"], rough=0.85, spec=0.25, sheen=0.4),
        "collar": U.material("MAT_ShirtCollar", PAL["collar"], rough=0.9, spec=0.2, sheen=0.3),
        "print": U.material("MAT_ShirtPrint", PAL["print"], rough=0.7, spec=0.3, image=print_img),
        "pants": U.material("MAT_Pants", PAL["pants"], rough=0.8, spec=0.25, sheen=0.3),
        "shoe": U.material("MAT_Shoes", PAL["shoe"], rough=0.45, spec=0.5, coat=0.3),
        "sole": U.material("MAT_ShoeSole", PAL["sole"], rough=0.7),
        "frame": U.material("MAT_GlassesFrame", PAL["frame"], rough=0.3, spec=0.6, coat=0.5),
        "bud": U.material("MAT_Earphones", PAL["bud"], rough=0.3, spec=0.6),
        "hair": U.material("MAT_Hair", PAL["hair"], rough=0.68, spec=0.35, sheen=0.3),
        "hair_hi": U.material("MAT_HairShine", PAL["hair_hi"], rough=0.6, spec=0.4),
    }


def build(coll):
    joints()
    mats = materials()
    head = build_head(coll, mats)
    shirt = build_shirt(coll, mats)
    build_print(coll, mats, shirt)
    build_pants(coll, mats)
    build_shoes(coll, mats)
    build_arms(coll, mats)
    bpy.context.view_layer.update()
    hb = U.bvh_of(head)
    build_glasses(coll, mats, hb)
    build_earphones(coll, mats, U.bvh_of(shirt))
    return mats, hb
