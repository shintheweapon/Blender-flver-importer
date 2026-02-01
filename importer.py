import bpy
import bmesh
import time
from pathlib import Path
from mathutils import Matrix, Vector
from bpy.app.translations import pgettext

from .flver_utils import read_flver


def import_flver(file_path, z_up=True):
    """
    Import a FLVER file into Blender.

    Args:
        file_path (Path): Path to the .flver file.
        z_up (bool): If True, convert to Blender's Z-up coordinate system.
                     If False, keep FromSoftware's Y-up coordinate system.
    """
    file_path = Path(file_path)
    print(f"Importing FLVER from {file_path}")

    time_start = time.perf_counter()

    base_name = file_path.stem

    # Read FLVER data
    flver_data = read_flver(file_path)
    inflated_meshes = flver_data.inflate()

    # Create collection for this model
    collection = bpy.data.collections.new(base_name)
    bpy.context.scene.collection.children.link(collection)

    # Create armature only if there are bones
    armature = None
    if len(flver_data.bones) > 0:
        armature = create_armature(base_name, collection, flver_data, z_up)

    # Create meshes
    for flver_mesh, inflated_mesh in zip(flver_data.meshes, inflated_meshes):
        if inflated_mesh is None:
            continue

        create_mesh(
            base_name,
            collection,
            flver_data,
            flver_mesh,
            inflated_mesh,
            armature,
            z_up
        )

    time_end = time.perf_counter()
    print(f"FLVER import completed in {time_end - time_start:.2f}s")


def convert_coordinates(x, y, z, z_up):
    """Convert coordinates based on coordinate system setting."""
    if z_up:
        return (x, z, y)  # Swap Y and Z for Blender's Z-up
    else:
        return (x, y, z)  # Keep original Y-up


def create_mesh(base_name, collection, flver_data, flver_mesh, inflated_mesh, armature, z_up):
    """
    Create a Blender mesh from inflated FLVER mesh data.
    """
    material_name = flver_data.materials[flver_mesh.material_index].name
    mesh_name = f"{base_name}_{material_name}"

    # Create vertices with coordinate conversion
    verts = [
        Vector(convert_coordinates(v[0], v[1], v[2], z_up))
        for v in inflated_mesh.vertices.positions
    ]

    # Create mesh
    mesh = bpy.data.meshes.new(name=mesh_name)
    mesh.from_pydata(verts, [], inflated_mesh.faces)

    # Create object and link to collection
    obj = bpy.data.objects.new(mesh_name, mesh)
    collection.objects.link(obj)

    # Setup armature modifier (only if armature exists)
    if armature is not None:
        obj.modifiers.new(type="ARMATURE", name=pgettext(
            "Armature")).object = armature
        obj.parent = armature

        # Create vertex groups for bones
        for bone_index in flver_mesh.bone_indices:
            try:
                obj.vertex_groups.new(name=flver_data.bones[bone_index].name)
            except IndexError:
                pass

    # Use bmesh for UVs and bone weights
    bm = bmesh.new()
    bm.from_mesh(mesh)

    # Create UV layer
    uv_layer = bm.loops.layers.uv.new()
    for face in bm.faces:
        for loop in face.loops:
            u, v = inflated_mesh.vertices.uv[loop.vert.index][:2]
            loop[uv_layer].uv = (u, 1.0 - v)
        face.smooth = True

    # Apply bone weights (only if armature exists)
    if armature is not None:
        weight_layer = bm.verts.layers.deform.new()

        debug_count = 0

        for vert in bm.verts:
            try:
                weights = inflated_mesh.vertices.bone_weights[vert.index]
                indices = inflated_mesh.vertices.bone_indices[vert.index]

                if debug_count < 5:
                    print(f"=== Vertex {vert.index} ===")
                    print(
                        f"  mesh.bone_indices (palette): {list(flver_mesh.bone_indices)[:10]}...")
                    print(f"  vertex bone_indices: {indices}")
                    print(f"  vertex bone_weights: {weights}")
                    print(f"  num vertex groups: {len(obj.vertex_groups)}")
                    debug_count += 1

                for index, weight in zip(indices, weights):
                    if weight != 0.0:
                        vert[weight_layer][index] = weight
            except IndexError:
                continue

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def get_rotation_matrix(bone):
    """Get rotation matrix from bone's rotation (Y, Z, X order)."""
    return (
        Matrix.Rotation(bone.rotation[1], 4, 'Y') @
        Matrix.Rotation(bone.rotation[2], 4, 'Z') @
        Matrix.Rotation(bone.rotation[0], 4, 'X')
    )


def create_armature(name, collection, flver_data, z_up):
    """
    Create a Blender armature from FLVER bone data.

    Args:
        name (str): Base name for the armature.
        collection (Collection): Blender collection to place the armature in.
        flver_data (Flver): FLVER data containing bone information.
        z_up (bool): If True, convert to Z-up coordinate system.

    Returns:
        Object: The armature object, or None if no bones.
    """
    if len(flver_data.bones) == 0:
        return None

    armature = bpy.data.objects.new(name, bpy.data.armatures.new(name))
    collection.objects.link(armature)
    armature.data.display_type = "OCTAHEDRAL"
    armature.show_in_front = True

    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.editmode_toggle()

    # Create all edit bones first
    root_bones = []
    for f_bone in flver_data.bones:
        bone = armature.data.edit_bones.new(f_bone.name)
        if f_bone.parent_index < 0:
            root_bones.append(bone)

    # Process bones using parent chain traversal
    def transform_bone(bone_index, parent_matrix):
        if bone_index < 0 or bone_index >= len(flver_data.bones):
            return

        flver_bone = flver_data.bones[bone_index]
        edit_bone = armature.data.edit_bones[bone_index]

        # Set parent if valid
        if 0 <= flver_bone.parent_index < len(flver_data.bones):
            edit_bone.parent = armature.data.edit_bones[flver_bone.parent_index]

        # Get local transform components
        translation_vector = Vector(flver_bone.translation)
        rotation_matrix = get_rotation_matrix(flver_bone)

        # Compute head position from parent matrix
        head = parent_matrix @ translation_vector
        # Tail uses LOCAL rotation only (like original code)
        tail = head + rotation_matrix @ Vector((0, 0.05, 0))

        # Apply coordinate conversion
        edit_bone.head = convert_coordinates(head[0], head[1], head[2], z_up)
        edit_bone.tail = convert_coordinates(tail[0], tail[1], tail[2], z_up)

        # Compute matrix for children
        child_matrix = parent_matrix @ Matrix.Translation(
            translation_vector) @ rotation_matrix

        # Process child
        if flver_bone.child_index >= 0 and flver_bone.child_index < len(flver_data.bones):
            transform_bone(flver_bone.child_index, child_matrix)

        # Process sibling (with same parent matrix)
        if flver_bone.next_sibling_index >= 0 and flver_bone.next_sibling_index < len(flver_data.bones):
            transform_bone(flver_bone.next_sibling_index, parent_matrix)

    # Start from bone 0 if it exists
    if len(flver_data.bones) > 0:
        transform_bone(0, Matrix())

    # Post-process to connect bones (like original code)
    def connect_bone(bone):
        children = bone.children
        if len(children) == 0:
            parent = bone.parent
            if parent is not None:
                direction = parent.tail - parent.head
                direction.normalize()
                length = (bone.tail - bone.head).magnitude
                bone.tail = bone.head + direction * length
            return
        if len(children) > 1:
            for child in children:
                connect_bone(child)
            return
        child = children[0]
        bone.tail = child.head
        child.use_connect = True
        connect_bone(child)

    for bone in root_bones:
        connect_bone(bone)

    bpy.ops.object.editmode_toggle()
    return armature
