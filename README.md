# Workflow Toolkit

A free Blender add-on that gathers everyday cleanup, geometry and organization tasks into one sidebar panel,
so you can tidy a scene in a few clicks instead of digging through menus.

**Location:** 3D View → Sidebar (N) → **Toolkit** · **Version:** 1.2.0 · **Blender:** 5.2 LTS (works from 4.2)
**Author:** Hiro Hiro Senpai · [Gumroad](https://hirohirosenpai.gumroad.com)

## Features

### Modifiers and Geometry
- **Apply Modifiers** / **Remove Modifiers and Constraints** (asks first)
- **Triangulate** / **Tris to Quads**
- **Merge by Distance** with an adjustable distance
- **Recalculate Normals**, **Origin to Geometry**, **Drop to Floor**

### Cleanup and Optimization
- **Remove Unused Materials** (fake users are kept)
- **Remove Hidden / Empty** objects in the current scene (asks first)
- **Purge Unused Data** to make the file lighter (asks first)
- **Light Viewport**: Simplify on / off, nothing in your objects changes
- **Clear Scene** (asks first)

### Organization and Renaming
- **Sequential Rename** with your own base name, **Prefix by Type** (MESH_, CAM_, LGT_...)
- **Group into New Collection**, **Group by Type**

Every tool supports **Ctrl+Z**. Interface in English and Spanish.

## Installation

1. Download `Toolkit_EN.py` (or the zip from the Releases / Gumroad page).
2. In Blender: **Edit → Preferences → Add-ons → ∨ → Install from Disk…**
3. Select the file and enable **Workflow Toolkit**.

## Files

```
Toolkit_EN.py          the add-on
docs/                  README_EN.txt, README_ES.txt
WorkflowToolkit_<ver>.zip, gumroad_form.txt
store/                 cover, thumbnail and demo video
```
