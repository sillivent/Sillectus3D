import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler

def purge_all():
    if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for block in (
        bpy.data.meshes,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
        bpy.data.curves,
        bpy.data.node_groups,
    ):
        for item in list(block):
            item.user_clear()
            block.remove(item, do_unlink=True)

purge_all()

scene = bpy.context.scene
if scene.world is None:
    scene.world = bpy.data.worlds.new("Starbase_World")
scene.world.use_nodes = True
bg_node = scene.world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs[0].default_value = (0.035, 0.045, 0.065, 1.0)
    bg_node.inputs[1].default_value = 1.1

def create_principled_material(name, color, metallic=0.0, roughness=0.5, emission_color=None, emission_strength=0.0, noise_scale=0.0, bump_strength=0.0, brick_grid=False):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.diffuse_color = (color[0], color[1], color[2], 1.0)
    mat.metallic = metallic
    mat.roughness = roughness
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
        if emission_color and emission_strength > 0.0:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = (emission_color[0], emission_color[1], emission_color[2], 1.0)
            elif "Emission" in bsdf.inputs:
                bsdf.inputs["Emission"].default_value = (emission_color[0], emission_color[1], emission_color[2], 1.0)
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emission_strength
        if brick_grid:
            tex_coord = nodes.new("ShaderNodeTexCoord")
            brick = nodes.new("ShaderNodeTexBrick")
            brick.offset = 0.5
            brick.offset_frequency = 2
            brick.squash = 1.0
            brick.inputs["Scale"].default_value = 34.0
            brick.inputs["Mortar Size"].default_value = 0.038
            brick.inputs["Mortar Smooth"].default_value = 0.08
            brick.inputs["Color1"].default_value = (color[0] * 1.25, color[1] * 1.25, color[2] * 1.25, 1.0)
            brick.inputs["Color2"].default_value = (color[0] * 0.78, color[1] * 0.78, color[2] * 0.78, 1.0)
            brick.inputs["Mortar"].default_value = (0.002, 0.002, 0.003, 1.0)
            bump = nodes.new("ShaderNodeBump")
            bump.inputs["Strength"].default_value = 0.52
            bump.inputs["Distance"].default_value = 0.04
            links.new(tex_coord.outputs["Object"], brick.inputs["Vector"])
            links.new(brick.outputs["Color"], bsdf.inputs["Base Color"])
            links.new(brick.outputs["Fac"], bump.inputs["Height"])
            links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
        elif noise_scale > 0.0:
            tex_coord = nodes.new("ShaderNodeTexCoord")
            noise = nodes.new("ShaderNodeTexNoise")
            noise.inputs["Scale"].default_value = noise_scale
            noise.inputs["Detail"].default_value = 12.0
            ramp = nodes.new("ShaderNodeValToRGB")
            r_low = max(0.02, roughness - 0.12)
            r_high = min(0.98, roughness + 0.12)
            ramp.color_ramp.elements[0].position = 0.35
            ramp.color_ramp.elements[0].color = (r_low, r_low, r_low, 1.0)
            ramp.color_ramp.elements[1].position = 0.65
            ramp.color_ramp.elements[1].color = (r_high, r_high, r_high, 1.0)
            links.new(tex_coord.outputs["Object"], noise.inputs["Vector"])
            links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
            links.new(ramp.outputs["Color"], bsdf.inputs["Roughness"])
            if bump_strength > 0.0:
                bump = nodes.new("ShaderNodeBump")
                bump.inputs["Strength"].default_value = bump_strength
                bump.inputs["Distance"].default_value = 0.05
                links.new(noise.outputs["Fac"], bump.inputs["Height"])
                links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat

mat_titanium = create_principled_material("V5_Brushed_Titanium", (0.58, 0.60, 0.64), metallic=0.92, roughness=0.38, noise_scale=18.0, bump_strength=0.04)
mat_titanium_dark = create_principled_material("V5_Dark_Alloy", (0.22, 0.24, 0.27), metallic=0.88, roughness=0.45, noise_scale=25.0, bump_strength=0.05)
mat_heat_tiles = create_principled_material("V5_Ceramic_Heat_Tiles", (0.024, 0.024, 0.028), metallic=0.08, roughness=0.84, brick_grid=True)
mat_heat_grout = create_principled_material("V5_Tile_Grout_Seams", (0.003, 0.003, 0.004), metallic=0.02, roughness=0.98)
mat_tower_steel = create_principled_material("Mechazilla_Steel", (0.09, 0.10, 0.11), metallic=0.85, roughness=0.52, noise_scale=12.0, bump_strength=0.06)
mat_engine_metal = create_principled_material("Raptor_Nozzle_Alloy", (0.04, 0.045, 0.05), metallic=0.92, roughness=0.35)
mat_copper_turbopump = create_principled_material("Raptor_Copper_Lines", (0.45, 0.25, 0.15), metallic=0.90, roughness=0.32)
mat_cockpit_glass = create_principled_material("Shuttle_Cockpit_Glass", (0.08, 0.55, 0.95), metallic=0.1, roughness=0.08, emission_color=(0.12, 0.65, 1.0), emission_strength=8.5)
mat_cabin_glass = create_principled_material("Cabin_Deck_Glass", (0.20, 0.72, 1.0), metallic=0.1, roughness=0.1, emission_color=(0.25, 0.78, 1.0), emission_strength=11.0)
mat_concrete = create_principled_material("Spaceport_Concrete", (0.26, 0.27, 0.28), metallic=0.0, roughness=0.92, noise_scale=6.0, bump_strength=0.18)
mat_trench_char = create_principled_material("Trench_Scorched_Concrete", (0.05, 0.05, 0.055), metallic=0.05, roughness=0.96, noise_scale=10.0, bump_strength=0.25)
mat_cryo_white = create_principled_material("Cryo_Tank_White", (0.86, 0.88, 0.90), metallic=0.15, roughness=0.32, noise_scale=8.0)
mat_semi_white = create_principled_material("Tesla_Semi_Pearl", (0.90, 0.91, 0.93), metallic=0.35, roughness=0.22)
mat_semi_glass = create_principled_material("Tesla_Semi_Windshield", (0.015, 0.02, 0.025), metallic=0.2, roughness=0.05)
mat_tire_rubber = create_principled_material("Semi_Tire_Rubber", (0.015, 0.015, 0.015), metallic=0.0, roughness=0.95)
mat_wheel_rim = create_principled_material("Semi_Alcoa_Rim", (0.75, 0.77, 0.80), metallic=0.95, roughness=0.20)
mat_hivis_orange = create_principled_material("Ground_Crew_HiVis", (1.0, 0.32, 0.02), metallic=0.0, roughness=0.6, emission_color=(1.0, 0.35, 0.0), emission_strength=1.8)
mat_headlight = create_principled_material("LED_Headlight", (0.9, 0.95, 1.0), metallic=0.0, roughness=0.1, emission_color=(0.9, 0.95, 1.0), emission_strength=14.0)
mat_terminal_metal = create_principled_material("Terminal_Architectural_Alloy", (0.72, 0.75, 0.79), metallic=0.65, roughness=0.28)
mat_terminal_glass = create_principled_material("Terminal_Curtain_Glass", (0.10, 0.38, 0.65), metallic=0.2, roughness=0.06, emission_color=(0.18, 0.55, 0.88), emission_strength=3.2)

def finalize_mesh_object(name, bm, mat=None, smooth=False, location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0)):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    if smooth:
        for poly in mesh.polygons:
            poly.use_smooth = True
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    obj.rotation_euler = rotation
    bpy.context.collection.objects.link(obj)
    if mat:
        obj.data.materials.append(mat)
    return obj

def bm_add_box(bm, center, dims, rot_euler=(0.0, 0.0, 0.0), mat_idx=0):
    dx, dy, dz = dims[0] * 0.5, dims[1] * 0.5, dims[2] * 0.5
    local_coords = [
        Vector((-dx, -dy, -dz)), Vector((dx, -dy, -dz)), Vector((dx, dy, -dz)), Vector((-dx, dy, -dz)),
        Vector((-dx, -dy, dz)),  Vector((dx, -dy, dz)),  Vector((dx, dy, dz)),  Vector((-dx, dy, dz)),
    ]
    rot_mat = Euler(rot_euler, 'XYZ').to_matrix()
    c_vec = Vector(center)
    verts = [bm.verts.new(c_vec + (rot_mat @ v)) for v in local_coords]
    face_indices = [
        (0, 3, 2, 1), (4, 5, 6, 7),
        (0, 1, 5, 4), (1, 2, 6, 5),
        (2, 3, 7, 6), (3, 0, 4, 7),
    ]
    for f_idx in face_indices:
        f = bm.faces.new([verts[i] for i in f_idx])
        f.material_index = mat_idx

def bm_add_strut(bm, p1, p2, width, mat_idx=0):
    v1 = Vector(p1)
    v2 = Vector(p2)
    vec = v2 - v1
    length = vec.length
    if length < 1e-4:
        return
    w_dir = vec.normalized()
    up = Vector((0.0, 0.0, 1.0)) if abs(w_dir.z) < 0.95 else Vector((1.0, 0.0, 0.0))
    u_dir = w_dir.cross(up).normalized() * (width * 0.5)
    v_dir = w_dir.cross(u_dir).normalized() * (width * 0.5)
    b0 = bm.verts.new(v1 - u_dir - v_dir)
    b1 = bm.verts.new(v1 + u_dir - v_dir)
    b2 = bm.verts.new(v1 + u_dir + v_dir)
    b3 = bm.verts.new(v1 - u_dir + v_dir)
    t0 = bm.verts.new(v2 - u_dir - v_dir)
    t1 = bm.verts.new(v2 + u_dir - v_dir)
    t2 = bm.verts.new(v2 + u_dir + v_dir)
    t3 = bm.verts.new(v2 - u_dir + v_dir)
    for quad in ((b0, b3, b2, b1), (t0, t1, t2, t3), (b0, b1, t1, t0), (b1, b2, t2, t1), (b2, b3, t3, t2), (b3, b0, t0, t3)):
        f = bm.faces.new(quad)
        f.material_index = mat_idx

def bm_add_cylinder_frustum(bm, center, r_bottom, r_top, height, segments=64, rot_euler=(0.0, 0.0, 0.0), cap_ends=True, mat_idx=0):
    rot_mat = Euler(rot_euler, 'XYZ').to_matrix()
    c_vec = Vector(center)
    hz = height * 0.5
    bot_verts = []
    top_verts = []
    for i in range(segments):
        ang = (2.0 * math.pi * i) / segments
        ca, sa = math.cos(ang), math.sin(ang)
        bot_verts.append(bm.verts.new(c_vec + rot_mat @ Vector((ca * r_bottom, sa * r_bottom, -hz))))
        top_verts.append(bm.verts.new(c_vec + rot_mat @ Vector((ca * r_top, sa * r_top, hz))))
    for i in range(segments):
        ni = (i + 1) % segments
        f = bm.faces.new((bot_verts[i], bot_verts[ni], top_verts[ni], top_verts[i]))
        f.material_index = mat_idx
    if cap_ends:
        if r_bottom > 1e-4:
            fb = bm.faces.new(list(reversed(bot_verts)))
            fb.material_index = mat_idx
        if r_top > 1e-4:
            ft = bm.faces.new(top_verts)
            ft.material_index = mat_idx

bm_pad = bmesh.new()
bm_add_box(bm_pad, (-126.0, 0.0, -12.5), (220.0, 560.0, 25.0), mat_idx=0)
bm_add_box(bm_pad, (126.0, 0.0, -12.5), (220.0, 560.0, 25.0), mat_idx=0)
bm_add_box(bm_pad, (-16.8, 0.0, 0.45), (1.8, 560.0, 0.9), mat_idx=0)
bm_add_box(bm_pad, (16.8, 0.0, 0.45), (1.8, 560.0, 0.9), mat_idx=0)
bm_add_box(bm_pad, (-16.2, 0.0, -12.5), (0.8, 560.0, 25.0), mat_idx=1)
bm_add_box(bm_pad, (16.2, 0.0, -12.5), (0.8, 560.0, 25.0), mat_idx=1)
for step in range(4):
    z_step = -2.2 - step * 5.8
    x_off = 15.8 - step * 0.45
    bm_add_box(bm_pad, (-x_off, 0.0, z_step), (1.2, 560.0, 5.8), mat_idx=1)
    bm_add_box(bm_pad, (x_off, 0.0, z_step), (1.2, 560.0, 5.8), mat_idx=1)
for rib_y in range(-260, 265, 16):
    bm_add_box(bm_pad, (-15.5, float(rib_y), -12.5), (0.9, 1.2, 24.8), mat_idx=1)
    bm_add_box(bm_pad, (15.5, float(rib_y), -12.5), (0.9, 1.2, 24.8), mat_idx=1)
bm_add_box(bm_pad, (0.0, 0.0, -26.5), (34.0, 560.0, 3.0), mat_idx=1)
pad_obj = finalize_mesh_object("Launchpad_And_Flame_Trench", bm_pad, mat=mat_concrete, smooth=False)
pad_obj.data.materials.append(mat_trench_char)

bm_defl = bmesh.new()
defl_w = 14.5
defl_l = 48.0
defl_z_base = -25.0
defl_z_peak = -9.5
v_d0 = bm_defl.verts.new((-defl_w, -defl_l, defl_z_base))
v_d1 = bm_defl.verts.new((defl_w, -defl_l, defl_z_base))
v_d2 = bm_defl.verts.new((defl_w, 0.0, defl_z_peak))
v_d3 = bm_defl.verts.new((-defl_w, 0.0, defl_z_peak))
v_d4 = bm_defl.verts.new((-defl_w, defl_l, defl_z_base))
v_d5 = bm_defl.verts.new((defl_w, defl_l, defl_z_base))
bm_defl.faces.new((v_d0, v_d1, v_d2, v_d3))
bm_defl.faces.new((v_d3, v_d2, v_d5, v_d4))
bm_defl.faces.new((v_d0, v_d4, v_d5, v_d1))
bm_defl.faces.new((v_d0, v_d3, v_d4))
bm_defl.faces.new((v_d1, v_d5, v_d2))
for rx in range(-12, 14, 3):
    bm_add_strut(bm_defl, (rx, -defl_l, defl_z_base + 0.3), (rx, 0.0, defl_z_peak + 0.3), 0.45)
    bm_add_strut(bm_defl, (rx, defl_l, defl_z_base + 0.3), (rx, 0.0, defl_z_peak + 0.3), 0.45)
for ny in range(-120, 125, 10):
    bm_add_cylinder_frustum(bm_defl, (-15.0, ny, -4.5), 0.42, 0.30, 3.2, segments=12, rot_euler=(0.0, math.radians(75), 0.0))
    bm_add_cylinder_frustum(bm_defl, (15.0, ny, -4.5), 0.42, 0.30, 3.2, segments=12, rot_euler=(0.0, math.radians(-75), 0.0))
finalize_mesh_object("Steel_Flame_Deflector", bm_defl, mat=mat_tower_steel, smooth=False)

bm_olm = bmesh.new()
olm_z_bot = 2.0
olm_z_top = 10.0
olm_r_in = 8.4
olm_r_mid = 11.2
olm_r_out = 13.8
olm_segs = 64

ring_verts = []
for r_val in (olm_r_in, olm_r_mid, olm_r_out):
    for z_val in (olm_z_bot, olm_z_top):
        ring = []
        for i in range(olm_segs):
            ang = (2.0 * math.pi * i) / olm_segs
            ring.append(bm_olm.verts.new((math.cos(ang) * r_val, math.sin(ang) * r_val, z_val)))
        ring_verts.append(ring)

for i in range(olm_segs):
    ni = (i + 1) % olm_segs
    bm_olm.faces.new((ring_verts[0][ni], ring_verts[0][i], ring_verts[1][i], ring_verts[1][ni]))
    bm_olm.faces.new((ring_verts[4][i], ring_verts[4][ni], ring_verts[5][ni], ring_verts[5][i]))
    bm_olm.faces.new((ring_verts[1][i], ring_verts[1][ni], ring_verts[5][ni], ring_verts[5][i]))
    bm_olm.faces.new((ring_verts[0][ni], ring_verts[0][i], ring_verts[4][i], ring_verts[4][ni]))

for i in range(6):
    ang = (i * math.pi / 3.0) + (math.pi / 6.0)
    lx = math.cos(ang) * 11.8
    ly = math.sin(ang) * 11.8
    bm_add_cylinder_frustum(bm_olm, (lx, ly, -1.5), 2.1, 1.85, 47.0, segments=28)
    bm_add_cylinder_frustum(bm_olm, (lx * 0.84, ly * 0.84, -1.5), 0.65, 0.65, 47.0, segments=16)
    bm_add_cylinder_frustum(bm_olm, (lx * 1.12, ly * 1.12, -1.5), 0.45, 0.45, 47.0, segments=14)
    bm_add_cylinder_frustum(bm_olm, (lx * 0.96, ly * 0.96, 8.0), 0.32, 0.32, 28.0, segments=12)
    wall_x = -16.0 if lx < 0 else 16.0
    bm_add_strut(bm_olm, (lx, ly, 12.0), (wall_x, ly, -1.5), 1.4)
    bm_add_strut(bm_olm, (lx, ly, 2.0), (wall_x, ly, -12.0), 1.4)

for i in range(40):
    ang = (2.0 * math.pi * i) / 40.0
    ca, sa = math.cos(ang), math.sin(ang)
    bm_add_box(bm_olm, (ca * 9.55, sa * 9.55, 30.85), (1.15, 0.90, 2.3), rot_euler=(0.0, 0.0, ang))
    bm_add_box(bm_olm, (ca * 9.08, sa * 9.08, 30.35), (0.65, 0.60, 1.35), rot_euler=(0.0, 0.0, ang))
    bm_add_cylinder_frustum(bm_olm, (ca * 10.25, sa * 10.25, 30.9), 0.18, 0.18, 1.4, segments=10, rot_euler=(0.0, math.radians(65), ang))
    bm_add_strut(bm_olm, (ca * 14.3, sa * 14.3, 23.2), (ca * 13.5, sa * 13.5, 21.8), 0.28)
    bm_add_strut(bm_olm, (ca * 14.3, sa * 14.3, 23.2), (ca * 9.2, sa * 9.2, 20.6), 0.24)
    bm_add_strut(bm_olm, (ca * 14.3, sa * 14.3, 28.4), (ca * 10.4, sa * 10.4, 29.8), 0.20)
    bm_add_strut(bm_olm, (ca * 14.3, sa * 14.3, 23.2), (ca * 14.3, sa * 14.3, 28.4), 0.16)
    bm_add_box(bm_olm, (ca * 13.9, sa * 13.9, 25.8), (0.55, 0.45, 0.85), rot_euler=(0.0, 0.0, ang))

for i in range(48):
    ang = (2.0 * math.pi * i) / 48.0
    nx = math.cos(ang) * 8.65
    ny = math.sin(ang) * 8.65
    bm_add_cylinder_frustum(bm_olm, (nx, ny, 21.6), 0.22, 0.11, 1.9, segments=10, rot_euler=(0.0, math.radians(-50), ang))

for z_m, r_m, rad_tube in ((23.2, 14.3, 0.72), (28.4, 14.3, 0.45), (20.8, 9.6, 0.55), (25.5, 14.1, 0.35)):
    for i in range(olm_segs):
        a0 = (2.0 * math.pi * i) / olm_segs
        a1 = (2.0 * math.pi * (i + 1)) / olm_segs
        p0 = (math.cos(a0) * r_m, math.sin(a0) * r_m, z_m)
        p1 = (math.cos(a1) * r_m, math.sin(a1) * r_m, z_m)
        bm_add_strut(bm_olm, p0, p1, rad_tube * 1.4)

for i in range(64):
    a0 = (2.0 * math.pi * i) / 64.0
    a1 = (2.0 * math.pi * (i + 1)) / 64.0
    bm_add_strut(bm_olm, (math.cos(a0) * 14.9, math.sin(a0) * 14.9, 25.8), (math.cos(a1) * 14.9, math.sin(a1) * 14.9, 25.8), 0.9)
    if i % 2 == 0:
        bm_add_strut(bm_olm, (math.cos(a0) * 15.3, math.sin(a0) * 15.3, 25.8), (math.cos(a0) * 15.3, math.sin(a0) * 15.3, 27.1), 0.12)
    bm_add_strut(bm_olm, (math.cos(a0) * 15.3, math.sin(a0) * 15.3, 27.1), (math.cos(a1) * 15.3, math.sin(a1) * 15.3, 27.1), 0.10)

bm_add_box(bm_olm, (-11.8, -3.5, 33.5), (3.5, 4.2, 7.0), rot_euler=(0.0, math.radians(10), 0.0))
finalize_mesh_object("Orbital_Launch_Mount", bm_olm, mat=mat_tower_steel, smooth=False)

bm_booster = bmesh.new()
sh_z_base = 10.0
sh_height = 130.0
sh_radius = 9.0
sh_segs = 128
sh_rings = 52

b_grid = []
for r_idx in range(sh_rings + 1):
    z = sh_z_base + (r_idx / sh_rings) * (sh_height - 3.5)
    ring = []
    for s_idx in range(sh_segs):
        ang = (2.0 * math.pi * s_idx) / sh_segs
        ring.append(bm_booster.verts.new((math.cos(ang) * sh_radius, math.sin(ang) * sh_radius, z)))
    b_grid.append(ring)

for r_idx in range(sh_rings):
    for s_idx in range(sh_segs):
        ns = (s_idx + 1) % sh_segs
        f = bm_booster.faces.new((b_grid[r_idx][s_idx], b_grid[r_idx][ns], b_grid[r_idx + 1][ns], b_grid[r_idx + 1][s_idx]))
        f.material_index = 0

for z_ring in range(34, 156, 4):
    bm_add_cylinder_frustum(bm_booster, (0.0, 0.0, float(z_ring)), 9.04, 9.04, 0.22, segments=128, cap_ends=False, mat_idx=0)

for chine_ang in (math.radians(-95), math.radians(95)):
    cx = math.cos(chine_ang) * 8.95
    cy = math.sin(chine_ang) * 8.95
    bm_add_box(bm_booster, (cx, cy, 92.0), (0.95, 1.35, 118.0), rot_euler=(0.0, 0.0, chine_ang), mat_idx=1)

bm_add_cylinder_frustum(bm_booster, (0.0, 0.0, 158.25), 8.5, 8.5, 3.5, segments=96, cap_ends=True, mat_idx=1)
bm_add_cylinder_frustum(bm_booster, (0.0, 0.0, 156.65), 9.06, 9.06, 0.4, segments=128, cap_ends=True, mat_idx=1)
bm_add_cylinder_frustum(bm_booster, (0.0, 0.0, 159.85), 9.06, 9.06, 0.4, segments=128, cap_ends=True, mat_idx=1)
for i in range(48):
    ang = (2.0 * math.pi * i) / 48.0
    sx = math.cos(ang) * 8.92
    sy = math.sin(ang) * 8.92
    bm_add_box(bm_booster, (sx, sy, 158.25), (0.35, 0.22, 3.1), rot_euler=(0.0, 0.0, ang), mat_idx=1)

booster_obj = finalize_mesh_object("Super_Heavy_Booster", bm_booster, mat=mat_titanium, smooth=True)
booster_obj.data.materials.append(mat_titanium_dark)

bm_raptors = bmesh.new()
raptor_rings = [
    (0.0, 3, 1.85),
    (0.0, 10, 4.55),
    (0.0, 20, 7.45),
]
for phase, count, ring_r in raptor_rings:
    for i in range(count):
        ang = phase + (2.0 * math.pi * i) / count
        rx = math.cos(ang) * ring_r
        ry = math.sin(ang) * ring_r
        bm_add_cylinder_frustum(bm_raptors, (rx, ry, 27.3), 1.12, 0.34, 3.2, segments=28, cap_ends=False, mat_idx=0)
        bm_add_cylinder_frustum(bm_raptors, (rx, ry, 25.85), 1.19, 1.13, 0.45, segments=28, cap_ends=True, mat_idx=0)
        bm_add_cylinder_frustum(bm_raptors, (rx, ry, 26.25), 0.94, 0.94, 1.1, segments=24, cap_ends=True, mat_idx=0)
        for h_z, h_r in ((26.4, 1.09), (26.75, 1.02), (27.1, 0.96), (27.5, 0.88), (27.9, 0.80), (28.5, 0.62)):
            bm_add_cylinder_frustum(bm_raptors, (rx, ry, h_z), h_r, h_r, 0.10, segments=24, cap_ends=True, mat_idx=1)
        bm_add_cylinder_frustum(bm_raptors, (rx, ry, 29.55), 0.48, 0.56, 1.4, segments=20, cap_ends=True, mat_idx=1)
        for p_idx in range(4):
            p_ang = ang + p_idx * (math.pi / 2.0)
            px = rx + math.cos(p_ang) * 0.56
            py = ry + math.sin(p_ang) * 0.56
            bm_add_cylinder_frustum(bm_raptors, (px, py, 29.4), 0.22, 0.18, 1.05, segments=12, cap_ends=True, mat_idx=1)
            p_top = (px, py, 29.88)
            p_mid = (rx + math.cos(p_ang) * 0.88, ry + math.sin(p_ang) * 0.88, 28.45)
            p_lip = (rx + math.cos(p_ang) * 1.08, ry + math.sin(p_ang) * 1.08, 26.35)
            bm_add_strut(bm_raptors, p_top, p_mid, 0.11, mat_idx=1)
            bm_add_strut(bm_raptors, p_mid, p_lip, 0.09, mat_idx=1)
            bm_add_box(bm_raptors, p_mid, (0.16, 0.16, 0.16), rot_euler=(0.0, 0.0, p_ang), mat_idx=0)
            next_ang = p_ang + (math.pi / 2.0)
            p_next = (rx + math.cos(next_ang) * 0.88, ry + math.sin(next_ang) * 0.88, 28.45)
            bm_add_strut(bm_raptors, p_mid, p_next, 0.07, mat_idx=1)
        g_ang = ang + math.radians(45.0)
        bm_add_strut(bm_raptors, (rx + math.cos(g_ang) * 0.3, ry + math.sin(g_ang) * 0.3, 30.2), (rx + math.cos(g_ang) * 0.92, ry + math.sin(g_ang) * 0.92, 27.8), 0.10, mat_idx=0)

raptors_obj = finalize_mesh_object("Super_Heavy_33_Raptors", bm_raptors, mat=mat_engine_metal, smooth=True)
raptors_obj.data.materials.append(mat_copper_turbopump)

bm_gf = bmesh.new()
gf_angles = [math.radians(38), math.radians(142), math.radians(218), math.radians(322)]
gf_z = 153.2
gf_span = 7.6
gf_chord = 5.4
gf_depth = 0.72

for ang in gf_angles:
    rot_m = Euler((0.0, 0.0, ang), 'XYZ').to_matrix()
    mount_pos = rot_m @ Vector((9.35, 0.0, gf_z))
    bm_add_box(bm_gf, mount_pos, (1.5, 2.1, 1.8), rot_euler=(0.0, 0.0, ang), mat_idx=0)
    r_start = 9.8
    r_end = r_start + gf_span
    r_mid = 0.5 * (r_start + r_end)
    bm_add_box(bm_gf, rot_m @ Vector((r_mid, -gf_chord * 0.5, gf_z)), (gf_span, 0.24, gf_depth * 1.12), rot_euler=(0.0, 0.0, ang))
    bm_add_box(bm_gf, rot_m @ Vector((r_mid, gf_chord * 0.5, gf_z)), (gf_span, 0.24, gf_depth * 1.12), rot_euler=(0.0, 0.0, ang))
    bm_add_box(bm_gf, rot_m @ Vector((r_start, 0.0, gf_z)), (0.28, gf_chord, gf_depth * 1.12), rot_euler=(0.0, 0.0, ang))
    bm_add_box(bm_gf, rot_m @ Vector((r_end, 0.0, gf_z)), (0.24, gf_chord, gf_depth * 1.12), rot_euler=(0.0, 0.0, ang))
    num_span_slats = 16
    num_chord_slats = 12
    for s_i in range(1, num_span_slats):
        r_curr = r_start + (s_i / num_span_slats) * gf_span
        is_major_s = (s_i % 4 == 0)
        thick_s = 0.11 if is_major_s else (0.065 if s_i % 2 == 0 else 0.042)
        depth_s = gf_depth * (1.06 if is_major_s else (0.94 if s_i % 2 == 0 else 0.80))
        for c_j in range(num_chord_slats):
            y_curr = -gf_chord * 0.5 + (c_j + 0.5) * (gf_chord / num_chord_slats)
            cell_pos = rot_m @ Vector((r_curr, y_curr, gf_z))
            bm_add_box(bm_gf, cell_pos, (thick_s, (gf_chord / num_chord_slats) * 1.04, depth_s), rot_euler=(0.0, 0.0, ang))
    for c_j in range(1, num_chord_slats):
        y_curr = -gf_chord * 0.5 + (c_j / num_chord_slats) * gf_chord
        is_major_c = (c_j % 3 == 0)
        thick_c = 0.11 if is_major_c else (0.065 if c_j % 2 == 0 else 0.042)
        depth_c = gf_depth * (1.04 if is_major_c else (0.92 if c_j % 2 == 0 else 0.78))
        for s_i in range(num_span_slats):
            r_curr = r_start + (s_i + 0.5) * (gf_span / num_span_slats)
            cell_pos = rot_m @ Vector((r_curr, y_curr, gf_z))
            bm_add_box(bm_gf, cell_pos, ((gf_span / num_span_slats) * 1.04, thick_c, depth_c), rot_euler=(0.0, 0.0, ang))
    for s_i in range(4, num_span_slats, 4):
        r_curr = r_start + (s_i / num_span_slats) * gf_span
        for c_j in range(3, num_chord_slats, 3):
            y_curr = -gf_chord * 0.5 + (c_j / num_chord_slats) * gf_chord
            spike_pos = rot_m @ Vector((r_curr, y_curr, gf_z))
            bm_add_box(bm_gf, spike_pos, (0.16, 0.16, gf_depth * 1.22), rot_euler=(0.0, 0.0, ang))

finalize_mesh_object("Super_Heavy_Waffle_Grid_Fins", bm_gf, mat=mat_titanium_dark, smooth=False)

v5_z_base = 160.0
v5_cyl_h = 90.0
v5_nose_z_base = v5_z_base + v5_cyl_h
v5_nose_h = 32.0
v5_radius = 9.0
v5_segs = 128
v5_cyl_rings = 60
v5_nose_rings = 72

def v5_radius_at_z(z_world):
    if z_world <= v5_nose_z_base:
        return v5_radius
    z_local = min(v5_nose_h, max(0.0, z_world - v5_nose_z_base))
    if z_local >= v5_nose_h - 1e-5:
        return 0.0
    cos_arg = max(-1.0, min(1.0, 1.0 - 2.0 * (v5_nose_h - z_local) / v5_nose_h))
    theta = math.acos(cos_arg)
    r_vk = (v5_radius / math.sqrt(math.pi)) * math.sqrt(max(0.0, theta - 0.5 * math.sin(2.0 * theta)))
    rho = (v5_radius**2 + v5_nose_h**2) / (2.0 * v5_radius)
    r_tan = math.sqrt(max(0.0, rho**2 - z_local**2)) + v5_radius - rho
    return 0.55 * r_vk + 0.45 * r_tan

bm_v5 = bmesh.new()
v5_rings_verts = []
z_samples = []
for i in range(v5_cyl_rings):
    z_samples.append(v5_z_base + (i / v5_cyl_rings) * v5_cyl_h)
for i in range(v5_nose_rings):
    z_samples.append(v5_nose_z_base + (i / v5_nose_rings) * v5_nose_h)

for z_val in z_samples:
    rad = v5_radius_at_z(z_val)
    ring = []
    for s_idx in range(v5_segs):
        ang = (2.0 * math.pi * s_idx) / v5_segs + math.pi  # 180° rotation
        ring.append(bm_v5.verts.new((math.cos(ang) * rad, math.sin(ang) * rad, z_val)))
    v5_rings_verts.append(ring)

for r_idx in range(len(v5_rings_verts) - 1):
    for s_idx in range(v5_segs):
        ns = (s_idx + 1) % v5_segs
        bm_v5.faces.new((v5_rings_verts[r_idx][s_idx], v5_rings_verts[r_idx][ns], v5_rings_verts[r_idx + 1][ns], v5_rings_verts[r_idx + 1][s_idx]))

# Tip cone removed — nose ends at the last full ring (slightly truncated ogive)
top_ring = v5_rings_verts[-1]
# optional flat cap
bm_v5.faces.new(list(reversed(top_ring)))

bm_v5.faces.new(list(reversed(v5_rings_verts[0])))
finalize_mesh_object("Starship_V5_Hull", bm_v5, mat=mat_titanium, smooth=True)

bm_shield = bmesh.new()
hs_rings = []
for z_val in z_samples:
    rad = v5_radius_at_z(z_val) + 0.025
    ring = []
    for s_idx in range(v5_segs):
        ang = (2.0 * math.pi * s_idx) / v5_segs + math.pi  # 180° rotation
        ring.append(bm_shield.verts.new((math.cos(ang) * rad, math.sin(ang) * rad, z_val)))
    hs_rings.append(ring)

for r_idx in range(len(hs_rings) - 1):
    for s_idx in range(v5_segs):
        ns = (s_idx + 1) % v5_segs
        v00 = hs_rings[r_idx][s_idx]
        v01 = hs_rings[r_idx][ns]
        v11 = hs_rings[r_idx + 1][ns]
        v10 = hs_rings[r_idx + 1][s_idx]
        center = (v00.co + v01.co + v11.co + v10.co) * 0.25
        is_nose_cap = center.z > 276.8
        ang = math.atan2(center.y, center.x)
        # True belly = negative Y (around -90 deg / 270 deg), ±80 deg arc
        is_belly = abs((ang + math.pi/2 + math.pi) % (2*math.pi) - math.pi) < math.radians(80)
        # Exclude leeward (+Y / around +90 deg) window and cargo zones
        is_leeward_window_or_cargo = (abs((ang - math.pi/2 + math.pi) % (2*math.pi) - math.pi) < math.radians(50) and 210.0 < center.z < 276.0)
        if (is_nose_cap or is_belly) and not is_leeward_window_or_cargo:
            f = bm_shield.faces.new((v00, v01, v11, v10))
            f.material_index = 1

# Heat-shield tip cone removed
# (no hs_tip geometry)

unused_verts = [v for v in bm_shield.verts if not v.link_faces]
bmesh.ops.delete(bm_shield, geom=unused_verts, context='VERTS')

quad_faces = [f for f in bm_shield.faces if len(f.verts) == 4]
bmesh.ops.inset_individual(bm_shield, faces=quad_faces, thickness=0.068, depth=0.048)
for f in quad_faces:
    f.material_index = 0

bmesh.ops.solidify(bm_shield, geom=bm_shield.faces[:], thickness=0.15)
shield_obj = finalize_mesh_object("Starship_V5_Physical_Heat_Shield", bm_shield, mat=mat_heat_tiles, smooth=False)
shield_obj.data.materials.append(mat_heat_grout)

bm_flaps = bmesh.new()

def build_vertical_flap(bm, side_sign, z_bot_root, z_top_root, z_bot_tip, z_top_tip, span_out, add_hinge=True):
    stations = 12
    prof_pts = 8
    rings = []
    for i in range(stations + 1):
        u = i / stations
        z_b = z_bot_root * (1.0 - u) + z_bot_tip * u
        z_t = z_top_root * (1.0 - u) + z_top_tip * u
        half_thick = 0.62 * (1.0 - 0.65 * u)
        ring = []
        for k in range(prof_pts):
            t_ang = (2.0 * math.pi * k) / prof_pts
            z_curr = 0.5 * (z_b + z_t) + 0.5 * (z_t - z_b) * math.cos(t_ang)
            y_curr = half_thick * math.sin(t_ang)
            r_hull = v5_radius_at_z(z_curr) - 0.25
            x_root = side_sign * r_hull
            x_tip = side_sign * (v5_radius_at_z(z_bot_root) + span_out)
            x_curr = x_root * (1.0 - u) + x_tip * u
            ring.append(bm.verts.new((x_curr, y_curr, z_curr)))
        rings.append(ring)
    for i in range(stations):
        for k in range(prof_pts):
            nk = (k + 1) % prof_pts
            bm.faces.new((rings[i][k], rings[i][nk], rings[i + 1][nk], rings[i + 1][k]))
    bm.faces.new(rings[-1])
    if add_hinge:
        z_hinge_mid = 0.5 * (z_bot_root + z_top_root)
        r_hinge = v5_radius_at_z(z_hinge_mid) - 0.1
        bm_add_cylinder_frustum(bm, (side_sign * r_hinge, 0.0, z_hinge_mid), 0.78, 0.65, (z_top_root - z_bot_root) * 1.04, segments=20)

build_vertical_flap(bm_flaps, 1.0, 161.5, 189.5, 160.5, 174.5, 8.8)
build_vertical_flap(bm_flaps, -1.0, 161.5, 189.5, 160.5, 174.5, 8.8)
build_vertical_flap(bm_flaps, 1.0, 257.5, 273.5, 257.0, 265.0, 4.6, add_hinge=False)
build_vertical_flap(bm_flaps, -1.0, 257.5, 273.5, 257.0, 265.0, 4.6, add_hinge=False)
finalize_mesh_object("Starship_V5_Aerodynamic_Stabilizers", bm_flaps, mat=mat_heat_tiles, smooth=True)

bm_windows = bmesh.new()

def add_leeward_cockpit_window(bm, z_low, z_high, deg_start, deg_end, mat_glass_idx, mat_frame_idx):
    steps_u = 6
    steps_v = 4
    frame_pad_z = 0.22
    frame_pad_deg = 1.3
    for is_frame, m_idx, r_off, z0, z1, d0, d1 in (
        (True, mat_frame_idx, 0.05, z_low - frame_pad_z, z_high + frame_pad_z, deg_start - frame_pad_deg, deg_end + frame_pad_deg),
        (False, mat_glass_idx, 0.09, z_low, z_high, deg_start, deg_end),
    ):
        grid = []
        for iv in range(steps_v + 1):
            fv = iv / steps_v
            zc = z0 + fv * (z1 - z0)
            sweep_drop = 0.016 * ((0.5 * (d0 + d1))**2) * 0.05
            zc_swept = zc - sweep_drop
            rad = v5_radius_at_z(zc_swept) + r_off
            row = []
            for iu in range(steps_u + 1):
                fu = iu / steps_u
                ang = math.radians(d0 + fu * (d1 - d0))
                row.append(bm.verts.new((math.cos(ang) * rad, math.sin(ang) * rad, zc_swept)))
            grid.append(row)
        for iv in range(steps_v):
            for iu in range(steps_u):
                f = bm.faces.new((grid[iv][iu], grid[iv][iu + 1], grid[iv + 1][iu + 1], grid[iv + 1][iu]))
                f.material_index = m_idx

def add_horizontal_oval_window(bm, center_deg, z_center, half_w_deg, half_h_z, mat_glass_idx, mat_frame_idx):
    segs = 20
    for r_off, dw, dh, m_idx in (
        (0.05, half_w_deg + 0.9, half_h_z + 0.14, mat_frame_idx),
        (0.09, half_w_deg, half_h_z, mat_glass_idx),
    ):
        ring_verts = []
        for i in range(segs):
            theta = (2.0 * math.pi * i) / segs
            d_curr = center_deg + dw * math.cos(theta)
            z_curr = z_center + dh * math.sin(theta)
            rad = v5_radius_at_z(z_curr) + r_off
            ang = math.radians(d_curr)
            ring_verts.append(bm.verts.new((math.cos(ang) * rad, math.sin(ang) * rad, z_curr)))
        f = bm.faces.new(ring_verts)
        f.material_index = m_idx

shuttle_panes = [
    (226.0, 240.0, 272.0, 274.8),
    (242.5, 256.0, 272.4, 275.2),
    (258.5, 268.8, 272.8, 275.6),
    (271.2, 281.5, 272.8, 275.6),
    (284.0, 297.5, 272.4, 275.2),
    (300.0, 314.0, 272.0, 274.8),
]
for d0, d1, zl, zh in shuttle_panes:
    add_leeward_cockpit_window(bm_windows, zl, zh, d0, d1, mat_glass_idx=0, mat_frame_idx=2)

for deck_z in (228.0, 235.0, 242.0, 249.0):
    for p_deg in range(234, 312, 12):
        add_horizontal_oval_window(bm_windows, float(p_deg), deck_z, half_w_deg=4.2, half_h_z=0.48, mat_glass_idx=1, mat_frame_idx=2)

win_obj = finalize_mesh_object("Starship_V5_Cockpit_And_Cabin_Windows", bm_windows, mat=mat_cockpit_glass, smooth=True)
win_obj.data.materials.append(mat_cabin_glass)
win_obj.data.materials.append(mat_titanium_dark)

bm_cargo = bmesh.new()

def add_curved_hull_patch(bm, z0, z1, d0, d1, r_off, steps_u, steps_v, mat_idx):
    grid = []
    for iv in range(steps_v + 1):
        zc = z0 + (iv / steps_v) * (z1 - z0)
        rad = v5_radius_at_z(zc) + r_off
        row = []
        for iu in range(steps_u + 1):
            ang = math.radians(d0 + (iu / steps_u) * (d1 - d0))
            row.append(bm.verts.new((math.cos(ang) * rad, math.sin(ang) * rad, zc)))
        grid.append(row)
    created_faces = []
    for iv in range(steps_v):
        for iu in range(steps_u):
            f = bm.faces.new((grid[iv][iu], grid[iv][iu + 1], grid[iv + 1][iu + 1], grid[iv + 1][iu]))
            f.material_index = mat_idx
            created_faces.append(f)
    return created_faces

cd_z_bot = 214.0
cd_z_top = 219.0
cd_deg_min = 235.0
cd_deg_max = 305.0
add_curved_hull_patch(bm_cargo, cd_z_bot - 0.35, cd_z_top + 0.35, cd_deg_min - 2.2, cd_deg_max + 2.2, 0.05, 16, 8, mat_idx=1)
door_faces = add_curved_hull_patch(bm_cargo, cd_z_bot, cd_z_top, cd_deg_min, cd_deg_max, 0.09, 14, 6, mat_idx=0)
bmesh.ops.solidify(bm_cargo, geom=door_faces, thickness=0.14)

add_curved_hull_patch(bm_cargo, cd_z_bot, cd_z_top, -0.45, 0.45, 0.17, 2, 6, mat_idx=1)
for z_seam in (217.25, 218.50, 219.75):
    add_curved_hull_patch(bm_cargo, z_seam - 0.07, z_seam + 0.07, cd_deg_min, cd_deg_max, 0.17, 14, 1, mat_idx=1)

for z_hinge in (216.6, 217.8, 219.2, 220.4):
    for d_hinge in (cd_deg_min - 1.2, cd_deg_max + 1.2):
        ang_h = math.radians(d_hinge)
        r_h = v5_radius_at_z(z_hinge) + 0.12
        bm_add_box(bm_cargo, (math.cos(ang_h) * r_h, math.sin(ang_h) * r_h, z_hinge), (0.28, 0.42, 0.48), rot_euler=(0.0, 0.0, ang_h), mat_idx=1)

for z_latch in (216.8, 218.5, 220.2):
    r_l = v5_radius_at_z(z_latch) + 0.16
    bm_add_box(bm_cargo, (r_l, 0.0, z_latch), (0.20, 0.55, 0.28), mat_idx=1)

person_door_faces = add_curved_hull_patch(bm_cargo, 226.5, 229.3, -29.0, -21.0, 0.08, 6, 4, mat_idx=1)
bmesh.ops.solidify(bm_cargo, geom=person_door_faces, thickness=0.10)

cargo_obj = finalize_mesh_object("Starship_V5_Cargo_Bay_Door", bm_cargo, mat=mat_titanium, smooth=False)
cargo_obj.data.materials.append(mat_titanium_dark)

bm_tower = bmesh.new()
tw_cx, tw_cy = -42.0, 6.0
tw_half = 9.5
tw_height = 312.0
tw_bays = 64
bay_h = tw_height / tw_bays

bm_add_box(bm_tower, (tw_cx, tw_cy, 4.0), (24.0, 24.0, 8.0), mat_idx=0)

cols = [
    (tw_cx - tw_half, tw_cy - tw_half),
    (tw_cx + tw_half, tw_cy - tw_half),
    (tw_cx + tw_half, tw_cy + tw_half),
    (tw_cx - tw_half, tw_cy + tw_half),
]
for cx, cy in cols:
    bm_add_cylinder_frustum(bm_tower, (cx, cy, tw_height * 0.5), 1.45, 1.30, tw_height, segments=20, mat_idx=0)

bm_add_box(bm_tower, (tw_cx - 3.5, tw_cy, tw_height * 0.5), (4.5, 5.5, tw_height - 4.0), mat_idx=0)

faces_pairs = [(0, 1), (1, 2), (2, 3), (3, 0)]
for b_idx in range(tw_bays):
    z0 = b_idx * bay_h
    z1 = (b_idx + 1) * bay_h
    zm = 0.5 * (z0 + z1)
    for c_a, c_b in faces_pairs:
        xa, ya = cols[c_a][0], cols[c_a][1]
        xb, yb = cols[c_b][0], cols[c_b][1]
        xm, ym = 0.5 * (xa + xb), 0.5 * (ya + yb)
        p_a0 = (xa, ya, z0)
        p_b0 = (xb, yb, z0)
        p_a1 = (xa, ya, z1)
        p_b1 = (xb, yb, z1)
        p_am = (xa, ya, zm)
        p_bm = (xb, yb, zm)
        p_m0 = (xm, ym, z0)
        p_m1 = (xm, ym, z1)
        p_mm = (xm, ym, zm)
        bm_add_strut(bm_tower, p_a1, p_b1, 0.68, mat_idx=0)
        bm_add_strut(bm_tower, p_am, p_bm, 0.34, mat_idx=0)
        bm_add_strut(bm_tower, p_m0, p_m1, 0.30, mat_idx=0)
        bm_add_strut(bm_tower, p_a0, p_b1, 0.52, mat_idx=0)
        bm_add_strut(bm_tower, p_b0, p_a1, 0.52, mat_idx=0)
        bm_add_strut(bm_tower, p_a0, p_bm, 0.24, mat_idx=0)
        bm_add_strut(bm_tower, p_b0, p_am, 0.24, mat_idx=0)
        bm_add_strut(bm_tower, p_am, p_b1, 0.24, mat_idx=0)
        bm_add_strut(bm_tower, p_bm, p_a1, 0.24, mat_idx=0)
        bm_add_strut(bm_tower, p_a0, p_mm, 0.18, mat_idx=0)
        bm_add_strut(bm_tower, p_b0, p_mm, 0.18, mat_idx=0)
        bm_add_strut(bm_tower, p_a1, p_mm, 0.18, mat_idx=0)
        bm_add_strut(bm_tower, p_b1, p_mm, 0.18, mat_idx=0)
    if b_idx % 2 == 0:
        bm_add_strut(bm_tower, (cols[0][0], cols[0][1], z1), (cols[2][0], cols[2][1], z1), 0.42, mat_idx=0)
        bm_add_strut(bm_tower, (cols[1][0], cols[1][1], z1), (cols[3][0], cols[3][1], z1), 0.42, mat_idx=0)
    if b_idx % 4 == 0 and b_idx > 0:
        bm_add_box(bm_tower, (tw_cx, tw_cy, z1), (18.2, 18.2, 0.28), mat_idx=0)
        bm_add_box(bm_tower, (tw_cx, tw_cy - tw_half - 1.2, z1), (19.6, 2.2, 0.24), mat_idx=0)
        bm_add_box(bm_tower, (tw_cx - tw_half - 1.2, tw_cy, z1), (2.2, 19.6, 0.24), mat_idx=0)
        bm_add_strut(bm_tower, (tw_cx - tw_half - 0.8, tw_cy - tw_half - 2.2, z1 + 1.1), (tw_cx + tw_half + 0.8, tw_cy - tw_half - 2.2, z1 + 1.1), 0.12, mat_idx=0)
        bm_add_strut(bm_tower, (tw_cx - tw_half - 2.2, tw_cy - tw_half - 0.8, z1 + 1.1), (tw_cx - tw_half - 2.2, tw_cy + tw_half + 0.8, z1 + 1.1), 0.12, mat_idx=0)

for pipe_y in (tw_cy - 6.8, tw_cy - 5.2, tw_cy - 3.6, tw_cy + 4.8, tw_cy + 6.4):
    bm_add_cylinder_frustum(bm_tower, (tw_cx - tw_half - 0.9, pipe_y, tw_height * 0.5), 0.36, 0.36, tw_height - 6.0, segments=12, mat_idx=0)
for pipe_x in (tw_cx - 6.0, tw_cx - 2.5, tw_cx + 2.5, tw_cx + 6.0):
    bm_add_cylinder_frustum(bm_tower, (pipe_x, tw_cy + tw_half + 0.9, tw_height * 0.5), 0.32, 0.32, tw_height - 6.0, segments=12, mat_idx=0)
for clamp_z in range(12, int(tw_height), 12):
    bm_add_box(bm_tower, (tw_cx - tw_half - 0.9, tw_cy, clamp_z), (0.9, 16.0, 0.45), mat_idx=0)
    bm_add_box(bm_tower, (tw_cx, tw_cy + tw_half + 0.9, clamp_z), (16.0, 0.9, 0.45), mat_idx=0)

lad_x = tw_cx + 5.5
lad_y = tw_cy - tw_half - 0.85
bm_add_strut(bm_tower, (lad_x - 0.32, lad_y, 8.0), (lad_x - 0.32, lad_y, tw_height - 4.0), 0.10, mat_idx=0)
bm_add_strut(bm_tower, (lad_x + 0.32, lad_y, 8.0), (lad_x + 0.32, lad_y, tw_height - 4.0), 0.10, mat_idx=0)
for rz in range(9, int(tw_height - 4), 2):
    bm_add_strut(bm_tower, (lad_x - 0.32, lad_y, float(rz)), (lad_x + 0.32, lad_y, float(rz)), 0.06, mat_idx=0)
    if rz % 4 == 1:
        bm_add_cylinder_frustum(bm_tower, (lad_x, lad_y - 0.45, float(rz)), 0.55, 0.55, 0.12, segments=12, cap_ends=False, mat_idx=0)
for strap_x in (lad_x - 0.52, lad_x, lad_x + 0.52):
    bm_add_strut(bm_tower, (strap_x, lad_y - 0.95, 10.0), (strap_x, lad_y - 0.95, tw_height - 4.0), 0.06, mat_idx=0)

bm_add_box(bm_tower, (tw_cx + 3.0, tw_cy, tw_height + 3.5), (26.0, 22.0, 7.0), mat_idx=0)
bm_add_cylinder_frustum(bm_tower, (tw_cx, tw_cy, tw_height + 16.0), 0.6, 0.1, 18.0, segments=12, mat_idx=0)

car_z = 146.5
bm_add_box(bm_tower, (-30.5, tw_cy, car_z), (4.5, 24.0, 9.0), mat_idx=0)
for arm_y in (-11.6, 11.6):
    x_start = -29.0
    x_end = 7.5
    arm_bays = 14
    dx_bay = (x_end - x_start) / arm_bays
    for ab in range(arm_bays):
        ax0 = x_start + ab * dx_bay
        ax1 = ax0 + dx_bay
        h0 = 4.2 * (1.0 - 0.45 * (ab / arm_bays))
        h1 = 4.2 * (1.0 - 0.45 * ((ab + 1) / arm_bays))
        for y_rail in (arm_y - 1.1, arm_y + 1.1):
            bm_add_strut(bm_tower, (ax0, y_rail, car_z + h0 * 0.5), (ax1, y_rail, car_z + h1 * 0.5), 0.48, mat_idx=0)
            bm_add_strut(bm_tower, (ax0, y_rail, car_z - h0 * 0.5), (ax1, y_rail, car_z - h1 * 0.5), 0.48, mat_idx=0)
            bm_add_strut(bm_tower, (ax0, y_rail, car_z - h0 * 0.5), (ax0, y_rail, car_z + h0 * 0.5), 0.40, mat_idx=0)
            bm_add_strut(bm_tower, (ax0, y_rail, car_z - h0 * 0.5), (ax1, y_rail, car_z + h1 * 0.5), 0.36, mat_idx=0)
            bm_add_strut(bm_tower, (ax0, y_rail, car_z + h0 * 0.5), (ax1, y_rail, car_z - h1 * 0.5), 0.36, mat_idx=0)
        bm_add_strut(bm_tower, (ax1, arm_y - 1.1, car_z + h1 * 0.5), (ax1, arm_y + 1.1, car_z + h1 * 0.5), 0.38, mat_idx=0)
        bm_add_strut(bm_tower, (ax1, arm_y - 1.1, car_z - h1 * 0.5), (ax1, arm_y + 1.1, car_z - h1 * 0.5), 0.38, mat_idx=0)

def build_umbilical_arm(bm, z_arm, y_arm, x_tower_face, x_ship_target):
    bays = 10
    dx = (x_ship_target - x_tower_face) / bays
    w_y = 1.6
    h_z = 2.0
    bm_add_box(bm, (x_tower_face - 0.8, y_arm, z_arm), (2.2, 4.2, 4.8), mat_idx=0)
    for b in range(bays):
        x0 = x_tower_face + b * dx
        x1 = x0 + dx
        for sy in (-w_y * 0.5, w_y * 0.5):
            bm_add_strut(bm, (x0, y_arm + sy, z_arm - h_z * 0.5), (x1, y_arm + sy, z_arm - h_z * 0.5), 0.28, mat_idx=0)
            bm_add_strut(bm, (x0, y_arm + sy, z_arm + h_z * 0.5), (x1, y_arm + sy, z_arm + h_z * 0.5), 0.28, mat_idx=0)
            bm_add_strut(bm, (x0, y_arm + sy, z_arm - h_z * 0.5), (x0, y_arm + sy, z_arm + h_z * 0.5), 0.24, mat_idx=0)
            bm_add_strut(bm, (x0, y_arm + sy, z_arm - h_z * 0.5), (x1, y_arm + sy, z_arm + h_z * 0.5), 0.22, mat_idx=0)
        bm_add_strut(bm, (x1, y_arm - w_y * 0.5, z_arm + h_z * 0.5), (x1, y_arm + w_y * 0.5, z_arm + h_z * 0.5), 0.22, mat_idx=0)
        bm_add_strut(bm, (x1, y_arm - w_y * 0.5, z_arm - h_z * 0.5), (x1, y_arm + w_y * 0.5, z_arm - h_z * 0.5), 0.22, mat_idx=0)
    for pz_off in (-0.55, 0.55):
        for py_off in (-0.42, 0.42):
            bm_add_strut(bm, (x_tower_face, y_arm + py_off, z_arm + pz_off), (x_ship_target + 0.6, y_arm + py_off * 0.7, z_arm + pz_off * 0.7), 0.42, mat_idx=2)
    bm_add_box(bm, (x_ship_target + 0.45, y_arm, z_arm), (0.95, 2.8, 3.0), mat_idx=0)
    bm_add_strut(bm, (x_tower_face, y_arm, z_arm - 6.5), (x_tower_face + 0.55 * (x_ship_target - x_tower_face), y_arm, z_arm - h_z * 0.5), 0.45, mat_idx=0)

build_umbilical_arm(bm_tower, 44.0, 2.8, -32.2, -9.55)
build_umbilical_arm(bm_tower, 196.0, 2.8, -32.2, -9.55)

tower_obj = finalize_mesh_object("Mechazilla_312m_Launch_Tower", bm_tower, mat=mat_tower_steel, smooth=False)
tower_obj.data.materials.append(mat_cabin_glass)
tower_obj.data.materials.append(mat_cryo_white)

bm_crew_tower = bmesh.new()
ct_cx, ct_cy = 44.0, 0.0
ct_half = 7.5
ct_height = 258.0
ct_bays = 43
ct_bay_h = ct_height / ct_bays

bm_add_box(bm_crew_tower, (ct_cx, ct_cy, 3.5), (20.0, 20.0, 7.0), mat_idx=0)
ct_cols = [
    (ct_cx - ct_half, ct_cy - ct_half),
    (ct_cx + ct_half, ct_cy - ct_half),
    (ct_cx + ct_half, ct_cy + ct_half),
    (ct_cx - ct_half, ct_cy + ct_half),
]
for cx, cy in ct_cols:
    bm_add_cylinder_frustum(bm_crew_tower, (cx, cy, ct_height * 0.5), 1.15, 1.0, ct_height, segments=18, mat_idx=0)

for b_idx in range(ct_bays):
    z0 = b_idx * ct_bay_h
    z1 = (b_idx + 1) * ct_bay_h
    zm = 0.5 * (z0 + z1)
    for c_a, c_b in faces_pairs:
        p_a0 = (ct_cols[c_a][0], ct_cols[c_a][1], z0)
        p_b0 = (ct_cols[c_b][0], ct_cols[c_b][1], z0)
        p_a1 = (ct_cols[c_a][0], ct_cols[c_a][1], z1)
        p_b1 = (ct_cols[c_b][0], ct_cols[c_b][1], z1)
        p_am = (ct_cols[c_a][0], ct_cols[c_a][1], zm)
        p_bm = (ct_cols[c_b][0], ct_cols[c_b][1], zm)
        bm_add_strut(bm_crew_tower, p_a1, p_b1, 0.55, mat_idx=0)
        bm_add_strut(bm_crew_tower, p_am, p_bm, 0.30, mat_idx=0)
        bm_add_strut(bm_crew_tower, p_a0, p_b1, 0.42, mat_idx=0)
        bm_add_strut(bm_crew_tower, p_b0, p_a1, 0.42, mat_idx=0)
    if b_idx % 4 == 0 and b_idx > 0:
        bm_add_box(bm_crew_tower, (ct_cx, ct_cy, z1), (14.6, 14.6, 0.25), mat_idx=0)

bm_add_box(bm_crew_tower, (ct_cx, ct_cy, ct_height + 2.5), (19.0, 19.0, 5.0), mat_idx=2)

elev_x = ct_cx
elev_y = ct_cy - ct_half - 2.6
elev_h = 240.0
for ex_off in (-1.8, 1.8):
    for ey_off in (-1.6, 1.6):
        bm_add_strut(bm_crew_tower, (elev_x + ex_off, elev_y + ey_off, 0.0), (elev_x + ex_off, elev_y + ey_off, elev_h), 0.32, mat_idx=0)
for ez in range(6, int(elev_h), 6):
    bm_add_box(bm_crew_tower, (elev_x, elev_y, float(ez)), (3.8, 3.4, 0.22), mat_idx=0)
bm_add_box(bm_crew_tower, (elev_x, elev_y, elev_h * 0.5), (3.3, 2.9, elev_h - 2.0), mat_idx=3)

for cab_z in (92.0, 188.0):
    bm_add_box(bm_crew_tower, (elev_x, elev_y, cab_z), (3.6, 3.2, 5.2), mat_idx=2)
    bm_add_box(bm_crew_tower, (elev_x, elev_y - 0.1, cab_z), (3.7, 2.6, 3.6), mat_idx=1)

jw_z = 228.0
jw_x0 = 9.25
jw_x1 = ct_cx - ct_half
jw_len = jw_x1 - jw_x0
jw_cx = 0.5 * (jw_x0 + jw_x1)
jw_y = -3.8
bm_add_box(bm_crew_tower, (jw_cx, jw_y, jw_z - 1.65), (jw_len, 4.2, 0.45), mat_idx=2)
bm_add_box(bm_crew_tower, (jw_cx, jw_y, jw_z + 1.65), (jw_len, 4.2, 0.45), mat_idx=2)
bm_add_box(bm_crew_tower, (jw_cx, jw_y, jw_z), (jw_len - 0.4, 3.6, 2.6), mat_idx=1)
for jx in range(int(jw_x0) + 1, int(jw_x1), 3):
    bm_add_strut(bm_crew_tower, (float(jx), jw_y - 2.0, jw_z - 1.5), (float(jx + 2.5), jw_y - 2.0, jw_z + 1.5), 0.20, mat_idx=0)
    bm_add_strut(bm_crew_tower, (float(jx), jw_y + 2.0, jw_z - 1.5), (float(jx + 2.5), jw_y + 2.0, jw_z + 1.5), 0.20, mat_idx=0)
    bm_add_strut(bm_crew_tower, (float(jx), jw_y - 2.0, jw_z - 1.5), (float(jx), jw_y - 2.0, jw_z + 1.5), 0.22, mat_idx=0)
    bm_add_strut(bm_crew_tower, (float(jx), jw_y + 2.0, jw_z - 1.5), (float(jx), jw_y + 2.0, jw_z + 1.5), 0.22, mat_idx=0)
bm_add_box(bm_crew_tower, (9.45, jw_y, jw_z), (0.8, 4.6, 3.8), mat_idx=0)
bm_add_strut(bm_crew_tower, (jw_x1, jw_y - 1.8, jw_z - 9.5), (jw_x0 + 6.0, jw_y - 1.8, jw_z - 1.65), 0.55, mat_idx=0)
bm_add_strut(bm_crew_tower, (jw_x1, jw_y + 1.8, jw_z - 9.5), (jw_x0 + 6.0, jw_y + 1.8, jw_z - 1.65), 0.55, mat_idx=0)
# Enclosed indoor platform connecting passenger elevator and jetway
plat_z = jw_z
plat_cx = (elev_x + jw_cx) * 0.5
plat_cy = (elev_y + jw_y) * 0.5
plat_len = abs(jw_cx - elev_x) + 8.0
plat_w = 9.0
bm_add_box(bm_crew_tower, (plat_cx, plat_cy, plat_z - 0.4), (plat_len, plat_w, 0.8), mat_idx=0)
bm_add_box(bm_crew_tower, (plat_cx, plat_cy, plat_z + 1.8), (plat_len - 0.6, plat_w - 0.6, 0.25), mat_idx=1)
# side walls / enclosure
for side_y in (-plat_w*0.45, plat_w*0.45):
    bm_add_box(bm_crew_tower, (plat_cx, plat_cy + side_y, plat_z + 1.0), (plat_len - 1.0, 0.2, 2.2), mat_idx=2)
bm_add_box(bm_crew_tower, (elev_x, elev_y, plat_z + 1.0), (4.2, 3.8, 2.4), mat_idx=2)
# Cargo elevator (open heavy-duty steel box pulled by cables) inside the same tower
cargo_elev_x = ct_cx + 4.5
cargo_elev_y = ct_cy
cargo_elev_h = 220.0
# cables
for cx_off in (-1.4, 1.4):
    for cy_off in (-1.4, 1.4):
        bm_add_strut(bm_crew_tower, (cargo_elev_x + cx_off, cargo_elev_y + cy_off, 0.0), (cargo_elev_x + cx_off, cargo_elev_y + cy_off, cargo_elev_h), 0.18, mat_idx=0)
# open steel box (cargo deck)
box_z = 160.0
bm_add_box(bm_crew_tower, (cargo_elev_x, cargo_elev_y, box_z), (6.5, 5.5, 0.4), mat_idx=0)
bm_add_box(bm_crew_tower, (cargo_elev_x - 3.1, cargo_elev_y, box_z + 1.2), (0.25, 5.5, 2.0), mat_idx=0)
bm_add_box(bm_crew_tower, (cargo_elev_x + 3.1, cargo_elev_y, box_z + 1.2), (0.25, 5.5, 2.0), mat_idx=0)
bm_add_box(bm_crew_tower, (cargo_elev_x, cargo_elev_y - 2.6, box_z + 1.2), (6.5, 0.25, 2.0), mat_idx=0)
bm_add_box(bm_crew_tower, (cargo_elev_x, cargo_elev_y + 2.6, box_z + 1.2), (6.5, 0.25, 2.0), mat_idx=0)
# guide rails
bm_add_strut(bm_crew_tower, (cargo_elev_x - 3.4, cargo_elev_y - 2.8, 0.0), (cargo_elev_x - 3.4, cargo_elev_y - 2.8, cargo_elev_h), 0.35, mat_idx=0)
bm_add_strut(bm_crew_tower, (cargo_elev_x + 3.4, cargo_elev_y + 2.8, 0.0), (cargo_elev_x + 3.4, cargo_elev_y + 2.8, cargo_elev_h), 0.35, mat_idx=0)


cp_z = 216.0
cp_x0 = 9.30
cp_x1 = ct_cx - ct_half
cp_len = cp_x1 - cp_x0
cp_cx = 0.5 * (cp_x0 + cp_x1)
cp_w = 11.5
bm_add_box(bm_crew_tower, (cp_cx, 0.0, cp_z - 0.6), (cp_len, cp_w, 1.2), mat_idx=0)
bm_add_box(bm_crew_tower, (cp_cx, 0.0, cp_z + 0.1), (cp_len - 0.5, cp_w - 0.8, 0.25), mat_idx=2)
for rail_y in (-cp_w * 0.5 + 0.25, cp_w * 0.5 - 0.25):
    bm_add_strut(bm_crew_tower, (cp_x0 + 0.5, rail_y, cp_z + 1.2), (cp_x1, rail_y, cp_z + 1.2), 0.18, mat_idx=2)
    bm_add_strut(bm_crew_tower, (cp_x0 + 0.5, rail_y, cp_z + 0.6), (cp_x1, rail_y, cp_z + 0.6), 0.12, mat_idx=2)
    for rx in range(int(cp_x0) + 1, int(cp_x1), 3):
        bm_add_strut(bm_crew_tower, (float(rx), rail_y, cp_z), (float(rx), rail_y, cp_z + 1.2), 0.14, mat_idx=2)
for sy in (-4.8, 0.0, 4.8):
    bm_add_strut(bm_crew_tower, (cp_x1, sy, cp_z - 14.0), (cp_x0 + 4.5, sy, cp_z - 1.0), 0.85, mat_idx=0)
    bm_add_strut(bm_crew_tower, (cp_x1, sy, cp_z - 7.0), (cp_x0 + 12.0, sy, cp_z - 1.0), 0.65, mat_idx=0)
bm_add_strut(bm_crew_tower, (cp_x0 + 2.0, -4.5, cp_z), (cp_x0 + 2.0, -4.5, cp_z + 6.5), 0.45, mat_idx=2)
bm_add_strut(bm_crew_tower, (cp_x0 + 2.0, 4.5, cp_z), (cp_x0 + 2.0, 4.5, cp_z + 6.5), 0.45, mat_idx=2)
bm_add_strut(bm_crew_tower, (cp_x0 + 2.0, -4.5, cp_z + 6.5), (cp_x0 + 2.0, 4.5, cp_z + 6.5), 0.50, mat_idx=2)

term_x, term_y = 72.0, -8.0
bm_add_box(bm_crew_tower, (term_x, term_y, 4.0), (78.0, 92.0, 8.0), mat_idx=2)
bm_add_box(bm_crew_tower, (term_x, term_y, 8.2), (82.0, 96.0, 0.8), mat_idx=2)
bm_add_box(bm_crew_tower, (term_x, term_y, 12.5), (64.0, 74.0, 7.5), mat_idx=3)
bm_add_box(bm_crew_tower, (term_x, term_y, 16.5), (68.0, 78.0, 0.9), mat_idx=2)
bm_add_box(bm_crew_tower, (term_x - 4.0, term_y, 20.5), (48.0, 54.0, 6.5), mat_idx=1)
bm_add_box(bm_crew_tower, (term_x - 4.0, term_y, 24.0), (54.0, 60.0, 1.1), mat_idx=2)
for col_y in range(int(term_y - 24), int(term_y + 26), 6):
    bm_add_cylinder_frustum(bm_crew_tower, (term_x - 22.5, float(col_y), 7.0), 0.45, 0.45, 14.0, segments=14, mat_idx=2)
    bm_add_cylinder_frustum(bm_crew_tower, (term_x + 22.5, float(col_y), 7.0), 0.45, 0.45, 14.0, segments=14, mat_idx=2)
for col_x in range(int(term_x - 18), int(term_x + 20), 6):
    bm_add_cylinder_frustum(bm_crew_tower, (float(col_x), term_y - 26.5, 7.0), 0.45, 0.45, 14.0, segments=14, mat_idx=2)

crew_tower_obj = finalize_mesh_object("Passenger_Cargo_Tower_And_Terminal", bm_crew_tower, mat=mat_tower_steel, smooth=False)
crew_tower_obj.data.materials.append(mat_cabin_glass)
crew_tower_obj.data.materials.append(mat_terminal_metal)
crew_tower_obj.data.materials.append(mat_terminal_glass)

bm_tanks = bmesh.new()
tank_x_base = 115.0
for row_i in range(2):
    for col_j in range(4):
        tx = tank_x_base + row_i * 26.0
        ty = 25.0 + col_j * 32.0
        bm_add_cylinder_frustum(bm_tanks, (tx, ty, 26.0), 8.2, 8.2, 52.0, segments=48, mat_idx=0)
        bm_add_cylinder_frustum(bm_tanks, (tx, ty, 54.0), 8.2, 2.2, 4.0, segments=48, mat_idx=0)
        bm_add_cylinder_frustum(bm_tanks, (tx, ty, 56.8), 2.2, 0.1, 1.6, segments=32, mat_idx=0)
        bm_add_cylinder_frustum(bm_tanks, (tx - 8.6, ty, 26.0), 0.5, 0.5, 50.0, segments=12, mat_idx=1)

bm_add_box(bm_tanks, (128.0, 15.0, 4.5), (68.0, 2.5, 9.0), mat_idx=1)
bm_add_box(bm_tanks, (128.0, 140.0, 4.5), (68.0, 2.5, 9.0), mat_idx=1)
bm_add_box(bm_tanks, (94.0, 77.5, 4.5), (2.5, 127.0, 9.0), mat_idx=1)
bm_add_box(bm_tanks, (162.0, 77.5, 4.5), (2.5, 127.0, 9.0), mat_idx=1)
bm_add_box(bm_tanks, (52.0, 20.0, 2.2), (84.0, 3.2, 2.8), mat_idx=1)

tanks_obj = finalize_mesh_object("Orbital_Propellant_Tank_Farm", bm_tanks, mat=mat_cryo_white, smooth=True)
tanks_obj.data.materials.append(mat_tower_steel)

bm_semis = bmesh.new()

def add_tesla_semi(bm, orig_x, orig_y, heading_deg):
    rot_m = Euler((0.0, 0.0, math.radians(heading_deg)), 'XYZ').to_matrix()
    base_v = Vector((orig_x, orig_y, 0.0))

    def tr(pt):
        return base_v + (rot_m @ Vector(pt))

    rot_e = (0.0, 0.0, math.radians(heading_deg))
    bm_add_box(bm, tr((0.0, 4.8, 0.85)), (1.1, 7.2, 0.35), rot_euler=rot_e, mat_idx=3)
    bm_add_box(bm, tr((0.0, 4.3, 0.95)), (2.48, 5.4, 0.75), rot_euler=rot_e, mat_idx=0)
    bm_add_box(bm, tr((0.0, 8.48, 0.58)), (2.28, 0.24, 0.32), rot_euler=rot_e, mat_idx=1)
    bm_add_box(bm, tr((0.0, 2.45, 1.18)), (1.15, 1.15, 0.16), rot_euler=rot_e, mat_idx=3)

    cab_stations = [
        (8.40, 0.45, 1.15, 2.20),
        (7.95, 0.45, 1.48, 2.36),
        (6.65, 1.35, 2.85, 2.44),
        (5.10, 1.35, 3.88, 2.52),
        (3.40, 1.35, 4.12, 2.58),
    ]
    cab_rings = []
    for y_st, z_low, z_high, w_st in cab_stations:
        hw = w_st * 0.5
        r_pts = [
            bm.verts.new(tr((-hw, y_st, z_low))),
            bm.verts.new(tr((hw, y_st, z_low))),
            bm.verts.new(tr((hw * 0.94, y_st, z_high))),
            bm.verts.new(tr((-hw * 0.94, y_st, z_high))),
        ]
        cab_rings.append(r_pts)
    for idx in range(len(cab_rings) - 1):
        for k in range(4):
            nk = (k + 1) % 4
            f = bm.faces.new((cab_rings[idx][k], cab_rings[idx][nk], cab_rings[idx + 1][nk], cab_rings[idx + 1][k]))
            f.material_index = 1 if (idx == 1 and k in (1, 2, 3)) else 0
    f_front = bm.faces.new(list(reversed(cab_rings[0])))
    f_front.material_index = 0
    f_back = bm.faces.new(cab_rings[-1])
    f_back.material_index = 0

    for side_s in (-1.0, 1.0):
        sx = side_s * 1.25
        bm_add_box(bm, tr((sx, 5.75, 1.95)), (0.05, 0.04, 1.45), rot_euler=rot_e, mat_idx=1)
        bm_add_box(bm, tr((sx, 4.55, 2.05)), (0.05, 0.04, 1.65), rot_euler=rot_e, mat_idx=1)
        bm_add_box(bm, tr((sx, 5.15, 1.25)), (0.05, 1.24, 0.04), rot_euler=rot_e, mat_idx=1)
        bm_add_box(bm, tr((sx, 5.15, 2.75)), (0.05, 1.24, 0.04), rot_euler=rot_e, mat_idx=1)
        bm_add_box(bm, tr((sx * 1.02, 4.82, 1.72)), (0.06, 0.22, 0.06), rot_euler=rot_e, mat_idx=1)
        bm_add_box(bm, tr((sx * 1.01, 5.20, 0.62)), (0.14, 0.85, 0.06), rot_euler=rot_e, mat_idx=3)
        bm_add_box(bm, tr((sx * 1.01, 5.20, 0.84)), (0.14, 0.85, 0.06), rot_euler=rot_e, mat_idx=3)
        bm_add_strut(bm, tr((side_s * 1.18, 6.45, 2.28)), tr((side_s * 1.54, 6.25, 2.34)), 0.06, mat_idx=1)
        bm_add_strut(bm, tr((side_s * 1.18, 6.45, 1.98)), tr((side_s * 1.54, 6.25, 2.12)), 0.05, mat_idx=1)
        bm_add_box(bm, tr((side_s * 1.56, 6.22, 2.24)), (0.10, 0.24, 0.56), rot_euler=rot_e, mat_idx=0)
        bm_add_box(bm, tr((side_s * 1.56, 6.10, 2.24)), (0.08, 0.04, 0.50), rot_euler=rot_e, mat_idx=1)

    for rib_x in (-0.96, -0.48, 0.0, 0.48, 0.96):
        bm_add_strut(bm, tr((rib_x, 6.40, 2.92)), tr((rib_x, 5.05, 3.92)), 0.07, mat_idx=0)
        bm_add_strut(bm, tr((rib_x, 5.05, 3.92)), tr((rib_x, 3.42, 4.16)), 0.07, mat_idx=0)
    bm_add_box(bm, tr((-1.26, 3.32, 2.65)), (0.06, 0.42, 2.85), rot_euler=rot_e, mat_idx=0)
    bm_add_box(bm, tr((1.26, 3.32, 2.65)), (0.06, 0.42, 2.85), rot_euler=rot_e, mat_idx=0)

    bm_add_box(bm, tr((-0.92, 8.38, 0.82)), (0.38, 0.12, 0.16), rot_euler=rot_e, mat_idx=4)
    bm_add_box(bm, tr((0.92, 8.38, 0.82)), (0.38, 0.12, 0.16), rot_euler=rot_e, mat_idx=4)

    bm_add_box(bm, tr((0.0, -4.8, 2.70)), (2.60, 16.15, 2.90), rot_euler=rot_e, mat_idx=0)
    bm_add_box(bm, tr((0.0, 3.38, 2.65)), (1.55, 0.35, 1.85), rot_euler=rot_e, mat_idx=1)
    for tr_y in range(-12, 3, 2):
        bm_add_box(bm, tr((-1.31, float(tr_y), 2.70)), (0.03, 0.06, 2.82), rot_euler=rot_e, mat_idx=0)
        bm_add_box(bm, tr((1.31, float(tr_y), 2.70)), (0.03, 0.06, 2.82), rot_euler=rot_e, mat_idx=0)
    bm_add_box(bm, tr((-1.26, -3.5, 0.95)), (0.08, 7.5, 0.65), rot_euler=rot_e, mat_idx=0)
    bm_add_box(bm, tr((1.26, -3.5, 0.95)), (0.08, 7.5, 0.65), rot_euler=rot_e, mat_idx=0)
    bm_add_box(bm, tr((-0.95, 1.1, 0.75)), (0.18, 0.18, 1.0), rot_euler=rot_e, mat_idx=3)
    bm_add_box(bm, tr((0.95, 1.1, 0.75)), (0.18, 0.18, 1.0), rot_euler=rot_e, mat_idx=3)
    bm_add_box(bm, tr((0.0, -12.88, 0.72)), (2.45, 0.12, 0.15), rot_euler=rot_e, mat_idx=3)

    wheel_rot = (0.0, math.radians(90), math.radians(heading_deg))
    steer_y = 7.15
    for wx in (-1.12, 1.12):
        bm_add_cylinder_frustum(bm, tr((wx, steer_y, 0.52)), 0.52, 0.52, 0.28, segments=24, rot_euler=wheel_rot, mat_idx=2)
        bm_add_cylinder_frustum(bm, tr((wx * 1.03, steer_y, 0.52)), 0.30, 0.30, 0.30, segments=18, rot_euler=wheel_rot, mat_idx=3)

    dual_axles_y = [3.45, 2.15, -10.20, -11.50]
    for ay in dual_axles_y:
        bm_add_cylinder_frustum(bm, tr((0.0, ay, 0.52)), 0.14, 0.14, 2.30, segments=12, rot_euler=wheel_rot, mat_idx=3)
        for wx in (-1.15, -0.87, 0.87, 1.15):
            bm_add_cylinder_frustum(bm, tr((wx, ay, 0.52)), 0.52, 0.52, 0.24, segments=24, rot_euler=wheel_rot, mat_idx=2)
            bm_add_cylinder_frustum(bm, tr((wx * 1.01, ay, 0.52)), 0.30, 0.30, 0.26, segments=18, rot_euler=wheel_rot, mat_idx=3)

semi_placements = [
    (36.0, -75.0, 0.0),
    (46.0, -108.0, 0.0),
    (36.0, -145.0, 12.0),
    (-38.0, -82.0, 0.0),
    (-50.0, -118.0, -8.0),
    (58.0, -55.0, -90.0),
]
for sx, sy, s_ang in semi_placements:
    add_tesla_semi(bm_semis, sx, sy, s_ang)

semis_obj = finalize_mesh_object("Tesla_Semi_18Wheeler_Fleet", bm_semis, mat=mat_semi_white, smooth=False)
semis_obj.data.materials.append(mat_semi_glass)
semis_obj.data.materials.append(mat_tire_rubber)
semis_obj.data.materials.append(mat_wheel_rim)
semis_obj.data.materials.append(mat_headlight)

bm_crew = bmesh.new()
crew_coords = [
    (30.0, -45.0), (32.5, -46.5), (31.0, -52.0), (39.5, -68.0), (41.0, -70.0),
    (33.0, -92.0), (49.5, -102.0), (42.0, -125.0), (31.0, -135.0), (54.0, -62.0),
    (-30.0, -42.0), (-32.0, -44.0), (-34.5, -55.0), (-42.0, -72.0), (-33.0, -78.0),
    (-46.0, -95.0), (-38.0, -110.0), (-54.0, -112.0), (29.0, -18.0), (31.0, -15.0),
    (-29.5, -22.0), (-31.0, -19.0), (34.0, 12.0), (36.0, 15.0), (-32.0, 35.0),
    (68.0, -85.0), (70.0, -88.0), (-65.0, -65.0), (-67.0, -68.0), (28.5, -80.0),
]
for cx, cy in crew_coords:
    bm_add_cylinder_frustum(bm_crew, (cx, cy, 0.90), 0.24, 0.22, 1.80, segments=12, mat_idx=0)

finalize_mesh_object("Spaceport_Ground_Crew", bm_crew, mat=mat_hivis_orange, smooth=True)

sun_data = bpy.data.lights.new(name="Starbase_Sun", type='SUN')
sun_data.energy = 6.5
sun_data.color = (1.0, 0.96, 0.90)
sun_data.angle = math.radians(1.2)
sun_obj = bpy.data.objects.new(name="Starbase_Sun", object_data=sun_data)
bpy.context.collection.objects.link(sun_obj)
sun_obj.location = (250.0, -350.0, 320.0)
sun_obj.rotation_euler = (math.radians(58.0), math.radians(12.0), math.radians(38.0))

fill_data = bpy.data.lights.new(name="Sky_Fill_Light", type='SUN')
fill_data.energy = 1.6
fill_data.color = (0.65, 0.80, 1.0)
fill_obj = bpy.data.objects.new(name="Sky_Fill_Light", object_data=fill_data)
bpy.context.collection.objects.link(fill_obj)
fill_obj.location = (-250.0, -250.0, 180.0)
fill_obj.rotation_euler = (math.radians(70.0), 0.0, math.radians(-42.0))

cam_data = bpy.data.cameras.new(name="IMAX_Camera")
cam_data.lens = 26.0
cam_data.sensor_width = 36.0
cam_data.clip_start = 0.5
cam_data.clip_end = 6000.0
cam_obj = bpy.data.objects.new(name="IMAX_Camera", object_data=cam_data)
bpy.context.collection.objects.link(cam_obj)
cam_obj.location = (28.0, -345.0, 18.0)

target_point = Vector((-8.0, 0.0, 142.0))
direction = target_point - cam_obj.location
cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
scene.camera = cam_obj

for window in bpy.context.window_manager.windows:
    for area in window.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.clip_start = 0.5
                    space.clip_end = 6000.0
                    space.shading.type = 'MATERIAL'
                    space.overlay.show_overlays = False
                    if space.region_3d:
                        space.region_3d.view_perspective = 'CAMERA'
