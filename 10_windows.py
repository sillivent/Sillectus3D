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
    """One wraparound windshield. The outline is a smooth horseshoe, not a stack of rectangles."""
    def band(r_off, z_extra, ang_extra, mat_idx, steps_u, steps_v):
        grid = []
        for iv in range(steps_v + 1):
            v = iv / steps_v
            row = []
            for iu in range(steps_u + 1):
                s = -1.0 + 2.0 * (iu / steps_u)
                ang = math.radians(s * (56.0 + ang_extra))
                z_lo = peak - 0.40 - z_extra - 2.90 * (s * s)
                z_hi = peak + 1.15 + z_extra - 1.95 * (s * s)
                z = z_lo * (1.0 - v) + z_hi * v
                rad = v5_radius_at_z(z) + r_off
                row.append(bm.verts.new((math.cos(ang) * rad, math.sin(ang) * rad, z)))
            grid.append(row)
        for iv in range(steps_v):
            for iu in range(steps_u):
                f = bm.faces.new((grid[iv][iu], grid[iv][iu + 1], grid[iv + 1][iu + 1], grid[iv + 1][iu]))
                f.material_index = mat_idx
    band(0.05, 0.16, 1.6, 2, 36, 6)
    band(0.11, 0.0, 0.0, 0, 36, 6)
    for s_m in (-0.62, -0.28, 0.0, 0.28, 0.62):
        ang = math.radians(s_m * 56.0)
        z_lo = peak - 0.35 - 2.90 * (s_m * s_m)
        z_hi = peak + 1.10 - 1.95 * (s_m * s_m)
        z_mid = 0.5 * (z_lo + z_hi)
        rad = v5_radius_at_z(z_mid) + 0.14
        bm_add_box(
            bm,
            (math.cos(ang) * rad, math.sin(ang) * rad, z_mid),
            (0.10, 0.16, (z_hi - z_lo) * 0.92),
            rot_euler=(0.0, 0.0, ang),
            mat_idx=2,
        )

add_horseshoe_cockpit(bm_windows, COCKPIT_PEAK_Z)

for deck_z in CABIN_DECK_Z:
    for p_deg in (-24.0, -12.0, 0.0, 12.0, 24.0):
        add_horizontal_oval_window(bm_windows, p_deg, deck_z, half_w_deg=4.0, half_h_z=0.62, mat_glass_idx=1, mat_frame_idx=2)
for p_deg in (-18.0, -9.0, 0.0, 9.0, 18.0):
    add_horizontal_oval_window(bm_windows, p_deg, ENG_DECK_Z, half_w_deg=2.1, half_h_z=0.32, mat_glass_idx=1, mat_frame_idx=2)

win_obj = finalize_mesh_object("Starship_V5_Cockpit_And_Cabin_Windows", bm_windows, mat=mat_cockpit_glass, smooth=True)
win_obj.data.materials.append(mat_cabin_glass)
win_obj.data.materials.append(mat_titanium_dark)

