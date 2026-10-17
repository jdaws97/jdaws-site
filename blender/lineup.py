import sys, os, math, bpy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import reset
from mathutils import Vector
GLB, OUT = sys.argv[1], sys.argv[2]
reset(); sc = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=GLB)
order = ['observatory','house_a','house_b','house_gpu','station','gondola','obelisk','tree_pine_a','tree_pine_b','tree_broad_a','tree_broad_b']
widths = {'observatory':3.0,'station':0.9,'house_gpu':0.8}
x = 0
for n in order:
    o = bpy.data.objects[n]; w = widths.get(n, 0.65); x += w/2
    o.location = (x, 0, 0.3 if n=='gondola' else 0); x += w/2
    if n.startswith('house') or n=='station': o.rotation_euler=(0,0,math.radians(-30))
bpy.ops.mesh.primitive_plane_add(size=40, location=(x/2, 0, 0))
pl = bpy.context.active_object; m = bpy.data.materials.new('g'); m.use_nodes=True
m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.45,0.6,0.3,1); pl.data.materials.append(m)
for o in sc.objects:
    if o.type=='MESH':
        for s in o.material_slots:
            if s.material and s.material.use_nodes:
                nt=s.material.node_tree; bs=nt.nodes.get('Principled BSDF')
                # multiply baked AO into base color for the preview
                if bs and o.data.color_attributes:
                    ca=nt.nodes.new('ShaderNodeVertexColor'); ca.layer_name=o.data.color_attributes[0].name
                    mul=nt.nodes.new('ShaderNodeMix'); mul.data_type='RGBA'; mul.blend_type='MULTIPLY'; mul.inputs[0].default_value=1
                    col=bs.inputs['Base Color'].default_value[:]
                    mul.inputs[6].default_value=col; nt.links.new(ca.outputs[0], mul.inputs[7]); nt.links.new(mul.outputs[2], bs.inputs['Base Color'])
sun = bpy.data.lights.new('sun','SUN'); sun.energy=4; so=bpy.data.objects.new('sun',sun); sc.collection.objects.link(so); so.rotation_euler=(math.radians(50),0,math.radians(-40))
sc.world = bpy.data.worlds.new('w'); sc.world.use_nodes=True; sc.world.node_tree.nodes['Background'].inputs[0].default_value=(0.75,0.85,0.95,1); sc.world.node_tree.nodes['Background'].inputs[1].default_value=0.8
cam = bpy.data.cameras.new('c'); cam.lens=50; co=bpy.data.objects.new('c',cam); sc.collection.objects.link(co); sc.camera=co
co.location=(x/2, -9.5, 4.2); d=Vector((x/2,0,0.45))-co.location; co.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
sc.render.engine='CYCLES'; sc.cycles.samples=48; sc.cycles.use_denoising=False
sc.render.resolution_x=1600; sc.render.resolution_y=560; sc.render.filepath=OUT; sc.view_settings.view_transform='AgX'
bpy.ops.render.render(write_still=True)
