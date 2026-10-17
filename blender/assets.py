"""Build the Booz Allen island's hero assets and the tree set, bake soft shadows
(ambient occlusion) into each one's vertex colors, and export a single GLB.

Run: python3 -I blender/assets.py <out.glb>
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from common import *
import islands

OUT = sys.argv[1] if len(sys.argv) > 1 else 'assets.glb'
reset()
scene = bpy.context.scene

M = dict(
    stone=mat('stone', '#efebe3', 0.85),
    stone_dark=mat('stone_dark', '#d3cbbb', 0.9),
    stone_light=mat('stone_light', '#f8f5ef', 0.8),
    roof=mat('roof', '#b65a3c', 0.8),
    roof_b=mat('roof_b', '#c7774c', 0.8),
    slate=mat('slate', '#56616f', 0.7),
    timber=mat('timber', '#8a6643', 0.9),
    door=mat('door', '#5b4330', 0.9),
    window=mat('window', '#34404f', 0.4),
    glow=mat('glow', '#ffcf8a', 0.5, emit='#ffb347', emit_strength=2.0),
    dome=mat('dome', '#86bfa8', 0.55, 0.15),
    interior=mat('interior', '#20262e', 1.0),
    brass=mat('brass', '#c9a25a', 0.35, 0.6),
    gold=mat('gold', '#e0bd6e', 0.3, 0.7),
    metal=mat('metal', '#9aa3ad', 0.45, 0.5),
    red=mat('gondola', '#c4553a', 0.7),
    pine=mat('pine', '#3d6b38', 0.9),
    pine2=mat('pine2', '#33603a', 0.9),
    leaf=mat('leaf', '#5f8f45', 0.9),
    leaf2=mat('leaf2', '#7aa24e', 0.9),
    bark=mat('bark', '#6d5035', 0.95),
)
TAU = math.tau


# ---------------------------------------------------------------- observatory
def observatory():
    P = []
    P.append(cyl(1.34, 0.1, (0, 0, 0.05), M['stone_dark'], 16, bevel=0.02))
    P.append(cyl(1.2, 0.08, (0, 0, 0.14), M['stone_dark'], 16, bevel=0.015))
    P.append(cyl(1.0, 0.62, (0, 0, 0.49), M['stone'], 16, r2=0.96))
    P.append(cyl(1.08, 0.07, (0, 0, 0.835), M['stone_dark'], 16, bevel=0.015))
    door_az = -math.pi / 2  # faces -Y, toward the camera
    for i in range(16):
        a = i / 16 * TAU + TAU / 32
        if abs(math.atan2(math.sin(a - door_az), math.cos(a - door_az))) < 0.35:
            continue
        P.append(box((0.07, 0.05, 0.62), (math.cos(a) * 1.0, math.sin(a) * 1.0, 0.49), M['stone_light'], rot=(0, 0, a)))
        if i % 2 == 0:
            P.append(box((0.03, 0.07, 0.17), (math.cos(a + TAU / 32) * 0.985, math.sin(a + TAU / 32) * 0.985, 0.6), M['window'], rot=(0, 0, a + TAU / 32)))
    # portico with columns, architrave and pediment
    P.append(box((0.26, 0.12, 0.36), (0, -0.98, 0.36), M['door']))
    for x in (-0.2, 0.2):
        P.append(cyl(0.035, 0.42, (x, -1.2, 0.39), M['stone_light'], 8))
    P.append(box((0.56, 0.3, 0.05), (0, -1.1, 0.625), M['stone'], bevel=0.008))
    P.append(prism(0.56, 0.14, 0.3, (0, -1.1, 0.65), M['stone'], bevel=0.0))
    P[-1].rotation_euler = (0, 0, math.pi / 2)
    P.append(box((0.6, 0.16, 0.05), (0, -1.33, 0.155), M['stone_dark']))
    P.append(box((0.68, 0.16, 0.05), (0, -1.45, 0.105), M['stone_dark']))
    # dome with a viewing slit, ribs and a telescope
    slit_az = math.radians(-123.75)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=0.9, location=(0, 0, 0.87))
    d = bpy.context.active_object; d.data.materials.append(M['dome'])
    delete_verts(d, lambda w: w.z < 0.87 - 1e-4)
    def in_slit(c):
        az = math.atan2(c.y, c.x)
        return abs(math.atan2(math.sin(az - slit_az), math.cos(az - slit_az))) < math.radians(9) and c.z > 0.87 + 0.18
    delete_faces(d, in_slit)
    P.append(d)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=0.84, location=(0, 0, 0.87))
    di = bpy.context.active_object; di.data.materials.append(M['interior'])
    delete_verts(di, lambda w: w.z < 0.87 - 1e-4)
    P.append(di)
    for deg in (-135, -112.5, -67.5, -22.5, 22.5, 67.5, 112.5, 157.5):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.905, minor_radius=0.02, major_segments=40, minor_segments=4,
                                         location=(0, 0, 0), rotation=(math.pi / 2, 0, 0))
        r = bpy.context.active_object
        with bpy.context.temp_override(object=r, active_object=r, selected_objects=[r], selected_editable_objects=[r]):
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        delete_verts(r, lambda w: w.z < -0.03 or w.x < -0.03)
        r.rotation_euler = (0, 0, math.radians(deg)); r.location = (0, 0, 0.87)
        r.data.materials.append(M['stone_light'])
        P.append(r)
    P.append(cyl(0.06, 0.06, (0, 0, 1.79), M['brass'], 8))
    P.append(cone(0.035, 0.2, (0, 0, 1.92), M['brass'], 6))
    el = math.radians(38)
    dvec = Vector((math.cos(slit_az) * math.cos(el), math.sin(slit_az) * math.cos(el), math.sin(el)))
    rot = dvec.to_track_quat('Z', 'Y').to_euler()
    c = Vector((0, 0, 1.0)) + dvec * 0.6
    P.append(cyl(0.085, 0.95, tuple(c), M['slate'], 10, r2=0.07, rot=rot))
    P.append(cyl(0.095, 0.06, tuple(Vector((0, 0, 1.0)) + dvec * 1.02), M['brass'], 10, rot=rot))
    return join(P, 'observatory')


# ---------------------------------------------------------------- houses
def house(name, roofm, chimney_x=0.11, gpu=False):
    P = []
    P.append(box((0.46, 0.38, 0.04), (0, 0, 0.02), M['stone_dark']))
    P.append(box((0.42, 0.34, 0.3), (0, 0, 0.19), M['stone'], bevel=0.01))
    P.append(prism(0.34, 0.16, 0.42, (0, 0, 0.34), M['stone']))
    th = math.atan2(0.16, 0.17); L = math.hypot(0.17, 0.16) + 0.05
    for s in (1, -1):
        P.append(box((0.5, L, 0.035), (0, s * 0.093, 0.432), roofm, rot=(-s * th, 0, 0), bevel=0.006))
    P.append(box((0.52, 0.035, 0.035), (0, 0, 0.51), roofm, bevel=0.006))
    P.append(box((0.06, 0.06, 0.18), (chimney_x, 0.075, 0.49), M['stone_dark'], bevel=0.006))
    P.append(box((0.08, 0.08, 0.02), (chimney_x, 0.075, 0.585), M['slate']))
    # door and window on the +X gable end (faces the observatory), windows on the long sides
    P.append(box((0.012, 0.09, 0.15), (0.211, 0, 0.115), M['door']))
    P.append(box((0.012, 0.06, 0.06), (0.211, 0, 0.4), M['window']))
    for x in (-0.1, 0.1):
        for s in (1, -1):
            P.append(box((0.07, 0.012, 0.075), (x, s * 0.171, 0.22), M['glow'] if gpu else M['window']))
    P.append(box((0.012, 0.07, 0.075), (-0.211, 0.06, 0.22), M['window']))
    if gpu:
        # compute annex: a flat-roofed wing with glowing windows and fans on the roof
        P.append(box((0.2, 0.26, 0.2), (-0.31, 0, 0.12), M['stone'], bevel=0.008))
        P.append(box((0.23, 0.29, 0.03), (-0.31, 0, 0.235), M['slate']))
        for y in (-0.07, 0.07):
            P.append(cyl(0.045, 0.03, (-0.31, y, 0.265), M['metal'], 10))
            P.append(box((0.012, 0.07, 0.05), (-0.416, y, 0.13), M['glow']))
        for x in (-0.1, 0.06):
            P.append(cyl(0.022, 0.06, (x, 0, 0.55), M['metal'], 8))
    return join(P, name)


# ---------------------------------------------------------------- obelisk (Security+)
def obelisk():
    P = []
    for i, w in enumerate((0.44, 0.34, 0.26)):
        P.append(box((w, w, 0.06), (0, 0, 0.03 + i * 0.06), M['stone_dark'], bevel=0.008))
    P.append(cyl(0.125, 1.1, (0, 0, 0.73), M['stone'], 4, r2=0.08, rot=(0, 0, math.pi / 4)))
    P.append(cone(0.08, 0.13, (0, 0, 1.345), M['gold'], 4, rot=(0, 0, math.pi / 4)))
    P.append(box((0.1, 0.012, 0.08), (0, -0.09, 0.42), M['gold']))
    return join(P, 'obelisk')


# ---------------------------------------------------------------- cable car
def station():
    P = []
    P.append(box((0.62, 0.52, 0.3), (0, 0, 0.15), M['stone'], bevel=0.012))
    P.append(box((0.5, 0.42, 0.22), (0, 0, 0.41), M['timber'], bevel=0.008))
    P.append(box((0.012, 0.16, 0.1), (0.251, 0, 0.42), M['window']))
    P.append(prism(0.5, 0.16, 0.6, (0, 0, 0.52), M['slate']))
    for s in (1, -1):  # A-frame tower carrying the cable wheel
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=1.15, location=(0.18, s * 0.12, 1.07), rotation=(s * 0.18, 0, 0))
        o = bpy.context.active_object; o.data.materials.append(M['timber']); P.append(o)
    P.append(box((0.06, 0.32, 0.04), (0.18, 0, 1.25), M['timber']))
    bpy.ops.mesh.primitive_torus_add(major_radius=0.13, minor_radius=0.018, major_segments=16, minor_segments=4, location=(0.18, 0, 1.55), rotation=(math.pi / 2, 0, 0))
    o = bpy.context.active_object; o.data.materials.append(M['metal']); P.append(o)
    P.append(cyl(0.03, 0.1, (0.18, 0, 1.55), M['slate'], 8, rot=(math.pi / 2, 0, 0)))
    return join(P, 'station')


def gondola():
    P = []
    P.append(cyl(0.012, 0.09, (0, 0, -0.045), M['slate'], 6))
    P.append(box((0.08, 0.03, 0.02), (0, 0, 0.0), M['metal']))
    P.append(box((0.2, 0.14, 0.13), (0, 0, -0.155), M['red'], bevel=0.012))
    P.append(box((0.22, 0.16, 0.02), (0, 0, -0.085), M['slate']))
    P.append(box((0.205, 0.145, 0.04), (0, 0, -0.145), M['window']))
    return join(P, 'gondola')


# ---------------------------------------------------------------- trees
def pine(name, tiers, seed, h=1.0):
    P = [cyl(0.04, 0.22 * h, (0, 0, 0.11 * h), M['bark'], 6, r2=0.03)]
    rs = [0.27, 0.22, 0.16, 0.11][:tiers]
    for i, r in enumerate(rs):
        z = (0.24 + i * 0.17) * h
        o = cone(r, 0.32 * h, (0, 0, z + 0.16 * h), M['pine'] if i % 2 == 0 else M['pine2'], 7, rot=(0, 0, seed * 1.3 + i))
        jitter(o, 0.018, seed * 10 + i)
        P.append(o)
    return join(P, name)


def broad(name, lumps, seed):
    P = [cyl(0.045, 0.32, (0, 0, 0.16), M['bark'], 6, r2=0.035)]
    for i, (x, y, z, r) in enumerate(lumps):
        o = ico(r, (x, y, z), M['leaf'] if i % 2 == 0 else M['leaf2'], 1, rot=(seed + i, seed * 2 + i, 0))
        o.scale = (1, 1, 0.85)
        jitter(o, r * 0.12, seed * 7 + i)
        P.append(o)
    return join(P, name)


ASSETS = [
    observatory(),
    house('house_a', M['roof']), house('house_b', M['roof_b'], chimney_x=-0.11), house('house_gpu', M['slate'], gpu=True),
    obelisk(), station(), gondola(),
    pine('tree_pine_a', 3, 1), pine('tree_pine_b', 4, 2, h=1.12),
    broad('tree_broad_a', [(0, 0, 0.5, 0.27)], 3),
    broad('tree_broad_b', [(0.06, 0.02, 0.46, 0.21), (-0.09, -0.04, 0.42, 0.17), (0.0, 0.0, 0.62, 0.17)], 4),
] + islands.build(M)

# ---------------------------------------------------------------- bake soft shadows
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 128
scene.render.bake.target = 'VERTEX_COLORS'
if scene.world is None:
    scene.world = bpy.data.worlds.new('World')
bpy.ops.mesh.primitive_plane_add(size=12, location=(0, 0, 0))
ground = bpy.context.active_object; ground.name = 'ground'
DIST = {'observatory': 0.5, 'station': 0.35, 'hall': 0.4, 'lighthouse': 0.35, 'control': 0.35, 'pylon': 0.3, 'stadium': 0.45}
NO_GROUND = {'gondola', 'rocket', 'sailboat'}
for a in ASSETS:
    if a.name.endswith('_glass'):
        continue
    for o in ASSETS:
        o.hide_render = o is not a
    ground.hide_render = a.name in NO_GROUND
    scene.world.light_settings.distance = DIST.get(a.name, 0.25)
    ca = a.data.color_attributes.new('AO', 'BYTE_COLOR', 'CORNER')
    a.data.color_attributes.active_color = ca
    try: a.data.attributes.active_color = ca
    except Exception: pass
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    a.select_set(True); bpy.context.view_layer.objects.active = a
    bpy.ops.object.bake(type='AO')
    print('baked', a.name, len(a.data.polygons), 'faces', flush=True)
bpy.data.objects.remove(ground)
for o in ASSETS:
    o.hide_render = False
    o.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True, export_apply=True, export_yup=True,
                          export_vertex_color='ACTIVE', export_materials='EXPORT')
print('wrote', OUT, os.path.getsize(OUT), 'bytes')
