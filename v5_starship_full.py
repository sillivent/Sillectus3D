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

# NOTE: Full script content continues below in the actual file. This is a test upload of the header.
print('Patched V5 Starship scene - see modular files for components')
