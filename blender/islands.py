"""Assets for Penn State, Raytheon, the lab, and the shared road/sea props.
Front faces Blender -Y (three.js +Z). Units match the three.js scene.
"""
import math
import bpy
from mathutils import Vector
from common import *

TAU = math.tau


def strut(p1, p2, r, material, verts=5):
    a, b = Vector(p1), Vector(p2); d = b - a
    rot = d.to_track_quat('Z', 'Y').to_euler()
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=d.length, location=tuple((a + b) / 2), rotation=rot)
    o = bpy.context.active_object; o.data.materials.append(material); return o


def lattice(P, base_w, top_w, h, levels, r, material, z0=0.0):
    """Tapered square lattice tower: corner posts, rings and zig-zag braces."""
    def corner(i, z):
        w = base_w + (top_w - base_w) * (z - z0) / h
        sx, sy = ((1, 1), (-1, 1), (-1, -1), (1, -1))[i]
        return (sx * w / 2, sy * w / 2, z)
    zs = [z0 + h * k / levels for k in range(levels + 1)]
    for i in range(4):
        P.append(strut(corner(i, z0), corner(i, z0 + h), r * 1.4, material))
    for k in range(1, levels + 1):
        for i in range(4):
            j = (i + 1) % 4
            P.append(strut(corner(i, zs[k]), corner(j, zs[k]), r, material))
            if k % 2: P.append(strut(corner(i, zs[k - 1]), corner(j, zs[k]), r * 0.8, material))
            else: P.append(strut(corner(j, zs[k - 1]), corner(i, zs[k]), r * 0.8, material))


def build(M):
    M.update(
        brick=mat('brick', '#b5654a', 0.9),
        trim=mat('trim', '#f6f2ea', 0.8),
        concrete=mat('concrete', '#c9c4ba', 0.95),
        scorch=mat('scorch', '#6d6a66', 1.0),
        steel=mat('steel', '#c8553d', 0.6, 0.3),
        rocket=mat('rocket', '#f4f2ee', 0.5),
        band=mat('band', '#2b2f36', 0.6),
        fin=mat('fin', '#c8553d', 0.6),
        lamp=mat('lamp', '#2a2216', 0.5, emit='#ffc35a', emit_strength=3.0),
        glass=mat('glass', '#dff3ff', 0.05),
        frame=mat('frame', '#f2f0ea', 0.7),
        sail=mat('sail', '#f7f3ea', 0.9),
        hull=mat('hull', '#3d5a73', 0.7),
        deck=mat('deck', '#b58a5c', 0.9),
        map_land=mat('map_land', '#9cc77a', 0.9),
        map_water=mat('map_water', '#7fbfdc', 0.6),
        parcel_a=mat('parcel_a', '#f3d38a', 0.9), parcel_b=mat('parcel_b', '#f2a58a', 0.9), parcel_c=mat('parcel_c', '#b9d8f0', 0.9),
        pin=mat('pin', '#e04f3a', 0.5),
        fort=mat('fort', '#d9cdb4', 0.9), banner=mat('banner', '#d9a03a', 0.6),
        rack=mat('rack', '#2b313a', 0.5, 0.3),
        led_g=mat('led_g', '#7dffb0', 0.4, emit='#3dff8a', emit_strength=3.0),
        led_b=mat('led_b', '#8fd0ff', 0.4, emit='#4ab0ff', emit_strength=3.0),
        stripe=mat('stripe', '#c8553d', 0.7),
        lh_white=mat('lh_white', '#f6f3ec', 0.8),
    )
    out = []

    # ------------------------------------------------ Penn State: a brick hall with a clock tower
    P = []
    P.append(box((1.32, 0.74, 0.06), (0, 0, 0.03), M['stone_dark']))
    P.append(box((1.2, 0.6, 0.42), (0, 0, 0.27), M['brick'], bevel=0.008))
    P.append(box((1.25, 0.65, 0.045), (0, 0, 0.5), M['trim'], bevel=0.006))
    P.append(prism(0.66, 0.2, 1.26, (0, 0, 0.52), M['slate']))
    for x in (-0.5, -0.36, -0.22, 0.22, 0.36, 0.5):
        for z in (0.2, 0.37):
            for s in (-1, 1):
                P.append(box((0.07, 0.012, 0.1), (x, s * 0.301, z), M['window']))
                P.append(box((0.085, 0.014, 0.015), (x, s * 0.302, z - 0.058), M['trim']))
    for x in (-0.6, 0.6):
        for z in (0.2, 0.37):
            P.append(box((0.012, 0.07, 0.1), (x * 1.0017, 0, z), M['window']))
    for x in (-0.17, -0.057, 0.057, 0.17):
        P.append(cyl(0.028, 0.36, (x, -0.37, 0.24), M['trim'], 8))
    P.append(box((0.46, 0.15, 0.05), (0, -0.36, 0.445), M['trim'], bevel=0.005))
    pd = prism(0.46, 0.12, 0.15, (0, -0.36, 0.47), M['trim']); pd.rotation_euler = (0, 0, math.pi / 2); P.append(pd)
    P.append(box((0.12, 0.02, 0.2), (0, -0.305, 0.16), M['door']))
    P.append(box((0.5, 0.1, 0.03), (0, -0.48, 0.045), M['stone_dark']))
    P.append(box((0.56, 0.1, 0.03), (0, -0.55, 0.015), M['stone_dark']))
    P.append(box((0.22, 0.22, 0.52), (0, 0.05, 0.76), M['trim'], bevel=0.006))
    for a in range(4):
        ang = a * math.pi / 2
        d = Vector((math.sin(ang), -math.cos(ang), 0))
        P.append(cyl(0.065, 0.012, tuple(Vector((0, 0.05, 0.9)) + d * 0.111), M['stone_light'], 16, rot=(math.pi / 2, 0, ang)))
        P.append(box((0.008, 0.008, 0.05), tuple(Vector((0, 0.05, 0.915)) + d * 0.118), M['band'], rot=(0, 0, ang)))
        P.append(box((0.04, 0.008, 0.008), tuple(Vector((0.012, 0.05, 0.9)) + d * 0.118), M['band'], rot=(0, 0, ang)))
    for sx in (-1, 1):
        for sy in (-1, 1):
            P.append(box((0.035, 0.035, 0.14), (sx * 0.09, 0.05 + sy * 0.09, 1.09), M['trim']))
    P.append(box((0.25, 0.25, 0.03), (0, 0.05, 1.175), M['trim']))
    P.append(cone(0.17, 0.32, (0, 0.05, 1.35), M['slate'], 4, rot=(0, 0, math.pi / 4)))
    P.append(cone(0.012, 0.12, (0, 0.05, 1.56), M['brass'], 6))
    out.append(join(P, 'hall'))

    P = []  # an electrical pylon: the EE degree
    lattice(P, 0.26, 0.06, 1.1, 6, 0.008, M['metal'])
    for z, w in ((0.92, 0.44), (1.08, 0.3)):
        P.append(box((w, 0.03, 0.025), (0, 0, z), M['metal']))
        for sx in (-1, 1):
            P.append(cyl(0.012, 0.06, (sx * w / 2 * 0.9, 0, z - 0.04), M['band'], 6))
    P.append(cone(0.03, 0.1, (0, 0, 1.15), M['metal'], 4))
    out.append(join(P, 'pylon'))

    # ------------------------------------------------ Raytheon: mission control, radar, launch pads, rockets
    P = []
    P.append(box((1.0, 0.7, 0.05), (0, 0, 0.025), M['concrete']))
    P.append(box((0.8, 0.5, 0.26), (0, 0, 0.18), M['stone'], bevel=0.01))
    P.append(box((0.82, 0.52, 0.03), (0, 0, 0.325), M['slate']))
    P.append(box((0.7, 0.012, 0.07), (0, -0.251, 0.22), M['glow']))
    P.append(box((0.4, 0.34, 0.2), (-0.12, 0.02, 0.44), M['stone'], bevel=0.008))
    P.append(box((0.42, 0.36, 0.025), (-0.12, 0.02, 0.55), M['slate']))
    P.append(box((0.32, 0.012, 0.06), (-0.12, -0.151, 0.46), M['window']))
    P.append(cyl(0.05, 0.2, (0.22, 0.05, 0.43), M['metal'], 8))
    P.append(cyl(0.012, 0.42, (-0.24, 0.12, 0.76), M['metal'], 5))
    P.append(cyl(0.025, 0.02, (-0.24, 0.12, 0.98), M['pin'], 8))
    out.append(join(P, 'control'))

    P = []  # radar dish, rotates in three.js around its vertical axis
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=0.22, location=(0, 0, 0))
    d = bpy.context.active_object; d.data.materials.append(M['stone_light'])
    delete_verts(d, lambda w: w.z > -0.11)
    d.scale = (1, 1, 0.7); d.location = (0, 0, 0.21); d.rotation_euler = (math.radians(-60), 0, 0)
    P.append(d)
    P.append(cyl(0.025, 0.14, (0, 0, 0.07), M['metal'], 8))
    P.append(strut((0, -0.04, 0.15), (0, -0.14, 0.2), 0.008, M['metal']))
    P.append(ico(0.025, (0, -0.15, 0.205), M['metal'], 1))
    out.append(join(P, 'radar_dish'))

    P = []  # launch pad: concrete, flame trench, a red service gantry
    P.append(cyl(0.34, 0.06, (0, 0, 0.03), M['concrete'], 8, bevel=0.01))
    P.append(cyl(0.16, 0.012, (0, 0, 0.066), M['scorch'], 10))
    P.append(box((0.08, 0.36, 0.04), (0, 0.18, 0.04), M['scorch']))
    lattice(P, 0.1, 0.07, 0.62, 6, 0.006, M['steel'], z0=0.06)
    for o in P[3:]:
        o.location.x += 0.22
    for z in (0.36, 0.56):
        P.append(box((0.16, 0.025, 0.02), (0.14, 0, z), M['steel']))
    P.append(cone(0.02, 0.06, (0.22, 0, 0.71), M['steel'], 4))
    out.append(join(P, 'pad'))

    P = []  # rocket, nose along +Z, origin at its middle
    P.append(cyl(0.065, 0.36, (0, 0, 0), M['rocket'], 10))
    P.append(cyl(0.066, 0.04, (0, 0, 0.1), M['band'], 10))
    P.append(cyl(0.066, 0.025, (0, 0, -0.12), M['fin'], 10))
    P.append(cyl(0.065, 0.14, (0, 0, 0.25), M['rocket'], 10, r2=0.0))
    P.append(cone(0.04, 0.05, (0, 0, 0.3), M['fin'], 10))
    P.append(cyl(0.04, 0.06, (0, 0, -0.21), M['band'], 8, r2=0.055))
    for i in range(4):
        a = i * math.pi / 2
        f = box((0.012, 0.09, 0.1), (math.cos(a) * 0.09, math.sin(a) * 0.09, -0.14), M['fin'], rot=(0, 0, a + math.pi / 2))
        P.append(f)
    out.append(join(P, 'rocket'))

    # ------------------------------------------------ The lab: greenhouses, project emblems, lighthouse
    P = []
    P.append(box((0.72, 0.48, 0.06), (0, 0, 0.03), M['stone_dark'], bevel=0.006))
    for sx in (-1, 0, 1):
        for sy in (-1, 1):
            P.append(box((0.022, 0.022, 0.26), (sx * 0.34, sy * 0.22, 0.19), M['frame']))
    for sy in (-1, 1):
        P.append(box((0.7, 0.022, 0.022), (0, sy * 0.22, 0.32), M['frame']))
    th = math.atan2(0.14, 0.23)
    for sx in (-1, 0, 1):
        for sy in (-1, 1):
            P.append(strut((sx * 0.34, sy * 0.225, 0.32), (sx * 0.34, 0, 0.46), 0.011, M['frame'], 4))
    P.append(box((0.72, 0.026, 0.026), (0, 0, 0.465), M['frame']))
    P.append(box((0.08, 0.012, 0.2), (0.0, -0.226, 0.16), M['door']))
    out.append(join(P, 'greenhouse'))

    P = []  # the glass, kept separate so it never shades the terrain bake
    for sy in (-1, 1):
        P.append(box((0.68, 0.006, 0.26), (0, sy * 0.22, 0.19), M['glass']))
    for sx in (-1, 1):
        P.append(box((0.006, 0.44, 0.26), (sx * 0.34, 0, 0.19), M['glass']))
        P.append(prism(0.44, 0.14, 0.006, (sx * 0.34, 0, 0.32), M['glass']))
    L = math.hypot(0.23, 0.14)
    for sy in (-1, 1):
        P.append(box((0.68, L, 0.006), (0, sy * 0.113, 0.39), M['glass'], rot=(-sy * th, 0, 0)))
    out.append(join(P, 'greenhouse_glass'))

    P = []  # civic data: a map table with parcels and pins
    P.append(box((0.36, 0.26, 0.02), (0, 0, 0.13), M['timber']))
    for sx in (-1, 1):
        for sy in (-1, 1):
            P.append(box((0.02, 0.02, 0.12), (sx * 0.16, sy * 0.11, 0.06), M['timber']))
    P.append(box((0.32, 0.22, 0.012), (0, 0, 0.146), M['map_land']))
    P.append(box((0.1, 0.22, 0.013), (0.11, 0, 0.147), M['map_water']))
    import random
    rng = random.Random(5)
    for i in range(4):
        for j in range(3):
            m = M[('parcel_a', 'parcel_b', 'parcel_c')[rng.randrange(3)]]
            P.append(box((0.038, 0.04, 0.01 + rng.random() * 0.03), (-0.13 + i * 0.05, -0.065 + j * 0.065, 0.16), m))
    for x, y in ((-0.08, 0.0), (-0.03, 0.06), (0.02, -0.05)):
        P.append(cyl(0.004, 0.08, (x, y, 0.19), M['band'], 4))
        P.append(ico(0.016, (x, y, 0.235), M['pin'], 1))
    out.append(join(P, 'emblem_map'))

    P = []  # game simulator: a little walled fort with towers and a banner
    for sx, sy in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
        P.append(cyl(0.045, 0.2, (sx * 0.12, sy * 0.12, 0.1), M['fort'], 8))
        P.append(cone(0.055, 0.08, (sx * 0.12, sy * 0.12, 0.24), M['roof'], 8))
    for (x, y, w, d) in ((0, 0.12, 0.24, 0.03), (0, -0.12, 0.24, 0.03), (0.12, 0, 0.03, 0.24), (-0.12, 0, 0.03, 0.24)):
        P.append(box((w, d, 0.12), (x, y, 0.06), M['fort']))
        n = 4
        for k in range(n):
            t = (k + 0.5) / n - 0.5
            P.append(box((0.025 if d > w else 0.03, 0.03 if d > w else 0.025, 0.03), (x + (t * w if w > d else 0), y + (t * d if d > w else 0), 0.135), M['fort']))
    P.append(box((0.1, 0.1, 0.16), (0, 0, 0.08), M['fort']))
    P.append(cyl(0.005, 0.14, (0, 0, 0.23), M['band'], 4))
    P.append(box((0.06, 0.004, 0.035), (0.03, 0, 0.28), M['banner']))
    out.append(join(P, 'emblem_fort'))

    P = []  # homelab: a server rack with blinking lights and a router
    P.append(box((0.14, 0.12, 0.3), (-0.04, 0, 0.15), M['rack'], bevel=0.006))
    for k in range(6):
        z = 0.05 + k * 0.042
        P.append(box((0.11, 0.005, 0.02), (-0.04, -0.061, z), M['band']))
        P.append(box((0.012, 0.006, 0.008), (-0.08, -0.064, z), M['led_g'] if k % 2 else M['led_b']))
        P.append(box((0.012, 0.006, 0.008), (-0.06, -0.064, z), M['led_b'] if k % 3 else M['led_g']))
    P.append(box((0.1, 0.07, 0.03), (0.1, 0, 0.015), M['rack'], bevel=0.004))
    for sx in (-1, 1):
        P.append(cyl(0.005, 0.1, (0.1 + sx * 0.035, 0.025, 0.08), M['band'], 4))
    P.append(box((0.06, 0.005, 0.008), (0.1, -0.036, 0.02), M['led_b']))
    out.append(join(P, 'emblem_rack'))

    P = []  # lighthouse: banded tower, gallery, lantern, keeper's stair
    P.append(cyl(0.26, 0.08, (0, 0, 0.04), M['stone_dark'], 10, bevel=0.01))
    bands = 6; h = 1.0
    for k in range(bands):
        z0 = 0.08 + h * k / bands; z1 = 0.08 + h * (k + 1) / bands
        r0 = 0.19 - 0.06 * k / bands; r1 = 0.19 - 0.06 * (k + 1) / bands
        P.append(cyl(r0, z1 - z0, (0, 0, (z0 + z1) / 2), M['stripe'] if k % 2 else M['lh_white'], 12, r2=r1))
    P.append(box((0.07, 0.012, 0.13), (0, -0.186, 0.15), M['door']))
    for z in (0.45, 0.75):
        P.append(box((0.04, 0.012, 0.06), (0, -(0.19 - 0.06 * (z - 0.08)) - 0.002, z), M['window']))
    P.append(cyl(0.2, 0.03, (0, 0, 1.095), M['slate'], 12))
    for k in range(12):
        a = k / 12 * TAU
        P.append(cyl(0.005, 0.07, (math.cos(a) * 0.19, math.sin(a) * 0.19, 1.145), M['slate'], 4))
    P.append(cyl(0.2, 0.01, (0, 0, 1.18), M['slate'], 12))
    P.append(cyl(0.11, 0.03, (0, 0, 1.125), M['lh_white'], 12))
    P.append(ico(0.07, (0, 0, 1.2), M['lamp'], 1))
    for k in range(6):
        a = k / 6 * TAU
        P.append(cyl(0.006, 0.15, (math.cos(a) * 0.105, math.sin(a) * 0.105, 1.215), M['band'], 4))
    P.append(cone(0.14, 0.12, (0, 0, 1.35), M['stripe'], 12))
    P.append(cyl(0.012, 0.08, (0, 0, 1.44), M['band'], 6))
    P.append(ico(0.018, (0, 0, 1.49), M['brass'], 1))
    out.append(join(P, 'lighthouse'))

    P = []
    for k in range(6):
        a = k / 6 * TAU
        P.append(box((0.006, 0.02, 0.15), (math.cos(a) * 0.105, math.sin(a) * 0.105, 1.215), M['glass'], rot=(0, 0, a)))
    P.append(cyl(0.104, 0.15, (0, 0, 1.215), M['glass'], 6))
    out.append(join(P, 'lighthouse_glass'))

    # ------------------------------------------------ shared: road lantern and sailboat
    P = []
    P.append(cyl(0.035, 0.04, (0, 0, 0.02), M['slate'], 6))
    P.append(cyl(0.016, 0.5, (0, 0, 0.27), M['slate'], 6, r2=0.012))
    P.append(cyl(0.045, 0.02, (0, 0, 0.53), M['slate'], 6))
    P.append(ico(0.055, (0, 0, 0.6), M['lamp'], 1))
    P.append(cone(0.06, 0.05, (0, 0, 0.67), M['slate'], 6))
    out.append(join(P, 'lantern'))

    me = bpy.data.meshes.new('hull')
    v = [(-0.33, -0.1, 0.12), (0.02, -0.125, 0.12), (0.37, 0, 0.13), (0.02, 0.125, 0.12), (-0.33, 0.1, 0.12),
         (-0.29, -0.05, 0.0), (0.02, -0.06, -0.02), (0.31, 0, 0.03), (0.02, 0.06, -0.02), (-0.29, 0.05, 0.0)]
    f = [(0, 1, 2, 3, 4)[::-1], (5, 6, 1, 0), (6, 7, 2, 1), (7, 8, 3, 2), (8, 9, 4, 3), (9, 5, 0, 4), (5, 9, 8, 7, 6)]
    me.from_pydata(v, [], f); me.update()
    hull = bpy.data.objects.new('hull', me); bpy.context.collection.objects.link(hull)
    import bmesh as _bm
    bm = _bm.new(); bm.from_mesh(me); _bm.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    hull.data.materials.append(M['hull'])
    P = [hull]
    P.append(box((0.5, 0.18, 0.012), (-0.02, 0, 0.12), M['deck']))
    P.append(cyl(0.01, 0.8, (0.02, 0, 0.52), M['timber'], 5))
    P.append(cyl(0.008, 0.36, (-0.15, 0, 0.2), M['timber'], 5, rot=(0, math.pi / 2, 0)))
    for pts in (((0.03, 0, 0.2), (0.03, 0, 0.9), (-0.32, 0, 0.21)), ((0.06, 0, 0.18), (0.06, 0, 0.78), (0.35, 0, 0.16))):
        sm = bpy.data.meshes.new('sail'); sm.from_pydata(list(pts), [], [(0, 1, 2)]); sm.update()
        so = bpy.data.objects.new('sail', sm); bpy.context.collection.objects.link(so); so.data.materials.append(M['sail'])
        mod = so.modifiers.new('s', 'SOLIDIFY'); mod.thickness = 0.008
        with bpy.context.temp_override(object=so, active_object=so, selected_objects=[so]):
            bpy.ops.object.modifier_apply(modifier='s')
        P.append(so)
    out.append(join(P, 'sailboat'))
    out.append(stadium(M))
    return out


def stadium(M):
    """A big oval college football stadium in navy and white: field, lower bowl, concourse,
    tall upper deck, press box and light towers. Long axis along X."""
    import bmesh as _bm
    M.update(navy=mat('navy', '#1f3c6e', 0.8), navy2=mat('navy2', '#34599a', 0.8), seat_w=mat('seat_w', '#eef1f5', 0.8),
             turf=mat('turf', '#5f9a43', 0.95), turf2=mat('turf2', '#6aa64b', 0.95), lines=mat('lines', '#f7f7f2', 0.8))
    N = 40
    def ring(a, b, z, sq=3.2):  # superellipse: a rounded rectangle, like a real stadium
        out = []
        for i in range(N):
            t = i / N * math.tau; c, s = math.cos(t), math.sin(t)
            out.append((a * math.copysign(abs(c) ** (2 / sq), c), b * math.copysign(abs(s) ** (2 / sq), s), z))
        return out
    bands = [((0.40, 0.25, 0.035), (0.70, 0.52, 0.26), 'navy'), ((0.70, 0.52, 0.26), (0.74, 0.56, 0.27), 'seat_w'),
             ((0.74, 0.56, 0.27), (0.96, 0.76, 0.55), 'navy2'), ((0.96, 0.76, 0.55), (1.0, 0.8, 0.58), 'seat_w'),
             ((1.0, 0.8, 0.58), (1.0, 0.8, 0.0), 'stone')]
    P = []
    for (a0, b0, z0), (a1, b1, z1), m in bands:
        me = bpy.data.meshes.new('band'); r0, r1 = ring(a0, b0, z0), ring(a1, b1, z1)
        me.from_pydata(r0 + r1, [], [(i, (i + 1) % N, N + (i + 1) % N, N + i) for i in range(N)]); me.update()
        o = bpy.data.objects.new('band', me); bpy.context.collection.objects.link(o)
        bm = _bm.new(); bm.from_mesh(me); _bm.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
        o.data.materials.append(M[m]); P.append(o)
    # seating rows: thin white rings across both decks so the bowl reads as stands
    for k in range(1, 4):
        t = k / 4
        a, b, z = 0.40 + 0.30 * t, 0.25 + 0.27 * t, 0.035 + 0.225 * t
        bpy.ops.mesh.primitive_torus_add(major_radius=1, minor_radius=0.004, major_segments=N, minor_segments=3, location=(0, 0, z + 0.004))
        o = bpy.context.active_object; o.scale = (a + 0.004, b + 0.004, 1); o.data.materials.append(M['seat_w']); P.append(o)
    for k in range(1, 5):
        t = k / 5
        a, b, z = 0.74 + 0.22 * t, 0.56 + 0.20 * t, 0.27 + 0.28 * t
        bpy.ops.mesh.primitive_torus_add(major_radius=1, minor_radius=0.004, major_segments=N, minor_segments=3, location=(0, 0, z + 0.004))
        o = bpy.context.active_object; o.scale = (a + 0.004, b + 0.004, 1); o.data.materials.append(M['seat_w']); P.append(o)
    # field with stripes, end zones and yard lines
    P.append(box((0.8, 0.5, 0.03), (0, 0, 0.015), M['turf']))
    for i in range(10):
        P.append(box((0.05, 0.36, 0.002), (-0.25 + i * 0.0556 + 0.0278, 0, 0.031), M['turf2'] if i % 2 else M['turf']))
    for sx in (-1, 1):
        P.append(box((0.06, 0.36, 0.003), (sx * 0.31, 0, 0.031), M['navy']))
    for i in range(11):
        P.append(box((0.004, 0.36, 0.004), (-0.28 + i * 0.056, 0, 0.033), M['lines']))
    P.append(box((0.62, 0.004, 0.004), (0, 0.18, 0.033), M['lines'])); P.append(box((0.62, 0.004, 0.004), (0, -0.18, 0.033), M['lines']))
    # exterior: steel columns all the way round and a navy fascia under the rim
    ext = ring(1.0, 0.8, 0)
    for i in range(N):
        x, y, _ = ext[i]; x2, y2, _ = ext[(i + 1) % N]
        P.append(box((0.018, 0.022, 0.5), (x * 1.008, y * 1.01, 0.25), M['metal'], rot=(0, 0, math.atan2(y2 - y, x2 - x))))
    me = bpy.data.meshes.new('fascia'); r0, r1 = ring(1.012, 0.812, 0.47), ring(1.012, 0.812, 0.575)
    me.from_pydata(r0 + r1, [], [(i, (i + 1) % N, N + (i + 1) % N, N + i) for i in range(N)]); me.update()
    o = bpy.data.objects.new('fascia', me); bpy.context.collection.objects.link(o)
    bm = _bm.new(); bm.from_mesh(me); _bm.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    o.data.materials.append(M['navy']); P.append(o)
    # press box on the far side, above the upper deck
    P.append(box((0.62, 0.12, 0.12), (0, 0.84, 0.64), M['stone'], bevel=0.008))
    P.append(box((0.6, 0.012, 0.05), (0, 0.779, 0.66), M['window']))
    P.append(box((0.66, 0.15, 0.02), (0, 0.84, 0.71), M['slate']))
    # four light towers
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * 0.98, sy * 0.66
            P.append(cyl(0.012, 0.85, (x, y, 0.425), M['metal'], 6))
            P.append(box((0.12, 0.025, 0.07), (x, y, 0.87), M['metal']))
            P.append(box((0.11, 0.008, 0.055), (x - sx * 0.0, y - sy * 0.017, 0.87), M['glow']))
    return join(P, 'stadium')
