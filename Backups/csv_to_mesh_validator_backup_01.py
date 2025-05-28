import bpy
import csv

# --- CONFIGURATION ---
CSV_PATH = "I:/Blender/MyScripts/csv_to_json/GameData.csv"  # Update this path!
PREFIX_LIST = ['SM_', 'SK_', 'MM_']  # Unreal Engine naming conventions

# --- UTILITY FUNCTIONS ---

def strip_prefix(name, prefixes=PREFIX_LIST):
    for prefix in prefixes:
        if name.startswith(prefix):
            return name[len(prefix):]
    # If no known prefix, strip up to first underscore
    if "_" in name:
        return name.split("_", 1)[1]
    return name

def clear_custom_properties(obj):
    keys_to_remove = [k for k in obj.keys() if not k.startswith("_")]
    for k in keys_to_remove:
        del obj[k]
    print(f"Cleared custom properties for {obj.name}.")

def print_custom_properties(obj):
    print(f"Custom properties for {obj.name}:")
    for k in obj.keys():
        if not k.startswith("_"):
            print(f"  {k}: {obj[k]}")

# --- CSV DATA ACCESS ---

def get_csv_row_for_asset(asset_name):
    with open(CSV_PATH, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if strip_prefix(row.get('AssetName', '')) == strip_prefix(asset_name):
                return row
    return None

# --- MAIN LOGIC FUNCTIONS ---

def process_asset(obj):
    """Rename and tag the object based on CSV data."""
    clear_custom_properties(obj)
    asset_name = strip_prefix(obj.name)
    row = get_csv_row_for_asset(asset_name)
    if not row:
        print(f"No CSV row found for {obj.name} (asset '{asset_name}').")
        return

    # Store original name if not already present
    if "original_name" not in obj:
        obj["original_name"] = obj.name

    # Assign asset name property
    obj["AssetName"] = row['AssetName']
    print(f"Asset name '{row['AssetName']}' matches the selected object '{obj.name}'.")

    # Asset type logic
    asset_type = row.get('Category', None)
    if asset_type:
        print(f"Asset type '{asset_type}' found and stored.")
        if asset_type in ("Environment", "Prop"):
            obj["AssetType"] = "StaticMesh"
            new_name = f"SM_{row['AssetName']}"
        elif asset_type == "Character":
            obj["AssetType"] = "SkeletalMesh"
            new_name = f"SK_{row['AssetName']}"
        else:
            obj["AssetType"] = asset_type
            new_name = obj.name  # No change
    else:
        print("Asset type not found in CSV row.")
        new_name = obj.name

    # Rename if needed
    if obj.name != new_name:
        print(f"Renaming object from '{obj.name}' to '{new_name}'")
        obj.name = new_name

    # Optionally assign master material
    assign_master_material(obj, row)

def assign_master_material(obj, row=None):
    """Assigns the master material from CSV to the object."""
    if not row:
        asset_name = strip_prefix(obj.name)
        row = get_csv_row_for_asset(asset_name)
        if not row:
            print(f"No CSV row found for {obj.name} for material assignment.")
            return

    master_material = row.get('MasterMaterial', None)
    if not master_material:
        print(f"No MasterMaterial found for {obj.name} in CSV.")
        return

    # Ensure MM_ prefix
    if not master_material.startswith("MM_"):
        master_material = "MM_" + master_material

    obj["MasterMaterial"] = master_material
    print(f"Assigned MasterMaterial '{master_material}' to {obj.name} as custom property.")

    # Assign Blender material
    mat = bpy.data.materials.get(master_material)
    if not mat:
        mat = bpy.data.materials.new(name=master_material)
        print(f"Created new material: {master_material}")
    if obj.type == 'MESH':
        if not obj.data.materials:
            obj.data.materials.append(mat)
        else:
            for i in range(len(obj.data.materials)):
                obj.data.materials[i] = mat
        print(f"Assigned material '{master_material}' to {obj.name}.")
    else:
        print(f"Object '{obj.name}' is not a mesh, cannot assign material.")

# --- BLENDER OPERATORS AND PANEL ---

class CSV2MESH_OT_ProcessSelected(bpy.types.Operator):
    bl_idname = "csv2mesh.process_selected"
    bl_label = "Process Selected Assets"
    bl_description = "Process selected objects using CSV data"

    def execute(self, context):
        for obj in context.selected_objects:
            process_asset(obj)
            print_custom_properties(obj)
        self.report({'INFO'}, "Processed selected assets.")
        return {'FINISHED'}

class CSV2MESH_OT_ClearCustomProps(bpy.types.Operator):
    bl_idname = "csv2mesh.clear_custom_props"
    bl_label = "Clear Custom Properties"
    bl_description = "Clear custom properties from selected objects"

    def execute(self, context):
        for obj in context.selected_objects:
            clear_custom_properties(obj)
        self.report({'INFO'}, "Cleared custom properties.")
        return {'FINISHED'}

class CSV2MESH_OT_AssignMasterMaterial(bpy.types.Operator):
    bl_idname = "csv2mesh.assign_master_material"
    bl_label = "Assign Master Material"
    bl_description = "Assign master material from CSV to selected objects"

    def execute(self, context):
        for obj in context.selected_objects:
            assign_master_material(obj)
        self.report({'INFO'}, "Assigned master material.")
        return {'FINISHED'}

class CSV2MESH_PT_ToolsPanel(bpy.types.Panel):
    bl_label = "CSV to Mesh Validator"
    bl_idname = "CSV2MESH_PT_tools_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "CSV2Mesh"

    def draw(self, context):
        layout = self.layout
        layout.label(text="CSV Asset Tools")
        layout.operator("csv2mesh.process_selected", icon='CHECKMARK')
        layout.operator("csv2mesh.assign_master_material", icon='MATERIAL')
        layout.operator("csv2mesh.clear_custom_props", icon='X')

# --- REGISTRATION ---

classes = (
    CSV2MESH_OT_ProcessSelected,
    CSV2MESH_OT_ClearCustomProps,
    CSV2MESH_OT_AssignMasterMaterial,
    CSV2MESH_PT_ToolsPanel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()