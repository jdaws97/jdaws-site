"""Shared helpers for building low-poly assets with bpy (Blender as a Python module).

Blender is Z-up; the glTF exporter converts to three.js Y-up. An asset's
"front" faces Blender -Y, which becomes three.js +Z (toward the camera).
"""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)


def srgb_to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hexlin(h):
    h = h.lstrip('#')
    return tuple(srgb_to_lin(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4)) + (1.0,)


_MATS = {}


def mat(name, hexcol, rough=0.85, metal=0.0, emit=None, emit_strength=0.0):
    if name in _MATS:
        return _MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = hexlin(hexcol)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if emit:
        b.inputs['Emission Color'].default_value = hexlin(emit)
        b.inputs['Emission Strength'].default_value = emit_strength
    _MATS[name] = m
    return m


def _finish(obj, material, bevel=0.0, bevel_segments=1):
    obj.data.materials.clear()
    obj.data.materials.append(material)
    if bevel > 0:
        mod = obj.modifiers.new('bevel', 'BEVEL')
        mod.width = bevel
        mod.segments = bevel_segments
        mod.limit_method = 'ANGLE'
        mod.angle_limit = math.radians(35)
        with bpy.context.temp_override(object=obj, active_object=obj, selected_objects=[obj]):
            bpy.ops.object.modifier_apply(modifier=mod.name)
    return obj


def _active(obj):
    bpy.context.view_layer.objects.active = obj
    return obj


def box(size, loc, material, rot=(0, 0, 0), bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = _active(bpy.context.active_object)
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return _finish(o, material, bevel)


def cyl(r, depth, loc, material, verts=12, r2=None, rot=(0, 0, 0), bevel=0.0):
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=r2, depth=depth, location=loc, rotation=rot)
    return _finish(_active(bpy.context.active_object), material, bevel)


def cone(r, depth, loc, material, verts=8, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=0, depth=depth, location=loc, rotation=rot)
    return _finish(_active(bpy.context.active_object), material)


def ico(r, loc, material, subdiv=1, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdiv, radius=r, location=loc, rotation=rot)
    return _finish(_active(bpy.context.active_object), material)


def prism(width_y, height, length_x, loc, material, bevel=0.0):
    """Triangular prism: triangle in the YZ plane (base width_y, apex up), extruded along X."""
    me = bpy.data.meshes.new('prism')
    hy, hx = width_y / 2, length_x / 2
    v = [(-hx, -hy, 0), (-hx, hy, 0), (-hx, 0, height), (hx, -hy, 0), (hx, hy, 0), (hx, 0, height)]
    f = [(0, 2, 1), (3, 4, 5), (0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5)]
    me.from_pydata(v, [], f)
    me.update()
    o = bpy.data.objects.new('prism', me)
    bpy.context.collection.objects.link(o)
    o.location = loc
    bpy.context.view_layer.update()
    with bpy.context.temp_override(object=o, active_object=o, selected_objects=[o], selected_editable_objects=[o]):
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    me.validate()
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    return _finish(o, material, bevel)


def jitter(obj, amount, seed):
    rng = random.Random(seed)
    for v in obj.data.vertices:
        v.co += Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1))) * amount
    obj.data.update()


def delete_verts(obj, pred):
    bm = bmesh.new(); bm.from_mesh(obj.data)
    kill = [v for v in bm.verts if pred(obj.matrix_world @ v.co)]
    bmesh.ops.delete(bm, geom=kill, context='VERTS')
    bm.to_mesh(obj.data); bm.free(); obj.data.update()


def delete_faces(obj, pred):
    bm = bmesh.new(); bm.from_mesh(obj.data)
    kill = [f for f in bm.faces if pred(obj.matrix_world @ f.calc_center_median())]
    bmesh.ops.delete(bm, geom=kill, context='FACES_ONLY')
    bm.to_mesh(obj.data); bm.free(); obj.data.update()


def join(parts, name):
    """Join parts into one object with origin at world (0,0,0), flat shaded."""
    for o in parts:
        o.select_set(False)
    with bpy.context.temp_override(object=parts[0], active_object=parts[0], selected_objects=parts, selected_editable_objects=parts):
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        if len(parts) > 1:
            bpy.ops.object.join()
    o = parts[0]
    o.name = name; o.data.name = name
    for p in o.data.polygons:
        p.use_smooth = False
    return o
