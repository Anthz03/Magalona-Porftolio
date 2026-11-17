"""Facial features as ONE mesh (GEO_Face) whose expressions are shape keys, so the
same morph targets drive the face in Blender and on the web.

Every feature is a flat 2D shape (x, z) projected onto the head surface. Each part
has a fixed topology, and `shape(key)` returns its 2D points for each shape key:
  Basis         happy closed eyes ^ ^, big toothy grin (the reference portrait)
  EyeOpen_L/R   round open eyes with a sparkle (blinks go open -> ^ -> open)
  EyeSquint     flatter ^ ^ (the "blink" while smiling)
  EyeLaugh      > < squeezed eyes
  BrowRaise_L/R, BrowWorry
  MouthSmile    closed smile        MouthLaugh  wide open laugh with tongue
  MouthOh       small round "oh"    MouthHmm    flat, lopsided thinking mouth
  BlushHot      bigger, stronger cheek blush
"""
import math

import bpy
from mathutils import Vector

from . import util as U
from .model import BLUSH_Z, E_Z, EYE_X, M_Z

KEYS = ["EyeOpen_L", "EyeOpen_R", "EyeSquint", "EyeLaugh", "BrowRaise_L", "BrowRaise_R", "BrowWorry",
        "MouthSmile", "MouthLaugh", "MouthOh", "MouthHmm", "BlushHot"]
N_EYE, N_BROW, N_MOUTH, N_RIM, N_BLUSH, N_SPARK = 16, 12, 18, 18, 20, 10


# --------------------------------------------------------------------------- #
# 2D shape helpers
# --------------------------------------------------------------------------- #
def strip(center, thick):
    """center: list of (x, z); thick: list of widths. Returns top + reversed(bottom) edges."""
    n = len(center)
    top, bot = [], []
    for i in range(n):
        a = center[max(i - 1, 0)]
        b = center[min(i + 1, n - 1)]
        tx, tz = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(tx, tz) or 1.0
        nx, nz = -tz / ln, tx / ln
        h = thick[i] / 2
        top.append((center[i][0] + nx * h, center[i][1] + nz * h))
        bot.append((center[i][0] - nx * h, center[i][1] - nz * h))
    return top, bot


def arc(cx, cz, hw, h, n, power=0.9):
    return [(cx + (2 * i / (n - 1) - 1) * hw, cz + h * math.sin(math.pi * i / (n - 1)) ** power) for i in range(n)]


def taper(n, base, ends=0.35):
    return [base * (ends + (1 - ends) * math.sin(math.pi * i / (n - 1)) ** 0.5) for i in range(n)]


def eye_strip(s, key):
    """Top and bottom edges of one eye (s = +1 his left / -1 his right)."""
    cx = EYE_X * s
    n = N_EYE
    tag = "L" if s > 0 else "R"
    if key == f"EyeOpen_{tag}":
        rx, rz = 0.025, 0.036
        top, bot = [], []
        for i in range(n):
            a = math.pi * i / (n - 1)
            x = cx - rx * math.cos(a)
            top.append((x, E_Z + 0.004 + rz * math.sin(a)))
            bot.append((x, E_Z + 0.004 - rz * math.sin(a)))
        return top, bot
    if key == "EyeSquint":
        return strip(arc(cx, E_Z - 0.018, 0.056, 0.014, n), taper(n, 0.014, 0.4))
    if key == "EyeLaugh":
        pts = []
        for i in range(n):
            u = i / (n - 1)
            leg = u * 2 if u < 0.5 else (1 - u) * 2          # 0 at the outer ends, 1 at the tip
            x = cx + s * (0.036 - 0.072 * leg)                   # tip points toward the nose
            z = E_Z + (0.032 if u < 0.5 else -0.032) * (1 - leg)
            pts.append((x, z))
        return strip(pts, taper(n, 0.014, 0.5))
    return strip(arc(cx, E_Z - 0.016, 0.054, 0.034, n), taper(n, 0.021, 0.45))


def sparkle(s, key):
    tag = "L" if s > 0 else "R"
    cx, cz = EYE_X * s + 0.008, E_Z + 0.018
    r = 0.0085 if key == f"EyeOpen_{tag}" else 0.0
    return [(cx + math.cos(2 * math.pi * k / N_SPARK) * r, cz + math.sin(2 * math.pi * k / N_SPARK) * r * 1.1)
            for k in range(N_SPARK)]


def brow(s, key):
    n = N_BROW
    inner, outer = 0.085 * s, 0.208 * s
    lift_in = lift_out = 0.0
    arch = 0.016
    tag = "L" if s > 0 else "R"
    if key == f"BrowRaise_{tag}":
        lift_in, lift_out, arch = 0.03, 0.026, 0.018
    if key == "BrowWorry":
        lift_in, lift_out, arch = 0.022, -0.006, 0.004
    pts = []
    for i in range(n):
        u = i / (n - 1)
        x = inner + (outer - inner) * u
        z = 1.556 + arch * math.sin(math.pi * u) - 0.006 * u + lift_in * (1 - u) + lift_out * u
        pts.append((x, z))
    th = [0.034 * (0.42 + 0.58 * math.sin(math.pi * (0.12 + 0.76 * i / (n - 1))) ** 0.7) * (1 - 0.15 * i / (n - 1))
          for i in range(n)]       # thick, soft-ended brush stroke
    return strip(pts, th)


# --- mouth -------------------------------------------------------------------- #
MOUTH_KEYS = ("MouthSmile", "MouthLaugh", "MouthOh", "MouthHmm")


def mouth_edges(key):
    """Returns (cx, xs, top(x), bottom(x)) for the mouth opening."""
    if key == "MouthSmile":
        hw, cx = 0.07, 0.0
        top = lambda x: M_Z + 0.006 + 0.022 * (x / hw) ** 2
        bot = lambda x: top(x) - 0.006 * (1 - (x / hw) ** 2) ** 0.5
    elif key == "MouthLaugh":
        hw, cx = 0.088, 0.0
        top = lambda x: M_Z + 0.03 + 0.012 * (x / hw) ** 2
        bot = lambda x: top(x) - 0.125 * max(1 - (x / hw) ** 2, 0) ** 0.72
    elif key == "MouthOh":
        hw, cx = 0.03, 0.0
        top = lambda x: M_Z + 0.006 + 0.026 * max(1 - (x / hw) ** 2, 0) ** 0.5
        bot = lambda x: M_Z + 0.006 - 0.03 * max(1 - (x / hw) ** 2, 0) ** 0.5
    elif key == "MouthHmm":
        hw, cx = 0.045, 0.022
        top = lambda x: M_Z + 0.012 + 0.008 * (x / hw) + 0.003 * math.sin(3 * x / hw)
        bot = lambda x: top(x) - 0.007 * max(1 - (x / hw) ** 2, 0) ** 0.5
    else:   # Basis: big D-shaped grin
        hw, cx = 0.1, 0.0
        top = lambda x: M_Z + 0.022 + 0.02 * (x / hw) ** 2
        bot = lambda x: top(x) - 0.074 * max(1 - (x / hw) ** 2, 0) ** 0.55
    xs = [-hw * math.cos(math.pi * i / (N_MOUTH - 1)) for i in range(N_MOUTH)]
    return cx, xs, top, bot


def mouth_loop(key, grow=0.0):
    """Closed loop: top edge left->right, bottom edge right->left (corners shared)."""
    key = key if key in MOUTH_KEYS else "Basis"
    cx, xs, top, bot = mouth_edges(key)
    pts = [(x, top(x)) for x in xs] + [(x, bot(x)) for x in reversed(xs[1:-1])]
    if grow:
        out = []
        n = len(pts)
        mx = sum(p[0] for p in pts) / n
        mz = sum(p[1] for p in pts) / n
        for i, (x, z) in enumerate(pts):
            a, b = pts[i - 1], pts[(i + 1) % n]
            tx, tz = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(tx, tz) or 1
            nx, nz = tz / ln, -tx / ln
            if (x - mx) * nx + (z - mz) * nz < 0:
                nx, nz = -nx, -nz
            out.append((x + nx * grow, z + nz * grow))
        pts = out
    return [(x + cx, z) for x, z in pts]


def teeth(key):
    key = key if key in MOUTH_KEYS else "Basis"
    cx, xs, top, bot = mouth_edges(key)
    band = {"Basis": 1.0, "MouthLaugh": 0.22}.get(key, 0.0)
    inset = 0.93
    t, b = [], []
    for x in xs:
        xi = x * inset
        tt, bb = top(xi) - 0.0025, bot(xi)
        depth = tt - bb
        lo = max(tt - depth * band, bb + 0.003)
        if band == 0.0:
            lo = tt
        lo = min(lo, tt)
        t.append((xi + cx, tt))
        b.append((xi + cx, lo))
    return t, b


def teeth_line(key):
    key = key if key in MOUTH_KEYS else "Basis"
    cx, xs, top, bot = mouth_edges(key)
    pts = []
    for i in range(10):
        x = (2 * i / 9 - 1) * 0.8 * (max(abs(v) for v in xs))
        pts.append((x + cx, top(x) - (top(x) - bot(x)) * 0.48))
    th = [(0.0042 * (0.5 + 0.5 * math.sin(math.pi * i / 9)) if key == "Basis" else 0.0) for i in range(10)]
    if key != "Basis":
        mid = pts[5]
        pts = [mid] * 10
    return strip(pts, th)


def tongue(key):
    key = key if key in MOUTH_KEYS else "Basis"
    cx, xs, top, bot = mouth_edges(key)
    n = 12
    if key == "MouthLaugh":
        rx, h = 0.044, 0.034
    else:
        rx, h = 0.0, 0.0
    t, b = [], []
    for i in range(n):
        x = -rx * math.cos(math.pi * i / (n - 1))
        base = bot(x) + 0.003
        t.append((x + cx, base + h * max(1 - (x / max(rx, 1e-6)) ** 2, 0) ** 0.6 if rx else bot(0) + 0.003))
        b.append((x + cx, base if rx else bot(0) + 0.003))
    return t, b


def blush(s, key):
    hot = key == "BlushHot"
    rx, rz = (0.085, 0.052) if hot else (0.066, 0.038)
    cx, cz = 0.226 * s, BLUSH_Z - 0.016 + (0.004 if hot else 0)
    rot = -0.18 * s
    out = []
    for k in range(N_BLUSH):
        a = 2 * math.pi * k / N_BLUSH
        x, z = math.cos(a) * rx, math.sin(a) * rz
        out.append((cx + x * math.cos(rot) - z * math.sin(rot), cz + x * math.sin(rot) + z * math.cos(rot)))
    return out


# --------------------------------------------------------------------------- #
def blush_image():
    import numpy as np
    n = 128
    y, x = np.mgrid[0:n, 0:n]
    r = np.hypot((x + 0.5) / n * 2 - 1, (y + 0.5) / n * 2 - 1)
    a = np.clip(1 - r, 0, 1) ** 1.3
    hatch = 1 - 0.18 * (np.sin(((x - y) / n) * 40) > 0.6) * (r < 0.7)
    rgba = np.stack([np.full_like(a, 0.96), np.full_like(a, 0.55) * hatch + 0.02, np.full_like(a, 0.53) * hatch,
                     np.clip(a * 1.5, 0, 0.95)], axis=-1).astype(np.float32)
    return U.image_from_pixels("TEX_Blush", n, n, rgba.ravel())


PARTS = []          # (name, material, bone, kind, fn) kind: 'strip' | 'fan'


def build(coll, head_bvh):
    mats = {
        "line": U.material("MAT_FaceLine", "#3a1c16", rough=0.8, spec=0.2),
        "brow": U.material("MAT_Brow", "#1a1c27", rough=0.75, spec=0.2),
        "inner": U.material("MAT_MouthInner", "#8a2c34", rough=0.6),
        "teeth": U.material("MAT_Teeth", "#fffdf8", rough=0.35, spec=0.5),
        "tongue": U.material("MAT_Tongue", "#e47f7a", rough=0.5),
        "spark": U.material("MAT_EyeSparkle", "#ffffff", rough=0.3, emission=0.6),
        "blush": U.material("MAT_Blush", "#f39d93", rough=0.8, alpha="tex", image=blush_image()),
    }
    order = ["line", "brow", "inner", "teeth", "tongue", "spark", "blush"]
    mi = {k: i for i, k in enumerate(order)}

    def to3(x, z, off):
        loc, nrm, _i, _d = head_bvh.ray_cast(Vector((x, -1.0, z)), Vector((0, 1, 0)))
        return loc + nrm * off

    parts = []
    for s in (-1, 1):
        t = "L" if s > 0 else "R"
        parts += [(f"eye{t}", "line", f"eye.{t}", "strip", lambda k, s=s: eye_strip(s, k), 0.004),
                  (f"spark{t}", "spark", f"eye.{t}", "fan", lambda k, s=s: sparkle(s, k), 0.0065),
                  (f"brow{t}", "brow", "head", "strip", lambda k, s=s: brow(s, k), 0.004),
                  (f"blush{t}", "blush", "head", "fan", lambda k, s=s: blush(s, k), 0.0025)]
    parts += [("mouthRim", "line", "head", "fan", lambda k: mouth_loop(k, 0.0095), 0.0035),
              ("mouthInner", "inner", "head", "fan", lambda k: mouth_loop(k), 0.005),
              ("tongue", "tongue", "head", "strip", tongue, 0.0062),
              ("teeth", "teeth", "head", "strip", teeth, 0.007),
              ("teethLine", "line", "head", "strip", teeth_line, 0.0078)]

    # Build topology from the Basis shape, remember each part's vertex range.
    verts, faces, fmat, groups, uvs = [], [], [], {}, []
    shapes_2d = {}
    for name, mat, bone, kind, fn, off in parts:
        start = len(verts)
        if kind == "strip":
            top, bot = fn("Basis")
            n = len(top)
            pts2 = top + bot
            fcs = [(start + i, start + i + 1, start + n + i + 1, start + n + i) for i in range(n - 1)]
        else:
            loop = fn("Basis")
            n = len(loop)
            pts2 = [None] + loop                   # fan centre filled per key
            fcs = [(start, start + 1 + i, start + 1 + (i + 1) % n) for i in range(n)]
        for k in range(len(pts2)):
            verts.append(None)
            uvs.append((0.5, 0.5))
        if kind == "fan":
            for i in range(n):
                a = 2 * math.pi * i / n
                uvs[start + 1 + i] = (0.5 + 0.5 * math.cos(a), 0.5 + 0.5 * math.sin(a))
        faces += fcs
        fmat += [mi[mat]] * len(fcs)
        groups.setdefault(bone, []).extend(range(start, len(verts)))
        shapes_2d[name] = (start, kind, fn, off)

    def positions(key):
        out = [None] * len(verts)
        for name, (start, kind, fn, off) in shapes_2d.items():
            if kind == "strip":
                top, bot = fn(key)
                pts = top + bot
            else:
                loop = fn(key)
                cx = sum(p[0] for p in loop) / len(loop)
                cz = sum(p[1] for p in loop) / len(loop)
                pts = [(cx, cz)] + loop
            for i, (x, z) in enumerate(pts):
                out[start + i] = to3(x, z, off)
        return out

    base = positions("Basis")
    o = U.new_object("part_Face", base, faces, coll, [mats[k] for k in order], smooth_shade=True, mat_index=fmat)
    uv = o.data.uv_layers.new(name="UVMap")
    for loop in o.data.loops:
        uv.data[loop.index].uv = uvs[loop.vertex_index]
    for bone, idx in groups.items():
        o.vertex_groups.new(name=bone).add(idx, 1.0, "REPLACE")
    o["prebound"] = True                      # rig: keep these weights
    o.shape_key_add(name="Basis")
    for key in KEYS:
        kb = o.shape_key_add(name=key, from_mix=False)
        kb.value = 0.0
        kb.slider_min, kb.slider_max = 0.0, 1.0
        for i, p in enumerate(positions(key)):
            kb.data[i].co = p
    return o
