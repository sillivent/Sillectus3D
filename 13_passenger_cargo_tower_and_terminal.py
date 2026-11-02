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

