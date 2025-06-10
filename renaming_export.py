import bpy
from bpy.props import StringProperty, BoolProperty, IntProperty
from bpy.types import Operator, Panel
import os
from mathutils import Vector
import pprint as pprint

# import pathlib

# path_to_json = pathlib.Path('.') / "UnrealExport"
#print(f"Path to JSON: {path_to_json}")





#import csv
import json


# --- CONFIGURATION ---
#csv_path = "I:/Blender/MyScripts/csv_to_json/GameData.csv"  # Update this path!
add_to = "material"  # Options: 'object', 'material'

def show_message(message="", title="Error", icon='ERROR'):
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)

def batch_import_fbx(directory, apply_transform=False):
    """Batch import FBX files from a directory into Blender."""
    if not os.path.isdir(directory):
        show_message(f"Directory does not exist: {directory}", title="Import Error", icon='ERROR')
        return

    # Get all FBX files in the directory
    fbx_files = [f for f in os.listdir(directory) if f.lower().endswith('.fbx')]
    if not fbx_files:
        show_message("No FBX files found in the directory.", title="Import Error", icon='ERROR')
        return

    for fbx_file in fbx_files:
        file_path = os.path.join(directory, fbx_file)
        bpy.ops.import_scene.fbx(filepath=file_path, use_custom_props=True)


def export_fbx(obj, export_path, apply_transform=True):
    # Store original location 
    original_location = obj.location.copy()
    # Move the object to the origin before export
    obj.location = Vector((0.0, 0.0, 0.0))

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

    # Restore original location
    obj.location = original_location




class UEExportPanel_PT_Export(bpy.types.Panel):
    bl_label = "Unreal Export"
    bl_idname = "VIEW3D_PT_unreal_export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'CSV2Mesh'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="FBX Import", icon='IMPORT')
        layout.prop(scene, "fbx_import_path", text="FBX Path", icon='FILE_FOLDER')
        row = layout.row()
        row.operator("ueexportpanel.import_fbx", icon='IMPORT', text="Import FBX Files")
        row.operator("ueexportpanel.offset_fbx", text="Offset Imported FBX")


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

class UEExportPanel_OT_ImportFBX(bpy.types.Operator):
    bl_idname = "ueexportpanel.import_fbx"
    bl_label = "Import FBX Files"
    bl_description = "Import multiple FBX files from the specified path"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        fbx_path = bpy.path.abspath(scene.fbx_import_path)
        if not os.path.isdir(fbx_path):
            self.report({'ERROR'}, "FBX import path does not exist.")
            return {'CANCELLED'}
        
        batch_import_fbx(fbx_path, apply_transform=True)
        return {'FINISHED'}       

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
        
        
        export_multiple = scene.ue_export_multiple
        if export_multiple:
            for obj in selected_objects:
                if "original_name"  in obj:
                    del obj["original_name"]
                export_name = obj.name
                fbx_path = os.path.join(export_path, f"{export_name}.fbx")
                export_fbx(obj, fbx_path, apply_transform=True)
                write_custom_properties_to_json(obj, scene.export_custom_props)

                    
        else:
            # If exporting a single object, use the active object's name
            fbx_path = os.path.join(export_path, f"{export_name}.fbx")
            export_fbx(obj, fbx_path, apply_transform=True)
            write_custom_properties_to_json(obj, scene.export_custom_props)
            return {'FINISHED'}

        
        return {'FINISHED'}

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

    if "original_name" in obj:
        del obj["original_name"]  # Remove original_name if it exists

    
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

class UEExportPanel_OT_OffsetFBX(bpy.types.Operator):
    bl_idname = "ueexportpanel.offset_fbx"
    bl_label = "Offset Imported FBX"
    bl_description = "Offset the imported FBX files by 100 units in the X direction"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
         # Collect root objects (armatures or meshes) for selected meshes
        roots = []
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                root = obj
                while root.parent:
                    root = root.parent
                if root not in roots:
                    roots.append(root)

        # Sort roots by name for consistent order
        roots.sort(key=lambda o: o.name)

        current_x = 0.0
        for root in roots:
            # Calculate the bounding box in world space for the root and all its children
            all_objs = [root] + list(root.children_recursive)
            all_meshes = [o for o in all_objs if o.type == 'MESH']
            if not all_meshes:
                continue

            # Get all world-space bounding box corners
            all_bbox_points = []
            for mesh_obj in all_meshes:
                all_bbox_points.extend([mesh_obj.matrix_world @ Vector(corner) for corner in mesh_obj.bound_box])

            min_x = min(v.x for v in all_bbox_points)
            max_x = max(v.x for v in all_bbox_points)
            length_x = max_x - min_x

            # Move root so its min_x aligns with current_x
            offset = current_x - min_x
            root.location.x += offset

            self.report({'INFO'}, f"Placed {root.name} at X={current_x:.2f} (length {length_x:.2f})")
            current_x += length_x  # Next object's position

        return {'FINISHED'}
    

     
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
    UEExportPanel_OT_Export,
    UEExportPanel_OT_ImportFBX,
    UEExportPanel_OT_OffsetFBX

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
    ),
    "fbx_import_path": StringProperty(
        name="FBX Import Path",
        description="Path to import FBX files from",
        default="//",
        subtype='DIR_PATH'
    ),
    # "multi_fbx_import": BoolProperty(
    #     name="Import FBX Files",
    #     description="Toggle to import multiple FBX files from the specified path",
    #     default=False
    # )
}

def register(): 
    
    for prop_name, prop in properties.items():
        setattr(bpy.types.Scene, prop_name, prop)
    for cls in classes:
        bpy.utils.register_class(cls)
    

   

def unregister():
    for prop_name in properties.keys():
        delattr(bpy.types.Scene, prop_name)
    
    for cls in classes:
        bpy.utils.unregister_class(cls)

     
