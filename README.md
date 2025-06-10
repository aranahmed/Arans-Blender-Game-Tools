# Aran's Game Tools for Blender

**Aran's Game Tools** is a Blender add-on designed to streamline the asset pipeline between Blender and Unreal Engine, with a strong focus on **CSV-driven asset management** and seamless Unreal Python integration. This toolkit is ideal for game developers and technical artists who want to automate repetitive tasks, enforce naming/material conventions, and ensure their assets are always Unreal-ready.

---
## Install

[![Watch the video](https://img.youtube.com/vi/josrG0BzsxI/maxresdefault.jpg)]([https://youtu.be/josrG0BzsxI])

## Overview Video 0.0.2

[![Watch the video](https://img.youtube.com/vi/WJ-lLqbd884&t=2s/maxresdefault.jpg)]([https://youtu.be/WJ-lLqbd884&t=2s])

## 🚀 Key Features

### CSV-Driven Asset Management

- **CSV-Based Validation:**  
  Import a CSV file containing your asset data (name, type, master material, etc). The add-on checks selected Blender objects against this data, ensuring consistency and correctness.

- **Custom Properties from CSV:**  
  Automatically assigns asset metadata (like `AssetName`, `AssetType`, `MasterMaterial`) as custom properties on your Blender objects, making your scene data-rich and ready for export.

- **Smart Renaming & Batch Correction:**  
  Instantly spot naming mismatches and batch-rename all assets to match your CSV conventions, including prefix/suffix rules.

- **Master Material Assignment:**  
  Assigns the correct master material from your CSV to each object, creating the material if it doesn't exist.

- **Error Reporting:**  
  Clear UI feedback for missing CSV data, incorrect names, or missing materials.

### Blender-to-Unreal Workflow

- **Loose Parts to Vertex Colors:**  
  Color each mesh island with a unique vertex color for easy ID map creation.

- **Bake Vertex Colors to Texture:**  
  Bake vertex colors to an image for export.

- **Vertex Groups from Loose Parts:**  
  Optionally create vertex groups for each loose part.

- **Lightmap UVs:**  
  One-click creation of a second UV channel for Unreal lightmaps.

- **Naming & Export Helpers:**  
  Set up prefixes, suffixes, and export paths for Unreal Engine assets.

### Unreal Python Integration

- **Automated Import:**  
  Use the provided Unreal Python scripts to batch-import assets, read the same CSV, and automatically assign master materials and correct naming inside Unreal.

- **Data Table Support:**  
  Import your CSV/JSON data directly into Unreal Engine DataTables for further automation and validation.

---

## 🎮 Use Cases in Game Development

- **Consistent Asset Naming:**  
  Enforce naming conventions across large teams and projects.

- **Automated Material Assignment:**  
  Guarantee every asset uses the correct master material, reducing manual errors.

- **Metadata-Driven Workflows:**  
  Store and transfer asset metadata from Blender to Unreal, enabling advanced pipelines (e.g., procedural spawning, gameplay tagging).

- **Batch Asset Validation:**  
  Quickly validate and correct hundreds of assets before export or import.

---

## 🛠️ How to Install

1. Download or clone this repo.
2. In Blender, go to `Edit > Preferences > Add-ons > Install`.
3. Select the `.zip` or the folder with this add-on.
4. Enable **Aran's Game Tools** in the add-ons list.

---

## 📝 How to Use

- All tools are available in the 3D Viewport > Sidebar (`N`) > **Game Tools** tab.
- Import your CSV in the **CSV2Mesh** panel.
- Use the validation, renaming, and material assignment tools as needed.
- Export your assets and use the Unreal Python scripts to automate import and setup in Unreal Engine.

---

## ⚡ Plans for Future Improvement

- **Faster loose part detection** for large meshes.
- **Custom color palettes** for vertex color ID maps.
- **Batch export tools** for large asset libraries.
- **More robust error messages** and validation.
- **Support for baking additional maps** (AO, normals, etc).
- **Enhanced UI** and in-panel help.
- **Deeper Unreal integration:**  
  - Automated DataTable population  
  - Blueprint and gameplay tag assignment  
  - Asset reimport/update workflows

---

## 🤝 Contributing

Found a bug? Have an idea? Want to help out?  
Open an issue or a pull request!

---

## 📄 License

MIT License

**Author:** Aran Ahmed  
**Category:** Game Development
