import bpy
import bmesh
import mathutils
import os

# Function Definitions (Your existing code)
def bake_morph_textures(obj, frame_range, scale, name, output_dir):
    """ Bake and export morph textures for the specified object and frame range """
    
    pixels_pos = []
    pixels_nrm = []
    pixels_tan = []
    width = 0
    
    # Bake the morph textures
    for i in range(frame_range[1] - frame_range[0]):
        f = i + frame_range[0]
        temp_obj = new_object_from_frame(obj, f)
        new_pixels = get_vertex_data_from_frame(temp_obj, scale)
        width = len(new_pixels)
        
        for pixel in new_pixels:
            pixels_pos.extend(pixel[0])
            pixels_nrm.extend(pixel[1])
            pixels_tan.extend(pixel[2])
    
    height = frame_range[1] - frame_range[0]
    
    write_output_image(pixels_pos, name + '_position', [width, height], output_dir)
    write_output_image(pixels_nrm, name + '_normal', [width, height], output_dir)
    write_output_image(pixels_tan, name + '_tangent', [width, height], output_dir)
    
    frame_zero = new_object_from_frame(obj, 0)
    create_morph_uv_set(frame_zero)
    export_mesh(frame_zero, output_dir, name)
    
    return frame_zero

def write_output_image(pixel_list, name, size, output_dir):
    # Ensure the directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    image = bpy.data.images.new(name, width=size[0], height=size[1])
    image.pixels = pixel_list
    image.filepath_raw = os.path.join(output_dir, name + ".png")
    image.file_format = 'PNG'
    image.save()

def new_object_from_frame(obj, f):
    """ Create a new mesh from the evaluated version of obj at frame f """
    
    context = bpy.context
    scene = context.scene
    scene.frame_set(f)
    
    dg = context.view_layer.depsgraph
    eval_obj = obj.evaluated_get(dg)
    duplicate = bpy.data.objects.new('frame_' + str(f), bpy.data.meshes.new_from_object(eval_obj))
    
    return duplicate

def get_vertex_data_from_frame(obj, position_scale):
    """ Given an object, return the Position, Normal, and Tangent from each vertex """
    
    obj.data.calc_tangents()
    vertex_data = [None] * len(obj.data.vertices)
    
    for face in obj.data.polygons:
        for vert in [obj.data.loops[i] for i in face.loop_indices]:
            index = vert.vertex_index
            tangent = unsign_vector(vert.tangent.copy())
            normal = unsign_vector(vert.normal.copy())
            position = unsign_vector(obj.data.vertices[index].co.copy() / position_scale)
            
            # Ensure each component is correctly extended to [r, g, b, a]
            tangent.append(1.0)
            normal.append(1.0)
            position.append(1.0)
            
            vertex_data[index] = [position, normal, tangent]
    
    return vertex_data

def unsign_vector(vec, as_list=True):
    """ Rescale input vector from -1..1 to 0..1 """
    
    vec += mathutils.Vector((1.0, 1.0, 1.0))
    vec /= 2.0
    
    if as_list:
        return list(vec.to_tuple())
    else:
        return vec

def create_morph_uv_set(obj):
    """ Creates a new UV set that runs across the UV with evenly spaced vertices """
    
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    
    # Ensure the primary UV map exists
    if not obj.data.uv_layers:
        bm.loops.layers.uv.new("UVMap")
    
    # Create or get the second UV layer
    uv_layer = bm.loops.layers.uv.get("UVMap2")
    if not uv_layer:
        uv_layer = bm.loops.layers.uv.new("UVMap2")
    
    pixel_size = 1.0 / len(bm.verts)
    
    for i, v in enumerate(bm.verts):
        for l in v.link_loops:
            uv_data = l[uv_layer]
            uv_data.uv = mathutils.Vector((i * pixel_size, 0.0))
    
    bm.to_mesh(obj.data)
    bm.free()

    # Make sure UV layers are assigned to the mesh
    obj.data.update()

def export_mesh(obj, output_dir, name):
    context = bpy.context
    context.collection.objects.link(obj)
    context.view_layer.objects.active = obj
    
    output_file = os.path.join(output_dir, name + "_mesh.fbx")
    
    bpy.ops.export_scene.fbx(
        filepath=output_file,
        use_selection=True,
        add_leaf_bones=False,
        use_mesh_modifiers=True,
        mesh_smooth_type='FACE',
        bake_space_transform=True,
        apply_scale_options='FBX_SCALE_ALL',
        object_types={'MESH'},
        path_mode='AUTO',
        embed_textures=False
    )

# Operator to Execute the Bake
class OBJECT_OT_BakeMorphTextures(bpy.types.Operator):
    """Bake Morph Textures"""
    bl_idname = "object.bake_morph_textures"
    bl_label = "Bake Morph Textures"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if not obj:
            self.report({'ERROR'}, "No active object selected")
            return {'CANCELLED'}

        output_dir = bpy.path.abspath(context.window_manager.bake_morph_output_dir)
        output_dir = os.path.normpath(output_dir)  # Normalize the path

        if not output_dir:
            self.report({'ERROR'}, "Output directory is not set")
            return {'CANCELLED'}

        try:
            bake_morph_textures(
                obj,
                [0, 60],  # Frame range
                1.0,  # Scale
                "T_VAT_" + obj.name,  # Name
                output_dir  # Output directory
            )
            self.report({'INFO'}, "Morph textures baked successfully")
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        return {'FINISHED'}

# Panel to Display the Operator
class VIEW3D_PT_BakeMorphTexturesPanel(bpy.types.Panel):
    """Panel for Baking Morph Textures"""
    bl_label = "Bake Morph Textures"
    bl_idname = "VIEW3D_PT_bake_morph_textures"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Morph Tools'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(context.window_manager, "bake_morph_output_dir", text="Output Directory")

        layout.operator("object.bake_morph_textures", text="Bake Morph Textures")

# Register and Unregister Classes
def register():
    bpy.utils.register_class(OBJECT_OT_BakeMorphTextures)
    bpy.utils.register_class(VIEW3D_PT_BakeMorphTexturesPanel)

    bpy.types.WindowManager.bake_morph_output_dir = bpy.props.StringProperty(
        name="Output Directory",
        description="Directory to save the baked textures and mesh",
        default="",
        subtype='DIR_PATH'
    )

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_BakeMorphTextures)
    bpy.utils.unregister_class(VIEW3D_PT_BakeMorphTexturesPanel)

    del bpy.types.WindowManager.bake_morph_output_dir

if __name__ == "__main__":
    register()