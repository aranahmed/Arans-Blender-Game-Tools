# Aran's Game Tools for Blender

**Aran's Game Tools** is a Blender add-on designed to streamline common game asset preparation tasks, especially for Unreal Engine workflows. It provides tools for mesh renaming, vertex color ID map generation, lightmap UV creation, and more—all accessible from the Blender UI.

---

## Features

- **Loose Parts to Vertex Colors:**  
  Assigns unique vertex colors to each disconnected mesh island (loose part) for easy ID map creation.

- **Bake Vertex Colors to Texture:**  
  Bake your vertex color ID map to a texture for export to game engines.

- **Create Vertex Groups from Loose Parts:**  
  Optionally create a vertex group for each loose part.

- **Lightmap UV Generation:**  
  Automatically create and unwrap a second UV channel for lightmapping, compatible with Unreal Engine.

- **Custom Prefix/Suffix Tools:**  
  Easily set naming conventions for static meshes, VFX meshes, and LODs.

- **Export Path Management:**  
  Set and manage export directories for Unreal Engine assets.

---

## Installation

1. Download or clone this repository.
2. In Blender, go to **Edit > Preferences > Add-ons > Install**.
3. Select the `.zip` or the folder containing this add-on.
4. Enable **Aran's Game Tools** in the add-ons list.

---

## Usage

All tools are available in the **3D Viewport > Sidebar (N) > Game Tools** tab.

### Vertex Color ID Map

1. Select your mesh.
2. In the **Game Tools** panel, click **Loose Parts to Vertex Colors**.
   - Optionally, enable "Create Vertex Groups from Loose Parts" to generate vertex groups.
3. To bake the vertex colors to a texture, click **Bake Vertex Colors to Image**.

### Lightmap UVs

1. Select your mesh(es).
2. In the **Game Tools** panel, enable **AutoUnwrap Lightmap UVs**.
3. Click **Create Lightmap UVs**.

### Naming and Export Tools

- Set prefixes, suffixes, and export paths as needed for Unreal Engine compatibility.

---

## Requirements

- Blender 3.0 or newer (tested on Blender 4.3)

---

## Known Issues

- **Performance:** The loose parts detection can be slow on very large or complex meshes.
- **Vertex Color Layer Overwrite:** If you run the loose parts tool multiple times, it will create multiple "LooseParts" vertex color layers.
- **Bake Node Setup:** The bake operator replaces certain nodes in the active material; custom node setups may be affected.
- **No Undo for Some Actions:** Some operations (like UV creation) may not be fully undoable in all Blender versions.
- **Limited Color Palette:** If you have more loose parts than colors in the palette, colors will repeat.

---

## Planned Features

- **Faster Loose Parts Detection:** Optimize the algorithm for large meshes.
- **Custom Color Palettes:** Allow users to define their own color sets.
- **Batch Export Tools:** Export multiple assets with one click.
- **Better Error Handling:** More robust checks and user feedback.
- **Support for More Bake Types:** Including AO, normals, etc.
- **Improved UI/UX:** More intuitive controls and documentation in the Blender UI.

---

## Development

Feel free to fork, contribute, or submit issues!

---

## License

MIT License

---

**Author:** Aran Ahmed  
**Category:** Game Development  
