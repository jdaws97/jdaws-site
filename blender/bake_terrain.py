"""Bake soft shadows (ambient occlusion) onto the three.js terrain.

Inputs come from natural.html?export=1: the terrain's non-indexed vertex positions,
the other static models as a GLB, and the placements of trees and Booz Allen assets.
Output: one byte per terrain vertex, in three.js vertex order.

Run: python3 -I blender/bake_terrain.py <in dir> <assets.glb> <out .bin>
"""
import sys, os, math, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, numpy as np
from mathutils import Matrix, Vector
from common import reset

IN, ASSETS, OUT = sys.argv[1:4]
reset(); sc = bpy.context.scene

# three.js (x, y, z) Y-up  ->  Blender (x, -z, y) Z-up; rotation about three Y = rotation about Blender Z
pos = np.fromfile(os.path.join(IN, 'terrain_pos.bin'), dtype=np.float32).reshape(-1, 3)
verts = np.stack([pos[:, 0], -pos[:, 2], pos[:, 1]], axis=1)
n = len(verts)
me = bpy.data.meshes.new('terrain')
me.vertices.add(n); me.vertices.foreach_set('co', verts.ravel())
nf = n // 3
me.loops.add(n); me.loops.foreach_set('vertex_index', np.arange(n, dtype=np.int32))
me.polygons.add(nf); me.polygons.foreach_set('loop_start', np.arange(0, n, 3, dtype=np.int32))
me.update(); me.validate(verbose=False)
assert len(me.loops) == n, ('loop count changed', len(me.loops), n)
terrain = bpy.data.objects.new('terrain', me); sc.collection.objects.link(terrain)
terrain.data.materials.append(bpy.data.materials.new('t'))

bpy.ops.import_scene.gltf(filepath=os.path.join(IN, 'occluders.glb'))
before = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=ASSETS)
lib = {o.name: o for o in set(bpy.data.objects) - before if o.parent is None}
for o in lib.values():
    o.hide_render = True  # the library originals sit at the origin; only placed copies count

P = json.load(open(os.path.join(IN, 'placements.json')))
def put(name, x, y, z, rot, s):
    src = lib[name]; o = src.copy(); sc.collection.objects.link(o); o.hide_render = False
    o.matrix_world = Matrix.Translation((x, -z, y)) @ Matrix.Rotation(rot, 4, 'Z') @ Matrix.Diagonal((s, s, s, 1))
for t in P['trees']:
    put(t['variant'], t['x'], t['y'], t['z'], t['rot'], t['s'])
for b in P['booz']:
    put(b['name'], b['x'], b['y'], b['z'], b['rot'], b['s'])
print('scene ready:', n, 'terrain verts,', len(P['trees']), 'trees,', len(P['booz']), 'buildings', flush=True)

sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 96
sc.render.bake.target = 'VERTEX_COLORS'
sc.world = sc.world or bpy.data.worlds.new('World')
sc.world.light_settings.distance = float(os.environ.get('AO_DIST', 1.4))
ca = me.color_attributes.new('AO', 'BYTE_COLOR', 'CORNER'); me.color_attributes.active_color = ca
for o in bpy.context.view_layer.objects: o.select_set(False)
terrain.select_set(True); bpy.context.view_layer.objects.active = terrain
t0 = time.time(); bpy.ops.object.bake(type='AO'); print('bake took', round(time.time() - t0, 1), 's', flush=True)

col = np.empty(n * 4, dtype=np.float32); ca.data.foreach_get('color', col)
ao = np.clip(col.reshape(-1, 4)[:, 0] * 255 + 0.5, 0, 255).astype(np.uint8)
ao.tofile(OUT)
print('wrote', OUT, ao.size, 'bytes; mean', round(float(ao.mean()), 1), 'min', int(ao.min()))
