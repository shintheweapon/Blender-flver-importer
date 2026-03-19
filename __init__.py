import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import BoolProperty, StringProperty, CollectionProperty, EnumProperty
from pathlib import Path


_translations = {
    "zh_CN": {
        ("*", "Coordinate System"):
            "坐标系",
        ("*", "Z-up (Blender)"):
            "Z轴朝上 (Blender)",
        ("*", "Convert to Blender's Z-up coordinate system"):
            "转换为 Blender 的 Z 轴朝上坐标系",
        ("*", "Y-up (Native)"):
            "Y轴朝上 (原生)",
        ("*", "Keep FromSoftware's Y-up coordinate system"):
            "保留 FromSoftware 的 Y 轴朝上坐标系",
        ("*", "Connect Child Bones"):
            "连接子骨骼",
        ("*", "Connect single-child bones to their parent (sets use_connect). Branching bones are unaffected."):
            "将单子骨骼连接到父骨骼（设置 use_connect）。分支骨骼不受影响。",
    },
}
_translations["zh_HANS"] = _translations["zh_CN"]


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

    connect_bones: BoolProperty(
        name="Connect Child Bones",
        description="Connect single-child bones to their parent (sets use_connect). "
                    "Branching bones are unaffected.",
        default=True,
    )

    def execute(self, context):
        from .importer import import_flver

        z_up = (self.coordinate_system == 'Z_UP')
        connect_bones = self.connect_bones

        for file in self.files:
            file_path = Path(self.directory) / file.name
            import_flver(file_path, z_up=z_up, connect_bones=connect_bones)

        return {"FINISHED"}


def menu_import(self, context):
    self.layout.operator(FLVER_OT_importer.bl_idname)


def register():
    bpy.app.translations.register(__name__, _translations)
    bpy.utils.register_class(FLVER_OT_importer)
    bpy.types.TOPBAR_MT_file_import.append(menu_import)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_import)
    bpy.utils.unregister_class(FLVER_OT_importer)
    bpy.app.translations.unregister(__name__)
