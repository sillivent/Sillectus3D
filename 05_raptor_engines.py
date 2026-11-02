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

