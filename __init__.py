import bpy

from bpy.props import StringProperty, BoolProperty, IntProperty
from bpy.types import Operator, Panel



bl_info = {
    "name": "Arans Game Tools",
    "description": "Description of this addon",
    "author": "Aran Ahmed",
    "version": (0, 0, 1),
    "blender": (4, 3, 0),
    "location": "View3D",
    "warning": "Early version.",
    "wiki_url": "",
    "category": "Game Development",
}

from .renaming_export import (
    UEExportPanel, PrefixForUE, OBJECT_OT_SetPrefix, properties
)


# class SuffixForLODAssets(bpy.types.Panel):
#     bl_label = "Renamer For UE LODs"
#     bl_idname = "VIEW3D_PT_suffix_for_ue_lods"
#     bl_space_type = 'VIEW_3D'
#     bl_region_type = 'UI'
#     bl_category = 'Game Tools'

    
#     def execute(self, context):
#         """
#         This function is called when the button is clicked.
#         It sets the suffix for UE LODs.
#         """
#         lod_count = context.scene.ue_lod_count
#         # Check if the lod_count is valid
#         if lod_count < 0:
#             self.report({'ERROR'}, "Invalid LOD count")
#             return {'CANCELLED'}
        
#         for i in range(lod_count):
#             # Set the suffix for each LOD
#             context.scene.suffix_for_ue_lods = f"LOD{i}"
#             for obj in context.selected_objects:
#                 if obj.type == 'MESH':
#                     # Set the suffix for the object
#                     obj.name = f"{obj.name}_{context.scene.suffix_for_ue_lods}"
#                     """""
#                     # Export the object with the new name
#                     bpy.ops.export_scene.fbx(filepath=f"{context.scene.ue_export_path}/{obj.name}.fbx", use_selection=True)
#                     """
#         self.report({'INFO'}, f"Suffix set to {context.scene.suffix_for_ue_lods} for LODs")
#         return {'FINISHED'}
 

#     """
#     If You Click this button, it should set the Suffix as UCX for UE LODs
#     """

#     def draw(self, context):
#         layout = self.layout
#         scene = context.scene

#         # Export path property
#         layout.prop(scene, "suffix_for_ue_lods")
        
       
        
#         # # Export button
#         # layout.operator("export_scene.ue_export", icon='EXPORT')


    
class VIEW3D_PT_CreateLightMapUVs(bpy.types.Panel):
        
    """
    This operator will create lightmap UVs for the selected objects

    Only do on static meshes, not on VFX meshes
    
    generate One image texture

    Two UVs

    UV Map 1 : Normal UVs
    UV Map 2 : Lightmap UVs

    """
    bl_label = "Unreal Export"
    bl_idname = "VIEW3D_PT_create_lightmap_uvs"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Game Tools'
    bl_label = "Create Lightmap UVs"
    

    
    def draw(self, context):
        layout = self.layout
        scene = context.scene   

        # Export path property
        layout.prop(scene, "create_lightmap_uvs")
        
        # Export button
        layout.operator("object.create_lightmap_uvs", icon='EXPORT')

class OBJECT_OT_CreateLightmapUVs(bpy.types.Operator):

    """Create Lightmap UVs for the selected objects"""
    bl_idname = "object.create_lightmap_uvs"
    bl_label = "Create Lightmap UVs"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Create lightmap UVs for the selected objects"

    def execute(self, context):
        """
        This function is called when the button is clicked.
        It creates lightmap UVs for the selected objects.
        """
        # Check if the selected object is a mesh
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                
                # Create new lightmap UV channel
                if "lightmap_uv_channel" not in obj.data.uv_layers:
                    obj.data.uv_layers.new(name="lightmap_uv_channel", do_init=True)
                else:
                    self.report({'INFO'}, f"Lightmap UVs already exist for :{obj.name}")
    

                # Set the active UV map to the lightmap UV channel
                obj.data.uv_layers.active = obj.data.uv_layers["lightmap_uv_channel"]
                bpy.context.object.data.uv_layers["lightmap_uv_channel"].active_render = True

                # Unwrap the mesh using the lightmap UV channel
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')

                # Unwrap the mesh using the lightmap UV channel if the checkbox is checked
                if context.scene.create_lightmap_uvs:
                    bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)


                bpy.ops.object.mode_set(mode='OBJECT')
                
                self.report({'INFO'}, f"Lightmap UVs created for {obj.name}")
            else:
                self.report({'ERROR'}, f"{obj.name} is not a mesh")
                return {'CANCELLED'}
        return {'FINISHED'}

def properties():

        
    bpy.types.Scene.prefix_for_ue = StringProperty(
    name="PREFIX FOR UNREAL Static Mesh",
    description="PrefixSet for UE Assets",
    default= "SM",
        
    )
    
    bpy.types.Scene.prefix_for_ue = StringProperty(
        name="PREFIX FOR UNREAL VFX Mesh",
        description="PrefixSet for UE Assets that are VFX meshes",
        default= "SM",
        subtype='DIR_PATH'
    )

    bpy.types.Scene.suffix_for_ue_lods = IntProperty(
        name="Number of LODs",
        description="Suffix for LODs", 
        default=0,
        min=0,
        max=6,
    )

    bpy.types.Scene.ue_vfx_toggle = BoolProperty(
        name="VFX MESH",
        description="Ïs it a VFX mesh?",
        default=False, 
    )   

    bpy.types.Scene.ue_export_path = StringProperty(
        name="Export Path",
        description="Directory to export Unreal assets to",
        default="//", 
        subtype='DIR_PATH'
    )

    bpy.types.Scene.ue_export_multiple = BoolProperty(
        name="Export Multiple",
        description="Toggle to export multiple objects or a single object",
        default=False
    )


    bpy.types.Scene.create_lightmap_uvs = BoolProperty(
        name="AutoUnwrap Lightmap UVs",
        description="Create lightmap UVs for the selected objects",
        default=False
    )

        
classes = [UEExportPanel, PrefixForUE, OBJECT_OT_SetPrefix, VIEW3D_PT_CreateLightMapUVs, OBJECT_OT_CreateLightmapUVs]

def register():
    # Register the classes
    for cls in classes:
        bpy.utils.register_class(cls)

    # Register the properties
    properties()

    
def unregister():
    for cls in classes:
        if hasattr(bpy.types, cls.__name__):  # Check if the class is registered
            bpy.utils.unregister_class(cls)

if __name__ == "__main__":
        
    try:
        unregister()
    except Exception:
        pass
    register()