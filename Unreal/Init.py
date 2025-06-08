import sys
import unreal
import os

# Get the Unreal project directory
project_dir = unreal.SystemLibrary.get_project_directory()

# Build the path to your tools folder relative to the project directory
tools_path = os.path.join(project_dir, "Python")

# Add to sys.path if not already present
if tools_path not in sys.path:
    sys.path.append(tools_path)

import custom_import_unreal



unreal.log(f"Tools Path: {tools_path}")