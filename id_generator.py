import bpy
import random

HIGH_CONTRAST_COLORS = {
    "Red":     (1, 0, 0, 1),
    "Green":   (0, 1, 0, 1),
    "Blue":    (0, 0, 1, 1),
    "Yellow":  (1, 1, 0, 1),
    "Magenta": (1, 0, 1, 1),
    "Cyan":    (0, 1, 1, 1),
}

class OBJECT_OT_loose_parts_to_vertex_colors(bpy.types.Operator):
    bl_idname = "object.loose_parts_to_vertex_colors"
    bl_label = "Loose Parts to Vertex Colors"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Select a mesh object")
            return {'CANCELLED'}

        mesh = obj.data

        # Ensure a vertex color layer exists
        if not mesh.vertex_colors:
            vcol = mesh.vertex_colors.new(name="LooseParts")
        else:
            vcol = mesh.vertex_colors.active

        # Find loose parts
        verts = mesh.vertices
        visited = set()
        parts = []
        for v in verts:
            if v.index in visited:
                continue
            group = set()
            stack = [v.index]
            while stack:
                idx = stack.pop()
                if idx in visited:
                    continue
                visited.add(idx)
                group.add(idx)
                for e in mesh.edges:
                    if e.vertices[0] == idx and e.vertices[1] not in visited:
                        stack.append(e.vertices[1])
                    elif e.vertices[1] == idx and e.vertices[0] not in visited:
                        stack.append(e.vertices[0])
            if group:
                parts.append(group)

        color_names = list(HIGH_CONTRAST_COLORS.keys())
        if len(parts) > len(color_names):
            self.report({'WARNING'}, "More parts than unique colors! Some colors will repeat.")
        random.shuffle(color_names)

        # Assign colors by loose part
        for i, group in enumerate(parts):
            color_name = color_names[i % len(color_names)]
            color_value = HIGH_CONTRAST_COLORS[color_name]
            for poly in mesh.polygons:
                if any(vidx in group for vidx in poly.vertices):
                    for loop_idx in poly.loop_indices:
                        vcol.data[loop_idx].color = color_value

            # If the toggle is enabled, create a vertex group for this loose part
            if context.scene.create_vertex_groups_from_loose_parts:
                vg_name = f"ID_MAP_{i+1}"
                if vg_name not in obj.vertex_groups:
                    vg = obj.vertex_groups.new(name=vg_name)
                    vg.add(list(group), 1.0, 'ADD')



        

        self.report({'INFO'}, f"Assigned vertex colors to {len(parts)} loose parts.")
        return {'FINISHED'}

class VIEW3D_PT_ID_Map_Baker(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "ID Map Baker"
    bl_idname = "VIEW3D_PT_id_map_baker"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Game Tools'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Export button
        layout.prop(scene, "create_vertex_groups_from_loose_parts", text="Create Vertex Groups from Loose Parts")

        layout.operator("object.loose_parts_to_vertex_colors", icon='NONE')

        layout.operator("object.bake_vertex_colors_to_image", icon='EXPORT')

        

class OBJECT_OT_bake_vertex_colors_to_image(bpy.types.Operator):
    """Bake vertex colors to an image"""
    bl_idname = "object.bake_vertex_colors_to_image"
    bl_label = "Bake Vertex Colors to Image"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Select a mesh object")
            return {'CANCELLED'}

        # Ensure UV map exists
        if not obj.data.uv_layers:
            obj.data.uv_layers.new(name="UVMap")

        # Create a new image
        img = bpy.data.images.new("BakedVertexColors", width=1024, height=1024)

        # Ensure material and node setup
        mat = obj.active_material
        if not mat:
            mat = bpy.data.materials.new(name="BakeMat")
            obj.data.materials.append(mat)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        # Remove existing bake nodes if any
        for n in nodes:
            if n.name in {"BakeImage", "VCOL", "EMIT"}:
                nodes.remove(n)

        # Add image texture node
        img_node = nodes.new(type='ShaderNodeTexImage')
        img_node.name = "BakeImage"
        img_node.image = img

        # Add attribute node for vertex colors
        attr_node = nodes.new(type='ShaderNodeAttribute')
        attr_node.name = "VCOL"
        attr_node.attribute_name = obj.data.vertex_colors.active.name

        # Add emission node
        emit_node = nodes.new(type='ShaderNodeEmission')
        emit_node.name = "EMIT"

        # Connect attribute color to emission color
        links.new(attr_node.outputs['Color'], emit_node.inputs['Color'])
        # Connect emission to material output
        output_node = nodes.get("Material Output")
        links.new(emit_node.outputs['Emission'], output_node.inputs['Surface'])

        # Set image node as active for baking
        nodes.active = img_node

        # Set Cycles as render engine and bake type
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.cycles.bake_type = 'EMIT'

        # Bake!
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.bake(type='EMIT')

        # Save the image (optional)
        img.filepath_raw = bpy.path.abspath("//baked_vertex_colors.png")
        img.file_format = 'PNG'
        img.save()

        self.report({'INFO'}, "Vertex colors baked and image saved as baked_vertex_colors.png")
        return {'FINISHED'}

def properties():
    
    bpy.types.Scene.create_vertex_groups_from_loose_parts = bpy.props.BoolProperty(
        name="Create Vertex Groups from Loose Parts",
        description="Create vertex groups from loose parts",
        default=False
    )   
def register():
    bpy.utils.register_class(OBJECT_OT_loose_parts_to_vertex_colors)
    bpy.utils.register_class(VIEW3D_PT_ID_Map_Baker)
    bpy.utils.register_class(OBJECT_OT_bake_vertex_colors_to_image)

    properties()

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_loose_parts_to_vertex_colors)
    bpy.utils.unregister_class(VIEW3D_PT_ID_Map_Baker)
    bpy.utils.unregister_class(OBJECT_OT_bake_vertex_colors_to_image)

if __name__ == "__main__":
    register()