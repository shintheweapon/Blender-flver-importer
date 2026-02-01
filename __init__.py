bl_info = {
    "name": "FLVER Importer",
    "description": "Import FLVER model files from FromSoftware games",
    "author": "Felix Benter",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "category": "Import-Export",
    "location": "File > Import",
    "warning": "",
    "support": "COMMUNITY",
    "wiki_url": "https://github.com/FelixBenter/FromSoftware-Blender-Importer",
    "tracker_url": "https://github.com/FelixBenter/FromSoftware-Blender-Importer/issues",
}

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, CollectionProperty, EnumProperty
from pathlib import Path


class FLVER_OT_importer(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.flver"
    bl_label = "FromSoftware FLVER (.flver)"
    bl_options = {"REGISTER", "UNDO"}

    filter_glob: StringProperty(
        default="*.flver",
        options={"HIDDEN"}
    )

    files: CollectionProperty(
        type=bpy.types.OperatorFileListElement,
        options={"HIDDEN", "SKIP_SAVE"}
    )

    directory: StringProperty(
        subtype="DIR_PATH"
    )

    coordinate_system: EnumProperty(
        name="Coordinate System",
        items=[
            ('Z_UP', "Z-up (Blender)", "Convert to Blender's Z-up coordinate system"),
            ('Y_UP', "Y-up (Native)", "Keep FromSoftware's Y-up coordinate system"),
        ],
        default='Z_UP',
    )

    def execute(self, context):
        from .importer import import_flver

        z_up = (self.coordinate_system == 'Z_UP')

        for file in self.files:
            file_path = Path(self.directory) / file.name
            import_flver(file_path, z_up=z_up)

        return {"FINISHED"}


def menu_import(self, context):
    self.layout.operator(FLVER_OT_importer.bl_idname)


def register():
    bpy.utils.register_class(FLVER_OT_importer)
    bpy.types.TOPBAR_MT_file_import.append(menu_import)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_import)
    bpy.utils.unregister_class(FLVER_OT_importer)
