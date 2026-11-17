"""Animation actions, authored as key poses.

Pose spec: {bone: [ops]} where an op is
    ("X"|"Y"|"Z", deg)          rotate about an armature axis (as seen from the rest pose)
    ("twist"|"curl"|"spread", deg)   rotate about the bone's own Y / X / Z axis
    ("q", Quaternion)            a local rotation (from solve(): IK reach / aim)
    ("loc", (x, y, z))           translation in metres, armature axes
Armature axes: -Y is forward (toward the viewer), +X is his left, +Z up.
  +X tilts upward bones forward;   +Y tilts the top toward his left;   +Z turns toward his left.
Face spec: {shape_key: value} driven through the CTRL_face bone.

Actions: Idle, Wave, Happy, Thinking, Goodbye, Turn (30 fps). Idle and Thinking
loop in place; the rest start and end on the idle pose so they can loop or be
cross-faded in and out of Idle.
"""
import math
import os

import bpy
from mathutils import Matrix, Quaternion, Vector

from . import face as F
from .rig import SCALE

AX = {"X": Vector((1, 0, 0)), "Y": Vector((0, 1, 0)), "Z": Vector((0, 0, 1))}
LOCAL = {"twist": Vector((0, 1, 0)), "curl": Vector((1, 0, 0)), "spread": Vector((0, 0, 1))}
FINGER_NAMES = ("index", "middle", "ring", "pinky")


# --------------------------------------------------------------------------- #
# Pose helpers
# --------------------------------------------------------------------------- #
def ops_to_quat(rig, bname, ops):
    R = rig.data.bones[bname].matrix_local.to_3x3().to_quaternion()
    Ri = R.inverted()
    q = Quaternion()
    for op, val in ops:
        if op in AX:
            q = (Ri @ Quaternion(AX[op], math.radians(val)) @ R) @ q
        elif op in LOCAL:
            q = q @ Quaternion(LOCAL[op], math.radians(val))
        elif op == "q":
            q = val @ q
    return q


def apply_pose(rig, pose):
    for pb in rig.pose.bones:
        pb.location = (0, 0, 0)
        if pb.rotation_mode == "QUATERNION":
            pb.rotation_quaternion = Quaternion()
        else:
            pb.rotation_euler = (0, 0, 0)
    for bname, ops in pose.items():
        if not ops:
            continue
        pb = rig.pose.bones[bname]
        loc = next((v for o, v in ops if o == "loc"), None)
        if loc is not None:
            R = rig.data.bones[bname].matrix_local.to_3x3()
            pb.location = R.inverted() @ Vector(loc)
        if pb.rotation_mode == "QUATERNION":
            pb.rotation_quaternion = ops_to_quat(rig, bname, [o for o in ops if o[0] != "loc"])
        else:
            e = [0.0, 0.0, 0.0]
            for o, v in ops:
                if o in AX:
                    e["XYZ".index(o)] += math.radians(v)
            pb.rotation_euler = e


def hand(t, curls=(8, 10, 12, 14), thumb=8, spread=0.0, tips=1.0):
    """Finger pose: curls per finger (deg per joint) from index to pinky."""
    out = {}
    for name, c, sp in zip(FINGER_NAMES, curls, (1.2, 0.3, -0.5, -1.2)):
        out[f"{name}.01.{t}"] = [("curl", c), ("spread", sp * spread)]
        out[f"{name}.02.{t}"] = [("curl", c * 1.15 * tips)]
        out[f"{name}.03.{t}"] = [("curl", c * 0.9 * tips)]
    out[f"thumb.01.{t}"] = [("curl", thumb * 0.5)]
    out[f"thumb.02.{t}"] = [("curl", thumb)]
    out[f"thumb.03.{t}"] = [("curl", thumb)]
    return out


RELAXED = lambda t: hand(t, (10, 14, 17, 21), 10)          # noqa: E731
OPEN = lambda t: hand(t, (2, 2, 3, 4), 0, spread=10)        # noqa: E731
FIST = lambda t: hand(t, (78, 82, 85, 88), 40)             # noqa: E731
POINT = lambda t: hand(t, (4, 75, 82, 86), 30)             # noqa: E731


def base_pose():
    p = {
        "upper_arm.L": [("Y", 35), ("X", -4)], "upper_arm.R": [("Y", -35), ("X", -4)],
        "forearm.L": [("X", -14)], "forearm.R": [("X", -14)],
        "hand.L": [("twist", 6)], "hand.R": [("twist", -6)],
    }
    p.update(RELAXED("L"))
    p.update(RELAXED("R"))
    return p


def merge(*dicts):
    out = {}
    for d in dicts:
        out.update(d)
    return out


def D(v):
    """design units -> metres"""
    return Vector(v) * SCALE


def solve(kyle, pose, reaches=(), aims=()):
    """Bake IK reaches (wrist to a design-space target, elbow toward a pole point)
    and hand aims (bone Y -> y_dir, bone Z -> z_dir) into ("q", quat) ops on top of `pose`."""
    rig = kyle["rig"]
    sc = bpy.context.scene
    apply_pose(rig, pose)
    bpy.context.view_layer.update()
    out = {}
    for t, target, pole in reaches:
        tgt = bpy.data.objects.new("tmp_target", None)
        pol = bpy.data.objects.new("tmp_pole", None)
        sc.collection.objects.link(tgt)
        sc.collection.objects.link(pol)
        tgt.location, pol.location = D(target), D(pole)
        fa = rig.pose.bones[f"forearm.{t}"]
        ik = fa.constraints.new("IK")
        ik.target, ik.pole_target, ik.chain_count = tgt, pol, 2
        best = None
        for ang in range(-180, 180, 10):
            ik.pole_angle = math.radians(ang)
            bpy.context.view_layer.update()
            elbow = rig.pose.bones[f"upper_arm.{t}"].tail
            dist = (elbow - pol.location).length
            if best is None or dist < best[0]:
                best = (dist, ang)
        ik.pole_angle = math.radians(best[1])
        bpy.context.view_layer.update()
        mats = {}
        for b in (f"upper_arm.{t}", f"forearm.{t}"):
            pb = rig.pose.bones[b]
            mats[b] = rig.convert_space(pose_bone=pb, matrix=pb.matrix, from_space="POSE", to_space="LOCAL")
        fa.constraints.remove(ik)
        bpy.data.objects.remove(tgt)
        bpy.data.objects.remove(pol)
        for b, m in mats.items():
            q = m.to_quaternion()
            rig.pose.bones[b].rotation_quaternion = q
            out[b] = [("q", q)]
        bpy.context.view_layer.update()
    for bname, ydir, zdir in aims:
        pb = rig.pose.bones[bname]
        y = Vector(ydir).normalized()
        z = (Vector(zdir) - y * Vector(zdir).dot(y)).normalized()
        x = y.cross(z)
        m = Matrix((x, y, z)).transposed().to_4x4()
        m.translation = pb.head
        pb.matrix = m
        bpy.context.view_layer.update()
        q = pb.rotation_quaternion.copy()
        out[bname] = [("q", q)]
    return out


# --------------------------------------------------------------------------- #
# Action authoring
# --------------------------------------------------------------------------- #
class Act:
    def __init__(self, kyle, name, end, loop, base=None):
        self.rig = kyle["rig"]
        self.name = name
        self.base = base if base is not None else base_pose()
        self.last = {}
        act = bpy.data.actions.new(name)
        act.use_fake_user = True
        act.use_frame_range = True
        act.frame_start, act.frame_end = 0, end
        act["loop"] = loop
        self.rig.animation_data_create()
        self.rig.animation_data.action = act
        self.act = act

    def key(self, frame, pose=None, face=None):
        rig = self.rig
        full = merge(self.base, pose or {})
        apply_pose(rig, full)
        for pb in rig.pose.bones:
            n = pb.name
            if n.startswith("CTRL_face"):
                continue
            if pb.rotation_mode == "QUATERNION":
                q = pb.rotation_quaternion.copy()
                prev = self.last.get(n)
                if prev is not None and prev.dot(q) < 0:
                    q.negate()
                    pb.rotation_quaternion = q
                self.last[n] = q
                pb.keyframe_insert("rotation_quaternion", frame=frame, group=n)
            else:
                pb.keyframe_insert("rotation_euler", frame=frame, group=n)
            if n in ("root", "hips") or n.startswith("CTRL_foot_ik"):
                pb.keyframe_insert("location", frame=frame, group=n)
        fc = rig.pose.bones["CTRL_face"]
        vals = {k: 0.0 for k in F.KEYS}
        vals.update(face or {})
        for k, v in vals.items():
            fc[k] = float(v)
            fc.keyframe_insert(f'["{k}"]', frame=frame, group="CTRL_face")

    def done(self):
        ad = self.rig.animation_data
        track = ad.nla_tracks.new()
        track.name = self.name
        track.strips.new(self.name, 0, self.act)
        track.mute = True
        ad.action = None


def wave_cycle(a, f0, n, period, pose_a, pose_b, extra=None, face=None):
    """Alternate between two poses n times starting at f0 (half a period each)."""
    for i in range(n * 2):
        a.key(f0 + i * period // 2, merge(pose_a if i % 2 == 0 else pose_b, extra or {}), face)
    return f0 + n * period


# --------------------------------------------------------------------------- #
def build(kyle):
    rig = kyle["rig"]
    base = base_pose()
    sm = {"MouthSmile": 1.0}

    # ---------------------------------------------------------------- Idle (loop, 4 s)
    a = Act(kyle, "Idle", 120, True)
    for f in range(0, 121, 10):
        u = 2 * math.pi * f / 120
        br = math.sin(u * 2)                         # 2 breaths per loop
        sway = math.sin(u)
        a.key(f, {
            "hips": [("loc", (0, 0, 0.0025 * br)), ("Y", 1.2 * sway)],
            "spine": [("X", -0.8 * br), ("Y", -0.8 * sway)],
            "chest": [("X", -1.2 * br)],
            "neck": [("X", 0.8 * math.sin(u * 2 + 0.6))],
            "head": [("Y", 3.5 * math.sin(u + 0.8)), ("Z", 4 * math.sin(u * 1 + 2.2)), ("X", 1.5 * math.sin(u * 2 + 1))],
            "clavicle.L": [("Y", -1.5 * br)], "clavicle.R": [("Y", 1.5 * br)],
            "upper_arm.L": [("Y", 35 + 1.5 * math.sin(u + 1)), ("X", -4 + 2 * math.sin(u * 2 + 1.5))],
            "upper_arm.R": [("Y", -35 - 1.5 * math.sin(u + 1.3)), ("X", -4 + 2 * math.sin(u * 2 + 1.8))],
        }, {"EyeSquint": 0.0})
    # blink (squint pulse of the happy eyes) and a softer smile beat
    a.key(76, {}, {})
    a.key(79, {}, {"EyeSquint": 1.0})
    a.key(82, {}, {})
    a.done()

    # ---------------------------------------------------------------- Wave (one-shot, 2.8 s)
    up_a = solve(kyle, base, reaches=[("R", (-0.55, -0.07, 1.0), (-0.5, 0.05, 0.5))],
                 aims=[("hand.R", (-0.45, 0.0, 1.0), (0.0, -1.0, 0.0))])
    up_b = solve(kyle, base, reaches=[("R", (-0.48, -0.09, 1.03), (-0.5, 0.05, 0.5))],
                 aims=[("hand.R", (0.15, -0.05, 1.0), (0.0, -1.0, 0.0))])
    lift = solve(kyle, base, reaches=[("R", (-0.52, -0.05, 0.92), (-0.5, 0.05, 0.5))],
                 aims=[("hand.R", (-0.6, 0.0, 1.0), (0.2, -1.0, 0.0))])
    body = {"head": [("Y", -9), ("Z", -6), ("X", -2)], "spine": [("Y", 2.5)], "chest": [("Y", 2)],
            "upper_arm.L": [("Y", 40), ("X", -3)]}
    for d in (up_a, up_b, lift):
        d.update(OPEN("R"))
    hi = {"BlushHot": 0.35}
    a = Act(kyle, "Wave", 84, False)
    a.key(0)
    a.key(6, {"hips": [("loc", (0, 0, -0.008))], "head": [("X", 3)], "upper_arm.R": [("Y", -44)]})
    a.key(13, merge(lift, body, {"hips": [("loc", (0, 0, 0.004))]}), hi)
    f = wave_cycle(a, 18, 4, 12, up_a, up_b, body, hi)
    a.key(f, merge(up_a, body), hi)
    a.key(f + 8, merge(lift, {"head": [("Y", -4)]}), {"BlushHot": 0.2})
    a.key(84)
    a.done()

    # ---------------------------------------------------------------- Happy (one-shot, 2 s)
    cheer = solve(kyle, base, reaches=[("R", (-0.15, -0.3, 0.9), (-0.6, 0.1, 0.6)),
                                       ("L", (0.15, -0.3, 0.9), (0.6, 0.1, 0.6))],
                  aims=[("hand.R", (0.1, -0.3, 1.0), (0.4, 0.8, 0.0)), ("hand.L", (-0.1, -0.3, 1.0), (-0.4, 0.8, 0.0))])
    cheer.update(FIST("L"))
    cheer.update(FIST("R"))
    laugh = {"EyeLaugh": 1.0, "MouthLaugh": 1.0, "BlushHot": 1.0}

    def hop(z, feet=0.0, tilt=0.0):
        return {"hips": [("loc", (0, 0, z))], "CTRL_foot_ik.L": [("loc", (0, 0, feet))],
                "CTRL_foot_ik.R": [("loc", (0, 0, feet))], "head": [("X", -6 + tilt), ("Y", tilt * 0.6)],
                "chest": [("X", -3)]}
    a = Act(kyle, "Happy", 60, False)
    a.key(0)
    a.key(5, merge(hop(-0.022), cheer), {"EyeSquint": 1.0, "BlushHot": 0.5})
    a.key(11, merge(hop(0.03, 0.028, 5), cheer), laugh)
    a.key(17, merge(hop(-0.02, 0.0, -3), cheer), laugh)
    a.key(23, merge(hop(0.026, 0.024, -5), cheer), laugh)
    a.key(29, merge(hop(-0.018, 0.0, 3), cheer), laugh)
    a.key(36, merge(hop(0.004), cheer), merge(laugh, {"MouthLaugh": 0.6}))
    a.key(46, {"hips": [("loc", (0, 0, -0.004))]}, {"BlushHot": 0.4})
    a.key(60)
    a.done()

    # ---------------------------------------------------------------- Thinking (loop, 4 s)
    think = solve(kyle, base, reaches=[("R", (-0.03, -0.32, 0.99), (-0.45, -0.15, 0.6)),
                                       ("L", (-0.06, -0.27, 0.76), (0.55, 0.05, 0.62))],
                  aims=[("hand.R", (0.05, -0.25, 1.0), (0.1, 0.95, 0.2)), ("hand.L", (-1.0, 0.0, 0.15), (0.0, 0.0, 1.0))])
    think.update(POINT("R"))
    think.update(hand("L", (20, 25, 28, 32), 10))
    tb = {"head": [("Y", 9), ("X", -5), ("Z", 5)], "neck": [("Y", 2)], "spine": [("Y", -1.5)]}
    tf = {"EyeOpen_L": 1.0, "EyeOpen_R": 1.0, "MouthHmm": 1.0, "BrowRaise_L": 0.9, "BrowWorry": 0.25}
    a = Act(kyle, "Thinking", 120, True, base=merge(base, think, tb))
    tap = merge(think, tb, {"index.01.R": [("curl", 22)], "index.02.R": [("curl", 18)]})
    for f, extra, face in ((0, {}, tf), (20, {"head": [("Y", 11), ("X", -6), ("Z", 7)]}, tf),
                           (40, tap, tf), (44, {}, tf), (48, tap, tf), (52, {}, tf),
                           (70, {"head": [("Y", 7), ("X", -4), ("Z", 3)]}, tf),
                           (84, {}, tf), (87, {}, merge(tf, {"EyeOpen_L": 0.0, "EyeOpen_R": 0.0})), (90, {}, tf),
                           (120, {}, tf)):
        a.key(f, extra, face)
    a.done()

    # ---------------------------------------------------------------- Goodbye (one-shot, 3.3 s)
    bye_a = solve(kyle, base, reaches=[("R", (-0.52, -0.06, 1.34), (-0.75, 0.1, 0.85))],
                  aims=[("hand.R", (-0.4, 0.0, 1.0), (0.0, -1.0, 0.1))])
    bye_b = solve(kyle, base, reaches=[("R", (-0.42, -0.08, 1.4), (-0.75, 0.1, 0.85))],
                  aims=[("hand.R", (0.35, -0.05, 1.0), (0.0, -1.0, 0.1))])
    for d in (bye_a, bye_b):
        d.update(OPEN("R"))
    lean = {"head": [("Y", -7), ("Z", -4)], "spine": [("Y", 3)], "chest": [("Y", 3)], "upper_arm.L": [("Y", 40)]}
    bf = {"MouthSmile": 1.0, "BlushHot": 0.3}
    a = Act(kyle, "Goodbye", 100, False)
    a.key(0)
    a.key(10, merge(bye_a, lean, {"hips": [("loc", (0, 0, 0.004))]}), bf)
    f = wave_cycle(a, 16, 3, 18, bye_b, bye_a, lean, bf)
    a.key(f + 2, merge(bye_a, lean), bf)
    a.key(f + 12, {"head": [("X", 10)], "spine": [("X", 6)], "hips": [("loc", (0, 0, -0.006))]}, sm)   # little bow
    a.key(100, {}, {})
    a.done()

    # ---------------------------------------------------------------- Turn (one-shot / loopable, 3 s)
    spin = {"upper_arm.L": [("Y", 44)], "upper_arm.R": [("Y", -44)]}
    a = Act(kyle, "Turn", 90, False)
    a.key(0)
    a.key(8, {"root": [("Z", -8)], "hips": [("loc", (0, 0, -0.01))], "head": [("Z", 10)]})
    a.key(30, merge(spin, {"root": [("Z", 120)], "head": [("Z", 14)], "hips": [("loc", (0, 0, 0.012))]}))
    a.key(52, merge(spin, {"root": [("Z", 250)], "head": [("Z", 12)], "hips": [("loc", (0, 0, 0.012))]}))
    a.key(74, {"root": [("Z", 366)], "head": [("Z", -4)], "hips": [("loc", (0, 0, -0.006))]}, sm)
    a.key(90, {"root": [("Z", 360)]})
    a.done()

    bpy.context.scene.frame_start, bpy.context.scene.frame_end = 0, 120
    apply_pose(rig, {})


def assign(kyle, name):
    rig = kyle["rig"]
    act = bpy.data.actions[name]
    rig.animation_data.action = act
    try:
        rig.animation_data.action_slot = act.slots[0]
    except Exception:
        pass
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = int(act.frame_range[0]), int(act.frame_range[1])


SHEET = [("Idle", 0, "idle"), ("Wave", 22, "wave"), ("Happy", 11, "happy"), ("Thinking", 30, "thinking"),
         ("Goodbye", 20, "goodbye"), ("Turn", 41, "turn")]


def render_sheet(kyle, stage, out_dir):
    from . import stage as S
    os.makedirs(out_dir, exist_ok=True)
    S.setup_render("EEVEE", res=(720, 900), samples=32)
    for act, frame, label in SHEET:
        assign(kyle, act)
        S.render_view(stage, 0, os.path.join(out_dir, f"{label}.png"), frame)
