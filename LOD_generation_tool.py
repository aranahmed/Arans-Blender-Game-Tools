import bpy
import os
from bpy.types import Operator, Panel
from bpy.props import IntProperty, FloatProperty, StringProperty, BoolProperty

class LODGeneratorTool(bpy.types.Operator):
    bl_idname = "objects.lod_generator"
    bl_label = "Generate LODs"
    bl_options = {'REGISTER', 'UNDO'}

    #lod_count: IntProperty(name='LOD Count', default=3, min=1, max=5)
    #reduction_ratio: FloatProperty(name='Reduction Ratio', default=0.5, min=0.1, max=1.0)

    
    def execute(self, context):
        
        lod_count = context.scene.lod_count
        reduction_ratio = context.scene.reduction_ratio
        
        
        self.create_lods(context, lod_count, reduction_ratio)
        

        
        return{'FINISHED'}
    
    def create_lods(self, context, lod_count, reduction_ratio):
        selected_objects = context.selected_objects
        lod_count = context.scene.lod_count  # Get the value from the Scene
        
        if not selected_objects:
            self.report({'ERROR'}, "No Object Selected")
            return {'CANCELLED'}

        for obj in selected_objects:
            if obj.type == 'MESH':
                self.generate_lods_for_objects(obj, lod_count, reduction_ratio)
                
                
               # bpy.ops.export_scene.lods_to_fbx('INVOKE_DEFAULT').lod_collection = lod_collection

        
    def generate_lods_for_objects(self, obj, lod_count, reduction_ratio):
        
        # create a new collection and link to scene as a child of our Mesh
        lod_collection = bpy.data.collections.new(name=f"{obj.name}_LODs")
        bpy.context.scene.collection.children.link(lod_collection)
        
        # Create a copy of the original first
        """
        lod0 = obj.copy()
        lod0.data = obj.data.copy()
        lod0.name = f"{obj.name}_LOD0"
        bpy.context.collection.objects.link(lod0)
        """
        
        # Loop through and create LODs
        for i in range(0,lod_count):
            #Duplicate objects
            lod_obj = obj.copy()
            lod_obj.data = obj.data.copy()
            lod_obj.name = f"{obj.name}_LOD{i}"
            
            lod_collection.objects.link(lod_obj)
            

            # Apply decimation modifier
            print(f"Applying LOD {i} with reduction ratio: {reduction_ratio}")
            reduction_factor = reduction_ratio ** i
            decimate_mod = lod_obj.modifiers.new(name=f"LOD_{i}_Decimate", type='DECIMATE')
            decimate_mod.ratio = reduction_factor
            bpy.context.view_layer.objects.active = lod_obj
            bpy.ops.object.modifier_apply(modifier=decimate_mod.name)
            
            # Moving them a bit so that we can see LODs clearly
            lod_obj.location.x += 3 * (i + 1)
            
            """
            # Detaching from collection if exists
            for collection in obj.users_collection:
                if (collection !=0):
                    collection.objects.unlink(lod_obj)
            """    
            
            # Extension Idea
            # Export to File If Folder 
            
            # Else Put out a error message : You need to specify a folder
            
        # Original object is deselected so we dont export or delete it on accident
        obj.select_set(False)
        
       
        
        return lod_collection
        
    def set_collection(self, collection):
        self.lod_collection = collection
         
    """
    # For loop runs through each selected object
    for obj in selected_objects: 
        if obj.type == 'MESH': # grabs the meshes

            # LOD 1 - 50% Reduction
            decimate_mod_1 = obj.modifiers.new(name="LOD_1", type='DECIMATE')
            decimate_mod_1.ratio = 0.5

            # LOD 2 - 25% Reduction
            decimate_mod_2 = obj.modifiers.new(name="LOD_2", type='DECIMATE')
            decimate_mod_2.ratio = 0.25
            
            # LOD 3 - 12.5% Reduction
            decimate_mod_3 = obj.modifiers.new(name="LOD_3", type='DECIMATE')
            decimate_mod_3.ratio = 0.125
            
            # Applies the Decimation modifiers
            bpy.ops.object.modifier_apply(modifier="LOD_1")
            bpy.ops.object.modifier_apply(modifier="LOD_2")
            bpy.ops.object.modifier_apply(modifier="LOD_3")
    """
    
class LODGeneratorPanel(bpy.types.Panel):
    bl_label = "LOD Generator Panel"
    bl_idname = "OBJECT_PT_lod_generator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "LOD Tool"

    def draw(self, context):
        layout = self.layout
        layout.operator("objects.lod_generator")
        layout.prop(context.scene, "lod_count")
        layout.prop(context.scene, "reduction_ratio")
        
        layout.operator("operator_normal_map_baker")
        
        
    def execute(self, context):
        return {'FINISHED'}

class ExportLODsToFBX(bpy.types.Operator):
    bl_idname = "export_scene.lods_to_fbx"
    bl_label = "Export LODs to FBX"
    bl_options = {'REGISTER', 'UNDO'}
    
    export_path: StringProperty(
        name="Export Path",
        description="Directory to export FBX files",
        default="//",
        subtype='DIR_PATH'
    )
    
    single_mesh_toggle: BoolProperty(
        name="MultiMesh Export",
        description="Exports multiple meshes",
        default=False
    )


    
    def execute(self, context):
        # Define the output directory
        output_directory = bpy.path.abspath(self.export_path) # input from the user
        if not os.path.exists(output_directory): 
            os.makedirs(output_directory) # if it cant find dir then makes a directory
    
       # Search for collections with "_LODs" suffix
        lod_collections = [col for col in bpy.data.collections if col.name.endswith("_LODs")]

        if not lod_collections:
            self.report({'ERROR'}, "No LOD collections found")
            return {'CANCELLED'}
        
        for lod_collection in lod_collections:
            bpy.ops.object.select_all(action='DESELECT')
            
            # Select all objects in the LOD collection
            for obj in lod_collection.objects:
                obj.select_set(True)
                
                export_path = os.path.join(output_directory, f"{lod_collection.name}.fbx")
                
                if self.single_mesh_toggle:
                     bpy.ops.export_scene.fbx(
                    filepath=export_path,
                    use_selection=True, 
                    mesh_smooth_type='FACE',
                    add_leaf_bones=False,
                    bake_anim=False,
                    object_types={'MESH'}
                )
            
                    
            
            export_path = os.path.join(output_directory, f"{lod_collection.name}.fbx")
            
#            if self.single_mesh_toggle:
#                self.report({'INFO'}, "Option Enabled")
#            else:
#                self.report({'INFO'}, "Option Disabled")
            
            #export settings
            bpy.ops.export_scene.fbx(
                    filepath=export_path,
                    use_selection=True, 
                    mesh_smooth_type='FACE',
                    add_leaf_bones=False,
                    bake_anim=False,
                    object_types={'MESH'}
                )
            
        

        return {'FINISHED'}

class LODExportPanel(bpy.types.Panel):
    bl_label = "LOD Export Panel"
    bl_idname = "OBJECT_PT_lod_export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "CSV2Mesh"
    
     
 
    def draw(self, context):

        # Add a text box for the export path
        self.layout.prop(context.scene, "export_path")
        
        #self.layout.operator("export_scene.lods_to_fbx", text="Single Mesh Export").single_mesh_toggle

        # Add the export button
        self.layout.operator("export_scene.lods_to_fbx")
        
       
    

# Come back and make this
class NormalMapBaker(bpy.types.Operator):
    bl_label = "Generate Normal Map"
    bl_idname = "operator_normal_map_baker"
    bl_options = {'REGISTER', 'UNDO'}
    
    def bake_normal_map():
        pass
        

def register():
    bpy.utils.register_class(LODGeneratorTool)
    bpy.utils.register_class(LODGeneratorPanel)
    bpy.utils.register_class(ExportLODsToFBX)
    bpy.utils.register_class(LODExportPanel)
    #bpy.utils.register_class(NormalMapBaker)
    bpy.types.Scene.lod_count = IntProperty(name="LOD Count", default=3, min=1, max=5)
    bpy.types.Scene.reduction_ratio = FloatProperty(name="Reduction Ratio", default=0.5, min=0.1, max=1.0)
    
    bpy.types.Scene.export_path = StringProperty(
        name="Export Path",
        description="Dictionary to export FBX",
        default='//',
        subtype='DIR_PATH'
        )
        
    bpy.types.Scene.single_mesh_toggle = BoolProperty(
        name="Multi Mesh Export",
        description="Exports multiple meshes",
        default=False
    )



    


def unregister():
    bpy.utils.unregister_class(LODGeneratorTool)
    bpy.utils.register_class(LODGeneratorPanel)
    bpy.utils.register_class(ExportLODsToFBX)
    bpy.utils.register_class(LODExportPanel)
    
    #bpy.utils.register_class(NormalMapBaker)
    del bpy.types.Scene.lod_count
    del bpy.types.Scene.reduction_ratio
    del bpy.types.Scene.export_path


if __name__ == "__main__":
    register()
        
""""    
#Normal Map Baker

class NormalMapBaker(bpy.types.Operator):
    def GenerateNormalMap(resoltion):
        bpy.ops.image.new(name="Normal", width=resoltion, height=resoltion)
        normal_map = bpy.data.images['Normal']

        bpy.context.scene.render.bake.use_selected_to_active = True
        bpy.context.scene.render.bake.use_cage = True
        bpy.context.scene.render.bake.cage_extrusion = 0.1
        bpy.context.scene.render.bake.margin = 2
        bpy.context.scene.render.bake.use_pass_normal = True

        bpy.ops.object.bake(type='NORMAL')
"""

    