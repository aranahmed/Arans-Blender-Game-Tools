import unreal
import os
import json
import sys


#from unreal import DataTableFunctionLibrary as DataTableFunctionLibrary

class ImportAssetTool:
    import_path: str
    destination_path: str

    
    def __init__(self, import_path, destination_path):
        self.import_path = import_path
        self.destination_path = destination_path
        self.asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

    def strip_prefix(self, asset_name, prefix):
        asset_name.removeprefix(prefix)

    def get_master_material_from_json(self, json_filename):
        json_path = os.path.join(self.import_path, json_filename)
        if not os.path.exists(json_path):
            unreal.log_error(f"JSON file {json_path} does not exist.")
            return None
        with open(json_path, 'r') as file:
            data = json.load(file)
        if isinstance(data, dict):
            return data.get("MasterMaterial")
        elif isinstance(data, list) and data:
            return data[0].get("MasterMaterial")
        return None

    def fix_material_instance_names_by_json(self, output_folder, json_filename, strip_prefixes=("MI_", "SM_", "SK_")):
        """
        Renames all MaterialInstanceConstant assets in output_folder to MI_{AssetName}
        where AssetName is taken from the JSON file. Only renames if the parent matches the MasterMaterial in JSON.
        """
        # Load JSON data
        json_path = os.path.join(self.import_path, json_filename)
        if not os.path.exists(json_path):
            unreal.log_error(f"JSON file {json_path} does not exist.")
            return

        with open(json_path, 'r') as file:
            data = json.load(file)

        # Build a mapping: {MasterMaterial: AssetName}
        # If your JSON is a list of dicts:
        asset_map = {}
        if isinstance(data, list):
            for entry in data:
                asset_name = entry.get("AssetName")
                master_material = entry.get("MasterMaterial")
                if asset_name and master_material:
                    asset_map[master_material] = asset_name
        elif isinstance(data, dict):
            asset_name = data.get("AssetName")
            master_material = data.get("MasterMaterial")
            if asset_name and master_material:
                asset_map[master_material] = asset_name

        # Now process Unreal assets
        assets = unreal.EditorAssetLibrary.list_assets(output_folder, recursive=False, include_folder=False)
        for asset_path in assets:
            asset_data = unreal.EditorAssetLibrary.find_asset_data(asset_path)
            if str(asset_data.asset_class) != "MaterialInstanceConstant":
                continue
            mat_instance = unreal.EditorAssetLibrary.load_asset(asset_path)
            parent = mat_instance.get_editor_property("parent")
            if not parent:
                continue

            parent_name = parent.get_name()
            if parent_name not in asset_map:
                continue  # Only rename if parent is in JSON

            # Derive asset name (strip prefix if needed)
            asset_name = os.path.splitext(os.path.basename(asset_path))[0]
            for prefix in strip_prefixes:
                if asset_name.startswith(prefix):
                    asset_name = asset_name[len(prefix):]

            # New canonical name from JSON
            new_name = f"MI_{asset_map[parent_name]}"
            new_path = f"{output_folder}/{new_name}"
            if asset_path != new_path and not unreal.EditorAssetLibrary.does_asset_exist(new_path):
                print(f"Renaming {asset_path} to {new_path}")
                unreal.EditorAssetLibrary.rename_asset(asset_path, new_path)

    @staticmethod
    def create_material_instances(master_material_path, asset_paths, output_folder, prefix_to_strip= ("SM","SK")):
        # Load the master material
        if not master_material_path:
            unreal.log_error("Master material path is not provided.")
            return None
        
        master_material = unreal.EditorAssetLibrary.load_asset(master_material_path)
        if not master_material:
            unreal.log_error(f"Master material {master_material_path} not found.")
            return None
        
        for asset_path in asset_paths:
            asset_name = os.path.splitext(os.path.basename(asset_path))[0] # Get the asset name without extension

            if asset_name in prefix_to_strip:
                # Strip the prefix from the asset name
                for prefix in prefix_to_strip:
                    if asset_name.startswith(prefix):
                        asset_name = asset_name[len(prefix):]

            if asset_name.startswith(prefix_to_strip):
                asset_name = asset_name[len(prefix_to_strip):]
                
            # Strip the prefix
            # if unreal.StringLibrary.starts_with(master_material.get_name(), "MM_"):
            #     stripped_name = master_material.get_name().removeprefix("MM_")
            # else:
            material_instance_name = f"MI{asset_name}"
            
            material_instance_path = f"{output_folder}/{material_instance_name}"

            # Check if mat instance already exists
            if unreal.EditorAssetLibrary.does_asset_exist(material_instance_path):
                unreal.log_warning(f"Material instance {material_instance_name} already exists. Skipping creation.")
                return unreal.EditorAssetLibrary.load_asset(material_instance_path)
            # Create the material instance asset
            asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
            material_instance = asset_tools.create_asset(
                    asset_name=material_instance_name,
                    package_path=output_folder,
                    asset_class=unreal.MaterialInstanceConstant,
                    factory=unreal.MaterialInstanceConstantFactoryNew(),
                )
    
            if material_instance:
                # Set the parent material
                material_instance.set_editor_property("Parent", master_material)

                # Save the material instance
                unreal.EditorAssetLibrary.save_asset(material_instance_path, only_if_is_dirty=False)

            else:
                unreal.log_error(f"Failed to create material instance for {asset_name} at {material_instance_path}")
        

    def create_material_instances_from_json(tool, json_filename="custom.json", output_folder="/Game/ImportedAssets/MaterialInstances"):
        json_path = os.path.join(tool.import_path, json_filename)
        with open(json_path, 'r') as file:
            data = json.load(file)

        if isinstance(data, dict):
            data = [data]  # Make it a list for consistency

        imported_assets = tool.import_all()

        for entry in data:
            asset_name = entry.get("AssetName")
            master_material_name = entry.get("MasterMaterial")
            if not asset_name or not master_material_name:
                continue

            master_material_path = f"{tool.destination_path}/{master_material_name}"

            # Find the asset path(s) for this asset_name
            asset_paths = [
                path for path in imported_assets
                if os.path.splitext(os.path.basename(path))[0].endswith(asset_name)
            ]
            if not asset_paths:
                unreal.log_warning(f"No imported asset found for {asset_name}")
                continue

            ImportAssetTool.create_material_instances(
                master_material_path=master_material_path,
                asset_paths=asset_paths,
                output_folder=output_folder
            )
        return True
            
    def add_master_material_naming_to_instances(self, json_filename="custom.json", output_folder="/Game/ImportedAssets/MaterialInstances"):
        """
        For each material instance in the output_folder, set its parent to the correct master material from JSON,
        and rename it to MI_{AssetName} where AssetName comes from the JSON.
        """
        json_path = os.path.join(self.import_path, json_filename)
        if not os.path.exists(json_path):
            unreal.log_error(f"JSON file {json_path} does not exist.")
            return

        with open(json_path, 'r') as file:
            data = json.load(file)

        # Build a mapping: {AssetName: MasterMaterial}
        asset_map = {}
        if isinstance(data, list):
            for entry in data:
                asset_name = entry.get("AssetName")
                master_material = entry.get("MasterMaterial")
                if asset_name and master_material:
                    asset_map[asset_name] = master_material
        elif isinstance(data, dict):
            asset_name = data.get("AssetName")
            master_material = data.get("MasterMaterial")
            if asset_name and master_material:
                asset_map[asset_name] = master_material

        # Process Unreal assets
        assets = unreal.EditorAssetLibrary.list_assets(output_folder, recursive=False, include_folder=False)
        for asset_path in assets:
            mat_instance = unreal.EditorAssetLibrary.load_asset(asset_path)
            if not mat_instance or not isinstance(mat_instance, unreal.MaterialInstanceConstant):
                continue

            parent = mat_instance.get_editor_property("parent")
            if not parent:
                continue

            parent_name = parent.get_name()
            if parent_name not in asset_map:
                continue



    def import_asset(self, filename):
        task = unreal.AssetImportTask()
        task.filename = filename
        task.destination_path = self.destination_path
        task.automated = True
        task.save = True
        task.replace_existing = True # Replace existing assets if they exist
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        return task.imported_object_paths

    def import_all(self):
        imported_assets = []
        for file in os.listdir(self.import_path):
            full_path = os.path.join(self.import_path, file)
            if os.path.isfile(full_path):
                imported = self.import_asset(full_path)
                imported_assets.extend(imported)
        return imported_assets
    
    def import_json_to_unreal(self, json_path):
        task = unreal.AssetImportTask()
        task.filename = json_path
        task.destination_path = self.destination_path
        task.automated = True
        task.save = True
        task.replace_existing = True # Replace existing assets if they exist
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        return task.imported_object_paths
        print(f"Imported JSON from {json_path} to {self.destination_path}")

    def import_json_to_data_table(self, json_filename, data_table_path):
        json_path = os.path.join(self.import_path, json_filename)

        # Check if JSON exists
        if not os.path.exists(json_path):
            print(f"JSON file {json_path} does not exist.")
            return
        
        # Load data table asset
        data_table = unreal.EditorAssetLibrary.load_asset(data_table_path)
        if not data_table:
            print(f"Data table {data_table_path} does not exist.")
            return
        
        # Import JSON data into the data table

        success = unreal.DataTableFunctionLibrary.fill_data_table_from_json_file(data_table, json_path)
        if success:
            print(f"Successfully imported JSON data from {json_path} to {data_table_path}")
        else:
            print(f"Failed to import JSON data from {json_path} to {data_table_path}")

        
        

# not used, but can be used to search and update JSON files
    def search_and_update_json(self, json_filename, new_data):
        json_path = os.path.join(self.import_path, json_filename)
        
        with open(json_path, 'w') as file:
            json.dump(new_data, file, indent=4)
        
        print(f"{json_path}")
        #self.import_json_to_unreal(json_path)

        #unreal.DataTableFunctionLibrary.data_table_from_json_file(json_filename)

        """
        if os.path.exists(json_path):
            # Load existing JSON data
            with open(json_path, 'r') as file:
                existing_data = json.load(file)
            
            # Append new data and remove duplicates based on 'name' key
            combined_data = {item['name']: item for item in existing_data}
            for item in new_data:
                combined_data[item['name']] = item
            
            # Save updated JSON data
            with open(json_path, 'w') as file:
                json.dump(list(combined_data.values()), file, indent=4)
        else:
            # Create new JSON file with new data
            with open(json_path, 'w') as file:
                json.dump(new_data, file, indent=4)
        """


    def correct_material_instance_names(tool, material_instances_folder="/Game/ImportedAssets/MaterialInstances", json_filename="custom.json"):
        """
        For each material instance in the folder, set its parent to the correct master material from JSON,
        and rename it to MI_{AssetName} where AssetName comes from the JSON.
        """
        material_instances = unreal.EditorAssetLibrary.list_assets(material_instances_folder, recursive=False, include_folder=False)
        json_path = os.path.join(tool.import_path, json_filename)

        # Load JSON data (support both dict and list)
        with open(json_path, 'r') as file:
            data = json.load(file)

        # Build a mapping: {AssetName: MasterMaterial}
        asset_map = {}
        if isinstance(data, list):
            for entry in data:
                asset_name = entry.get("AssetName")
                master_material = entry.get("MasterMaterial")
                if asset_name and master_material:
                    asset_map[asset_name] = master_material
        elif isinstance(data, dict):
            asset_name = data.get("AssetName")
            master_material = data.get("MasterMaterial")
            if asset_name and master_material:
                asset_map[asset_name] = master_material

        for material_instance in material_instances:
            # Get asset name, strip known prefixes
            asset_name = os.path.splitext(os.path.basename(material_instance))[0]
            for prefix in ("MI_", "SM_", "SK_", "PropLit_", "CharacterLit_"):
                if asset_name.startswith(prefix):
                    asset_name = asset_name[len(prefix):]
                #print(f"{asset_name}")

            if asset_name not in asset_map:
                print(f"Asset name {asset_name} not found in asset map.")
                continue

            master_material_name = asset_map[asset_name]
            master_material_path = f"{tool.destination_path}/{master_material_name}"
            master_material_asset = unreal.EditorAssetLibrary.load_asset(master_material_path)
            if not master_material_asset:
                unreal.log_warning(f"Master material {master_material_path} not found for {asset_name}")
                continue

            mat_inst_asset = unreal.EditorAssetLibrary.load_asset(material_instance)
            if not mat_inst_asset:
                continue

            # Set parent if different
            current_parent = mat_inst_asset.get_editor_property("parent")
            print(f"{current_parent}")
            if current_parent != master_material_asset:
                mat_inst_asset.set_editor_property("parent", master_material_asset)
                unreal.EditorAssetLibrary.save_asset(material_instance)
                print(f"Set parent of {material_instance} to {master_material_path}")

            # Rename to MI_{AssetName}
            new_name = f"MI_{asset_name}"
            new_path = f"{material_instances_folder}/{new_name}"
            if material_instance != new_path and not unreal.EditorAssetLibrary.does_asset_exist(new_path):
                unreal.EditorAssetLibrary.rename_asset(material_instance, new_path)
                print(f"Renamed {material_instance} to {new_path}")


    # Try get an unreal object
    @staticmethod
    def get_unreal_object():    
        selected_objects = unreal.EditorLevelLibrary.get_selected_level_actors()
        for actor in selected_objects:
            unreal.log(f"Selected Actor: {actor.get_name()}")
            if isinstance(actor, unreal.MaterialInstanceConstant):
                unreal.log(f"Selected Material Instance: {actor.get_name()}")
            elif isinstance(actor, unreal.StaticMeshActor):
                static_mesh_component = actor.get_component_by_class(unreal.StaticMeshComponent)
                static_mesh = static_mesh_component.static_mesh if static_mesh_component else None
                if static_mesh:
                    # Always get the asset path and load the asset to ensure it's a valid asset object
                    asset_path = static_mesh.get_path_name()
                    
                    asset = unreal.EditorAssetLibrary.load_asset(asset_path)
                    unreal.log(f"Associated Static Mesh Asset: {static_mesh}")
                    unreal.log(f"Associated Static Mesh Asset: {asset.get_path_name()}")
                #     unreal.log(f"Associated Static Mesh Asset: {asset.get_path_name()}")            
                #     asset_path = static_mesh.get_path_name()
                #     unreal.log(f"Associated Static Mesh Asset: {asset_path}")
                #     # Load the asset and sync the browser to it
                #     asset = unreal.EditorAssetLibrary.load_asset(asset_path)
                # if asset:
                    return asset_path
                else:
                    unreal.log(f"Selected Actor {actor.get_name()} does not have a Static Mesh Component.")
                
            elif isinstance(actor, unreal.SkeletalMeshActor):
                skeletal_mesh_component = actor.skeletal_mesh_component
                skeletal_mesh = skeletal_mesh_component.skeletal_mesh
                if skeletal_mesh:
                    unreal.log(f"Associated Skeletal Mesh Asset: {skeletal_mesh.get_path_name()}")
                    return skeletal_mesh_component.skeletal_mesh
                else:
                    unreal.log("No skeletal mesh assigned.")
    
    def assign_material_to_actor(material_instance_path, new_material):
        material_instance_path = ImportAssetTool.get_unreal_object()
        
        material_instance_attached = unreal.EditorAssetLibrary.load_asset(material_instance_path)


        material_instance_attached.set_material(0,new_material)
        unreal.log(f"Material Instance Path: {material_instance_attached}")



            
            

            # else:
            #     unreal.log(f"Selected Asset: {actor.get_name()}")
            #     new_name = actor.get_name().replace(" ", "_")
            #     unreal.EditorAssetLibrary.rename_asset(actor.get_path_name(), f"/Game/ImportedAssets/{new_name}")




"""
# @unreal.uclass()
# class MyPythonBridge(unreal.BlueprintFunctionLibrary):
#     @unreal.ufunction(static=True, meta=dict(Category="ImportTools"))
#     def run_import_tool(import_path: str, destination_path: str):  
#         tool = ImportAssetTool(import_path, destination_path)
#         tool.import_all()

@unreal.uclass()
class RunFunctions(unreal.BlueprintFunctionLibrary):
    import_path: unreal.PyTestStruct.string 
    destination_path: unreal.PyTestStruct.string 
   

    @unreal.ufunction(static=True, meta=dict(Category="ImportTools"))
    def run_import_tool():  
        
        
        import_path= r"I:/Blender/MyScripts_Clone/AssetsToExportToUnreal"
        destination_path = "/Game/ImportedAssets"

        tool = ImportAssetTool(import_path, destination_path)
        tool.import_all()
""" 

# @unreal.uclass()
# class RunJsonFunctions(unreal.BlueprintFunctionLibrary):
#     # @unreal.ufunction(static=True, meta=dict(Category="FunctionLibrary"))
#     # def run_list_json_data_v2(import_path: str, destination_path: str, json_filename: str):
#     #     tool = ImportAssetTool(import_path=import_path, destination_path=destination_path)
#     #     json_path = os.path.join(tool.import_path, json_filename)
#     #     if not os.path.exists(json_path):
#     #         unreal.log_error(f"JSON file {json_path} does not exist.")
#     #         return
        
#     #     with open(json_path, 'r') as file:
#     #         data = json.load(file)
        
#     #     unreal.log(f"Data from {json_path}: {data}")


#     @unreal.ufunction(static=True, meta=dict(Category="FunctionLibrary"))
#     def run_import_json_to_data_table():
#         import_path = r"I:/Blender/MyScripts_Clone/AssetsToExportToUnreal"
#         destination_path = "/Game/ImportedAssets"
#         json_filename = "custom.json"
#         data_table_path = "/Game/Python/OnImportJSON/DT_CustomMeshes"


#         tool = ImportAssetTool(import_path=import_path, destination_path=destination_path)
#         tool.import_json_to_data_table(json_filename=json_filename, data_table_path=data_table_path)
#         return data_table_path
 






# Get the Unreal project directory
project_dir = unreal.SystemLibrary.get_project_directory()

# Build the path to your tools folder relative to the project directory
assets_path = os.path.join(project_dir, "Contest/ImportedAssets")

# Add to sys.path if not already present
if assets_path not in sys.path:
    sys.path.append(assets_path)

tool = ImportAssetTool(r"I:/Blender/MyScripts_Clone/AssetsToExportToUnreal", "/Game/ImportedAssets")

#tool.get_unreal_object()


#tool.import_all()
#correct_material_instance_names(tool, material_instances_folder="/Game/ImportedAssets/MaterialInstances", json_filename="custom.json")
#tool.create_material_instances_from_json(json_filename="custom.json", output_folder="/Game/ImportedAssets/MaterialInstances")   







#Example usage:
# tool = ImportAssetTool(r"I:/Blender/MyScripts_Clone/AssetsToExportToUnreal","/Game/ImportedAssets")

# json_import = tool.import_json_to_data_table("custom.json", "/Game/Python/OnImportJSON/DT_CustomMeshes")




# struct_for_json ={
#                   "AssetName": "Mesh",
#                   "AssetType" : "Type",
#                   "MasterMaterial" : "MM_PropLit"}



#tool.search_and_update_json("custom.json", new_data)

# imported = tool.import_all()
# print("Imported assets:", imported)



class BatchAssetImporter:
    def __init__(self, import_path, destination_path):
        self.import_path = import_path
        self.destination_path = destination_path
        self.asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

    def batch_import_static_meshes(self, replace_existing=True, combine_meshes=False):
            asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
            imported_assets = []
            for file in os.listdir(self.import_path):
                if not file.lower().endswith(".fbx"):
                    continue
                full_path = os.path.join(self.import_path, file)
                task = unreal.AssetImportTask()
                task.filename = full_path
                task.destination_path = self.destination_path
                task.automated = True
                task.save = True
                task.replace_existing = replace_existing

                # FBX import options
                options = unreal.FbxImportUI()
                options.import_mesh = True
                options.import_as_skeletal = False
                options.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
                options.static_mesh_import_data.combine_meshes = combine_meshes

                task.options = options

                asset_tools.import_asset_tasks([task])
                imported_assets.extend(task.imported_object_paths)
            unreal.log(f"Imported assets: {imported_assets}")
            return imported_assets

# Example usage:
# tool = BatchAssetImporter(r"I:/Blender/MyScripts_Clone/AssetsToExportToUnreal", "/Game/ImportedAssets")
# tool.batch_import_static_meshes(replace_existing=True, combine_meshes=False)