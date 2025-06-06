import unreal

def sync_selected_asset_to_content_browser():
    # Get selected assets in the editor
    selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
    if not selected_assets:
        unreal.log_warning("No asset selected.")
        return

    # Get asset paths
    asset_paths = [unreal.EditorAssetLibrary.get_path_name_for_loaded_asset(asset) for asset in selected_assets]
    if not asset_paths:
        unreal.log_warning("Could not get asset paths.")
        return

    # Sync to content browser
    unreal.EditorAssetLibrary.sync_browser_to_objects(asset_paths)
    unreal.log("Synced selected asset(s) to Content Browser.")

if __name__ == "__main__":
    sync_selected_asset_to_content_browser()
    