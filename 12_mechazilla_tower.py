# Slice of v5_starship_full.py — generated, do not edit by hand.
# Blender 5.2: Scripting workspace → Text → Open → Run Script.
# Do not paste this into the Python console, and do not paste shell commands there.
# Running this file clears the scene and builds only this piece.
# For the whole starbase, open v5_starship_full.py and Run Script.

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
mat_cockpit_glass = create_principled_material("Shuttle_Cockpit_Glass", (0.08, 0.55, 0.95), metallic=0.1, roughness=0.08, emission_color=(0.12, 0.65, 1.0), emission_strength=2.8)
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
CARGO_Z_TOP = CARGO_Z_BOT + 6.6
CARGO_DECK_Z = 0.5 * (CARGO_Z_BOT + CARGO_Z_TOP)
ENG_DECK_Z = CARGO_Z_TOP + 4.8
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
NOSE_CAP_R = 0.20 * HULL_R

def v5_radius_at_z(z_world):
    """Cylinder, tangent/von Karman ogive, then a hemisphere. The tip is round, not a flat disk."""
    if z_world <= SHIP_NOSE_Z:
        return HULL_R
    z_local = z_world - SHIP_NOSE_Z
    if z_local >= SHIP_NOSE_H - 1e-4:
        return 0.0
    t = max(0.0, min(1.0, z_local / SHIP_NOSE_H))
    cos_arg = max(-1.0, min(1.0, 1.0 - 2.0 * (1.0 - t)))
    theta = math.acos(cos_arg)
    r_vk = (HULL_R / math.sqrt(math.pi)) * math.sqrt(max(0.0, theta - 0.5 * math.sin(2.0 * theta)))
    rho = (HULL_R ** 2 + SHIP_NOSE_H ** 2) / (2.0 * HULL_R)
    r_tan = math.sqrt(max(0.0, rho ** 2 - z_local ** 2)) + HULL_R - rho
    r_ogive = max(0.0, 0.55 * r_vk + 0.45 * r_tan)
    cap_r = NOSE_CAP_R
    dz_from_tip = SHIP_NOSE_H - z_local
    if dz_from_tip >= cap_r:
        return r_ogive
    r_sphere = math.sqrt(max(0.0, cap_r * cap_r - (cap_r - dz_from_tip) ** 2))
    band = min(1.8, cap_r * 0.6)
    if dz_from_tip > cap_r - band:
        u = (cap_r - dz_from_tip) / band
        u = max(0.0, min(1.0, u))
        u = u * u * (3.0 - 2.0 * u)
        return r_ogive * (1.0 - u) + r_sphere * u
    return r_sphere

def ship_z_samples():
    """Cylinder rings, ogive rings, then extra rings around the round tip."""
    samples = []
    cyl_rings = 48
    for i in range(cyl_rings):
        samples.append(SHIP_BASE_Z + (i / cyl_rings) * SHIP_CYL_H)
    ogive_h = SHIP_NOSE_H - NOSE_CAP_R
    nose_rings = 36
    for i in range(nose_rings):
        samples.append(SHIP_NOSE_Z + (i / nose_rings) * ogive_h)
    cap_rings = 12
    for i in range(1, cap_rings + 1):
        dz = max(0.05, NOSE_CAP_R * (1.0 - i / cap_rings))
        samples.append(SHIP_TOP_Z - dz)
    return samples

# @@PREAMBLE_END@@

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

