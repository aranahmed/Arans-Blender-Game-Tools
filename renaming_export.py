import bpy
from bpy.props import StringProperty, BoolProperty, IntProperty
from bpy.types import Operator, Panel
import os

import pprint as pprint

# import pathlib

# path_to_json = pathlib.Path('.') / "UnrealExport"
#print(f"Path to JSON: {path_to_json}")


obj = bpy.context.active_object


#import csv
import json



# --- CONFIGURATION ---
#csv_path = "I:/Blender/MyScripts/csv_to_json/GameData.csv"  # Update this path!
add_to = "material"  # Options: 'object', 'material'

def show_message(message="", title="Error", icon='ERROR'):
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)



# not using atm
""" # Function to find asset name in CSV and compare with selected object
def FindAssetName():
    # --- READ CSV ---
    material_map = {}
    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)  # Read header row
        for row in reader:
            row_data = {header.strip(): value.strip() for header, value in zip(headers, row)}
            print(f"Row data: {row_data}")

            if 'AssetName' in row_data:
                asset_name = row_data['AssetName']
                # Compare with selected object name
                if obj.name != asset_name:
                    print(f"Error: Selected object name '{obj.name}' does not match asset name '{asset_name}' from CSV.")
                else:
                    if "original_name" not in obj:
                        
                        # Store the original name in a custom property
                        obj["original_name"] = obj.name
                    # Store the asset name in a custom property
                    obj["AssetName"] = asset_name
                    print(f"Asset name '{asset_name}' matches the selected object.")

                    # Parse the asset type from the row_data if present
                    asset_type = row_data.get('Category', None)
                    new_name = obj.name  # Default to current name
                    if asset_type:
                        obj["AssetType"] = asset_type
                        print(f"Asset type '{asset_type}' found and stored.")
                        if asset_type == "Environment" or "Prop":
                            #obj.name = obj["original_name"]  # Reset to original name
                            obj["AssetType"] = "StaticMesh"
                            new_name = f"SM_{asset_name}"
                        elif asset_type == "Character": 
                            #obj.name = obj["original_name"]  # Reset to original name
                            obj["AssetType"] = "SkeletalMesh"
                            new_name = f"SK_{asset_name}"
                    else:
                        print("Asset type not found in CSV row.")
                        obj.name = new_name

                    return True, asset_name, asset_type

            # Example: store in material_map if those columns exist
            if 'obj_name' in row_data and 'mat_name' in row_data:
                material_map[row_data['obj_name']] = row_data['mat_name']
"""

# not using atm
""" # Function to check asset type based on the asset name
def CheckAssetType(asset_name):
    
    pass
"""

def show_message(message="", title="Error", icon='ERROR'):
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)

def export_fbx(obj, export_path, apply_transform=True):
    # Ensure the export directory exists
    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    # Deselect all, select only the object to export
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    # Export FBX with Unreal-friendly settings
    bpy.ops.export_scene.fbx(
        filepath=export_path,
        use_selection=True,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        object_types={'MESH', 'ARMATURE'},
        bake_space_transform=apply_transform,
        axis_forward='-Z',
        axis_up='Y',
        use_mesh_modifiers=True,
        add_leaf_bones=False,
        path_mode='AUTO',
        use_custom_props=True
    )


class UEExportPanel_PT_Export(bpy.types.Panel):
    bl_label = "Unreal Export"
    bl_idname = "VIEW3D_PT_unreal_export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Game Tools'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Export path property
        layout.prop(scene, "ue_export_path", text="Export Path", icon='FILE_FOLDER')
        layout.prop(scene, "ue_export_with_custom_props", text="Export with Custom Properties")

        # VFX Toggle
        layout.prop(scene, "ue_vfx_toggle", text="VFX Mesh")
        # Toggle for single or multiple objects
        layout.prop(scene, "ue_export_multiple", text="Export Multiple Objects")
        
        #layout.prop(scene, "ue_export", text="Export Mesh", icon='EXPORT')
        
        # Export button
        layout.operator("export_scene.ue_export", icon='EXPORT')

        layout.separator()

        layout.prop(scene, "custom_props_toggle", text="Export Custom Properties")
        if scene.custom_props_toggle:
            layout.prop(scene, "export_custom_props", text="Export JSON Path")
            layout.operator("ueexportpanel.export_custom_props", icon='EXPORT')

        

class UEExportPanel_OT_Export(bpy.types.Operator):
    bl_idname = "export_scene.ue_export"
    bl_label = "Export to Unreal Engine"
    bl_description = "Export the selected object(s) to Unreal Engine format"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        export_path = bpy.path.abspath(scene.ue_export_path)
        if not os.path.isdir(export_path):
            os.makedirs(export_path, exist_ok=True)
        obj = context.active_object
        if not obj:
            self.report({'ERROR'}, "No active object to export.")
            return {'CANCELLED'}
        export_name = obj.name


        selected_objects = context.selected_objects
        if not selected_objects:
            self.report({'ERROR'}, "No objects selected for export.")
            return {'CANCELLED'}
        
        write_custom_properties_to_json(context.active_object, scene.export_custom_props)
        
        for obj in selected_objects:
            export_name = obj.name
            fbx_path = os.path.join(export_path, f"{export_name}.fbx")
            export_fbx(obj, fbx_path, apply_transform=True)
            if obj["original_name"] in obj.name:
                return {'FINISHED'} 
            else:
                write_custom_properties_to_json(context.active_object, scene.export_custom_props)

        # If exporting multiple objects, use the first selected object's name
        #export_fbx(obj, fbx_path, apply_transform=True)



        
        # vfx_toggle = scene.ue_vfx_toggle
        # export_multiple = scene.ue_export_multiple
        # #prefix_for_ue = scene.prefix_for_ue
        # export_custom_props = scene.ue_export_with_custom_props
        # if not export_path:
        #     self.report({'ERROR'}, "Export path is not set.")
        #     return {'CANCELLED'}
        # if export_custom_props:
        #     custom_props_path = bpy.path.abspath(export_path)
        #     if export_multiple:
        #         #self.report({'ERROR'}, "Custom properties export is not supported for multiple objects.")
        #         for obj in context.selected_objects:
        #             write_custom_properties_to_json(obj, custom_props_path)
        #             print(f"Custom properties for {obj.name} exported to {custom_props_path}")
        #             export_fbx(obj, fbx_path, apply_transform=True)
        #     else:
        #         write_custom_properties_to_json(context.active_object, scene.export_custom_props)
        #         export_fbx(context.active_object, fbx_path, apply_transform=True)
                

        #     if not custom_props_path:
        #         self.report({'ERROR'}, "Custom properties export path is not set.")
        #         return {'CANCELLED'}
        # if not context.selected_objects:
        #     self.report({'ERROR'}, "No objects selected for export.")
        #     return {'CANCELLED'}
        
      

        
        return {'FINISHED'}



class UEExport_PT_PrefixNameChanger(bpy.types.Panel):
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
        layout.operator("object.set_prefix_ue", icon='NONE')

# Register the operator classes

def write_custom_properties_to_json(obj, filepath):
    
    """Appends or Writes custom properties of the object to a JSON file."""
    abs_path = bpy.path.abspath(filepath)
    # Ensure json extension on file path
    if not abs_path.endswith('.json'):
        abs_path += '.json'
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)        

    # Prepare the new data
    custom_props = {k: v for k, v in obj.items() if not k.startswith("_")}
    unreal_obj = {"name": obj.name}
    unreal_obj.update(custom_props)

    
    # Loads existing data if the file exists
    if os.path.exists(abs_path):
        with open(abs_path, 'r', encoding='utf-8') as f:
            try: 
                data = json.load(f)
                if not isinstance(data, list):
                    data = [data]
            except Exception:
                show_message("Error reading JSON file. It may be corrupted.", title="JSON Error", icon='ERROR')
                data = []

    else: 
        data = []

    # Update or append the new object data
    updated = False
    for i, entry in enumerate(data):
        if entry.get("name") == obj.name:
            data[i] = unreal_obj
            updated = True
            break
    if not updated:
        data.append(unreal_obj)

 
    if "original_name" in obj:
        del obj["original_name"]  # Remove original_name if it exists
    
    # Write to JSON file
    if not custom_props:
        show_message("No custom properties found to export.", title="No Custom Properties", icon='ERROR')
    with open(abs_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    #   bpy.context.window_manager.popup_menu(f"Custom properties written to {filepath}.", title="Custom Properties Exported", icon='INFO')
    
class UEExportPanel_OT_ExportCustomProps(bpy.types.Operator):
    bl_idname = "ueexportpanel.export_custom_props"
    bl_label = "Export Custom Properties"
    bl_description = "Export custom properties of selected objects to a JSON file"
    bl_options = {'REGISTER', 'UNDO'}
    


    def execute(self, context):
        filepath = bpy.path.abspath(context.scene.export_custom_props)
        if not filepath:
             print("No export path specified for custom properties.")

        for obj in context.selected_objects:
            write_custom_properties_to_json(obj, filepath)
        return {'FINISHED'}
    
classes = [
    UEExportPanel_PT_Export,
    UEExportPanel_OT_ExportCustomProps, 
    UEExportPanel_OT_Export

]

properties = {
    "ue_export_path": StringProperty(
        name="Export Path",
        description="Path to export the asset",
        default="//",
        subtype='DIR_PATH'
    ),
    "ue_vfx_toggle": BoolProperty(
        name="VFX Mesh",
        description="Toggle for VFX mesh export",
        default=False
    ),
    "ue_export_multiple": BoolProperty(
        name="Export Multiple Objects",
        description="Toggle for exporting multiple objects",
        default=False
    ),
    "prefix_for_ue": StringProperty(
        name="Prefix for UE",
        description="Prefix to add to object names for Unreal Engine export",
        default=""
    ),
    "custom_props_toggle": BoolProperty(
        name="Export Custom Properties",
        description="Toggle to export custom properties as JSON",
        default=False
    ),
    "export_custom_props": StringProperty(
        name="Export JSON Path",
        description="Path to export custom properties as JSON",
        default="//custom_properties.json",
        subtype='FILE_PATH'
    ),
    "ue_export_with_custom_props": BoolProperty(
        name="Export with Custom Properties",
        description="Toggle to export with custom properties",
        default=False
    ),
    "export_scene.ue_export": StringProperty(
        name="Export Mesh",
        description="Button to export the mesh",
        default="Export Mesh",
    )
}

def register(): 
    
    for prop_name, prop in properties.items():
        setattr(bpy.types.Scene, prop_name, prop)
    for cls in classes:
        bpy.utils.register_class(cls)
    

   

def unregister():
    for prop_name, prop in properties.items():
        delattr(bpy.types.Scene, prop_name, prop)
    
    for cls in classes:
        bpy.utils.unregister_class(cls)

     

if __name__ == "__main__":
    register()
