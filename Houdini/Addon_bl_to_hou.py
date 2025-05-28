bl_info = {
    "name" : "Send To Houdini",
    "version" : (1,0),
    "blender" : (3,6,2),
    "location" : "View3D > Toolbar > Houdini",
    "description" : "sending the model to Houdini",
    "category" : "Houdini"
}

import bpy
import subprocess

class SimplePanel(bpy.types.Panel):
    bl_idname = "Houdini_panel"
    bl_category = "Houdini"
    bl_label = "Houdini Menu"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    def draw(self,context):
        layout  = self.layout
        layout.operator("object.send_houdini")

class LaunchHoudini(bpy.types.Operator):
    bl_idname = "object.send_houdini"
    bl_label = "Send to Houdini"

    def execute(self, context):
        fbxPath = 'F:/Tools/temp_geo.fbx'
        bpy.ops.export_scene.fbx(filepath=fbxPath, global_scale =  0.01)
        
        HoudiniPath = 'C:/Program Files/Side Effects Software/Houdini 19.5.682/bin/houdinifx.exe'
        HoudiniScript = 'F:/Tools/import_hou_fbx.py'

        cmd = [HoudiniPath, HoudiniScript]
        subprocess.Popen(cmd)


        return {"FINISHED"}

def register():
    bpy.utils.register_class(SimplePanel)
    bpy.utils.register_class(LaunchHoudini)

def unregister():
    bpy.utils.unregister_class(SimplePanel)
    bpy.utils.unregister_class(LaunchHoudini)

if __name__ == "__main__":
    register()

#bpy.utils.register_class(SimplePanel)
    
