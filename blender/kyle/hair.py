"""Hair: a scalp cap plus layered, flattened, tapered clumps (nape -> sides ->
crown -> top spikes -> bangs) and a few highlight streaks. Angles below are in
degrees: theta from the crown (0 = top), phi around the head (0 = front, +90 =
his left / +X, 180 = back)."""
import math
import random

from mathutils import Matrix, Vector

from . import util as U
from .model import HEAD_C, head_shape, sph_dir

CAP = 1.05          # cap sits this much outside the skull


def d(theta, phi):
    return sph_dir(math.radians(theta), math.radians(phi))


def surf(direction, k=CAP):
    return HEAD_C + head_shape(direction) * k


def slerp(a, b, t):
    a, b = a.normalized(), b.normalized()
    dot = max(-1.0, min(1.0, a.dot(b)))
    om = math.acos(dot)
    if om < 1e-5:
        return a
    return (a * math.sin((1 - t) * om) + b * math.sin(t * om)) / math.sin(om)


ELLIPSE = [(math.cos(2 * math.pi * k / 7), math.sin(2 * math.pi * k / 7) * (0.55 if k > 3 else 1.0))
           for k in range(7)]           # flatter underside so clumps sit on the cap


def clump(g, start, end, width, thick=0.035, lift=0.04, lift0=0.0, mid=None, bend=0.0, n=10, mat=0,
          tip_pow=0.62):
    """A tapered clump from direction `start` to `end` along the head (slerp), lifted
    off the surface toward the tip. `mid` optionally shapes the path; `bend` swings the
    tip sideways (fraction of the path length)."""
    path, sx, sy = [], [], []
    a, b = start.normalized(), end.normalized()
    side = a.cross(b).normalized() if a.cross(b).length > 1e-5 else Vector((1, 0, 0))
    for i in range(n):
        u = i / (n - 1)
        if mid is not None:
            dirv = slerp(slerp(a, mid, u), slerp(mid, b, u), u)
        else:
            dirv = slerp(a, b, u)
        dirv = (dirv + side * bend * u * u).normalized()
        lift_u = lift0 + (lift - lift0) * u ** 2.2
        taper = (1 - u) ** tip_pow * (0.78 + 0.22 * U.smooth(u / 0.22))
        p = surf(dirv, CAP + lift_u) + dirv * thick * 0.5 * taper
        path.append(p)
        sx.append(width * 0.5 * taper)
        sy.append(thick * 0.5 * taper)
    sx[-1] = sy[-1] = 0.0

    def up(i, p):
        return (p - HEAD_C).normalized()
    v, f = U.sweep(path, ELLIPSE, sx, sy, up_hint=up)
    g.add(v, f, mat)


def build(coll, mats):
    random.seed(7)
    j = random.uniform
    g = U.Geo()

    # --- scalp cap ------------------------------------------------------------ #
    dirs, faces = U.quad_sphere(14)

    def keep(dv, margin=0.0):
        th = math.degrees(math.acos(max(-1, min(1, dv.z))))
        ph = abs(math.degrees(math.atan2(dv.x, -dv.y)))
        if ph < 62:
            lim = 73 + 22 * (ph / 62) ** 2           # forehead -> temples
        elif ph < 86:
            lim = 106                                 # sideburns in front of the ears
        elif ph < 118:
            lim = 100                                 # above the ears
        else:
            lim = 118 + 22 * U.smooth((ph - 118) / 40)   # behind the ears -> nape
        return th < lim - margin
    kept = [f for f in faces if all(keep(dirs[i]) for i in f)]
    used = sorted({i for f in kept for i in f})
    remap = {o: n for n, o in enumerate(used)}
    g.add([surf(dirs[i]) for i in used], [tuple(remap[i] for i in f) for f in kept])

    # --- main mass: ~110 clumps flowing away from the crown whorl ------------- #
    # Roots are spread evenly (Fibonacci sphere) over the scalp; each clump follows the
    # great circle from the whorl through its root, so the hair "grows" outward and
    # down like a real cut, with random length, lift and sideways flick for mess.
    whorl = d(26, 180)
    n_pts = 300
    for k in range(n_pts):
        z = 1 - 2 * (k + 0.5) / n_pts
        r = math.sqrt(1 - z * z)
        a_ = k * math.pi * (3 - math.sqrt(5))
        root = Vector((r * math.cos(a_), r * math.sin(a_), z))
        if root.z < 0.0 or not keep(root, margin=14):
            continue
        axis = whorl.cross(root)
        if axis.length < 0.08:
            axis = Vector((1, 0, 0))
        back = root.y > 0.15 and root.z < 0.65
        length = j(0.6, 0.8) if back else j(0.42, 0.62)
        end = Matrix.Rotation(length, 3, axis.normalized()) @ root
        front = -root.y > 0.55 and root.z > 0.35          # forehead roots: keep close, bangs cover them
        clump(g, root, end, j(0.13, 0.18), 0.05, lift=(0.03 if front else j(0.06, 0.16)), lift0=0.03,
              bend=j(-0.12, 0.12), n=9)

    # --- sides: flat sideburns, a covering layer over the ears, outward spikes --- #
    for s in (-1, 1):
        for ph, th1, w in ((68, 104, 0.09), (79, 112, 0.1)):
            clump(g, d(50, s * (ph - 16)), d(th1, s * ph), w, 0.035, lift=0.015, lift0=0.02)
        for ph, th1 in ((90, 96), (104, 100), (120, 108)):
            clump(g, d(36, s * (ph - 24)), d(th1, s * ph), 0.16, 0.05, lift=0.05, lift0=0.03)
        for ph, th1, lift in ((88, 82, 0.2), (104, 88, 0.26), (122, 94, 0.24), (142, 100, 0.18)):
            clump(g, d(38, s * (ph - 28)), d(th1 + j(-3, 3), s * (ph + j(-4, 4))), 0.15, 0.055, lift=lift,
                  lift0=0.04, bend=0.06 * s)

    # --- crown: clumps radiating from a whorl at the back of the top ---------- #
    whorl = d(24, 180)
    for k in range(18):
        ph = -170 + k * (340 / 17) + j(-5, 5)
        th1 = 64 + j(0, 12) if abs(ph) < 60 else 76 + j(-6, 8)
        clump(g, whorl, d(th1, ph), 0.2, 0.06, lift=0.17 + j(0, 0.08), lift0=0.05, bend=j(-0.07, 0.07))

    # --- top spikes: a few short, upright, deliberate tufts -------------------- #
    for th0, ph, th1, ph1, lift in ((8, 160, 34, 120, 0.3), (10, -150, 36, -115, 0.32), (14, 60, 40, 30, 0.26),
                                    (14, -40, 40, -70, 0.28), (20, 180, 46, 205, 0.3), (6, 0, 30, 10, 0.27)):
        clump(g, d(th0, ph), d(th1, ph1), 0.12, 0.05, lift=lift, lift0=0.06, tip_pow=0.55)

    # --- front-top volume: bigger clumps sweeping forward over the forehead ----- #
    for k, ph in enumerate((-70, -50, -30, -10, 10, 30, 50, 70)):
        clump(g, d(12, 180 + ph * 0.3), d(62 + j(-2, 4), ph + j(-4, 4)), 0.2, 0.06,
              lift=0.13 + 0.04 * (k % 2), lift0=0.06, bend=j(-0.05, 0.05))

    # --- bangs: chunky pointed locks to just above the glasses ------------------ #
    bangs = ((-58, 82, 0.14), (-43, 88, 0.14), (-28, 81, 0.14), (-14, 89, 0.145), (0, 84, 0.145),
             (14, 90, 0.14), (28, 81, 0.14), (43, 87, 0.135), (58, 80, 0.13))
    for ph, th1, w in bangs:
        mid = d(46, ph * 0.85 - 4)
        clump(g, d(16, 180 + ph * 0.2), d(th1 + j(-1.5, 1.5), ph - 6), w, 0.05, lift=0.035, lift0=0.07,
              mid=mid, tip_pow=0.6)

    # --- highlight streaks (separate material) --------------------------------- #
    for ph, th in ((-34, 44), (-12, 40), (20, 41), (40, 46)):
        a, b = d(th - 4, ph - 3), d(th + 4, ph + 2)
        clump(g, a, b, 0.03, 0.006, lift=0.2, lift0=0.2, mat=1, n=6, tip_pow=0.6)

    return g.build("part_Hair", coll, [mats["hair"], mats["hair_hi"]])
