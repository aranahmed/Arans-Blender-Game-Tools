import bpy
from bpy.props import StringProperty, BoolProperty, IntProperty
from bpy.types import Operator, Panel




class UEExportPanel(bpy.types.Panel):
    bl_label = "Unreal Export"
    bl_idname = "VIEW3D_PT_unreal_export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Game Tools'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Export path property
        layout.prop(scene, "ue_export_path")

        # VFX Toggle
        layout.prop(scene, "ue_vfx_toggle", text="VFX Mesh")
        
        # Toggle for single or multiple objects
        layout.prop(scene, "ue_export_multiple", text="Export Multiple Objects")
        
        # Export button
        layout.operator("export_scene.ue_export", icon='EXPORT')



class PrefixForUE(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Prefix Name Changer"
    bl_idname = "VIEW3D_PT_prefix_for_ue"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Game Tools'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Adds a text box for the prefix
        layout.prop(scene, "prefix_for_ue")
       

        # Add the button to execute the operator
        layout.operator("object.set_prefix_ue", text="Set Prefix")

class OBJECT_OT_SetPrefix(bpy.types.Operator):
    """Set Prefix for UE Assets"""
    bl_idname = "object.set_prefix_ue"
    bl_label = "Set Prefix for UE"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        """
        This function is called when the button is clicked.
        It sets the prefix for UE assets.
        """
        prefix = context.scene.prefix_for_ue
        is_vfx = context.scene.ue_vfx_toggle    # Check if the VFX toggle is enabled
        # Check if the prefix is valid
        if not prefix:
            self.report({'ERROR'}, "Invalid Prefix")
            return {'CANCELLED'}
        
        for obj in context.selected_objects:
            self.report({'INFO'},f'{len(context.selected_objects)}')
            if obj.type == 'MESH':
                
                if "original_name" not in obj:

                    # Store the original name in a custom property
                    obj["original_name"] = obj.name

                # Reset the name to the original name before applying the new prefix # Avoids the issue of having multiple prefixes
                obj.name = obj["original_name"]

                full_prefix = f"{prefix}_VFX" if is_vfx else prefix

                if not obj.name.startswith(f"{full_prefix}_"):
                    # Set the prefix for the object
                    obj.name = f"{full_prefix}_{obj['original_name']}"

                else:
                    self.report({'INFO'}, f"Object {obj.name} ' already has the prefix {full_prefix}'")
                    """
                    # Export the object with the new name
                    bpy.ops.export_scene.fbx(filepath=f"{context.scene.ue_export_path}/{obj.name}.fbx", use_selection=True)
                    """
            self.report({'INFO'}, f"Prefix set to {prefix}")
        return {'FINISHED'}
    
def properties():
    bpy.types.Scene.prefix_for_ue = StringProperty(
        name="Prefix for Unreal Static Mesh",
        description="Prefix for UE Assets",
        default="SM"
    )
    bpy.types.Scene.ue_vfx_toggle = BoolProperty(
        name="VFX Mesh",
        description="Is it a VFX mesh?",
        default=False
    )
    bpy.types.Scene.ue_export_path = StringProperty(
        name="Export Path",
        description="Directory to export Unreal assets to",
        default="//",
        subtype='DIR_PATH'
    )
    bpy.types.Scene.ue_export_multiple = BoolProperty(
        name="Export Multiple",
        description="Export multiple objects",
        default=False
    )


classes = [UEExportPanel, PrefixForUE, OBJECT_OT_SetPrefix]

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

