import bpy

from bpy.props import StringProperty, BoolProperty, IntProperty
from bpy.types import Operator, Panel



bl_info = {
    "name": "Arans Game Tools",
    "description": "Description of this addon",
    "author": "Aran Ahmed",
    "version": (0, 0, 2),
    "blender": (4, 3, 0),
    "location": "View3D",
    "warning": "Early Alpha Version",
    "wiki_url": "https://github.com/aranahmed/Arans-Blender-Game-Tools",
    "category": "Game Development",
}

# from . id_generator import (
#     OBJECT_OT_loose_parts_to_vertex_colors, 
#     VIEW3D_PT_ID_Map_Baker, 
#     OBJECT_OT_bake_vertex_colors_to_image, 
#     OBJECT_OT_detect_overlapping_uvs, properties
# )


# from .renaming_export import (
#     UEExportPanel, PrefixForUE, OBJECT_OT_SetPrefix, properties
# )

from . import renaming_export

# from . import lightmap_generator
from . import id_generator

from . import csv_to_mesh_validator 


modules = [
                renaming_export,
                id_generator,
                csv_to_mesh_validator,
            #     lightmap_generator,
                  ]


# from .LOD_generation_tool import (


def properties():

    # bpy.types.Scene.create_vertex_groups_from_loose_parts = bpy.props.BoolProperty(
    # name="Create Vertex Groups from Loose Parts",
    # description="Create vertex groups from loose parts",
    # default=False
    # )

    # bpy.types.Scene.export_baked_ID = StringProperty(
    #     name="Export Baked ID Location",
    #     description="Export Baked ID",
    #     default= "//",
    #     subtype='DIR_PATH'
    # )
        
    # bpy.types.Scene.prefix_for_ue = StringProperty(
    # name="PREFIX FOR UNREAL Static Mesh",
    # description="PrefixSet for UE Assets",
    # default= "SM",
        
    # )
    
    # bpy.types.Scene.prefix_for_ue = StringProperty(
    #     name="PREFIX FOR UNREAL VFX Mesh",
    #     description="PrefixSet for UE Assets that are VFX meshes",
    #     default= "SM",
    #     subtype='DIR_PATH'
    # )

    # bpy.types.Scene.suffix_for_ue_lods = IntProperty(
    #     name="Number of LODs",
    #     description="Suffix for LODs", 
    #     default=0,
    #     min=0,
    #     max=6,
    # )

    # bpy.types.Scene.ue_vfx_toggle = BoolProperty(
    #     name="VFX MESH",
    #     description="Ïs it a VFX mesh?",
    #     default=False, 
    # )   

    # bpy.types.Scene.ue_export_path = StringProperty(
    #     name="Export Path",
    #     description="Directory to export Unreal assets to",
    #     default="//", 
    #     subtype='DIR_PATH'
    # )

    # bpy.types.Scene.ue_export_multiple = BoolProperty(
    #     name="Export Multiple",
    #     description="Toggle to export multiple objects or a single object",
    #     default=False
    # )
    pass

        
classes = [ 
            
            # OBJECT_OT_loose_parts_to_vertex_colors, 
            # VIEW3D_PT_ID_Map_Baker,
            # OBJECT_OT_bake_vertex_colors_to_image,
            # OBJECT_OT_detect_overlapping_uvs
            ]

def register():
    # Register the classes
    for cls in classes:
        bpy.utils.register_class(cls)

    # Register the properties
    properties()

    for m in modules:
        if hasattr(m, 'register'):
            m.register()


    
def unregister():
    for cls in classes:
        if hasattr(bpy.types, cls.__name__):  # Check if the class is registered
            bpy.utils.unregister_class(cls)

    for m in modules:
        if hasattr(m, 'unregister'):
            m.unregister()
            

if __name__ == "__main__":
        
    try:
        unregister()
    except Exception:
        pass
    register()