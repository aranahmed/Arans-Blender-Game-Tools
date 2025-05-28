# Aran's Game Tools for Blender

This Blender add-on is a collection of little helpers for anyone prepping assets for Unreal Engine or just wanting to speed up some repetitive Blender tasks. It's not perfect, but it gets the job done and saves you some clicks.

---

## What It Does

- **Loose Parts to Vertex Colors:**  
  Quickly color each floating mesh island (loose part) with a unique vertex color. Great for making ID maps.
  Identifies and combines overlapped geo to same vertex colour.

- **Bake Vertex Colors to Texture:**  
  Take those vertex colors and bake them down to a texture you can export.

- **Vertex Groups from Loose Parts:**  
  Optionally, make a vertex group for each loose part (if you want to select them later).

- **Lightmap UVs:**  
  One-click creation of a second UV channel for lightmaps, ready for Unreal.

- **Naming and Export Helpers:**  
  Set up prefixes, suffixes, and export paths for Unreal Engine assets.

  ## CSV-Driven Asset Validation & Management

- **CSV-Based Asset Validation:**  
  Automatically checks selected objects against a CSV file containing your asset data (name, type, master material, etc).

- **Smart Renaming:**  
  If an object's name doesn't match the CSV (including prefix rules), the tool can prompt you to rename it to the correct convention.

- **Batch Correction:**  
  See all naming mismatches at once and choose to batch-rename all assets to match your CSV.

- **Custom Properties Assignment:**  
  Assigns asset metadata (like `AssetName`, `AssetType`, `MasterMaterial`) as custom properties on your Blender objects, based on the CSV.

- **Master Material Assignment:**  
  Automatically assigns the correct master material from the CSV to your objects, creating the material if it doesn't exist.

- **Error Reporting:**  
  Clear popups and UI feedback for missing CSV data, incorrect names, or missing materials.

- **UI Integration:**  
  All CSV validation and correction tools are available in the **CSV2Mesh** tab in the 3D Viewport sidebar.

---


---

## How to Install

1. Download or clone this repo.
2. In Blender, go to **Edit > Preferences > Add-ons > Install**.
3. Pick the `.zip` or the folder with this add-on.
4. Enable **Aran's Game Tools** in the add-ons list.

---

## How to Use

Everything shows up in the **3D Viewport > Sidebar (N) > Game Tools** tab.

### Vertex Color ID Map

1. Select your mesh.
2. In the panel, click **Loose Parts to Vertex Colors**.
   - If you want vertex groups, check "Create Vertex Groups from Loose Parts" first.
3. To bake the colors to a texture, click **Bake Vertex Colors to Image**.

### Lightmap UVs

1. Select your mesh(es).
2. Check **AutoUnwrap Lightmap UVs** in the panel.
3. Click **Create Lightmap UVs**.

### Naming & Export

- Set your prefixes, suffixes, and export paths as needed.

---

## Requirements

- Blender 3.0 or newer (tested on Blender 4.3)
- Cycles render engine (for baking vertex colors to a texture)

---

## Known Issues

- **Slow on Big Meshes:** If your mesh has a ton of loose parts or vertices, the loose parts tool can take a while.
- **Vertex Color Layers:** Running the loose parts tool more than once will keep making new "LooseParts" layers.
- **Bake Node Setup:** The bake operator messes with your material nodes—if you have a fancy node setup, it might get changed.
- **Limited Colors:** If you have more loose parts than colors in the palette, colors will repeat.
- **Undo:** Some things (like UV creation) might not undo perfectly.

---

## Plans for the Future

- Make loose part detection faster for big meshes.
- Let you pick your own color palette.
- Batch export tools for lots of assets at once.
- More robust error messages and checks.
- Support for baking other maps (AO, normals, etc).
- Nicer UI and more in-panel help.

---

## Contributing

If you find a bug, have an idea, or want to help out, open an issue or a pull request!

---

## License

MIT License

---

**Author:** Aran Ahmed  
**Category:** Game Development  
