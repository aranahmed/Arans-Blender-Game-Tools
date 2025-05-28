import bpy

def bake_texture_maps():
    # Set the render engine to Cycles
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'GPU'  # Use GPU if available

    # Iterate through selected objects
    selected_objects = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']

    if not selected_objects:
        print("No valid selected objects found for baking.")
        return

    for obj in selected_objects:
        for slot in obj.material_slots:
            material = slot.material
            if not material or not material.use_nodes:
                continue  # Skip if no material or material doesn't use nodes

            # Select the object
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)

            # Create a new image for baking
            image_name = f"{obj.name}_baked_texture"
            # Check if the image already exists and remove it
            if image_name in bpy.data.images:
                bpy.data.images.remove(bpy.data.images[image_name])
            
            bpy.context.view_layer.objects.active = obj
            baked_image = bpy.data.images.new(image_name, width=1024, height=1024)

            # Add an image texture node to the material
            nodes = material.node_tree.nodes
            links = material.node_tree.links
            texture_node = nodes.new(type='ShaderNodeTexImage')
            texture_node.image = baked_image

            # Set the image texture node as active for baking
            material.node_tree.nodes.active = texture_node

            # Bake the DIFFUSE texture
            bpy.ops.object.bake(type='DIFFUSE')

            # Preview the basked image

            # Set the texture file name to unreal naming convention
            baked_image.name = f"T_{obj.name}_baked_texture"

            # Save the baked image
            baked_image.filepath_raw = f"//{image_name}.png"
            baked_image.file_format = 'PNG'
            baked_image