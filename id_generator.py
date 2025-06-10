import bpy
import random
from collections import defaultdict

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

    def check_for_overlapping_uvs(self, context, used_colors):
        print("Checking for overlapping UVs...")
        obj = bpy.context.active_object
        mesh = obj.data
        uv_layer = mesh.uv_layers.active.data

        # Map rounded UVs to list of vertex indices
        uv_to_verts = defaultdict(set)
        for poly in mesh.polygons:
            for li in poly.loop_indices:
                uv = uv_layer[li].uv
                # Round to 4 decimals to avoid floating point issues
                uv_key = (round(uv.x, 4), round(uv.y, 4))
                vert_idx = mesh.loops[li].vertex_index
                uv_to_verts[uv_key].add(vert_idx)

        # Find overlapped UVs (more than one vertex per UV)
        overlapped_verts = set()
        for verts in uv_to_verts.values():
            if len(verts) > 1:
                overlapped_verts.update(verts)

        # # Assign to a vertex group
        # vg = obj.vertex_groups.get("OverlappedUVs")
        # if not vg:
        #     vg = obj.vertex_groups.new(name="OverlappedUVs")
        # vg.add(list(overlapped_verts), 1.0, 'REPLACE')

        # Assign a unique vertex color to all overlapped UVs
        # Context from the colour picked before
        
        overlap_color = None  # Initialize to None
        for color in HIGH_CONTRAST_COLORS.values():
            print(overlap_color)
            if color not in used_colors:
                overlap_color = color
                break

        if overlap_color is None:
            
            while True:
                candidate = (random.random(), random.random(), random.random(), 1)
                if candidate not in used_colors:
                    overlap_color = candidate
                    break

         # Use the currently active vertex color layer
        vcol = mesh.vertex_colors.new(name="OverlappedUVs") if not mesh.vertex_colors else mesh.vertex_colors.active
        if vcol is None:
            self.report({'ERROR'}, "No active vertex color layer found!")
            return {'CANCELLED'}

        if len(mesh.vertex_colors) >= 8:  # Blender's default limit is 8
            self.report({'ERROR'}, "Too many vertex color layers!")
            return {'CANCELLED'}

        # Assign color to all loops whose vertex is in overlapped_verts
        for poly in mesh.polygons:
            for loop_idx in poly.loop_indices:
                vert_idx = mesh.loops[loop_idx].vertex_index
                if vert_idx in overlapped_verts:
                    vcol.data[loop_idx].color = overlap_color

                # Optionally, clear color for non-overlapped verts (for clarity)
        for poly in mesh.polygons:
            for loop_idx in poly.loop_indices:
                vert_idx = mesh.loops[loop_idx].vertex_index
                if vert_idx not in overlapped_verts:
                    vcol.data[loop_idx].color = (0, 0, 0, 1)  # Black or transparent


        print(f"Assigned {len(overlapped_verts)} vertices to 'OverlappedUVs' group.")

        


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

        used_colors = set()
        # Assign colors by loose part
        for i, group in enumerate(parts):
            color_name = color_names[i % len(color_names)]
            color_value = HIGH_CONTRAST_COLORS[color_name]
            used_colors.add(color_name)
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
            
            #self.check_for_overlapping_uvs(context, used_colors)


        self.report({'INFO'}, f"Assigned vertex colours to {len(parts)} loose parts.")
        return {'FINISHED'}

class VIEW3D_PT_ID_Map_Baker(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Vert Colour Tools"
    bl_idname = "VIEW3D_PT_id_map_baker"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'CSV2Mesh'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Export button
        layout.prop(scene, "create_vertex_groups_from_loose_parts", text="Create Vertex Groups from Loose Parts")

        layout.operator("object.loose_parts_to_vertex_colors", icon='NONE')

        layout.operator("object.bake_vertex_colors_to_image", icon='EXPORT')

        layout.prop(scene, "export_baked_ID", text="//", icon='FOLDER_REDIRECT')


        layout.operator("object.detect_overlapping_uvs", icon='NONE')

        layout.separator()
        layout.label(text="Bake BBOX Vert Colours:")

        grid = layout.grid_flow(row_major=True, columns=3, even_columns=True, even_rows=True, align=True)
        grid.prop(scene, "gradient_r_axis", text="Red Axis")
        grid.prop(scene, "gradient_g_axis", text="Green Axis")
        grid.prop(scene, "gradient_b_axis", text="Blue Axis")

        row = layout.row()
        row.prop(scene,"reverse_bbox_gradient_toggle", text="Reverse")
        row.operator("object.bake_bbox_gradient_to_vertex_colors", icon='NONE')

        layout.separator()
        layout.label(text="Bake Origin Radial Vert Colours:")
        layout.operator("object.bake_origin_radial_gradient_to_vertex_colours", icon='NONE')



        

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
        img = bpy.data.images.new(f"{obj.name}_ID", width=1024, height=1024)

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

class OBJECT_OT_detect_overlapping_uvs(bpy.types.Operator):
    """Detect overlapping UVs"""
    bl_idname = "object.detect_overlapping_uvs"
    bl_label = "Detect Overlapping UVs"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = bpy.context.active_object
        mesh = obj.data
        uv_layer = mesh.uv_layers.active.data

        # Map rounded UVs to list of vertex indices
        uv_to_verts = defaultdict(set)
        for poly in mesh.polygons:
            for li in poly.loop_indices:
                uv = uv_layer[li].uv
                # Round to 4 decimals to avoid floating point issues
                uv_key = (round(uv.x, 4), round(uv.y, 4))
                vert_idx = mesh.loops[li].vertex_index
                uv_to_verts[uv_key].add(vert_idx)

        # Find overlapped UVs (more than one vertex per UV)
        overlapped_verts = set()
        for verts in uv_to_verts.values():
            if len(verts) > 1:
                overlapped_verts.update(verts)

        # Assign to a vertex group
        vg = obj.vertex_groups.get("OverlappedUVs")
        if not vg:
            vg = obj.vertex_groups.new(name="OverlappedUVs")
        vg.add(list(overlapped_verts), 1.0, 'REPLACE')

        # Assign a unique vertex color to all overlapped UVs
        # Pick a color (e.g., Magenta)
        overlap_color = (1, 0, 1, 1)  # Magenta RGBA

        if not mesh.vertex_colors:
            vcol = mesh.vertex_colors.new(name="OverlappedUVs")
        else:
            vcol = mesh.vertex_colors.active

        if len(mesh.vertex_colors) >= 8:  # Blender's default limit is 8
            self.report({'ERROR'}, "Too many vertex color layers!")
            return {'CANCELLED'}

        # Assign color to all loops whose vertex is in overlapped_verts
        for poly in mesh.polygons:
            for loop_idx in poly.loop_indices:
                vert_idx = mesh.loops[loop_idx].vertex_index
                if vert_idx in overlapped_verts:
                    vcol.data[loop_idx].color = overlap_color


        print(f"Assigned {len(overlapped_verts)} vertices to 'OverlappedUVs' group.")

        return {'FINISHED'}
    
class OBJECT_OT_bake_bbox_gradient_to_vertex_colors(bpy.types.Operator):
    #Bake a BBOX-based gradient to vertex colors
    bl_idname = "object.bake_bbox_gradient_to_vertex_colors"
    bl_label = "Bake BBOX Gradient to Vertex Colors"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Select a mesh object")
            return {'CANCELLED'}

        mesh = obj.data

        # Ensure a vertex color layer exists
        if not mesh.vertex_colors:
            vcol = mesh.vertex_colors.new(name="BBOX_Gradient")
        else:
            vcol = mesh.vertex_colors.active

        # Get all vertex coordinates in object space
        coords = [v.co for v in mesh.vertices]
        min_x = min(v.x for v in coords)
        max_x = max(v.x for v in coords)
        min_y = min(v.y for v in coords)
        max_y = max(v.y for v in coords)
        min_z = min(v.z for v in coords)
        max_z = max(v.z for v in coords)

        # Avoid division by zero
        range_x = max_x - min_x if max_x != min_x else 1.0
        range_y = max_y - min_y if max_y != min_y else 1.0
        range_z = max_z - min_z if max_z != min_z else 1.0

        scene = context.scene
        axis_map = {
            'X' : lambda v: (v.x - min_x) / range_x,
            'Y' : lambda v: (v.y - min_y) / range_y,
            'Z' : lambda v: (v.z - min_z) / range_z,

        }

        r_axis = scene.gradient_r_axis
        g_axis = scene.gradient_g_axis
        b_axis = scene.gradient_b_axis


        # Assign gradient color to each loop (per face corner)
        for poly in mesh.polygons:
            for loop_idx in poly.loop_indices:
                vert_idx = mesh.loops[loop_idx].vertex_index
                v = mesh.vertices[vert_idx].co
                # Normalize to 0..1
                r = axis_map[r_axis](v)
                g = axis_map[g_axis](v)
                b = axis_map[b_axis](v)
                if scene.reverse_bbox_gradient_toggle:

                    # Reverse the gradient
                    r = 1.0 - r
                    g = 1.0 - g
                    b = 1.0 - b
                
                # Example: RGB = XYZ gradient
                vcol.data[loop_idx].color = (r, g, b, 1.0)

        self.report({'INFO'}, "BBOX gradient vertex colors assigned.")
        return {'FINISHED'}
    
class OBJECT_OT_bake_origin_radial_gradient_to_vertex_colors(bpy.types.Operator):
    # Bake a radial gradient from the object's origin to its edge
    bl_idname = "object.bake_origin_radial_gradient_to_vertex_colours"
    bl_label = "Bake Origin Radial Gradient"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Select a mesh object")
            return {'CANCELLED'}

        mesh = obj.data

        # Ensure a vertex color layer exists
        if not mesh.vertex_colors:
            vcol = mesh.vertex_colors.new(name="OriginRadialGradient")
        else:
            vcol = mesh.vertex_colors.active

        # Compute distances from origin for all vertices
        coords = [v.co for v in mesh.vertices]
        distances = [v.length for v in coords]
        max_dist = max(distances) if distances else 1.0

        # Assign gradient color to each loop (per face corner)
        for poly in mesh.polygons:
            for loop_idx in poly.loop_indices:
                vert_idx = mesh.loops[loop_idx].vertex_index
                v = mesh.vertices[vert_idx].co
                d = v.length / max_dist if max_dist != 0 else 0.0
                # Grayscale: all channels get the same value
                
                vcol.data[loop_idx].color = (d, d, d, 1.0)

        self.report({'INFO'}, "Radial gradient from origin assigned to vertex colors.")
        return {'FINISHED'}

def properties():
    
    bpy.types.Scene.create_vertex_groups_from_loose_parts = bpy.props.BoolProperty(
        name="Create Vertex Groups from Loose Parts",
        description="Create vertex groups from loose parts",
        default=False
    )
    bpy.types.Scene.reverse_bbox_gradient_toggle = bpy.props.BoolProperty(
      
        name="Toggle Reverse BBOX Gradient",
        description="Toggle the reverse BBOX gradient",
        default=False
    )   
    bpy.types.Scene.gradient_r_axis = bpy.props.EnumProperty(
        name="Red Axis",
        description="Axis for Red channel",
        items=[('X', "X", ""), ('Y', "Y", ""), ('Z', "Z", "")],
        default='Z'
    )
    bpy.types.Scene.gradient_g_axis = bpy.props.EnumProperty(
        name="Green Axis",
        description="Axis for Green channel",
        items=[('X', "X", ""), ('Y', "Y", ""), ('Z', "Z", "")],
        default='Z'
    )
    bpy.types.Scene.gradient_b_axis = bpy.props.EnumProperty(
        name="Blue Axis",
        description="Axis for Blue channel",
        items=[('X', "X", ""), ('Y', "Y", ""), ('Z', "Z", "")],
        default='Z'
    )
    
def register():
    bpy.utils.register_class(OBJECT_OT_loose_parts_to_vertex_colors)
    bpy.utils.register_class(VIEW3D_PT_ID_Map_Baker)
    bpy.utils.register_class(OBJECT_OT_bake_vertex_colors_to_image)
    bpy.utils.register_class(OBJECT_OT_detect_overlapping_uvs)
    bpy.utils.register_class(OBJECT_OT_bake_bbox_gradient_to_vertex_colors)
    bpy.utils.register_class(OBJECT_OT_bake_origin_radial_gradient_to_vertex_colors)

    properties()

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_loose_parts_to_vertex_colors)
    bpy.utils.unregister_class(VIEW3D_PT_ID_Map_Baker)
    bpy.utils.unregister_class(OBJECT_OT_bake_vertex_colors_to_image)
    bpy.utils.unregister_class(OBJECT_OT_detect_overlapping_uvs)
    bpy.utils.unregister_class(OBJECT_OT_bake_bbox_gradient_to_vertex_colors)
    bpy.utils.unregister_class(OBJECT_OT_bake_origin_radial_gradient_to_vertex_colors)

    del bpy.types.Scene.create_vertex_groups_from_loose_parts
    del bpy.types.Scene.gradient_r_axis
    del bpy.types.Scene.gradient_g_axis
    del bpy.types.Scene.gradient_b_axis
    del bpy.types.Scene.reverse_bbox_gradient_toggle


if __name__ == "__main__":
    register()