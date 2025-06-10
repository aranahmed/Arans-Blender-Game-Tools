import bpy

from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty, CollectionProperty, PointerProperty
import csv

# configs [to remove]
CSV_PATH = "I:/Blender/MyScripts/GameData.csv"  # Update this path!
PREFIX_LIST = ['SM_', 'SK_', 'MM_']  # unreal naming conventions

# utility functions

def is_triangle_count_within_budget(obj):
    if obj.type != 'MESH':
        return None  # Not applicable
    root = obj
    while root.parent:
        root = root.parent
    asset_name = strip_prefix(root.name)
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
    # If it cant find prefix, strip up to first underscore
    if "_" in name:
        return name.split("_", 1)[1]
    return name
    
def take_away_underscore(name):
    """
    Joins the two parts of the string split by the last underscore.
    Example: "SM_Asset_LOD1" -> "SM_AssetLOD1"
    """
    if "_" in name:
        parts = name.rsplit("_", 1)
        return parts[0] + parts[1]
    return name


# debug method
def show_message(message="", title="Error", icon='ERROR'):
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)



def clear_custom_properties(obj):
    keys_to_remove = [k for k in obj.keys() if not k.startswith("_")]
    for k in keys_to_remove:
        del obj[k]
    show_message(f"Cleared custom properties for {obj.name}.", title="Custom Properties Cleared", icon='INFO')


#CSV data read/write functions

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
        asset_name = strip_prefix(asset_name).lower()
        asset_name = take_away_underscore(asset_name.lower())

        csv_path = bpy.context.scene.csv_path.lower()
        with open(csv_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if strip_prefix(row.get('AssetName', '')).lower() == asset_name:
                    return row
                if strip_prefix(row.get('AssetName', '')).lower() in asset_name:
                    return row
        return None
    
# CSV write to update actual triangles count

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

# Main functions

def process_asset(obj):
    """Rename and tag the object based on CSV data."""
    clear_custom_properties(obj)
    root = obj
    while root.parent:
        root = root.parent
    asset_name = strip_prefix(root.name).lower()
    row = CSV2MESH_OT_SetCSVData.get_csv_row_for_asset(asset_name)

    if not row:
        show_message(f"No CSV row found for asset '{asset_name}'. Please check the CSV file.", title="CSV Row Not Found", icon='ERROR')
        return
    

    # Store original name if not already present
    if "original_name" not in root:
        root["original_name"] = root.name

    # Assign asset name property
    root["AssetName"] = row['AssetName']
    show_message(f"Asset name '{row['AssetName']}' matches the selected rootect '{root.name}'.", title="Asset Name Match", icon='INFO')

    # Asset type logic
    asset_type = row.get('Category', None)
    if asset_type:
        show_message(f"Asset type '{asset_type}' found and stored.", title="Asset Type", icon='INFO')
        if asset_type in ("Environment", "Prop"):
            root["AssetType"] = "StaticMesh"
            new_name = f"SM_{row['AssetName']}"
        elif asset_type == "Character":
            root["AssetType"] = "SkeletalMesh"
            new_name = f"SK_{row['AssetName']}"
        else:
            root["AssetType"] = asset_type
            new_name = root.name  # No change
    else:
        show_message("Asset type not found in CSV row.", title="Asset Type Not Found", icon='ERROR')
        print(f"root.name: {root.name}, new_name: {new_name}")
        print(f"Comparison result: {root.name.lower() == new_name.lower()}")
        new_name = root.name


    # Rename if needed
    if root.name.lower() != new_name.lower():
        if bpy.context.scene.csv2mesh_dont_ask_again:
            old_name = root.name
            root.name = new_name
            show_message(f"Renamed rootect from '{old_name}' to '{new_name}' without confirmation.", title="Renaming Rootect", icon='INFO')
        else:
            bpy.ops.csv2mesh.show_name_correction('INVOKE_DEFAULT', incorrect_name=root.name, correct_name=new_name)
            show_message(f"Renaming rootect from '{root.name}' to '{new_name}'", title="Renaming rootect", icon='INFO')
    else:
        show_message(f"No renaming needed for {root.name}, already matches '{new_name}'.", title="No Renaming Needed", icon='INFO')

    # Optionally assign master material
    assign_master_material(root, row)

def assign_master_material(obj, row=None):
    """Assigns the master material from CSV to the object."""
    if not row:
        root = obj
        while root.parent:
             root = root.parent
        asset_name = strip_prefix(root.name)
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

    # New Operation: Rename current material or Create a new one
    # Rename check
    mat = bpy.data.materials.get(obj.active_material.name) if obj.active_material else None
    if mat:
        if mat.name != master_material:
            old_name = mat.name
            mat.name = master_material
            show_message(f"Renamed material from '{old_name}' to '{master_material}' for {obj.name}.", title="Material Renamed", icon='INFO')
        else:
            show_message(f"Material '{master_material}' already assigned to {obj.name}.", title="Material Already Assigned", icon='INFO')

    if mat is None:
        # Create a new material if it doesn't exist
        mat = bpy.data.materials.new(name=master_material)
        show_message(f"Created new material: {master_material} for {obj.name}.", title="Material Created", icon='INFO')
        # Assign the new material to the object
        if obj.type == 'MESH':
            if not obj.data.materials:
                obj.data.materials.append(mat)
            else:
                # Replace existing materials with the new one
                for i in range(len(obj.data.materials)):
                    obj.data.materials[i] = mat
            show_message(f"Assigned material '{master_material}' to {obj.name}.", title="Material Assigned", icon='INFO')

    
    
    
    # Create and Assign Blender material
    # mat = bpy.data.materials.get(master_material)
    # if not mat:
    #     mat = bpy.data.materials.new(name=master_material)
    #     show_message(f"Created new material: {master_material}", title="Material Created", icon='INFO')
    # if obj.type == 'MESH':
    #     if not obj.data.materials:
    #         obj.data.materials.append(mat)
    #     else:
    #         for i in range(len(obj.data.materials)):
    #             obj.data.materials[i] = mat
    #     #show_message(f"Assigned material '{master_material}' to {obj.name}.", title="Material Assigned", icon='INFO')
    # else:
    #     show_message(f"Object '{obj.name}' is not a mesh, cannot assign material.", title="Invalid Object Type", icon='ERROR')

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
        
        # Draw custom properties if the toggle is enabled
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
    
        #draw_custom_props(self, context)
        

        layout.separator()
        layout.label(text="Mesh Validation Tools", icon='CHECKMARK')
        layout.operator("csv2mesh.validate_triangle_count", text="Validate Triangle Count", icon='TRIA_DOWN')

        obj = context.active_object
        if obj is not None and context.selected_objects:
            # Use parent name if available
            root = obj
            while root.parent:
                root = root.parent
            asset_name = strip_prefix(root.name)
            csv_row = CSV2MESH_OT_SetCSVData.get_csv_row_for_asset(asset_name)
            box = layout.box()
            row = box.row()
            col1 = row.column(align=True)
            col2 = row.column(align=True)
            col1.label(text=f"Active Object: {obj.name}", icon='OBJECT_DATA')
            if obj.type == 'MESH':
                col1.label(text=f"Actual Tris: {len(obj.data.polygons)}")
            else:
                col1.label(text="Actual Tris: N/A, not a mesh object")
            col2.label(text="CSV Data", icon='FILE_TEXT')
            if csv_row:
                col2.label(text=f"Max Tris: {csv_row.get('MaxTris', 'N/A')}")
            else:
                col2.label(text="Max Tris: N/A")
        else: 
            layout.label(text="No active object selected.", icon='ERROR')
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

            
        


        
                
        


class CSV2MESH_OT_ShowNameCorrection(bpy.types.Operator):
    bl_idname = "csv2mesh.show_name_correction"
    bl_label = "Asset Name Correction"
    bl_options = {'REGISTER', 'INTERNAL'}

    incorrect_name: StringProperty()
    correct_name: StringProperty()
    dont_ask_again: BoolProperty()

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
        layout.prop(context.scene, "csv2mesh_dont_ask_again", text="Don't ask me again")
        layout.label(text="Do you want to rename the asset?", icon='QUESTION')

class CSV2MESH_OT_DisplayCustomProps(bpy.types.Operator):
    bl_idname = "csv2mesh.display_custom_props"
    bl_label = "Display Custom Properties"
    bl_description = "Display custom properties of selected objects"

    def execute(self, context):
        for obj in context.selected_objects:
            #print_custom_properties(obj)
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
                root = obj
                while root.parent:
                    root = root.parent
                asset_name = strip_prefix(root.name)
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
    

class CSV2MESH_PT_RenameOperationsPanel(bpy.types.Panel):
    bl_label = "Rename Operations"
    bl_idname = "CSV2MESH_PT_rename_operations_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "CSV2Mesh"

    PREFIX_LIST = {
        
                    'StaticMesh':'SM_',
                    
                    'SkeletalMesh':'SK_',
                    
                    'MasterMaterial':'MM_'
                    } # Unreal Engine naming conventions


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.active_object


        layout.label(text="Viewport Names", icon='VIEW3D')
        # Updates the viewport display of asset names
        box =layout.box()
        box_row = box.row()
        #box.prop(scene, "csv2mesh_toggle_show_asset_names", text="Show Asset Names in Viewport")
        if obj and hasattr(obj, "show_name"):
            box_row.prop(obj, "show_name", text="Show Name in Viewport")
        else:
            box_row.label(text="No active object selected.", icon='ERROR')

        


        # Button version because above doesnt work for multiple objects
        box_row.operator("csv2mesh.show_all_asset_names_in_viewport", text="Toggle Asset Names in Viewport")            

        layout.operator("csv2mesh.rename_operations", icon='TEXT')
        layout.label(text="Custom Prefix List:", icon='PRESET')
        layout.operator("csv2mesh.populate_prefixes", icon='IMPORT', text="Populate Default Prefixes")
        row = layout.row()
        row.template_list(
            "CSV2MESH_UL_Prefixes", "",
            scene, "csv2mesh_prefixes",
            scene, "csv2mesh_prefix_index",
            rows=3
        )

        col = row.column(align=True)
        col.operator("csv2mesh.add_prefix", icon='ADD', text="")
        col.operator("csv2mesh.remove_prefix", icon='REMOVE', text="")
        col.separator()
        
        layout.operator("csv2mesh.assign_prefix", icon='PLUS', text="Assign Prefix to Active Object")
        layout.operator("csv2mesh.reset_name_to_original", icon='FILE_REFRESH', text="Reset Name to Original")


        # layout.row()
        # #layout.label(text="Prefix list", icon='INFO')
        #  # Display custom properties of the active object as a read-only list
        
        
        # layout.label(text="Prefix List:", icon='PRESET')
        # box = layout.box()
        # for k, v in self.PREFIX_LIST.items():
        #     row = box.row()
        #     row.label(text=f"{k}: {v}")
        # layout.separator()

class CSV2MESH_OT_RenameOperations(bpy.types.Operator):
    bl_idname = "csv2mesh.rename_operations"
    bl_label = "Remove Underscore Operation"
    bl_description = "Rename operations for selected objects based on CSV data"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        if not context.selected_objects:
            show_message("No objects selected.", title="No Selection", icon='ERROR')
            return {'CANCELLED'}
        else:
            for obj in context.selected_objects:
                if obj.parent is None:
                    obj["original_name"] = obj.name
                    new_name = take_away_underscore(obj.name)
                    obj.name = new_name
            return {'FINISHED'}
        
       



        
class CSV2MESH_PrefixItem(bpy.types.PropertyGroup):
    label: StringProperty(name="Label")
    prefix: StringProperty(name="Prefix", default="")
            

class CSV2MESH_OT_AssignPrefixes(bpy.types.Operator):
    bl_idname = "csv2mesh.assign_prefix"
    bl_label = "Assign Prefix"
    bl_description = "Assign selected prefix to active object"

    def execute(self, context):
        scene = context.scene
        idx = scene.csv2mesh_prefix_index
        if not scene.csv2mesh_prefixes or idx >= len(scene.csv2mesh_prefixes):
            show_message("No prefix selected.", title="Prefix Assignment", icon='ERROR')
            return {'CANCELLED'}
        prefix = scene.csv2mesh_prefixes[idx].prefix
        obj = context.active_object
        if obj:
            # Remove existing known prefix
            name_wo_prefix = strip_prefix(obj.name)
            obj.name = prefix + "_" + name_wo_prefix
            show_message(f"Assigned prefix '{prefix}' to '{obj.name}'", title="Prefix Assigned", icon='INFO')
            return {'FINISHED'}
        else:
            show_message("No active object.", title="Prefix Assignment", icon='ERROR')
            return {'CANCELLED'}


        


class CSV2MESH_UL_Prefixes(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT', 'GRID'}:
            layout.prop(item, "label", text="")
            layout.prop(item, "prefix", text="")
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.prefix)

class CSV2MESH_OT_PopulatePrefixes(bpy.types.Operator):
    bl_idname = "csv2mesh.populate_prefixes"
    bl_label = "Populate Default Prefixes"
    bl_description = "Populate the prefix list with default prefixes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
            scene = context.scene
            scene.csv2mesh_prefixes.clear()
            for label, prefix in [
                ("StaticMesh", "SM"),
                ("SkeletalMesh", "PP"),
                ("MasterMaterial", "MM"),
            ]:
                item = scene.csv2mesh_prefixes.add()
                item.label = label
                item.prefix = prefix
            return {'FINISHED'}
    

class CSV2MESH_OT_AddPrefix(bpy.types.Operator):
    bl_idname = "csv2mesh.add_prefix"
    bl_label = "Add Prefix"
    bl_description = "Add a new prefix to the prefix list"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        item = scene.csv2mesh_prefixes.add()
        item.label = "New Prefix"
        item.prefix = "XX_"
        scene.csv2mesh_prefix_index = len(scene.csv2mesh_prefixes) - 1
        return {'FINISHED'}
    
class CSV2MESH_OT_RemovePrefix(bpy.types.Operator):
    bl_idname = "csv2mesh.remove_prefix"
    bl_label = "Remove Prefix"
    bl_description = "Remove the selected prefix from the prefix list"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        idx = scene.csv2mesh_prefix_index
        if idx < len(scene.csv2mesh_prefixes):
            scene.csv2mesh_prefixes.remove(idx)
            scene.csv2mesh_prefix_index = max(0, idx - 1)
            return {'FINISHED'}
        else:
            show_message("No prefix to remove.", title="Remove Prefix", icon='ERROR')
            return {'CANCELLED'}

class CSV2MESH_OT_ResetNameToOriginal(bpy.types.Operator):
    bl_idname = "csv2mesh.reset_name_to_original"
    bl_label = "Reset Name to Original"
    bl_description = "Reset the name of the selected object to its original name"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        def revert_names(obj):
        # Revert this object if it has an original_name
            if "original_name" in obj:
                original_name = obj["original_name"]
                obj.name = original_name
                show_message(f"Reset name of {obj.name} to original name: {original_name}", title="Name Reset", icon='INFO')
            # Recurse for children
            for child in obj.children:
                revert_names(child)

        for obj in context.selected_objects:
            # Get the root object (topmost parent)
            root = obj
            while root.parent:
                root = root.parent
            revert_names(root)
        return {'FINISHED'}
        
class CSV2MESH_OT_ShowAssetNamesInViewport(bpy.types.Operator):
    bl_idname = "csv2mesh.show_asset_names_in_viewport"
    bl_label = "Show Asset Names in Viewport"
    bl_description = "Display asset names in the viewport for selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    # def execute(self, context):
    #     for obj in context.selected_objects:
    #         # Toggle the "Show Name" property in the object properties menu
    #         # In Blender, this is 'show_name' for viewport display
    #         if hasattr(obj, "show_name"):
    #             obj.show_name = not obj.show_name
    #     return {'FINISHED'}
    
    def execute(self, context):
        value = context.scene.csv2mesh_toggle_show_asset_names
        for obj in context.selected_objects:
            if hasattr(obj, "show_name"):
                obj.show_name = value
        return {'FINISHED'}
    
class CSV2MESH_OT_ShowAllAssetNamesInViewport(bpy.types.Operator):
    bl_idname = "csv2mesh.show_all_asset_names_in_viewport"
    bl_label = "Toggle Asset Names in Viewport"
    bl_description = "Toggle showing asset names in the viewport for all selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        value = not context.scene.csv2mesh_toggle_show_asset_names
        context.scene.csv2mesh_toggle_show_asset_names = value
        for obj in context.scene.objects:
            if hasattr(obj, "show_name"):
                obj.show_name = value
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
    CSV2MESH_OT_ValidateTriangleCount,
    CSV2MESH_PT_RenameOperationsPanel,
    CSV2MESH_OT_RenameOperations,
    CSV2MESH_PrefixItem,
    CSV2MESH_OT_AssignPrefixes,
    CSV2MESH_UL_Prefixes,
    CSV2MESH_OT_AddPrefix,
    CSV2MESH_OT_RemovePrefix,
    CSV2MESH_OT_ResetNameToOriginal,
    CSV2MESH_OT_ShowAssetNamesInViewport,
    CSV2MESH_OT_ShowAllAssetNamesInViewport,
    CSV2MESH_OT_PopulatePrefixes,

    
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
    bpy.types.Scene.csv2mesh_dont_ask_again = BoolProperty(
        name="Don't Ask Again",
        description="Don't show the asset name correction dialog again",
        default=False
    )
    bpy.types.Scene.csv2mesh_json_export_path = StringProperty(
        name="JSON Export Path",
        description="Path to export custom properties as JSON",
        default="//custom_properties.json",
        subtype='FILE_PATH'
    )
    bpy.types.Scene.csv2mesh_prefixes = CollectionProperty(type=CSV2MESH_PrefixItem)

    bpy.types.Scene.csv2mesh_prefix_index = IntProperty(
        name="Prefix Index",
        description="Index of the selected prefix",
        default=0,
        min=0
    )

    bpy.types.Scene.csv2mesh_toggle_show_asset_names = BoolProperty(
        name="Show Asset Names in Viewport",
        description="Toggle showing asset names in the viewport for selected objects",
        default=False,
        
    )

    



def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
    
    del bpy.types.Scene.csv_path
    del bpy.types.Scene.show_custom_props
    del bpy.types.Scene.csv2mesh_dont_ask_again
    del bpy.types.Scene.csv2mesh_json_export_path
    del bpy.types.Scene.csv2mesh_prefixes
    del bpy.types.Scene.csv2mesh_prefix_index
    del bpy.types.Scene.csv2mesh_toggle_show_asset_names
    

# if __name__ == "__main__":
#     register()
