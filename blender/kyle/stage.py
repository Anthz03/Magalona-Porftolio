"""Presentation stage: cyclorama backdrop, soft three-point lighting, cameras for
front / three-quarter / side / back stills, and a turntable pivot."""
import math

import bpy
from mathutils import Vector

from . import util as U

VIEWS = {"front": 0, "three_quarter": 35, "side": 90, "back": 180}


def build(height):
    """height: character height in scene units (after scaling)."""
    coll = U.collection("STAGE")
    h = height

    # Cyclorama: floor that curves up into a back wall.
    y0, r = h * 0.7, h * 1.3                     # (y, z) profile: floor -> quarter circle -> wall
    prof = [(-6 * h, 0.0)]
    for k in range(25):
        a = math.pi / 2 * k / 24
        prof.append((y0 + math.sin(a) * r, r - math.cos(a) * r))
    prof.append((y0 + r, 5 * h))
    verts, faces = [], []
    W = 6 * h
    for y, z in prof:
        verts += [(-W, y, z), (W, y, z)]
    for i in range(len(prof) - 1):
        a = 2 * i
        faces.append((a, a + 1, a + 3, a + 2))
    bg = U.material("MAT_Backdrop", "#ece8f3", rough=0.95, spec=0.2)
    U.new_object("STG_Cyclorama", verts, faces, coll, bg)

    def area(name, loc, target, power, size, color=(1, 1, 1), shape="DISK"):
        ld = bpy.data.lights.new(name, "AREA")
        ld.energy = power
        ld.shape = shape
        ld.size = size
        ld.color = color
        try:
            ld.use_shadow = True
        except Exception:
            pass
        lo = bpy.data.objects.new(name, ld)
        coll.objects.link(lo)
        lo.location = Vector(loc)
        lo.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        return lo

    c = (0, 0, h * 0.55)
    area("LGT_Key", (-h * 1.6, -h * 2.2, h * 1.9), c, 260 * h * h, h * 1.4, (1.0, 0.96, 0.92))
    area("LGT_Fill", (h * 2.4, -h * 1.8, h * 0.9), c, 90 * h * h, h * 2.4, (0.9, 0.94, 1.0))
    area("LGT_Rim", (h * 0.8, h * 1.6, h * 1.9), (0, 0, h * 0.8), 260 * h * h, h * 0.9, (0.8, 0.87, 1.0))
    area("LGT_Kicker", (-h * 1.4, h * 1.2, h * 1.0), (0, 0, h * 0.6), 120 * h * h, h * 0.8, (1.0, 0.9, 0.85))

    world = bpy.data.worlds.new("WLD_Studio")
    bpy.context.scene.world = world
    try:
        world.use_nodes = True
        bgn = world.node_tree.nodes["Background"]
        bgn.inputs[0].default_value = (*U.srgb("#f2eff7"), 1)
        bgn.inputs[1].default_value = 0.35
    except Exception:
        world.color = U.srgb("#f2eff7")

    cam_d = bpy.data.cameras.new("CAM_Main")
    cam_d.lens = 85
    cam = bpy.data.objects.new("CAM_Main", cam_d)
    coll.objects.link(cam)
    pivot = bpy.data.objects.new("CAM_Pivot", None)
    coll.objects.link(pivot)
    pivot.location = (0, 0, 0)
    cam.parent = pivot
    dist = h * 3.3
    cam.location = (0, -dist, h * 0.56)
    cam.rotation_euler = (math.radians(90), 0, 0)
    bpy.context.scene.camera = cam
    for o in coll.objects:                 # the whole studio orbits with the camera
        if o not in (pivot, cam):
            o.parent = pivot
    return {"camera": cam, "pivot": pivot, "coll": coll}


def setup_render(engine="EEVEE", res=(1080, 1350), samples=64):
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "AgX"
    try:
        sc.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass
    if engine == "CYCLES":
        sc.render.engine = "CYCLES"
        sc.cycles.samples = samples
        sc.cycles.use_denoising = True
        try:
            prefs = bpy.context.preferences.addons["cycles"].preferences
            prefs.compute_device_type = "METAL"
            prefs.get_devices()
            for dv in prefs.devices:
                dv.use = True
            sc.cycles.device = "GPU"
        except Exception:
            pass
    else:
        sc.render.engine = "BLENDER_EEVEE"
        ee = sc.eevee
        for attr, val in (("taa_render_samples", samples), ("use_shadows", True), ("use_raytracing", True),
                          ("shadow_ray_count", 2), ("shadow_step_count", 8), ("use_fast_gi", True),
                          ("fast_gi_distance", 0.3), ("use_gtao", True), ("gtao_distance", 0.25)):
            try:
                setattr(ee, attr, val)
            except Exception:
                pass


def render_view(stage, yaw_deg, path, frame=None):
    sc = bpy.context.scene
    if frame is not None:
        sc.frame_set(frame)
    stage["pivot"].rotation_euler = (0, 0, math.radians(yaw_deg))
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


def render_turntable(stage, path, kyle=None, frames=120):
    """360-degree orbit of the studio around the character (he idles while it turns)."""
    sc = bpy.context.scene
    pivot = stage["pivot"]
    if kyle is not None:
        from . import anim
        anim.assign(kyle, "Idle")
    pivot.rotation_euler = (0, 0, 0)
    pivot.keyframe_insert("rotation_euler", frame=0)
    pivot.rotation_euler = (0, 0, 2 * math.pi)
    pivot.keyframe_insert("rotation_euler", frame=frames)
    for kp in _all_keyframes(pivot):
        kp.interpolation = "LINEAR"
    sc.frame_start, sc.frame_end = 0, frames - 1
    try:
        sc.render.image_settings.media_type = "VIDEO"
    except Exception:
        pass
    sc.render.image_settings.file_format = "FFMPEG"
    sc.render.ffmpeg.format = "MPEG4"
    sc.render.ffmpeg.codec = "H264"
    sc.render.ffmpeg.constant_rate_factor = "HIGH"
    sc.render.filepath = path
    bpy.ops.render.render(animation=True)


def _all_keyframes(obj):
    """Keyframes of obj's action (layered actions in Blender 4.4+, legacy fcurves before)."""
    act = obj.animation_data.action
    if hasattr(act, "layers") and act.layers:
        for layer in act.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        yield from fc.keyframe_points
    else:
        for fc in act.fcurves:
            yield from fc.keyframe_points
