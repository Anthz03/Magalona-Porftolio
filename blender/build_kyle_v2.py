"""
Builds the rigged + animated "Kyle" mascot from scratch (reference: img/profile-dark.png).

Run from the repo root:
    /Applications/Blender.app/Contents/MacOS/Blender -b -P blender/build_kyle_v2.py -- [options]

Options:
    --stop model|face|rig|anim   stop after that phase (for quick previews)
    --views DIR                  render front / three-quarter / side / back stills into DIR
    --engine EEVEE|CYCLES        engine for --views (default EEVEE)
    --action NAME --frame N      pose the rig with an action frame before rendering views
    --turntable FILE.mp4         render a 360-degree turntable movie
    --sheet DIR                  render an expression / pose sheet (one still per action key moment)
    --export                     write model/kyle_rigged.glb
    --save                       write blender/kyle.blend (editable source scene)

Output conventions: metres, Z-up in Blender (glTF: Y-up, character faces +Z),
feet on the ground at the origin.
"""
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

for m in [k for k in sys.modules if k == "kyle" or k.startswith("kyle.")]:
    del sys.modules[m]
from kyle import anim, face, hair, model, rig, stage, util  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def arg(name, default=None):
    return argv[argv.index(name) + 1] if name in argv else default


STOP = arg("--stop")

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.fps = 30
scene.unit_settings.system = "METRIC"

root = util.collection("KYLE")
parts = util.collection("KYLE_parts", root)
mats, head_bvh = model.build(parts)
hair.build(parts, mats)
height = 2.2

if STOP != "model":
    face.build(parts, head_bvh)
    model.lower_head(0.05)
if STOP not in ("model", "face"):
    kyle = rig.build(root, parts)
    height = kyle["height"]
if STOP not in ("model", "face", "rig"):
    anim.build(kyle)

st = stage.build(height)
if "--close" in argv:                      # head close-up for face / hair review
    cam = st["camera"]
    cam.data.lens = 85
    cam.location = (0, -height * 1.45, height * 0.7)
if arg("--shape"):                         # e.g. --shape EyeOpen_L=1,MouthLaugh=1
    fo = bpy.data.objects.get("GEO_Face") or bpy.data.objects.get("part_Face")
    for kv in arg("--shape").split(","):
        k, v = kv.split("=")
        fo.data.shape_keys.key_blocks[k].value = float(v)

views = arg("--views")
if views:
    os.makedirs(views, exist_ok=True)
    stage.setup_render(arg("--engine", "EEVEE"), samples=int(arg("--samples", "48")))
    act, frame = arg("--action"), arg("--frame")
    if act and STOP not in ("model", "face", "rig"):
        anim.assign(kyle, act)
    for name, yaw in stage.VIEWS.items():
        if "--only" in argv and name not in arg("--only").split(","):
            continue
        stage.render_view(st, yaw, os.path.join(views, f"{name}.png"), int(frame) if frame else None)

if arg("--sheet"):
    anim.render_sheet(kyle, st, arg("--sheet"))

if arg("--turntable"):
    stage.setup_render(arg("--engine", "EEVEE"), res=(1080, 1350), samples=int(arg("--samples", "24")))
    stage.render_turntable(st, arg("--turntable"), kyle if STOP is None else None)

if "--save" in argv:
    path = os.path.join(HERE, "kyle.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path, compress=True)
    print("saved", path)

if "--export" in argv:
    rig.export_glb(kyle, os.path.join(ROOT, "model", "kyle_rigged.glb"))
