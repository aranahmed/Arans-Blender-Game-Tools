import sys
import unreal

# Optionally add your tools folder to sys.path
sys.path.append(r"I:/Unreal/EditorTools_2/EditorTools/Python")

# Import your main tool script (this registers your BlueprintFunctionLibrary, etc.)
import custom_import_unreal

unreal.log("Custom import tools loaded at startup!")