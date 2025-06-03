import unreal
import os
import json

#from unreal import DataTableFunctionLibrary as DataTableFunctionLibrary

class ImportAssetTool:
    import_path: str
    destination_path: str

    
    def __init__(self, import_path, destination_path):
        self.import_path = import_path
        self.destination_path = destination_path
        self.asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

    def import_asset(self, filename):
        task = unreal.AssetImportTask()
        task.filename = filename
        task.destination_path = self.destination_path
        task.automated = True
        task.save = True
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
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
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

    
#Example usage:
tool = ImportAssetTool(r"I:\Blender\MyScripts_Clone\AssetsToExportToUnreal", "/Game/ImportedAssets")
tool.import_json_to_data_table("custom.json", "/Game/Python/OnImportJSON/DT_CustomMeshes")

struct_for_json ={
                  "AssetName": "Mesh",
                  "AssetType" : "Type",
                  "MasterMaterial" : "MM_PropLit"}



#tool.search_and_update_json("custom.json", new_data)

imported = tool.import_all()
#print("Imported assets:", imported)