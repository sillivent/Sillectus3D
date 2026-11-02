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
    bg_node.inputs[0].default_value = (0.52, 0.66, 0.82, 1.0)
    bg_node.inputs[1].default_value = 0.9

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
mat_cockpit_glass = create_principled_material("Shuttle_Cockpit_Glass", (0.04, 0.22, 0.42), metallic=0.25, roughness=0.05, emission_color=(0.20, 0.62, 1.0), emission_strength=0.85)
mat_cabin_glass = create_principled_material("Cabin_Deck_Glass", (0.20, 0.72, 1.0), metallic=0.1, roughness=0.1, emission_color=(0.25, 0.78, 1.0), emission_strength=4.0)
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
mat_road_yellow = create_principled_material("Apron_Yellow_Paint", (0.92, 0.68, 0.05), metallic=0.0, roughness=0.55)
mat_road_white = create_principled_material("Apron_White_Paint", (0.84, 0.85, 0.86), metallic=0.0, roughness=0.48)

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


# =============================================================================
# VERTICAL DATUM  (z = 0 is the concrete trucks and ground crew stand on)
# The OLM ring stays at pad level. Its columns reach the trench floor.
# Starship sits ON the booster. A single sleeve crosses that joint.
#
# Hull diameter is 30 m so a Tesla Semi with trailer (~24 m long, 2.6 m wide,
# 4 m tall) fits on the cargo deck with room at both ends and overhead.
# Of the vehicle stack, the booster is 60% and the ship is 40%.
#
# World degrees are atan2(y, x). 0° is +X.
#   +X    passenger tower, jetway, horseshoe cockpit, cabin decks, cargo door
#   ±Y    stabilizer fins. Tiles run from one fin hinge to the other (the -X half).
#   -X    ceramic belly, facing Mechazilla.
# The upper half of the ship is the flight deck plus nine decks under it:
# seven cabin decks, then engineering / life support, then the cargo bay.
# The lower half is tankage (no windows).
# =============================================================================
HULL_R = 15.0
BOOSTER_BASE_Z = 3.2
BOOSTER_HEIGHT = 192.0
SHIP_STACK_H = 128.0
BOOSTER_TOP_Z = BOOSTER_BASE_Z + BOOSTER_HEIGHT
SHIP_BASE_Z = BOOSTER_TOP_Z
SHIP_NOSE_H = 36.0
SHIP_CYL_H = SHIP_STACK_H - SHIP_NOSE_H
SHIP_NOSE_Z = SHIP_BASE_Z + SHIP_CYL_H
SHIP_TOP_Z = SHIP_NOSE_Z + SHIP_NOSE_H
SHIP_MID_Z = SHIP_BASE_Z + SHIP_STACK_H * 0.5
CARGO_Z_BOT = SHIP_MID_Z
CARGO_DOOR_H = 8.25
CARGO_Z_TOP = CARGO_Z_BOT + CARGO_DOOR_H
CARGO_DECK_Z = 0.5 * (CARGO_Z_BOT + CARGO_Z_TOP)
# Engineering stays on the original deck line, clear of the taller door.
ENG_DECK_Z = SHIP_MID_Z + 6.6 + 4.8
CABIN_DECK_Z = tuple(ENG_DECK_Z + 6.2 + i * 5.6 for i in range(7))
# Highest passenger deck that is still on the cylinder. Decks above this ride the ogive.
JETWAY_Z = CABIN_DECK_Z[1]
COCKPIT_PEAK_Z = CABIN_DECK_Z[-1] + 7.2
COCKPIT_Z_TOP = COCKPIT_PEAK_Z + 1.35
WINDWARD_CENTER = math.pi
BELLY_HALF_RAD = math.radians(90.0)
FLAP_HINGE_DEGS = (90.0, -90.0)
UMBILICAL_DEG = 78.0
# Old cluster: bell lip ~25.7. Park the lip just below the pad. Skirt stays at 3.2.
RAPTOR_Z_SHIFT = -1.2 - 25.7
ENG_K = HULL_R / 9.0

def orm(old_r):
    """Shift a mount radius that was drawn for a 9 m hull out to HULL_R."""
    return old_r + (HULL_R - 9.0)

# Pad lip. The OLM ring can bear on it. The 30 m hull stays clear of the walls.
TRENCH_EDGE = 27.0
SHIP_SEGS = 128

def v5_radius_at_z(z_world):
    """Von Karman ogive. Radius falls the whole way, and the tip steepens instead of wearing a bulb."""
    if z_world <= SHIP_NOSE_Z:
        return HULL_R
    z_local = z_world - SHIP_NOSE_Z
    if z_local >= SHIP_NOSE_H - 1e-4:
        return 0.0
    t = max(0.0, min(1.0, z_local / SHIP_NOSE_H))
    theta = math.acos(max(-1.0, min(1.0, 2.0 * t - 1.0)))
    r_vk = (HULL_R / math.sqrt(math.pi)) * math.sqrt(max(0.0, theta - 0.5 * math.sin(2.0 * theta)))
    return max(0.0, r_vk)

def ship_z_samples():
    """Cylinder rings, then ogive rings packed toward the round tip."""
    samples = []
    cyl_rings = 48
    for i in range(cyl_rings):
        samples.append(SHIP_BASE_Z + (i / cyl_rings) * SHIP_CYL_H)
    nose_rings = 40
    for i in range(nose_rings):
        u = i / nose_rings
        u_b = 1.0 - (1.0 - u) ** 1.35
        samples.append(SHIP_NOSE_Z + u_b * (SHIP_NOSE_H - 0.04))
    return samples

# @@PREAMBLE_END@@
# @@OBJECT: 01_launchpad_and_trench.py
bm_pad = bmesh.new()
pad_x = TRENCH_EDGE + 110.0
bm_add_box(bm_pad, (-pad_x, 0.0, -12.5), (220.0, 560.0, 25.0), mat_idx=0)
bm_add_box(bm_pad, (pad_x, 0.0, -12.5), (220.0, 560.0, 25.0), mat_idx=0)
bm_add_box(bm_pad, (-(TRENCH_EDGE + 0.9), 0.0, 0.45), (1.8, 560.0, 0.9), mat_idx=0)
bm_add_box(bm_pad, (TRENCH_EDGE + 0.9, 0.0, 0.45), (1.8, 560.0, 0.9), mat_idx=0)
bm_add_box(bm_pad, (-(TRENCH_EDGE - 0.2), 0.0, -12.5), (0.9, 560.0, 25.0), mat_idx=1)
bm_add_box(bm_pad, (TRENCH_EDGE - 0.2, 0.0, -12.5), (0.9, 560.0, 25.0), mat_idx=1)
for step in range(4):
    z_step = -2.2 - step * 5.8
    x_off = (TRENCH_EDGE - 0.6) - step * 0.55
    bm_add_box(bm_pad, (-x_off, 0.0, z_step), (1.2, 560.0, 5.8), mat_idx=1)
    bm_add_box(bm_pad, (x_off, 0.0, z_step), (1.2, 560.0, 5.8), mat_idx=1)
for rib_y in range(-260, 265, 16):
    bm_add_box(bm_pad, (-(TRENCH_EDGE - 1.4), float(rib_y), -12.5), (0.9, 1.2, 24.8), mat_idx=1)
    bm_add_box(bm_pad, (TRENCH_EDGE - 1.4, float(rib_y), -12.5), (0.9, 1.2, 24.8), mat_idx=1)
bm_add_box(bm_pad, (0.0, 0.0, -26.5), (TRENCH_EDGE * 2.0 - 4.0, 560.0, 3.0), mat_idx=1)
for side in (-1.0, 1.0):
    bm_add_box(bm_pad, (side * (TRENCH_EDGE + 2.4), 0.0, 0.04), (0.20, 460.0, 0.05), mat_idx=3)
    for lane in (9.0, 18.0, 28.0):
        bm_add_box(bm_pad, (side * (TRENCH_EDGE + lane), 0.0, 0.035), (0.16, 400.0, 0.04), mat_idx=2)
    for jy in range(-220, 241, 40):
        bm_add_box(bm_pad, (side * (TRENCH_EDGE + 58.0), float(jy), 0.03), (108.0, 0.14, 0.035), mat_idx=1)
for stall in range(72, 164, 4):
    bm_add_box(bm_pad, (float(stall), -54.0, 0.04), (0.12, 14.0, 0.04), mat_idx=3)
for stripe in range(70, 156, 3):
    bm_add_box(bm_pad, (float(stripe), -40.0, 0.045), (0.55, 3.6, 0.04), mat_idx=3)
pad_obj = finalize_mesh_object("Launchpad_And_Flame_Trench", bm_pad, mat=mat_concrete, smooth=False)
pad_obj.data.materials.append(mat_trench_char)
pad_obj.data.materials.append(mat_road_yellow)
pad_obj.data.materials.append(mat_road_white)

# @@OBJECT: 02_flame_deflector.py
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
    wall_x = TRENCH_EDGE - 1.6
    bm_add_cylinder_frustum(bm_defl, (-wall_x, ny, -4.5), 0.42, 0.30, 3.2, segments=12, rot_euler=(0.0, math.radians(75), 0.0))
    bm_add_cylinder_frustum(bm_defl, (wall_x, ny, -4.5), 0.42, 0.30, 3.2, segments=12, rot_euler=(0.0, math.radians(-75), 0.0))
finalize_mesh_object("Steel_Flame_Deflector", bm_defl, mat=mat_tower_steel, smooth=False)

# @@OBJECT: 03_orbital_launch_mount.py
bm_olm = bmesh.new()
olm_z_bot = 0.40
olm_z_top = 4.20
olm_r_in = HULL_R + 0.55
olm_r_mid = HULL_R + 5.4
olm_r_out = TRENCH_EDGE + 1.15
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

leg_r = HULL_R + 6.2
leg_top = olm_z_top - 0.15
leg_bot = -24.55
leg_h = leg_top - leg_bot
leg_zc = 0.5 * (leg_top + leg_bot)
for i in range(6):
    ang = (i * math.pi / 3.0) + (math.pi / 6.0)
    lx = math.cos(ang) * leg_r
    ly = math.sin(ang) * leg_r
    bm_add_cylinder_frustum(bm_olm, (lx, ly, leg_zc), 1.70, 1.45, leg_h, segments=24)
    bm_add_cylinder_frustum(bm_olm, (lx * 0.86, ly * 0.86, leg_zc), 0.62, 0.55, leg_h, segments=14)
    bm_add_box(bm_olm, (lx, ly, leg_bot + 0.35), (4.6, 4.6, 1.15), rot_euler=(0.0, 0.0, ang))
    bm_add_box(bm_olm, (lx, ly, -25.05), (6.2, 6.2, 0.7), rot_euler=(0.0, 0.0, ang))
    wall_x = -TRENCH_EDGE if lx < 0 else TRENCH_EDGE
    bm_add_strut(bm_olm, (lx, ly, 3.6), (wall_x, ly * 0.55, 0.4), 1.05)
    bm_add_strut(bm_olm, (lx, ly, -6.0), (wall_x, ly * 0.35, -16.0), 0.85)
    bm_add_strut(bm_olm, (lx, ly, leg_bot + 1.2), (lx * 0.55, ly * 0.55, leg_bot + 1.2), 0.70)

for i in range(48):
    ang = (2.0 * math.pi * i) / 48.0
    ca, sa = math.cos(ang), math.sin(ang)
    cr = HULL_R + 0.48
    bm_add_box(bm_olm, (ca * cr, sa * cr, 3.55), (1.15, 0.85, 1.55), rot_euler=(0.0, 0.0, ang))
    bm_add_box(bm_olm, (ca * (HULL_R + 0.15), sa * (HULL_R + 0.15), 2.85), (0.62, 0.55, 0.95), rot_euler=(0.0, 0.0, ang))
    bm_add_cylinder_frustum(bm_olm, (ca * (HULL_R + 1.3), sa * (HULL_R + 1.3), 3.3), 0.18, 0.18, 1.2, segments=10, rot_euler=(0.0, math.radians(65), ang))
    bm_add_strut(bm_olm, (ca * olm_r_out, sa * olm_r_out, 1.6), (ca * (olm_r_out - 1.1), sa * (olm_r_out - 1.1), 0.45), 0.28)
    bm_add_strut(bm_olm, (ca * olm_r_out, sa * olm_r_out, 1.6), (ca * (HULL_R + 0.5), sa * (HULL_R + 0.5), 0.55), 0.22)
    bm_add_strut(bm_olm, (ca * olm_r_out, sa * olm_r_out, 3.55), (ca * (HULL_R + 1.5), sa * (HULL_R + 1.5), 4.15), 0.20)
    bm_add_box(bm_olm, (ca * (olm_r_mid + 1.2), sa * (olm_r_mid + 1.2), 2.5), (0.55, 0.42, 0.75), rot_euler=(0.0, 0.0, ang))

for i in range(48):
    ang = (2.0 * math.pi * i) / 48.0
    nx = math.cos(ang) * (HULL_R - 0.85)
    ny = math.sin(ang) * (HULL_R - 0.85)
    bm_add_cylinder_frustum(bm_olm, (nx, ny, 2.2), 0.22, 0.10, 1.5, segments=10, rot_euler=(0.0, math.radians(-50), ang))

for z_m, r_m, rad_tube in (
    (1.5, olm_r_out - 0.15, 0.62),
    (3.4, olm_r_out - 0.15, 0.40),
    (0.9, HULL_R + 0.9, 0.48),
    (2.4, olm_r_mid + 1.6, 0.32),
):
    for i in range(olm_segs):
        a0 = (2.0 * math.pi * i) / olm_segs
        a1 = (2.0 * math.pi * (i + 1)) / olm_segs
        p0 = (math.cos(a0) * r_m, math.sin(a0) * r_m, z_m)
        p1 = (math.cos(a1) * r_m, math.sin(a1) * r_m, z_m)
        bm_add_strut(bm_olm, p0, p1, rad_tube * 1.35)

rail_r = olm_r_out + 0.85
for i in range(64):
    a0 = (2.0 * math.pi * i) / 64.0
    a1 = (2.0 * math.pi * (i + 1)) / 64.0
    bm_add_strut(bm_olm, (math.cos(a0) * rail_r, math.sin(a0) * rail_r, 2.3), (math.cos(a1) * rail_r, math.sin(a1) * rail_r, 2.3), 0.55)
    if i % 2 == 0:
        bm_add_strut(bm_olm, (math.cos(a0) * (rail_r + 0.35), math.sin(a0) * (rail_r + 0.35), 2.3), (math.cos(a0) * (rail_r + 0.35), math.sin(a0) * (rail_r + 0.35), 3.6), 0.12)
    bm_add_strut(bm_olm, (math.cos(a0) * (rail_r + 0.35), math.sin(a0) * (rail_r + 0.35), 3.6), (math.cos(a1) * (rail_r + 0.35), math.sin(a1) * (rail_r + 0.35), 3.6), 0.10)

bm_add_box(bm_olm, (-(HULL_R + 4.8), -2.6, 2.6), (3.2, 3.8, 2.4), rot_euler=(0.0, math.radians(8), 0.0))
finalize_mesh_object("Orbital_Launch_Mount", bm_olm, mat=mat_tower_steel, smooth=False)

# @@OBJECT: 04_super_heavy_booster.py
bm_booster = bmesh.new()
sh_z_base = BOOSTER_BASE_Z
sh_height = BOOSTER_HEIGHT
sh_radius = HULL_R
sh_segs = 128
sh_rings = 48

b_grid = []
for r_idx in range(sh_rings + 1):
    z = sh_z_base + (r_idx / sh_rings) * sh_height
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

for z_ring in range(int(sh_z_base) + 8, int(BOOSTER_TOP_Z) - 2, 5):
    bm_add_cylinder_frustum(bm_booster, (0.0, 0.0, float(z_ring)), HULL_R + 0.04, HULL_R + 0.04, 0.22, segments=96, cap_ends=False, mat_idx=0)

for chine_ang in (math.radians(-95), math.radians(95)):
    cx = math.cos(chine_ang) * (HULL_R - 0.05)
    cy = math.sin(chine_ang) * (HULL_R - 0.05)
    bm_add_box(bm_booster, (cx, cy, sh_z_base + sh_height * 0.5), (0.95, 1.35, sh_height - 18.0), rot_euler=(0.0, 0.0, chine_ang), mat_idx=1)

# One sleeve crosses the joint onto the ship. No floating rings, no center pole.
joint_z = BOOSTER_TOP_Z
bm_add_cylinder_frustum(bm_booster, (0.0, 0.0, joint_z), HULL_R + 0.05, HULL_R + 0.05, 2.2, segments=96, cap_ends=False, mat_idx=1)
bm_add_cylinder_frustum(bm_booster, (0.0, 0.0, joint_z - 0.15), HULL_R - 0.45, HULL_R - 0.45, 1.4, segments=80, cap_ends=False, mat_idx=1)
for i in range(48):
    ang = (2.0 * math.pi * i) / 48.0
    sx = math.cos(ang) * (HULL_R + 0.12)
    sy = math.sin(ang) * (HULL_R + 0.12)
    bm_add_box(bm_booster, (sx, sy, joint_z), (0.28, 0.18, 2.0), rot_euler=(0.0, 0.0, ang), mat_idx=1)

booster_obj = finalize_mesh_object("Super_Heavy_Booster", bm_booster, mat=mat_titanium, smooth=True)
booster_obj.data.materials.append(mat_titanium_dark)

# @@OBJECT: 05_raptor_engines.py
bm_raptors = bmesh.new()
raptor_rings = [
    (0.0, 3, 1.85 * ENG_K),
    (0.0, 10, 4.55 * ENG_K),
    (0.15, 20, 7.45 * ENG_K),
]
for phase, count, ring_r in raptor_rings:
    for i in range(count):
        ang = phase + (2.0 * math.pi * i) / count
        rx = math.cos(ang) * ring_r
        ry = math.sin(ang) * ring_r
        bm_add_cylinder_frustum(bm_raptors, (rx, ry, 27.3 + RAPTOR_Z_SHIFT), 1.12, 0.34, 3.2, segments=28, cap_ends=False, mat_idx=0)
        bm_add_cylinder_frustum(bm_raptors, (rx, ry, 25.85 + RAPTOR_Z_SHIFT), 1.19, 1.13, 0.45, segments=28, cap_ends=True, mat_idx=0)
        bm_add_cylinder_frustum(bm_raptors, (rx, ry, 26.25 + RAPTOR_Z_SHIFT), 0.94, 0.94, 1.1, segments=24, cap_ends=True, mat_idx=0)
        for h_z, h_r in ((26.4, 1.09), (26.75, 1.02), (27.1, 0.96), (27.5, 0.88), (27.9, 0.80), (28.5, 0.62)):
            bm_add_cylinder_frustum(bm_raptors, (rx, ry, h_z + RAPTOR_Z_SHIFT), h_r, h_r, 0.10, segments=24, cap_ends=True, mat_idx=1)
        bm_add_cylinder_frustum(bm_raptors, (rx, ry, 29.55 + RAPTOR_Z_SHIFT), 0.48, 0.56, 1.4, segments=20, cap_ends=True, mat_idx=1)
        for p_idx in range(4):
            p_ang = ang + p_idx * (math.pi / 2.0)
            px = rx + math.cos(p_ang) * 0.56
            py = ry + math.sin(p_ang) * 0.56
            bm_add_cylinder_frustum(bm_raptors, (px, py, 29.4 + RAPTOR_Z_SHIFT), 0.22, 0.18, 1.05, segments=12, cap_ends=True, mat_idx=1)
            p_top = (px, py, 29.88 + RAPTOR_Z_SHIFT)
            p_mid = (rx + math.cos(p_ang) * 0.88, ry + math.sin(p_ang) * 0.88, 28.45 + RAPTOR_Z_SHIFT)
            p_lip = (rx + math.cos(p_ang) * 1.08, ry + math.sin(p_ang) * 1.08, 26.35 + RAPTOR_Z_SHIFT)
            bm_add_strut(bm_raptors, p_top, p_mid, 0.11, mat_idx=1)
            bm_add_strut(bm_raptors, p_mid, p_lip, 0.09, mat_idx=1)
            bm_add_box(bm_raptors, p_mid, (0.16, 0.16, 0.16), rot_euler=(0.0, 0.0, p_ang), mat_idx=0)
            next_ang = p_ang + (math.pi / 2.0)
            p_next = (rx + math.cos(next_ang) * 0.88, ry + math.sin(next_ang) * 0.88, 28.45 + RAPTOR_Z_SHIFT)
            bm_add_strut(bm_raptors, p_mid, p_next, 0.07, mat_idx=1)
        g_ang = ang + math.radians(45.0)
        bm_add_strut(bm_raptors, (rx + math.cos(g_ang) * 0.3, ry + math.sin(g_ang) * 0.3, 30.2 + RAPTOR_Z_SHIFT), (rx + math.cos(g_ang) * 0.92, ry + math.sin(g_ang) * 0.92, 27.8 + RAPTOR_Z_SHIFT), 0.10, mat_idx=0)

raptors_obj = finalize_mesh_object("Super_Heavy_33_Raptors", bm_raptors, mat=mat_engine_metal, smooth=True)
raptors_obj.data.materials.append(mat_copper_turbopump)

# @@OBJECT: 06_grid_fins.py
bm_gf = bmesh.new()
gf_angles = [math.radians(38), math.radians(142), math.radians(218), math.radians(322)]
gf_z = BOOSTER_TOP_Z - 8.0
gf_span = 7.6 * ENG_K
gf_chord = 5.4 * ENG_K * 0.82
gf_depth = 0.85

for ang in gf_angles:
    rot_m = Euler((0.0, 0.0, ang), 'XYZ').to_matrix()
    mount_pos = rot_m @ Vector((HULL_R + 0.40, 0.0, gf_z))
    bm_add_box(bm_gf, mount_pos, (1.7, 2.4, 2.0), rot_euler=(0.0, 0.0, ang), mat_idx=0)
    r_start = HULL_R + 0.90
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

# @@OBJECT: 07_starship_hull.py
bm_v5 = bmesh.new()
z_samples = ship_z_samples()
v5_rings_verts = []
for z_val in z_samples:
    rad = v5_radius_at_z(z_val)
    ring = []
    for s_idx in range(SHIP_SEGS):
        ang = (2.0 * math.pi * s_idx) / SHIP_SEGS
        ring.append(bm_v5.verts.new((math.cos(ang) * rad, math.sin(ang) * rad, z_val)))
    v5_rings_verts.append(ring)

for r_idx in range(len(v5_rings_verts) - 1):
    for s_idx in range(SHIP_SEGS):
        ns = (s_idx + 1) % SHIP_SEGS
        bm_v5.faces.new((v5_rings_verts[r_idx][s_idx], v5_rings_verts[r_idx][ns], v5_rings_verts[r_idx + 1][ns], v5_rings_verts[r_idx + 1][s_idx]))

tip = bm_v5.verts.new((0.0, 0.0, SHIP_TOP_Z))
top_ring = v5_rings_verts[-1]
for s_idx in range(SHIP_SEGS):
    ns = (s_idx + 1) % SHIP_SEGS
    bm_v5.faces.new((top_ring[s_idx], top_ring[ns], tip))

bm_v5.faces.new(list(reversed(v5_rings_verts[0])))
finalize_mesh_object("Starship_V5_Hull", bm_v5, mat=mat_titanium, smooth=True)

# @@OBJECT: 08_heat_shield.py
bm_shield = bmesh.new()
z_samples = ship_z_samples()
hs_rings = []
for z_val in z_samples:
    rad = v5_radius_at_z(z_val) + 0.03
    ring = []
    for s_idx in range(SHIP_SEGS):
        ang = (2.0 * math.pi * s_idx) / SHIP_SEGS
        ring.append(bm_shield.verts.new((math.cos(ang) * rad, math.sin(ang) * rad, z_val)))
    hs_rings.append(ring)

def _on_shield(z_c, ang):
    """Above the cockpit the whole nose is tiled. Below that, tiles run fin to fin across -X."""
    if z_c > COCKPIT_Z_TOP:
        return True
    belly_delta = abs((ang - WINDWARD_CENTER + math.pi) % (2.0 * math.pi) - math.pi)
    return belly_delta < BELLY_HALF_RAD

for r_idx in range(len(hs_rings) - 1):
    for s_idx in range(SHIP_SEGS):
        ns = (s_idx + 1) % SHIP_SEGS
        v00 = hs_rings[r_idx][s_idx]
        v01 = hs_rings[r_idx][ns]
        v11 = hs_rings[r_idx + 1][ns]
        v10 = hs_rings[r_idx + 1][s_idx]
        center = (v00.co + v01.co + v11.co + v10.co) * 0.25
        ang = math.atan2(center.y, center.x)
        if _on_shield(center.z, ang):
            f = bm_shield.faces.new((v00, v01, v11, v10))
            f.material_index = 1

tip_s = bm_shield.verts.new((0.0, 0.0, SHIP_TOP_Z + 0.03))
top_s = hs_rings[-1]
for s_idx in range(SHIP_SEGS):
    ns = (s_idx + 1) % SHIP_SEGS
    f = bm_shield.faces.new((top_s[s_idx], top_s[ns], tip_s))
    f.material_index = 0

unused_verts = [v for v in bm_shield.verts if not v.link_faces]
bmesh.ops.delete(bm_shield, geom=unused_verts, context='VERTS')

def _min_edge(face):
    vs = face.verts
    best = 1e9
    for i in range(len(vs)):
        best = min(best, (vs[i].co - vs[(i + 1) % len(vs)].co).length)
    return best

quad_faces = [f for f in bm_shield.faces if len(f.verts) == 4 and _min_edge(f) > 0.20]
quad_set = set(quad_faces)
for f in bm_shield.faces:
    if f not in quad_set and len(f.verts) >= 3:
        f.material_index = 0
if quad_faces:
    bmesh.ops.inset_individual(bm_shield, faces=quad_faces, thickness=0.055, depth=0.035)
    for f in quad_faces:
        f.material_index = 0

bmesh.ops.solidify(bm_shield, geom=list(bm_shield.faces), thickness=0.12)
shield_obj = finalize_mesh_object("Starship_V5_Physical_Heat_Shield", bm_shield, mat=mat_heat_tiles, smooth=False)
shield_obj.data.materials.append(mat_heat_grout)

# @@OBJECT: 09_stabilizer_fins.py
bm_flaps = bmesh.new()

def build_vertical_flap(bm, hinge_deg, z_bot_root, z_top_root, z_bot_tip, z_top_tip, span_out, add_hinge=True):
    hinge = math.radians(hinge_deg)
    ox, oy = math.cos(hinge), math.sin(hinge)
    tx, ty = -math.sin(hinge), math.cos(hinge)
    stations = 12
    prof_pts = 8
    rings = []
    r_tip_ref = v5_radius_at_z(z_bot_root) + span_out
    for i in range(stations + 1):
        u = i / stations
        z_b = z_bot_root * (1.0 - u) + z_bot_tip * u
        z_t = z_top_root * (1.0 - u) + z_top_tip * u
        half_thick = 0.72 * (1.0 - 0.55 * u)
        ring = []
        for k in range(prof_pts):
            t_ang = (2.0 * math.pi * k) / prof_pts
            z_curr = 0.5 * (z_b + z_t) + 0.5 * (z_t - z_b) * math.cos(t_ang)
            thick = half_thick * math.sin(t_ang)
            r_hull = max(1.2, v5_radius_at_z(z_curr) - 0.15)
            r_curr = r_hull * (1.0 - u) + r_tip_ref * u
            ring.append(bm.verts.new((ox * r_curr + tx * thick, oy * r_curr + ty * thick, z_curr)))
        rings.append(ring)
    for i in range(stations):
        for k in range(prof_pts):
            nk = (k + 1) % prof_pts
            bm.faces.new((rings[i][k], rings[i][nk], rings[i + 1][nk], rings[i + 1][k]))
    bm.faces.new(rings[-1])
    if add_hinge:
        z_hinge_mid = 0.5 * (z_bot_root + z_top_root)
        r_hinge = max(1.2, v5_radius_at_z(z_hinge_mid) - 0.05)
        bm_add_cylinder_frustum(
            bm, (ox * r_hinge, oy * r_hinge, z_hinge_mid),
            0.52, 0.46, (z_top_root - z_bot_root) * 0.90, segments=16,
        )

aft_span = 8.0 * ENG_K * 1.25
fwd_span = 4.0 * ENG_K * 1.25
aft0, aft1 = SHIP_BASE_Z + 4.0, SHIP_BASE_Z + 39.0
fwd0, fwd1 = SHIP_NOSE_Z + 2.0, SHIP_NOSE_Z + 18.0
for hinge_deg in FLAP_HINGE_DEGS:
    build_vertical_flap(bm_flaps, hinge_deg, aft0, aft1, aft0 - 1.0, aft0 + 17.0, aft_span, add_hinge=True)
    build_vertical_flap(bm_flaps, hinge_deg, fwd0, fwd1, fwd0 - 0.4, fwd0 + 10.6, fwd_span, add_hinge=False)
finalize_mesh_object("Starship_V5_Aerodynamic_Stabilizers", bm_flaps, mat=mat_heat_tiles, smooth=True)

# @@OBJECT: 10_windows.py
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
    """Horizontal oval: a polar disk on the hull, wider than it is tall. Not a square n-gon."""
    n_ang = 16
    n_rad = 4
    for r_off, dw, dh, m_idx in (
        (0.045, half_w_deg + 0.55, half_h_z + 0.08, mat_frame_idx),
        (0.12, half_w_deg, half_h_z, mat_glass_idx),
    ):
        c_ang = math.radians(center_deg)
        c_rad = v5_radius_at_z(z_center) + r_off
        center_v = bm.verts.new((math.cos(c_ang) * c_rad, math.sin(c_ang) * c_rad, z_center))
        rings = []
        for ir in range(1, n_rad + 1):
            rf = ir / n_rad
            ring = []
            for ia in range(n_ang):
                theta = (2.0 * math.pi * ia) / n_ang
                d_curr = center_deg + dw * rf * math.cos(theta)
                z_curr = z_center + dh * rf * math.sin(theta)
                rad = v5_radius_at_z(z_curr) + r_off
                ang = math.radians(d_curr)
                ring.append(bm.verts.new((math.cos(ang) * rad, math.sin(ang) * rad, z_curr)))
            rings.append(ring)
        for ia in range(n_ang):
            nia = (ia + 1) % n_ang
            f = bm.faces.new((center_v, rings[0][ia], rings[0][nia]))
            f.material_index = m_idx
        for ir in range(n_rad - 1):
            for ia in range(n_ang):
                nia = (ia + 1) % n_ang
                f = bm.faces.new((rings[ir][ia], rings[ir][nia], rings[ir + 1][nia], rings[ir + 1][ia]))
                f.material_index = m_idx

def add_horseshoe_cockpit(bm, peak):
    """One wraparound windshield. Tallest on the centerline, shorter as it wraps aft. Mullions follow the hull."""
    half_deg = 64.0

    def shell(r_off, z_pad, ang_pad, mat_idx, steps_u, steps_v):
        grid = []
        for iv in range(steps_v + 1):
            v = iv / steps_v
            row = []
            for iu in range(steps_u + 1):
                s = -1.0 + 2.0 * (iu / steps_u)
                ang = math.radians(s * (half_deg + ang_pad))
                crown = peak + 1.05 + z_pad - 1.15 * (s * s)
                sill = peak - 2.15 - z_pad + 0.55 * (s * s)
                z = sill * (1.0 - v) + crown * v
                rad = v5_radius_at_z(z) + r_off
                row.append(bm.verts.new((math.cos(ang) * rad, math.sin(ang) * rad, z)))
            grid.append(row)
        for iv in range(steps_v):
            for iu in range(steps_u):
                f = bm.faces.new((grid[iv][iu], grid[iv][iu + 1], grid[iv + 1][iu + 1], grid[iv + 1][iu]))
                f.material_index = mat_idx

    shell(0.035, 0.16, 1.5, 2, 48, 10)
    shell(0.08, 0.0, 0.0, 0, 48, 10)
    for s_m in (-0.76, -0.46, -0.16, 0.16, 0.46, 0.76):
        grid = []
        half = 0.016
        for iv in range(7):
            v = iv / 6.0
            row = []
            for s in (s_m - half, s_m + half):
                ang = math.radians(s * half_deg)
                crown = peak + 1.02 - 1.15 * (s * s)
                sill = peak - 2.12 + 0.55 * (s * s)
                z = sill * (1.0 - v) + crown * v
                rad = v5_radius_at_z(z) + 0.13
                row.append(bm.verts.new((math.cos(ang) * rad, math.sin(ang) * rad, z)))
            grid.append(row)
        for iv in range(6):
            f = bm.faces.new((grid[iv][0], grid[iv][1], grid[iv + 1][1], grid[iv + 1][0]))
            f.material_index = 2

add_horseshoe_cockpit(bm_windows, COCKPIT_PEAK_Z)

for deck_z in CABIN_DECK_Z:
    for p_deg in (-24.0, -12.0, 0.0, 12.0, 24.0):
        add_horizontal_oval_window(bm_windows, p_deg, deck_z, half_w_deg=4.0, half_h_z=0.62, mat_glass_idx=1, mat_frame_idx=2)
for p_deg in (-18.0, -9.0, 0.0, 9.0, 18.0):
    add_horizontal_oval_window(bm_windows, p_deg, ENG_DECK_Z, half_w_deg=2.1, half_h_z=0.32, mat_glass_idx=1, mat_frame_idx=2)

win_obj = finalize_mesh_object("Starship_V5_Cockpit_And_Cabin_Windows", bm_windows, mat=mat_cockpit_glass, smooth=True)
win_obj.data.materials.append(mat_cabin_glass)
win_obj.data.materials.append(mat_titanium_dark)

# @@OBJECT: 11_cargo_door.py
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

cd_z_bot = CARGO_Z_BOT
cd_z_top = CARGO_Z_TOP
cd_deg_min = -32.0
cd_deg_max = 32.0
add_curved_hull_patch(bm_cargo, cd_z_bot - 0.35, cd_z_top + 0.35, cd_deg_min - 1.6, cd_deg_max + 1.6, 0.05, 24, 10, mat_idx=1)
door_faces = add_curved_hull_patch(bm_cargo, cd_z_bot, cd_z_top, cd_deg_min, cd_deg_max, 0.09, 22, 8, mat_idx=0)
bmesh.ops.solidify(bm_cargo, geom=door_faces, thickness=0.14)

for d_split in (-10.6, 0.0, 10.6):
    add_curved_hull_patch(bm_cargo, cd_z_bot, cd_z_top, d_split - 0.32, d_split + 0.32, 0.17, 2, 8, mat_idx=1)
door_h = cd_z_top - cd_z_bot
for frac in (0.16, 0.33, 0.50, 0.67, 0.84):
    z_seam = cd_z_bot + door_h * frac
    add_curved_hull_patch(bm_cargo, z_seam - 0.07, z_seam + 0.07, cd_deg_min, cd_deg_max, 0.17, 20, 1, mat_idx=1)

for frac in (0.10, 0.28, 0.46, 0.64, 0.82):
    z_hinge = cd_z_bot + door_h * frac
    for d_hinge in (cd_deg_min - 0.9, cd_deg_max + 0.9):
        ang_h = math.radians(d_hinge)
        r_h = v5_radius_at_z(z_hinge) + 0.12
        bm_add_box(bm_cargo, (math.cos(ang_h) * r_h, math.sin(ang_h) * r_h, z_hinge), (0.32, 0.48, 0.55), rot_euler=(0.0, 0.0, ang_h), mat_idx=1)

for frac in (0.18, 0.50, 0.78):
    z_latch = cd_z_bot + door_h * frac
    r_l = v5_radius_at_z(z_latch) + 0.16
    bm_add_box(bm_cargo, (r_l, 0.0, z_latch), (0.22, 0.70, 0.32), mat_idx=1)

cargo_obj = finalize_mesh_object("Starship_V5_Cargo_Bay_Door", bm_cargo, mat=mat_titanium, smooth=False)
cargo_obj.data.materials.append(mat_titanium_dark)

# @@OBJECT: 12_mechazilla_tower.py
bm_tower = bmesh.new()
tw_cx, tw_cy = -40.0, 0.0
tw_half = 10.0
tw_height = SHIP_TOP_Z + 28.0
tw_bays = max(64, int(tw_height / 4.8))
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

# Chopsticks sit above the aft flaps and cradle the ship from ±Y.
# Arms stay outside the hull. Catch shoes reach in to the steel, not the tiles.
car_z = SHIP_BASE_Z + 46.0
arm_y_abs = HULL_R + 3.1
x_face = tw_cx + tw_half
x_start = x_face + 0.8
x_end = 6.0
bm_add_box(bm_tower, (x_face - 1.4, 0.0, car_z), (7.0, arm_y_abs * 2.0 + 10.0, 14.0), mat_idx=0)
bm_add_box(bm_tower, (x_face + 2.2, 0.0, car_z + 6.2), (4.0, arm_y_abs * 2.0 + 6.0, 2.2), mat_idx=0)
for arm_y in (-arm_y_abs, arm_y_abs):
    arm_bays = 11
    dx_bay = (x_end - x_start) / arm_bays
    rail = 1.85
    for ab in range(arm_bays):
        ax0 = x_start + ab * dx_bay
        ax1 = ax0 + dx_bay
        h0 = 6.4 * (1.0 - 0.32 * (ab / arm_bays))
        h1 = 6.4 * (1.0 - 0.32 * ((ab + 1) / arm_bays))
        for y_rail in (arm_y - rail, arm_y + rail):
            bm_add_strut(bm_tower, (ax0, y_rail, car_z + h0 * 0.5), (ax1, y_rail, car_z + h1 * 0.5), 0.62, mat_idx=0)
            bm_add_strut(bm_tower, (ax0, y_rail, car_z - h0 * 0.5), (ax1, y_rail, car_z - h1 * 0.5), 0.62, mat_idx=0)
            bm_add_strut(bm_tower, (ax0, y_rail, car_z - h0 * 0.5), (ax0, y_rail, car_z + h0 * 0.5), 0.48, mat_idx=0)
            bm_add_strut(bm_tower, (ax0, y_rail, car_z - h0 * 0.5), (ax1, y_rail, car_z + h1 * 0.5), 0.42, mat_idx=0)
            bm_add_strut(bm_tower, (ax0, y_rail, car_z + h0 * 0.5), (ax1, y_rail, car_z - h1 * 0.5), 0.42, mat_idx=0)
        bm_add_strut(bm_tower, (ax1, arm_y - rail, car_z + h1 * 0.5), (ax1, arm_y + rail, car_z + h1 * 0.5), 0.50, mat_idx=0)
        bm_add_strut(bm_tower, (ax1, arm_y - rail, car_z - h1 * 0.5), (ax1, arm_y + rail, car_z - h1 * 0.5), 0.50, mat_idx=0)
        bm_add_strut(bm_tower, (ax1, arm_y - rail, car_z - h1 * 0.5), (ax1, arm_y + rail, car_z + h1 * 0.5), 0.36, mat_idx=0)
    shoe_y = math.copysign(HULL_R + 0.50, arm_y)
    shoe_x = 0.4
    bm_add_box(bm_tower, (shoe_x, 0.5 * (arm_y + shoe_y), car_z), (8.0, abs(arm_y - shoe_y), 3.4), mat_idx=0)
    bm_add_box(bm_tower, (shoe_x, shoe_y, car_z), (6.4, 1.35, 9.0), mat_idx=0)
    for cable_x in (x_start + 1.5, 0.5 * (x_start + x_end), x_end - 1.2):
        bm_add_strut(bm_tower, (cable_x, arm_y, car_z + 7.4), (cable_x, arm_y, car_z + 3.2), 0.16, mat_idx=0)

def _truss_segment(bm, p0, p1, half_w, half_h):
    x0, y0, z0 = p0
    x1, y1, z1 = p1
    dx, dy = x1 - x0, y1 - y0
    span = math.sqrt(dx * dx + dy * dy) or 1.0
    px, py = -dy / span, dx / span
    bays = max(2, int(span / 3.2))
    for b in range(bays):
        u0 = b / bays
        u1 = (b + 1) / bays
        ax0, ay0 = x0 + dx * u0, y0 + dy * u0
        ax1, ay1 = x0 + dx * u1, y0 + dy * u1
        az0 = z0 + (z1 - z0) * u0
        az1 = z0 + (z1 - z0) * u1
        for s in (-half_w, half_w):
            ox, oy = px * s, py * s
            bm_add_strut(bm, (ax0 + ox, ay0 + oy, az0 - half_h), (ax1 + ox, ay1 + oy, az1 - half_h), 0.32, mat_idx=0)
            bm_add_strut(bm, (ax0 + ox, ay0 + oy, az0 + half_h), (ax1 + ox, ay1 + oy, az1 + half_h), 0.32, mat_idx=0)
            bm_add_strut(bm, (ax0 + ox, ay0 + oy, az0 - half_h), (ax0 + ox, ay0 + oy, az0 + half_h), 0.26, mat_idx=0)
            bm_add_strut(bm, (ax0 + ox, ay0 + oy, az0 - half_h), (ax1 + ox, ay1 + oy, az1 + half_h), 0.22, mat_idx=0)
        bm_add_strut(bm, (ax1 - px * half_w, ay1 - py * half_w, az1 + half_h), (ax1 + px * half_w, ay1 + py * half_w, az1 + half_h), 0.24, mat_idx=0)
        bm_add_strut(bm, (ax1 - px * half_w, ay1 - py * half_w, az1 - half_h), (ax1 + px * half_w, ay1 + py * half_w, az1 - half_h), 0.24, mat_idx=0)

def build_umbilical_dogleg(bm, z_arm):
    """Stay outside the cylinder, then elbow onto the stainless side. Do not cross the tiles."""
    ang = math.radians(UMBILICAL_DEG)
    qd_r = HULL_R + 0.40
    qd_x = math.cos(ang) * qd_r
    qd_y = math.sin(ang) * qd_r
    y_out = math.copysign(HULL_R + 3.6, qd_y)
    x_face = tw_cx + tw_half
    pts = (
        (x_face, 0.0, z_arm),
        (x_face + 3.0, y_out, z_arm),
        (qd_x, y_out, z_arm),
        (qd_x, qd_y, z_arm),
    )
    bm_add_box(bm, (x_face - 0.8, 0.0, z_arm), (2.6, 4.0, 5.4), mat_idx=0)
    for i in range(len(pts) - 1):
        _truss_segment(bm, pts[i], pts[i + 1], 0.85, 1.05)
    bm_add_box(bm, (qd_x, qd_y, z_arm), (1.15, 2.6, 3.3), rot_euler=(0.0, 0.0, ang), mat_idx=0)
    for pz in (-0.42, 0.42):
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]
            bm_add_strut(bm, (a[0], a[1], a[2] + pz), (b[0], b[1], b[2] + pz), 0.34, mat_idx=2)
    bm_add_strut(bm, (x_face, 0.0, z_arm - 9.0), (x_face + 3.0, y_out, z_arm - 1.1), 0.55, mat_idx=0)

build_umbilical_dogleg(bm_tower, BOOSTER_BASE_Z + 55.0)
build_umbilical_dogleg(bm_tower, SHIP_BASE_Z + 56.0)

tower_obj = finalize_mesh_object("Mechazilla_Launch_Tower", bm_tower, mat=mat_tower_steel, smooth=False)
tower_obj.data.materials.append(mat_cabin_glass)
tower_obj.data.materials.append(mat_cryo_white)

# @@OBJECT: 13_passenger_cargo_tower_and_terminal.py
bm_crew_tower = bmesh.new()
faces_pairs = [(0, 1), (1, 2), (2, 3), (3, 0)]
ct_cx, ct_cy = 43.0, 0.0
ct_half = 8.0
ct_height = JETWAY_Z
ct_bays = max(48, int(ct_height / 4.2))
ct_bay_h = ct_height / ct_bays

# The tower's own podium. The terminal does not sit on this footprint.
bm_add_box(bm_crew_tower, (ct_cx, ct_cy, 3.2), (22.0, 22.0, 6.4), mat_idx=0)
bm_add_box(bm_crew_tower, (ct_cx, ct_cy, 5.1), (16.0, 16.0, 3.6), mat_idx=3)
bm_add_box(bm_crew_tower, (ct_cx, ct_cy, 7.05), (22.8, 22.8, 0.55), mat_idx=2)
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
        ship_door = (c_a, c_b) == (3, 0) and not (z1 < CARGO_Z_BOT - 0.6 or z0 > CARGO_Z_TOP + 1.4)
        chord_in_door = ship_door and (CARGO_Z_BOT + 0.3) < z1 < (CARGO_Z_TOP + 0.4)
        if not chord_in_door:
            bm_add_strut(bm_crew_tower, p_a1, p_b1, 0.55, mat_idx=0)
        if not ship_door:
            bm_add_strut(bm_crew_tower, p_am, p_bm, 0.30, mat_idx=0)
            bm_add_strut(bm_crew_tower, p_a0, p_b1, 0.42, mat_idx=0)
            bm_add_strut(bm_crew_tower, p_b0, p_a1, 0.42, mat_idx=0)
    if b_idx % 4 == 0 and b_idx > 0:
        bm_add_box(bm_crew_tower, (ct_cx + 4.0, ct_cy, z1), (7.2, 14.2, 0.22), mat_idx=0)

# Glass lobby is the crown. Passenger elevator is inside the tower and opens onto this floor.
# The jetway leaves the lobby's ship-facing wall.
lobby_floor = ct_height
lobby_h = 8.0
lobby_z = lobby_floor + lobby_h * 0.5
lobby_dx, lobby_dy = 26.0, 16.0
lobby_cx = ct_cx - 5.0
lobby_cy = 0.0
lobby_x_ship = lobby_cx - lobby_dx * 0.5
bm_add_box(bm_crew_tower, (lobby_cx, lobby_cy, lobby_z), (lobby_dx, lobby_dy, lobby_h), mat_idx=3)
bm_add_box(bm_crew_tower, (lobby_cx, lobby_cy, lobby_floor + lobby_h), (lobby_dx + 1.6, lobby_dy + 1.6, 0.7), mat_idx=2)
bm_add_box(bm_crew_tower, (lobby_cx, lobby_cy, lobby_floor), (lobby_dx + 0.8, lobby_dy + 0.8, 0.45), mat_idx=2)
for mullion_y in (-6.4, -3.2, 0.0, 3.2, 6.4):
    bm_add_box(bm_crew_tower, (lobby_x_ship - 0.15, mullion_y, lobby_z), (0.28, 0.22, lobby_h), mat_idx=2)

elev_x = ct_cx + 1.8
elev_y = -2.4
for ex_off in (-1.15, 1.15):
    for ey_off in (-1.05, 1.05):
        bm_add_strut(bm_crew_tower, (elev_x + ex_off, elev_y + ey_off, 0.6), (elev_x + ex_off, elev_y + ey_off, lobby_floor), 0.20, mat_idx=0)
bm_add_box(bm_crew_tower, (elev_x, elev_y, lobby_floor - 1.5), (2.35, 2.15, 2.9), mat_idx=3)
bm_add_box(bm_crew_tower, (elev_x, elev_y, lobby_floor + 0.2), (2.6, 2.4, 0.28), mat_idx=2)

jw_z = lobby_floor + 2.05
jw_x0 = HULL_R + 0.45
jw_x1 = lobby_x_ship
jw_len = max(2.0, jw_x1 - jw_x0)
jw_cx = 0.5 * (jw_x0 + jw_x1)
jw_y = 0.0
bm_add_box(bm_crew_tower, (jw_cx, jw_y, jw_z - 1.55), (jw_len, 3.8, 0.40), mat_idx=2)
bm_add_box(bm_crew_tower, (jw_cx, jw_y, jw_z + 1.55), (jw_len, 3.8, 0.40), mat_idx=2)
bm_add_box(bm_crew_tower, (jw_cx, jw_y, jw_z), (jw_len - 0.2, 3.2, 2.6), mat_idx=1)
for jx in range(int(jw_x0) + 1, int(jw_x1), 3):
    bm_add_strut(bm_crew_tower, (float(jx), jw_y - 1.8, jw_z - 1.4), (float(jx + 2.2), jw_y - 1.8, jw_z + 1.4), 0.16, mat_idx=0)
    bm_add_strut(bm_crew_tower, (float(jx), jw_y + 1.8, jw_z - 1.4), (float(jx + 2.2), jw_y + 1.8, jw_z + 1.4), 0.16, mat_idx=0)
bm_add_box(bm_crew_tower, (jw_x0 + 0.2, jw_y, jw_z), (0.8, 4.0, 3.5), mat_idx=0)
bm_add_box(bm_crew_tower, (jw_x1 + 0.6, jw_y, jw_z), (1.8, 4.4, 3.6), mat_idx=2)
# Jetway truss. Every member lands on the bridge or on a tower column. Nothing ends in mid-air.
col_x = ct_cx - ct_half
col_y = ct_half
bm_add_strut(bm_crew_tower, (lobby_x_ship, -7.2, lobby_floor + 0.35), (lobby_x_ship, 7.2, lobby_floor + 0.35), 0.55, mat_idx=0)
bm_add_strut(bm_crew_tower, (lobby_x_ship, -7.2, lobby_floor + 0.35), (col_x, -col_y, lobby_floor + 0.35), 0.48, mat_idx=0)
bm_add_strut(bm_crew_tower, (lobby_x_ship, 7.2, lobby_floor + 0.35), (col_x, col_y, lobby_floor + 0.35), 0.48, mat_idx=0)
for sy in (-1.55, 1.55):
    bm_add_strut(bm_crew_tower, (jw_x1, sy, jw_z - 1.75), (jw_x0 + 0.4, sy, jw_z - 1.75), 0.36, mat_idx=0)
for sy in (-1.0, 1.0):
    bm_add_strut(bm_crew_tower, (col_x, sy * col_y, lobby_floor), (jw_cx, sy * 1.55, jw_z - 1.75), 0.50, mat_idx=0)
    bm_add_strut(bm_crew_tower, (col_x, sy * col_y, lobby_floor - 7.0), (jw_x0 + 1.6, sy * 1.55, jw_z - 1.75), 0.58, mat_idx=0)
    bm_add_strut(bm_crew_tower, (col_x, sy * 6.4, lobby_floor - 9.0), (lobby_x_ship, sy * 6.4, lobby_floor), 0.46, mat_idx=0)

# Cargo elevator. Guide rails run inside the tower, from the podium up to the lobby floor.
# The car is parked at the cargo deck. A trussed bridge leaves through a framed opening to the door.
tower_ship_x = col_x
shaft_x0 = tower_ship_x + 1.8
shaft_x1 = ct_cx - 0.6
shaft_y = 3.35
rail_xy = (
    (shaft_x0, -shaft_y),
    (shaft_x0, shaft_y),
    (shaft_x1, -shaft_y),
    (shaft_x1, shaft_y),
)
for rx, ry in rail_xy:
    bm_add_strut(bm_crew_tower, (rx, ry, 0.8), (rx, ry, lobby_floor - 0.6), 0.40, mat_idx=0)
for z_tie in range(12, int(lobby_floor) - 6, 16):
    zf = float(z_tie)
    bm_add_strut(bm_crew_tower, (shaft_x0, -shaft_y, zf), (shaft_x0, shaft_y, zf), 0.30, mat_idx=0)
    bm_add_strut(bm_crew_tower, (shaft_x1, -shaft_y, zf), (shaft_x1, shaft_y, zf), 0.30, mat_idx=0)
    bm_add_strut(bm_crew_tower, (shaft_x0, -shaft_y, zf), (shaft_x1, -shaft_y, zf), 0.26, mat_idx=0)
    bm_add_strut(bm_crew_tower, (shaft_x0, shaft_y, zf), (shaft_x1, shaft_y, zf), 0.26, mat_idx=0)
    bm_add_strut(bm_crew_tower, (tower_ship_x, -shaft_y, zf), (shaft_x0, -shaft_y, zf), 0.28, mat_idx=0)
    bm_add_strut(bm_crew_tower, (tower_ship_x, shaft_y, zf), (shaft_x0, shaft_y, zf), 0.28, mat_idx=0)
head_z = lobby_floor - 1.15
bm_add_box(bm_crew_tower, (0.5 * (shaft_x0 + shaft_x1), 0.0, head_z), (shaft_x1 - shaft_x0 + 0.8, shaft_y * 2.0 + 0.8, 0.70), mat_idx=0)
cab_z = CARGO_DECK_Z
for rx, ry in rail_xy:
    bm_add_strut(bm_crew_tower, (rx, ry, head_z - 0.4), (rx, ry, cab_z + 4.4), 0.08, mat_idx=0)
cab_cx = 0.5 * (shaft_x0 + shaft_x1)
bm_add_box(bm_crew_tower, (cab_cx, 0.0, cab_z), (shaft_x1 - shaft_x0 - 0.35, shaft_y * 2.0 - 0.45, 0.40), mat_idx=2)
for rx, ry in (
    (shaft_x0 + 0.25, -shaft_y + 0.25),
    (shaft_x0 + 0.25, shaft_y - 0.25),
    (shaft_x1 - 0.25, -shaft_y + 0.25),
    (shaft_x1 - 0.25, shaft_y - 0.25),
):
    bm_add_strut(bm_crew_tower, (rx, ry, cab_z), (rx, ry, cab_z + 4.3), 0.20, mat_idx=0)
bm_add_strut(bm_crew_tower, (shaft_x0 + 0.25, -shaft_y + 0.25, cab_z + 4.3), (shaft_x1 - 0.25, -shaft_y + 0.25, cab_z + 4.3), 0.18, mat_idx=0)
bm_add_strut(bm_crew_tower, (shaft_x0 + 0.25, shaft_y - 0.25, cab_z + 4.3), (shaft_x1 - 0.25, shaft_y - 0.25, cab_z + 4.3), 0.18, mat_idx=0)
bm_add_box(bm_crew_tower, (shaft_x0 + 0.15, 0.0, cab_z + 1.5), (0.16, shaft_y * 2.0 - 0.6, 2.6), mat_idx=0)

# Framed opening in the ship face, then the bridge out to the cargo door.
bm_add_strut(bm_crew_tower, (tower_ship_x, -4.3, CARGO_Z_BOT - 0.45), (tower_ship_x, 4.3, CARGO_Z_BOT - 0.45), 0.55, mat_idx=0)
bm_add_strut(bm_crew_tower, (tower_ship_x, -4.3, CARGO_Z_TOP + 0.7), (tower_ship_x, 4.3, CARGO_Z_TOP + 0.7), 0.55, mat_idx=0)
bm_add_strut(bm_crew_tower, (tower_ship_x, -4.3, CARGO_Z_BOT - 0.45), (tower_ship_x, -4.3, CARGO_Z_TOP + 0.7), 0.48, mat_idx=0)
bm_add_strut(bm_crew_tower, (tower_ship_x, 4.3, CARGO_Z_BOT - 0.45), (tower_ship_x, 4.3, CARGO_Z_TOP + 0.7), 0.48, mat_idx=0)

cp_z = CARGO_DECK_Z
cp_x0 = HULL_R + 0.40
cp_x1 = shaft_x0 + 0.2
cp_len = max(4.0, cp_x1 - cp_x0)
cp_cx = 0.5 * (cp_x0 + cp_x1)
cp_w = 6.4
bm_add_box(bm_crew_tower, (cp_cx, 0.0, cp_z + 0.18), (cp_len, cp_w, 0.40), mat_idx=2)
for beam_y in (-2.4, -0.8, 0.8, 2.4):
    bm_add_strut(bm_crew_tower, (cp_x0, beam_y, cp_z - 0.50), (cp_x1, beam_y, cp_z - 0.50), 0.50, mat_idx=0)
for beam_x_u in (0.18, 0.42, 0.66, 0.88):
    bx = cp_x0 + beam_x_u * cp_len
    bm_add_strut(bm_crew_tower, (bx, -cp_w * 0.5, cp_z - 0.50), (bx, cp_w * 0.5, cp_z - 0.50), 0.36, mat_idx=0)
for rail_y in (-cp_w * 0.5, cp_w * 0.5):
    bm_add_strut(bm_crew_tower, (cp_x0, rail_y, cp_z + 1.15), (tower_ship_x - 0.4, rail_y, cp_z + 1.15), 0.16, mat_idx=2)
for sy in (-1.0, 1.0):
    bm_add_strut(bm_crew_tower, (tower_ship_x, sy * col_y, cp_z - 14.0), (cp_x0 + 2.2, sy * 2.2, cp_z - 0.5), 0.62, mat_idx=0)
    bm_add_strut(bm_crew_tower, (tower_ship_x, sy * col_y, cp_z), (cp_x0 + 8.0, sy * 2.2, cp_z - 0.5), 0.48, mat_idx=0)
    bm_add_strut(bm_crew_tower, (tower_ship_x, sy * col_y, cp_z - 14.0), (tower_ship_x, sy * 3.2, cp_z - 0.5), 0.42, mat_idx=0)
bm_add_box(bm_crew_tower, (cp_x0 + 0.35, 0.0, cp_z + 1.35), (0.7, cp_w + 0.3, 2.5), mat_idx=0)

# Terminal stands clear of the tower, on its own slab, joined by a concourse on the east face.
tower_east = ct_cx + ct_half
term_w, term_d = 104.0, 74.0
term_west = tower_east + 12.0
term_x = term_west + term_w * 0.5
term_y = 0.0
bm_add_box(bm_crew_tower, (term_x, term_y, 3.3), (term_w, term_d, 6.6), mat_idx=2)
bm_add_box(bm_crew_tower, (term_x, term_y, 10.4), (term_w - 8.0, term_d - 8.0, 7.4), mat_idx=3)
bm_add_box(bm_crew_tower, (term_x, term_y, 14.4), (term_w + 6.0, term_d + 6.0, 0.9), mat_idx=2)
bm_add_box(bm_crew_tower, (term_x, term_y, 6.7), (term_w + 1.2, term_d + 1.2, 0.45), mat_idx=2)
conc_x = 0.5 * (tower_east + term_west)
conc_len = term_west - tower_east
bm_add_box(bm_crew_tower, (conc_x, 0.0, 3.6), (conc_len + 1.0, 14.0, 6.4), mat_idx=3)
bm_add_box(bm_crew_tower, (conc_x, 0.0, 7.0), (conc_len + 2.0, 16.0, 0.45), mat_idx=2)
for mx in range(int(term_west) + 6, int(term_west + term_w) - 4, 8):
    bm_add_box(bm_crew_tower, (float(mx), term_y - term_d * 0.5, 7.2), (0.38, 0.42, 14.0), mat_idx=2)
    bm_add_box(bm_crew_tower, (float(mx), term_y + term_d * 0.5, 7.2), (0.38, 0.42, 14.0), mat_idx=2)
for my in range(int(-term_d * 0.5) + 6, int(term_d * 0.5) - 4, 8):
    bm_add_box(bm_crew_tower, (term_west, float(my), 7.2), (0.42, 0.38, 14.0), mat_idx=2)
    bm_add_box(bm_crew_tower, (term_west + term_w, float(my), 7.2), (0.42, 0.38, 14.0), mat_idx=2)
for ix in range(int(term_west) + 14, int(term_west + term_w) - 10, 16):
    for iy in range(int(-term_d * 0.5) + 14, int(term_d * 0.5) - 10, 16):
        bm_add_cylinder_frustum(bm_crew_tower, (float(ix), float(iy), 6.6), 0.55, 0.48, 13.0, segments=12, mat_idx=2)
canopy_y = -(term_d * 0.5 + 7.0)
bm_add_box(bm_crew_tower, (term_x, canopy_y, 6.2), (42.0, 14.0, 0.45), mat_idx=2)
for cx in (term_x - 16.0, term_x, term_x + 16.0):
    bm_add_cylinder_frustum(bm_crew_tower, (cx, canopy_y - 4.5, 3.0), 0.42, 0.42, 6.0, segments=12, mat_idx=2)
bm_add_box(bm_crew_tower, (term_x, term_y - term_d * 0.5 + 1.2, 3.4), (18.0, 0.35, 6.2), mat_idx=1)

crew_tower_obj = finalize_mesh_object("Passenger_Cargo_Tower_And_Terminal", bm_crew_tower, mat=mat_tower_steel, smooth=False)
crew_tower_obj.data.materials.append(mat_cabin_glass)
crew_tower_obj.data.materials.append(mat_terminal_metal)
crew_tower_obj.data.materials.append(mat_terminal_glass)

# @@OBJECT: 14_propellant_tanks.py
bm_tanks = bmesh.new()
tank_x_base = 198.0
for row_i in range(2):
    for col_j in range(4):
        tx = tank_x_base + row_i * 26.0
        ty = 22.0 + col_j * 28.0
        bm_add_cylinder_frustum(bm_tanks, (tx, ty, 26.0), 8.2, 8.2, 52.0, segments=48, mat_idx=0)
        bm_add_cylinder_frustum(bm_tanks, (tx, ty, 54.0), 8.2, 2.2, 4.0, segments=48, mat_idx=0)
        bm_add_cylinder_frustum(bm_tanks, (tx, ty, 56.8), 2.2, 0.1, 1.6, segments=32, mat_idx=0)
        bm_add_cylinder_frustum(bm_tanks, (tx - 8.6, ty, 26.0), 0.5, 0.5, 50.0, segments=12, mat_idx=1)

bm_add_box(bm_tanks, (211.0, 12.0, 4.5), (70.0, 2.5, 9.0), mat_idx=1)
bm_add_box(bm_tanks, (211.0, 118.0, 4.5), (70.0, 2.5, 9.0), mat_idx=1)
bm_add_box(bm_tanks, (176.0, 65.0, 4.5), (2.5, 110.0, 9.0), mat_idx=1)
bm_add_box(bm_tanks, (246.0, 65.0, 4.5), (2.5, 110.0, 9.0), mat_idx=1)
bm_add_box(bm_tanks, (168.0, 18.0, 2.2), (24.0, 3.2, 2.8), mat_idx=1)

tanks_obj = finalize_mesh_object("Orbital_Propellant_Tank_Farm", bm_tanks, mat=mat_cryo_white, smooth=True)
tanks_obj.data.materials.append(mat_tower_steel)

# @@OBJECT: 15_tesla_semis.py
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

    bm_add_box(bm, tr((-0.92, 8.55, 0.95)), (0.55, 0.16, 0.22), rot_euler=rot_e, mat_idx=4)
    bm_add_box(bm, tr((0.92, 8.55, 0.95)), (0.55, 0.16, 0.22), rot_euler=rot_e, mat_idx=4)
    bm_add_box(bm, tr((0.0, 8.52, 1.05)), (1.70, 0.08, 0.08), rot_euler=rot_e, mat_idx=4)

    bm_add_box(bm, tr((0.0, -5.7, 2.70)), (2.60, 16.8, 2.90), rot_euler=rot_e, mat_idx=0)
    bm_add_box(bm, tr((0.0, 2.55, 2.65)), (1.55, 0.28, 1.85), rot_euler=rot_e, mat_idx=1)
    bm_add_box(bm, tr((0.0, -5.5, 0.92)), (2.68, 16.2, 0.62), rot_euler=rot_e, mat_idx=5)
    bm_add_box(bm, tr((0.0, 5.15, 0.70)), (2.20, 6.6, 0.42), rot_euler=rot_e, mat_idx=5)
    bm_add_box(bm, tr((0.0, 1.35, 0.78)), (1.35, 0.42, 1.15), rot_euler=rot_e, mat_idx=5)
    bm_add_box(bm, tr((0.0, -13.85, 2.55)), (2.52, 0.16, 2.55), rot_euler=rot_e, mat_idx=5)
    bm_add_box(bm, tr((0.0, -13.95, 2.55)), (2.20, 0.06, 2.15), rot_euler=rot_e, mat_idx=1)
    for my in range(-12, 3, 2):
        bm_add_box(bm, tr((0.0, float(my), 4.18)), (2.15, 0.08, 0.07), rot_euler=rot_e, mat_idx=4)
        bm_add_box(bm, tr((-1.22, float(my), 1.28)), (0.08, 0.10, 0.08), rot_euler=rot_e, mat_idx=4)
        bm_add_box(bm, tr((1.22, float(my), 1.28)), (0.08, 0.10, 0.08), rot_euler=rot_e, mat_idx=4)
    for tr_y in range(-12, 3, 2):
        bm_add_box(bm, tr((-1.31, float(tr_y), 2.70)), (0.03, 0.06, 2.82), rot_euler=rot_e, mat_idx=0)
        bm_add_box(bm, tr((1.31, float(tr_y), 2.70)), (0.03, 0.06, 2.82), rot_euler=rot_e, mat_idx=0)
    bm_add_box(bm, tr((-1.26, -3.5, 0.95)), (0.08, 7.5, 0.65), rot_euler=rot_e, mat_idx=0)
    bm_add_box(bm, tr((1.26, -3.5, 0.95)), (0.08, 7.5, 0.65), rot_euler=rot_e, mat_idx=0)
    bm_add_box(bm, tr((-0.95, 1.1, 0.75)), (0.18, 0.18, 1.0), rot_euler=rot_e, mat_idx=3)
    bm_add_box(bm, tr((0.95, 1.1, 0.75)), (0.18, 0.18, 1.0), rot_euler=rot_e, mat_idx=3)
    bm_add_box(bm, tr((0.0, -14.05, 0.72)), (2.45, 0.12, 0.18), rot_euler=rot_e, mat_idx=3)
    bm_add_box(bm, tr((-1.05, -14.05, 1.15)), (0.28, 0.08, 0.22), rot_euler=rot_e, mat_idx=4)
    bm_add_box(bm, tr((1.05, -14.05, 1.15)), (0.28, 0.08, 0.22), rot_euler=rot_e, mat_idx=4)

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
    (72.0, -168.0, 0.0),
    (128.0, -68.0, 90.0),
]
for sx, sy, s_ang in semi_placements:
    add_tesla_semi(bm_semis, sx, sy, s_ang)

semis_obj = finalize_mesh_object("Tesla_Semi_18Wheeler_Fleet", bm_semis, mat=mat_semi_white, smooth=False)
semis_obj.data.materials.append(mat_semi_glass)
semis_obj.data.materials.append(mat_tire_rubber)
semis_obj.data.materials.append(mat_wheel_rim)
semis_obj.data.materials.append(mat_headlight)
semis_obj.data.materials.append(mat_titanium_dark)

# @@OBJECT: 16_ground_crew.py
bm_crew = bmesh.new()

def add_person(bm, x, y):
    bm_add_cylinder_frustum(bm, (x - 0.09, y, 0.46), 0.07, 0.06, 0.92, segments=6, mat_idx=2)
    bm_add_cylinder_frustum(bm, (x + 0.09, y, 0.46), 0.07, 0.06, 0.92, segments=6, mat_idx=2)
    bm_add_box(bm, (x, y, 1.18), (0.40, 0.22, 0.64), mat_idx=0)
    bm_add_box(bm, (x - 0.26, y, 1.12), (0.10, 0.10, 0.46), mat_idx=0)
    bm_add_box(bm, (x + 0.26, y, 1.12), (0.10, 0.10, 0.46), mat_idx=0)
    bm_add_cylinder_frustum(bm, (x, y, 1.66), 0.11, 0.10, 0.22, segments=8, mat_idx=2)
    bm_add_cylinder_frustum(bm, (x, y, 1.82), 0.13, 0.13, 0.10, segments=8, mat_idx=0)

def add_bollard(bm, x, y):
    bm_add_cylinder_frustum(bm, (x, y, 0.50), 0.13, 0.11, 1.00, segments=8, mat_idx=0)
    bm_add_cylinder_frustum(bm, (x, y, 1.05), 0.15, 0.15, 0.10, segments=8, mat_idx=1)

def add_mast(bm, x, y):
    bm_add_box(bm, (x, y, 0.25), (1.6, 1.6, 0.50), mat_idx=1)
    bm_add_cylinder_frustum(bm, (x, y, 7.6), 0.32, 0.16, 14.6, segments=10, mat_idx=1)
    bm_add_box(bm, (x, y, 15.05), (3.4, 0.85, 0.28), mat_idx=1)
    bm_add_box(bm, (x, y, 14.82), (2.8, 0.55, 0.12), mat_idx=3)

def add_container(bm, x, y, z_rot, length):
    rot = (0.0, 0.0, z_rot)
    bm_add_box(bm, (x, y, 1.35), (2.44, length, 2.59), rot_euler=rot, mat_idx=4)
    bm_add_box(bm, (x, y, 0.18), (2.20, length - 0.4, 0.28), rot_euler=rot, mat_idx=1)
    bm_add_box(bm, (x, y + length * 0.5, 1.35), (2.30, 0.08, 2.30), rot_euler=rot, mat_idx=1)

crew_coords = [
    (30.0, -45.0), (32.5, -46.5), (31.0, -52.0), (39.5, -68.0), (41.0, -70.0),
    (33.0, -92.0), (49.5, -102.0), (42.0, -125.0), (31.0, -135.0), (54.0, -62.0),
    (-30.0, -42.0), (-32.0, -44.0), (-34.5, -55.0), (-42.0, -72.0), (-33.0, -78.0),
    (-46.0, -95.0), (-38.0, -110.0), (-54.0, -112.0), (29.0, -18.0), (31.0, -15.0),
    (-29.5, -22.0), (-31.0, -19.0), (34.0, 12.0), (36.0, 15.0), (-32.0, 35.0),
    (68.0, -85.0), (70.0, -88.0), (-65.0, -65.0), (-67.0, -68.0), (28.5, -80.0),
]
for cx, cy in crew_coords:
    add_person(bm_crew, cx, cy)

for by in range(-180, 80, 16):
    add_bollard(bm_crew, TRENCH_EDGE + 1.6, float(by))
    add_bollard(bm_crew, -(TRENCH_EDGE + 1.6), float(by))
for bx in range(80, 170, 14):
    add_bollard(bm_crew, float(bx), -28.0)

for mx, my in ((88.0, -20.0), (88.0, -110.0), (88.0, -190.0), (150.0, 28.0), (-88.0, -30.0), (-88.0, -120.0), (40.0, 70.0), (-40.0, 80.0)):
    add_mast(bm_crew, mx, my)

add_container(bm_crew, 96.0, -24.0, 0.0, 6.1)
add_container(bm_crew, 96.0, -32.0, 0.0, 6.1)
add_container(bm_crew, 102.0, -28.0, math.radians(90), 12.2)
add_container(bm_crew, -96.0, -48.0, 0.0, 6.1)

# Tug and a hose reel beside the apron.
bm_add_box(bm_crew, (62.0, -38.0, 0.85), (1.8, 3.4, 1.3), mat_idx=4)
bm_add_box(bm_crew, (62.0, -36.6, 1.15), (1.7, 0.9, 0.7), mat_idx=3)
bm_add_cylinder_frustum(bm_crew, (61.3, -39.2, 0.38), 0.32, 0.32, 0.28, segments=10, rot_euler=(0.0, math.radians(90), 0.0), mat_idx=2)
bm_add_cylinder_frustum(bm_crew, (62.7, -39.2, 0.38), 0.32, 0.32, 0.28, segments=10, rot_euler=(0.0, math.radians(90), 0.0), mat_idx=2)
bm_add_cylinder_frustum(bm_crew, (62.0, -36.4, 0.38), 0.32, 0.32, 0.28, segments=10, rot_euler=(0.0, math.radians(90), 0.0), mat_idx=2)
bm_add_cylinder_frustum(bm_crew, (58.0, -36.0, 0.85), 0.9, 0.9, 0.7, segments=16, rot_euler=(0.0, math.radians(90), 0.0), mat_idx=1)
bm_add_box(bm_crew, (58.0, -36.0, 0.35), (1.1, 1.6, 0.5), mat_idx=1)

# Fence along the south service road and the terminal approach.
for fx in range(40, 176, 8):
    bm_add_cylinder_frustum(bm_crew, (float(fx), -210.0, 1.3), 0.08, 0.08, 2.6, segments=6, mat_idx=1)
for fx0 in range(40, 168, 8):
    bm_add_strut(bm_crew, (float(fx0), -210.0, 0.7), (float(fx0 + 8), -210.0, 0.7), 0.06, mat_idx=1)
    bm_add_strut(bm_crew, (float(fx0), -210.0, 1.9), (float(fx0 + 8), -210.0, 1.9), 0.06, mat_idx=1)
for fy in range(-200, -20, 8):
    bm_add_cylinder_frustum(bm_crew, (176.0, float(fy), 1.3), 0.08, 0.08, 2.6, segments=6, mat_idx=1)
for fy0 in range(-200, -28, 8):
    bm_add_strut(bm_crew, (176.0, float(fy0), 0.7), (176.0, float(fy0 + 8), 0.7), 0.06, mat_idx=1)
    bm_add_strut(bm_crew, (176.0, float(fy0), 1.9), (176.0, float(fy0 + 8), 1.9), 0.06, mat_idx=1)

crew_obj = finalize_mesh_object("Spaceport_Ground_Crew", bm_crew, mat=mat_hivis_orange, smooth=False)
crew_obj.data.materials.append(mat_tower_steel)
crew_obj.data.materials.append(mat_tire_rubber)
crew_obj.data.materials.append(mat_headlight)
crew_obj.data.materials.append(mat_cryo_white)

# @@OBJECT: 17_lighting_and_camera.py
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
cam_obj.location = (120.0, -680.0, 145.0)

target_point = Vector((18.0, 0.0, 160.0))
direction = target_point - cam_obj.location
cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
scene.camera = cam_obj

if not bpy.app.background:
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