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

