import bpy

from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty
import csv

# --- CONFIGURATION ---
CSV_PATH = "I:/Blender/MyScripts/GameData.csv"  # Update this path!
PREFIX_LIST = ['SM_', 'SK_', 'MM_']  # Unreal Engine naming conventions

# --- UTILITY FUNCTIONS ---

def is_triangle_count_within_budget(obj):
    if obj.type != 'MESH':
        return None  # Not applicable
    asset_name = strip_prefix(obj.name)
    row = CSV2MESH_OT_SetCSVData.get_csv_row_for_asset(asset_name)
    if not row:
        return None  # No CSV row found
    max_tris = int(row.get('MaxTris', 0))
    actual_triangles = len(obj.data.polygons)
    return actual_triangles <= max_tris

def strip_prefix(name, prefixes=PREFIX_LIST):
    for prefix in prefixes:
        if name.startswith(prefix):
            return name[len(prefix):]
    # If no known prefix, strip up to first underscore
    if "_" in name:
        return name.split("_", 1)[1]
    return name


def show_message(message="", title="Error", icon='ERROR'):
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)



def clear_custom_properties(obj):
    keys_to_remove = [k for k in obj.keys() if not k.startswith("_")]
    for k in keys_to_remove:
        del obj[k]
    show_message(f"Cleared custom properties for {obj.name}.", title="Custom Properties Cleared", icon='INFO')

# def print_custom_properties(obj):
#     msg = f"Custom properties for {obj.name}:\n"
#     for k in obj.keys():
#         if not k.startswith("_"):
#             msg += f"  {k}: {obj[k]}\n"
#     show_message(msg, title="Custom Properties", icon='INFO')

# --- CSV DATA ACCESS ---

class CSV2MESH_OT_SetCSVData(bpy.types.Operator):

    bl_idname = "csv2mesh.set_csv_path"
    bl_label = "Set CSV Path"
    bl_description = "Set the path to the CSV file containing asset data"
    bl_options = {'REGISTER', 'UNDO'}
    
   
    def execute(self, context):
        global CSV_PATH
        CSV_PATH = self.csv_path
        show_message(f"CSV path set to: {CSV_PATH}", title="CSV Path Set", icon='INFO')
        self.report({'INFO'}, f"CSV path set to: {CSV_PATH}")
        return {'FINISHED'}
    
    def get_csv_row_for_asset(asset_name):
        asset_name = asset_name # Normalize asset name
        csv_path = bpy.context.scene.csv_path.lower()
        with open(csv_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if strip_prefix(row.get('AssetName', '')).lower() == strip_prefix(asset_name).lower():
                    return row
                if strip_prefix(row.get('AssetName', '')).lower() in asset_name.lower():
                    return row
        return None
    
# --- CSV Data Write Functions ---

    # very risky function, use with caution
    
def update_actual_tris_in_csv(asset_name, actual_tris, csv_path):
    if csv_path is None or not csv_path:
        show_message("CSV path is not set. Please set the CSV path first.", title="CSV Path Not Set", icon='ERROR')
        return
    rows = []
    updated = False
    
    # Read all rows
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames
        for row in reader:
            if strip_prefix(row.get('AssetName', '')) == strip_prefix(asset_name):
                row['ActualTris'] = str(actual_tris)
                updated = True
            rows.append(row)
    # Write all rows back
    if updated:
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        show_message(f"Updated ActualTris for {asset_name} to {actual_tris}.", title="CSV Updated", icon='INFO')
    else:
        show_message(f"Asset {asset_name} not found in CSV.", title="CSV Update Failed", icon='ERROR')

# --- MAIN LOGIC FUNCTIONS ---

def process_asset(obj):
    """Rename and tag the object based on CSV data."""
    clear_custom_properties(obj)
    asset_name = strip_prefix(obj.name).lower()
    row = CSV2MESH_OT_SetCSVData.get_csv_row_for_asset(asset_name)
    

    # Store original name if not already present
    if "original_name" not in obj:
        obj["original_name"] = obj.name

    # Assign asset name property
    obj["AssetName"] = row['AssetName']
    show_message(f"Asset name '{row['AssetName']}' matches the selected object '{obj.name}'.", title="Asset Name Match", icon='INFO')

    # Asset type logic
    asset_type = row.get('Category', None)
    if asset_type:
        show_message(f"Asset type '{asset_type}' found and stored.", title="Asset Type", icon='INFO')
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
        show_message("Asset type not found in CSV row.", title="Asset Type Not Found", icon='ERROR')
        print(f"obj.name: {obj.name}, new_name: {new_name}")
        print(f"Comparison result: {obj.name.lower() == new_name.lower()}")
        new_name = obj.name


    # Rename if needed
    if obj.name.lower() != new_name.lower():
        bpy.ops.csv2mesh.show_name_correction('INVOKE_DEFAULT', incorrect_name=obj.name, correct_name=new_name)
        show_message(f"Renaming object from '{obj.name}' to '{new_name}'", title="Renaming Object", icon='INFO')
    else:
        show_message(f"No renaming needed for {obj.name}, already matches '{new_name}'.", title="No Renaming Needed", icon='INFO')

    # Optionally assign master material
    assign_master_material(obj, row)

def assign_master_material(obj, row=None):
    """Assigns the master material from CSV to the object."""
    if not row:
        asset_name = strip_prefix(obj.name)
        row = CSV2MESH_OT_SetCSVData.get_csv_row_for_asset(asset_name)
        if not row:
            show_message(f"No CSV row found for {obj.name} for material assignment.", title="CSV Row Not Found", icon='ERROR')
            return

    master_material = row.get('MasterMaterial', None)
    if not master_material:
        show_message(f"No MasterMaterial found for {obj.name} in CSV.", title="Master Material Not Found", icon='ERROR')
        return

    # Ensure MM_ prefix
    if not master_material.startswith("MM_"):
        master_material = "MM_" + master_material

    obj["MasterMaterial"] = master_material
    show_message(f"Assigned MasterMaterial '{master_material}' to {obj.name} as custom property.", title="Master Material Assigned", icon='INFO')

    # Assign Blender material
    mat = bpy.data.materials.get(master_material)
    if not mat:
        mat = bpy.data.materials.new(name=master_material)
        show_message(f"Created new material: {master_material}", title="Material Created", icon='INFO')
    if obj.type == 'MESH':
        if not obj.data.materials:
            obj.data.materials.append(mat)
        else:
            for i in range(len(obj.data.materials)):
                obj.data.materials[i] = mat
        #show_message(f"Assigned material '{master_material}' to {obj.name}.", title="Material Assigned", icon='INFO')
    else:
        show_message(f"Object '{obj.name}' is not a mesh, cannot assign material.", title="Invalid Object Type", icon='ERROR')

# --- BLENDER OPERATORS AND PANEL ---

class CSV2MESH_OT_ProcessSelected(bpy.types.Operator):
    bl_idname = "csv2mesh.process_selected"
    bl_label = "Process Selected Assets"
    bl_description = "Process selected objects using CSV data"

    def execute(self, context):
        for obj in context.selected_objects:
            process_asset(obj)
            #print_custom_properties(obj)
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
        row = layout.row()
        
        row.prop(context.scene, "csv_path", text="CSV Path")
        
        layout.operator("csv2mesh.process_selected", icon='CHECKMARK')
        layout.operator("csv2mesh.assign_master_material", icon='MATERIAL')
        layout.operator("csv2mesh.clear_custom_props", icon='X')

        layout.separator()
        layout.label(text="Asset Management Tools", icon='ASSET_MANAGER')
        #layout.operator("csv2mesh.show_name_correction", text="Asset Name Correction", icon='ERROR')
        layout.prop(context.scene, "show_custom_props", text="Display Custom Properties")
        
        def draw_custom_props(self, context):
            
            if context.scene.show_custom_props:
                # Display custom properties of the active object as a read-only list
                obj = context.active_object
                if obj:
                    layout.label(text="Custom Properties:", icon='PRESET')
                    box = layout.box()
                    for k, v in obj.items():
                        if not k.startswith("_"):
                            row = box.row()
                            row.label(text=f"{k}: {v}")
                else:
                    layout.label(text="No active object selected.", icon='ERROR')
        
        draw_custom_props(self, context)

        layout.separator()
        layout.label(text="Mesh Validation Tools", icon='CHECKMARK')
        layout.operator("csv2mesh.validate_triangle_count", text="Validate Triangle Count", icon='TRIA_DOWN')

        def compare_triangle_count(self, context):
            obj = context.active_object
            if obj is not None and context.selected_objects:
               #layout.column(align=True)
               box = layout.box()
               row = box.row()
               col1 = row.column(align=True)
               col2 = row.column(align=True)
               col1.label(text=f"Active Object: {obj.name}", icon='OBJECT_DATA')
               col1.label(text=f"Actual Tris: {len(obj.data.polygons)}")
               #layout.column(align=True)
               col2.label(text="CSV Data", icon='FILE_TEXT')
               col2.label(text=f"Max Tris: {CSV2MESH_OT_SetCSVData.get_csv_row_for_asset(strip_prefix(obj.name)).get('MaxTris', 'N/A')}")


        compare_triangle_count(self, context)
        
        # Show triangle count status for active object
        obj = context.active_object
        if obj is not None and context.selected_objects:
            result = is_triangle_count_within_budget(obj)
            if result is True:
                layout.label(text="Triangle Count: OK", icon='CHECKMARK')
            elif result is False:
                layout.label(text="Triangle Count: Over Budget", icon='ERROR')
            else:
                layout.label(text="Triangle Count: N/A", icon='QUESTION')
        else:
            layout.label(text="No active object selected.", icon='ERROR')
                
        


class CSV2MESH_OT_ShowNameCorrection(bpy.types.Operator):
    bl_idname = "csv2mesh.show_name_correction"
    bl_label = "Asset Name Correction"
    bl_options = {'REGISTER', 'INTERNAL'}

    incorrect_name: StringProperty()
    correct_name: StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.incorrect_name)
        if obj and obj.name != self.correct_name:
            obj.name = self.correct_name
            show_message(f"Renamed '{self.incorrect_name}' to '{self.correct_name}'", title="Asset Renamed", icon='INFO')
            self.report({'INFO'}, f"Renamed '{self.incorrect_name}' to '{self.correct_name}'")
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=350)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Asset Name Correction", icon='INFO')
        box = layout.box()
        row = box.row()
        row.label(text="Incorrect Name", icon='ERROR')
        row.label(text="Correct Name", icon='CHECKMARK')
        row = box.row()
        row.label(text=self.incorrect_name)
        row.label(text=self.correct_name)
        layout.label(text="Do you want to rename the asset?", icon='QUESTION')

class CSV2MESH_OT_DisplayCustomProps(bpy.types.Operator):
    bl_idname = "csv2mesh.display_custom_props"
    bl_label = "Display Custom Properties"
    bl_description = "Display custom properties of selected objects"

    def execute(self, context):
        for obj in context.selected_objects:
            print_custom_properties(obj)
        self.report({'INFO'}, "Displayed custom properties.")
        return {'FINISHED'}
    
class CSV2MESH_OT_ValidateTriangleCount(bpy.types.Operator):
    bl_idname = "csv2mesh.validate_triangle_count"
    bl_label = "Validate Triangle Count"
    bl_description = "Validate triangle count of selected objects against CSV data"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                asset_name = strip_prefix(obj.name)
                row = CSV2MESH_OT_SetCSVData.get_csv_row_for_asset(asset_name)
                if not row:
                    show_message(f"No CSV row found for {obj.name}.", title="CSV Row Not Found", icon='ERROR')
                    continue

                csv_tris = row.get('ActualTris', 0)
               
                within_budget = is_triangle_count_within_budget(obj)
                max_tris = int(row.get('MaxTris', 0))
                actual_triangles = len(obj.data.polygons)

                

                if within_budget:
                    # show_message(
                    #     f"Triangle count within budget for {obj.name}: Expected {max_tris}, got {actual_triangles}.",
                    #     title="Triangle Count Within Budget",
                    #     icon='CHECKMARK'
                    #     )
                    update_actual_tris_in_csv(asset_name, actual_triangles, context.scene.csv_path)
                
                else:
                    show_message(
                f"Triangle count for {obj.name} is over budget: {actual_triangles}. Please use Decimation modifier or reduce polygons",
                title="Triangle Count Over Budget", 
                icon='ERROR'
                )

            else:
                show_message(f"{obj.name} is not a mesh object.", title="Invalid Object Type", icon='ERROR')

        return {'FINISHED'}
    




# --- REGISTRATION ---

classes = (
    CSV2MESH_OT_SetCSVData,
    CSV2MESH_OT_ProcessSelected,
    CSV2MESH_OT_ClearCustomProps,
    CSV2MESH_OT_AssignMasterMaterial,
    CSV2MESH_PT_ToolsPanel,
    CSV2MESH_OT_ShowNameCorrection,
    CSV2MESH_OT_DisplayCustomProps,
    CSV2MESH_OT_ValidateTriangleCount
    
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.csv_path = StringProperty(
        name="CSV Path",
        description="Path to the CSV file containing asset data",
        default=CSV_PATH,
        subtype='FILE_PATH'
    )   

    bpy.types.Scene.show_custom_props = BoolProperty(
        name="Show Custom Properties",
        description="Display custom properties of the active object",
        default=False
    )

    bpy.types.Scene.csv2mesh_json_export_path = StringProperty(
        name="JSON Export Path",
        description="Path to export custom properties as JSON",
        default="//custom_properties.json",
        subtype='FILE_PATH'
    )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
