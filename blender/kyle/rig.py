"""Rig: skin weights, final GEO_* meshes, the armature (deform bones + controls),
facial-expression drivers, and glTF export.

Weights are computed analytically per part (distance along each limb chain with
smooth blends at the joints) instead of bone-heat, which is unreliable on the
intersecting, non-manifold parts a stylised character is made of."""
import math

import bpy
from mathutils import Matrix, Vector

from . import face as F
from . import util as U
from .model import FINGERS, J, arm_dir, hand_frame, seg_dist, side_tag

SCALE = 0.5                     # design units -> metres
SIDES = (("L", 1), ("R", -1))


# --------------------------------------------------------------------------- #
# Weight functions (design units)
# --------------------------------------------------------------------------- #
def chain(c, pts, names, blends):
    """Weights along a polyline of joints; blends[i] = half-width of the blend at joint i+1."""
    L = [0.0]
    for a, b in zip(pts, pts[1:]):
        L.append(L[-1] + (b - a).length)
    best = None
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        dd, t = seg_dist(c, a, b)
        if best is None or dd < best[0]:
            best = (dd, L[i] + t * (b - a).length)
    x = best[1]
    w = {}
    for i, n in enumerate(names):
        up = 1.0 if i == 0 else U.smooth((x - (L[i] - blends[i - 1])) / (2 * blends[i - 1]))
        down = 1.0 if i == len(names) - 1 else 1 - U.smooth((x - (L[i + 1] - blends[i])) / (2 * blends[i]))
        w[n] = w.get(n, 0.0) + up * down
    return w


def mix(a, b, f):
    out = {}
    for k in set(a) | set(b):
        out[k] = a.get(k, 0.0) * (1 - f) + b.get(k, 0.0) * f
    return out


def torso_w(c):
    pts = [Vector((0, 0.01, 0.3)), J["spine"], J["chest"], J["neck"], J["head"], J["head_top"]]
    return chain(c, pts, ["hips", "spine", "chest", "neck", "head"], [0.07, 0.08, 0.04, 0.05])


def shirt_w(c):
    w = torso_w(c)
    for t, s in SIDES:
        if c.x * s < 0.05:
            continue
        S, d = J[f"shoulder{t}"], arm_dir(s)
        tt = (c - S).dot(d)
        r = (c - S - d * tt).length
        # only the sleeve itself (outside the torso silhouette) follows the arm
        sf = (U.smooth((tt + 0.06) / 0.16) * (1 - U.smooth((r - 0.08) / 0.08))
              * U.smooth((abs(c.x) - 0.16) / 0.1))
        cf = U.smooth((abs(c.x) - 0.06) / 0.12) * U.smooth((c.z - 0.88) / 0.1) * (1 - sf)
        w = mix(w, {f"upper_arm.{t}": 0.8, f"clavicle.{t}": 0.2}, sf)
        w = mix(w, {f"clavicle.{t}": 1.0}, cf * 0.6)
    return w


def arm_w(c, t):
    return chain(c, [J[f"shoulder{t}"], J[f"elbow{t}"], J[f"wrist{t}"], J[f"palm{t}"]],
                 [f"upper_arm.{t}", f"forearm.{t}", f"hand.{t}"], [0.05, 0.022])


def finger_chains(t):
    W = J[f"wrist{t}"]
    out = []
    for name, *_ in FINGERS:
        out.append(([W] + J[f"{name}{t}"], [f"hand.{t}"] + [f"{name}.0{k}.{t}" for k in (1, 2, 3)]))
    out.append(([W] + J[f"thumb{t}"], [f"hand.{t}"] + [f"thumb.0{k}.{t}" for k in (1, 2, 3)]))
    return out


def hand_w(c, t):
    best = None
    for pts, names in finger_chains(t):
        fpts = pts[1:]
        dd = min(seg_dist(c, a, b)[0] for a, b in zip(fpts, fpts[1:]))
        along = (c - fpts[0]).dot((fpts[1] - fpts[0]).normalized())
        if dd < 0.018 and along > -0.006 and (best is None or dd < best[0]):
            best = (dd, pts, names)
    if best is None:
        return {f"hand.{t}": 1.0}
    _dd, pts, names = best
    return chain(c, pts, names, [0.007, 0.006, 0.005])


def leg_w(c, t):
    h = J[f"hip{t}"]
    return chain(c, [Vector((h.x, 0, 0.8)), h, J[f"knee{t}"], J[f"ankle{t}"], J[f"ball{t}"]],
                 ["hips", f"thigh.{t}", f"shin.{t}", f"foot.{t}"], [0.06, 0.05, 0.03])


def pants_w(c):
    w = mix(leg_w(c, "R"), leg_w(c, "L"), U.smooth((c.x + 0.03) / 0.06))
    return mix(w, torso_w(c), U.smooth((c.z - 0.64) / 0.1))


def shoe_w(c):
    t = "L" if c.x > 0 else "R"
    return chain(c, [J[f"ankle{t}"], J[f"ball{t}"], J[f"toe{t}"]], [f"foot.{t}", f"toe.{t}"], [0.03])


def cable_w(c):
    return mix(torso_w(c), {"head": 1.0}, U.smooth((c.z - 1.1) / 0.12))


WEIGHTS = {
    "part_Head": lambda c: {"head": 1.0}, "part_EarL": lambda c: {"head": 1.0},
    "part_EarR": lambda c: {"head": 1.0}, "part_Hair": lambda c: {"head": 1.0},
    "part_Glasses": lambda c: {"head": 1.0}, "part_Neck": torso_w,
    "part_Shirt": shirt_w, "part_Collar": torso_w, "part_Print": shirt_w,
    "part_Pants": pants_w, "part_ShoeL": shoe_w, "part_ShoeR": shoe_w, "part_SoleL": shoe_w,
    "part_SoleR": shoe_w, "part_Earphones": cable_w,
    "part_ArmL": lambda c: arm_w(c, "L"), "part_ArmR": lambda c: arm_w(c, "R"),
    "part_HandL": lambda c: hand_w(c, "L"), "part_HandR": lambda c: hand_w(c, "R"),
}

GROUPS = {
    "GEO_Body": ["part_Head", "part_EarL", "part_EarR", "part_Neck", "part_ArmL", "part_ArmR", "part_HandL",
                 "part_HandR"],
    "GEO_Shirt": ["part_Shirt", "part_Collar", "part_Print"],
    "GEO_Pants": ["part_Pants"],
    "GEO_Shoes": ["part_ShoeL", "part_ShoeR", "part_SoleL", "part_SoleR"],
    "GEO_Hair": ["part_Hair"],
    "GEO_Glasses": ["part_Glasses"],
    "GEO_Earphones": ["part_Earphones"],
    "GEO_Face": ["part_Face"],
}


def assign_weights(obj, fn):
    groups = {}
    for v in obj.data.vertices:
        w = fn(v.co)
        tot = sum(x for x in w.values() if x > 0.01) or 1.0
        for name, x in w.items():
            if x > 0.01:
                groups.setdefault(name, []).append((v.index, x / tot))
    for name, items in groups.items():
        vg = obj.vertex_groups.get(name) or obj.vertex_groups.new(name=name)
        for i, x in items:
            vg.add([i], x, "REPLACE")


def ensure_uvs(obj):
    if obj.data.uv_layers:
        obj.data.uv_layers[0].name = "UVMap"
        return
    obj.data.uv_layers.new(name="UVMap")
    U.activate(obj)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.01)
    bpy.ops.object.mode_set(mode="OBJECT")


# --------------------------------------------------------------------------- #
# Armature
# --------------------------------------------------------------------------- #
def build_armature(coll):
    arm = bpy.data.armatures.new("ARM_Kyle")
    rig = bpy.data.objects.new("RIG_Kyle", arm)
    coll.objects.link(rig)
    arm.display_type = "OCTAHEDRAL"
    rig.show_in_front = True
    U.activate(rig)
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm.edit_bones
    S = SCALE

    def bone(name, head, tail, parent=None, roll=(0, -1, 0), deform=True, connect=False):
        b = eb.new(name)
        b.head, b.tail = Vector(head) * S, Vector(tail) * S
        b.align_roll(Vector(roll))
        b.use_deform = deform
        if parent:
            b.parent = eb[parent]
            b.use_connect = connect
        return b

    bone("root", (0, 0, 0), (0, 0.35, 0), roll=(0, 0, 1))
    bone("hips", J["hips"], J["spine"], "root")
    bone("spine", J["spine"], J["chest"], "hips", connect=True)
    bone("chest", J["chest"], J["neck"], "spine", connect=True)
    bone("neck", J["neck"], J["head"], "chest", connect=True)
    bone("head", J["head"], J["head_top"], "neck", connect=True)
    for t, s in SIDES:
        bone(f"clavicle.{t}", J[f"clavicle{t}"], J[f"shoulder{t}"], "chest")
        bone(f"upper_arm.{t}", J[f"shoulder{t}"], J[f"elbow{t}"], f"clavicle.{t}", connect=True)
        bone(f"forearm.{t}", J[f"elbow{t}"], J[f"wrist{t}"], f"upper_arm.{t}", connect=True)
        _f, _w, p = hand_frame(s)
        bone(f"hand.{t}", J[f"wrist{t}"], J[f"palm{t}"], f"forearm.{t}", roll=p, connect=True)
        for pts, names in finger_chains(t):
            for k in (1, 2, 3):
                bone(names[k], pts[k], pts[k + 1], names[k - 1], roll=p, connect=k > 1)
        bone(f"thigh.{t}", J[f"hip{t}"], J[f"knee{t}"], "hips")
        bone(f"shin.{t}", J[f"knee{t}"], J[f"ankle{t}"], f"thigh.{t}", connect=True)
        bone(f"foot.{t}", J[f"ankle{t}"], J[f"ball{t}"], f"shin.{t}", roll=(0, 0, 1), connect=True)
        bone(f"toe.{t}", J[f"ball{t}"], J[f"toe{t}"], f"foot.{t}", roll=(0, 0, 1), connect=True)
        bone(f"eye.{t}", J[f"eye{t}"], J[f"eye{t}"] + Vector((0, -0.08, 0)), "head", roll=(0, 0, 1))
        # controls
        bone(f"CTRL_foot_ik.{t}", J[f"ankle{t}"], J[f"ball{t}"], "root", roll=(0, 0, 1), deform=False)
        k = J[f"knee{t}"]
        bone(f"CTRL_knee_pole.{t}", (k.x, -0.7, k.z), (k.x, -0.78, k.z), "root", deform=False)
    bone("CTRL_face", (0, -0.62, 1.98), (0, -0.62, 2.08), "head", roll=(0, -1, 0), deform=False)
    bpy.ops.object.mode_set(mode="OBJECT")

    # Bone collections for the animator.
    cols = {n: arm.collections.new(n) for n in ("Body", "Fingers", "Face", "Controls")}
    for b in arm.bones:
        n = b.name
        if n.startswith("CTRL_face") or n.startswith("eye."):
            cols["Face"].assign(b)
        elif n.startswith("CTRL_"):
            cols["Controls"].assign(b)
        elif any(n.startswith(f) for f in ("thumb", "index", "middle", "ring", "pinky")):
            cols["Fingers"].assign(b)
        else:
            cols["Body"].assign(b)

    for pb in rig.pose.bones:
        pb.rotation_mode = "QUATERNION"
    rig.pose.bones["root"].rotation_mode = "XYZ"
    widgets(rig)
    leg_ik(rig)
    return rig


def widgets(rig):
    wc = U.collection("WGT_shapes")
    wc.hide_render = True
    wc.hide_viewport = True

    def circle(name, r=1.0, axis="Y"):
        pts = []
        for k in range(32):
            a = 2 * math.pi * k / 32
            pts.append((math.cos(a) * r, 0, math.sin(a) * r) if axis == "Y" else (math.cos(a) * r, math.sin(a) * r, 0))
        me = bpy.data.meshes.new(name)
        me.from_pydata(pts, [(k, (k + 1) % 32) for k in range(32)], [])
        o = bpy.data.objects.new(name, me)
        wc.objects.link(o)
        return o
    ring = circle("WGT_Ring", 1.0, "Y")
    foot = circle("WGT_Foot", 0.6, "Y")
    for pb in rig.pose.bones:
        if pb.name == "root":
            pb.custom_shape = ring
            pb.custom_shape_scale_xyz = (1.2, 1.2, 1.2)
        elif pb.name.startswith("CTRL_foot_ik"):
            pb.custom_shape = foot
        elif pb.name in ("CTRL_face",):
            pb.custom_shape = ring
            pb.custom_shape_scale_xyz = (0.5, 0.5, 0.5)


def leg_ik(rig):
    bpy.context.view_layer.update()
    for t, _s in SIDES:
        shin = rig.pose.bones[f"shin.{t}"]
        ik = shin.constraints.new("IK")
        ik.name = "IK_leg"
        ik.target, ik.subtarget = rig, f"CTRL_foot_ik.{t}"
        ik.pole_target, ik.pole_subtarget = rig, f"CTRL_knee_pole.{t}"
        ik.chain_count = 2
        best = None
        for ang in range(-180, 181, 15):           # pick the pole angle that keeps the rest pose
            ik.pole_angle = math.radians(ang)
            bpy.context.view_layer.update()
            err = 0.0
            for n in (f"thigh.{t}", f"shin.{t}"):
                posed, rest = rig.pose.bones[n].matrix, rig.data.bones[n].matrix_local
                err += sum((posed.col[i].to_3d() - rest.col[i].to_3d()).length for i in (0, 1))
            if best is None or err < best[0]:
                best = (err, ang)
        ik.pole_angle = math.radians(best[1])
        print(f"[rig] leg {t}: pole angle {best[1]} (rest error {best[0]:.4f})")
        cr = rig.pose.bones[f"foot.{t}"].constraints.new("COPY_ROTATION")
        cr.name = "Foot_follow_IK"
        cr.target, cr.subtarget = rig, f"CTRL_foot_ik.{t}"


def face_drivers(rig, face_obj):
    pb = rig.pose.bones["CTRL_face"]
    for key in F.KEYS:
        pb[key] = 0.0
        try:
            pb.id_properties_ui(key).update(min=0.0, max=1.0, soft_min=0.0, soft_max=1.0,
                                            description=f"Shape key {key}")
        except Exception:
            pass
        kb = face_obj.data.shape_keys.key_blocks[key]
        drv = kb.driver_add("value").driver
        drv.type = "AVERAGE"
        var = drv.variables.new()
        var.name = "v"
        var.type = "SINGLE_PROP"
        var.targets[0].id = rig
        var.targets[0].data_path = f'pose.bones["CTRL_face"]["{key}"]'


# --------------------------------------------------------------------------- #
def build(root_coll, parts_coll):
    for name, fn in WEIGHTS.items():
        assign_weights(bpy.data.objects[name], fn)
    for o in list(parts_coll.objects):
        ensure_uvs(o)

    geo_coll = U.collection("KYLE_Geometry", root_coll)
    meshes = {}
    for gname, members in GROUPS.items():
        objs = [bpy.data.objects[m] for m in members]
        o = U.join(objs, gname) if len(objs) > 1 else objs[0]
        o.name = o.data.name = gname
        for c in list(o.users_collection):
            c.objects.unlink(o)
        geo_coll.objects.link(o)
        o.data.transform(Matrix.Scale(SCALE, 4))
        if o.data.shape_keys:
            for kb in o.data.shape_keys.key_blocks:
                for d in kb.data:
                    d.co *= SCALE
        o.data.update()
        meshes[gname] = o
    bpy.data.collections.remove(parts_coll)

    rig_coll = U.collection("KYLE_Rig", root_coll)
    rig = build_armature(rig_coll)
    for o in meshes.values():
        o.parent = rig
        mod = o.modifiers.new("Armature", "ARMATURE")
        mod.object = rig
    face_drivers(rig, meshes["GEO_Face"])
    bpy.context.view_layer.update()
    height = max((meshes["GEO_Hair"].matrix_world @ v.co).z for v in meshes["GEO_Hair"].data.vertices)
    stats = {n: (len(o.data.vertices), sum(len(p.vertices) - 2 for p in o.data.polygons)) for n, o in meshes.items()}
    print("[rig] meshes (verts, tris):", stats, "total tris", sum(t for _v, t in stats.values()))
    print(f"[rig] height {height:.3f} m, bones {len(rig.data.bones)}")
    return {"rig": rig, "meshes": meshes, "height": height}


def export_glb(kyle, path):
    bpy.ops.object.select_all(action="DESELECT")
    kyle["rig"].select_set(True)
    for o in kyle["meshes"].values():
        o.select_set(True)
    bpy.context.view_layer.objects.active = kyle["rig"]
    kyle["rig"].animation_data.action = None
    bpy.context.scene.frame_set(0)
    bpy.ops.export_scene.gltf(
        filepath=path, export_format="GLB", use_selection=True, export_apply=False,
        export_yup=True, export_texcoords=True, export_normals=True, export_materials="EXPORT",
        export_image_format="AUTO", export_skins=True, export_def_bones=True, export_morph=True,
        export_morph_normal=False, export_animations=True, export_animation_mode="ACTIONS",
        export_force_sampling=True, export_frame_range=False, export_optimize_animation_size=True,
        export_anim_single_armature=True, export_rest_position_armature=True, export_cameras=False,
        export_lights=False, export_extras=False,
        export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=7,
        export_draco_position_quantization=14, export_draco_normal_quantization=10,
        export_draco_texcoord_quantization=12, export_draco_generic_quantization=12)
    import os
    print("[export]", path, os.path.getsize(path), "bytes")
