import bpy
from bpy.props import StringProperty, BoolProperty, IntProperty
from bpy.types import Operator, Panel


obj = bpy.context.active_object

import csv


# --- CONFIGURATION ---
csv_path = "I:/Blender/MyScripts/csv_to_json/GameData.csv"  # Update this path!
add_to = "material"  # Options: 'object', 'material'


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

def CheckAssetType(asset_name):
    # This function can be implemented as needed
    pass



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

        layout.separator()

        layout.prop_decorator



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
        layout.operator("object.set_prefix_ue", icon='NONE')

