================
WORKFLOW TOOLKIT
================

Everyday cleanup, geometry and organization tools for Blender in one sidebar panel. Tidy a scene in a few
clicks instead of digging through menus.

By Hiro Hiro Senpai · https://hirohirosenpai.gumroad.com · https://github.com/hirosenpai3d/Workflow-Toolkit

1. INSTALL
----------

1. Edit > Preferences > Add-ons > (v) > Install from Disk... and pick Toolkit_EN.py.
2. Tick Workflow Toolkit in the list.
3. In the 3D Viewport press N and open the Toolkit tab.

Made and tested for Blender 5.2 LTS (works from 4.2).
Updating from 1.1: install the new file over the old one (same name).

2. THE TOOLS
------------

Modifiers and Geometry (selected objects)
- Apply Modifiers: applies every modifier, top to bottom.
- Remove Modifiers and Constraints: strips them all. Asks first.
- Triangulate / Tris to Quads.
- Merge by Distance: welds duplicate vertices (you can change the distance).
- Recalculate Normals: fixes dark or odd shading.
- Origin to Geometry: centers the origin on the mesh.
- Drop to Floor: the lowest point of each object rests on Z = 0.

Cleanup and Optimization
- Remove Unused Materials (materials with a fake user are kept).
- Remove Hidden / Empty: hidden objects and meshes with no geometry in this scene. Asks first.
- Purge Unused Data: deletes data nothing uses to make the file lighter. Asks first.
- Light Viewport: turns Simplify on (subdivision at most 1). Press again to turn it off.
- Clear Scene: deletes every object in this scene. Asks first.

Organization and Renaming
- Sequential Rename: Name_001, Name_002... with the base name you type.
- Prefix by Type: MESH_, CAM_, LGT_... on the selected objects.
- Group into New Collection: moves the selection into a new collection you name.
- Group by Type: sorts the scene into Meshes, Cameras, Lights, Curves... collections.

Every tool works with Ctrl+Z, and every control has a tooltip.

3. LANGUAGE
-----------

English and Spanish: the interface follows Blender's language (Edit > Preferences > Interface > Translation).

4. WHAT'S NEW IN 1.2
--------------------

- Ctrl+Z works on every tool.
- Tools that delete ask first and say how many objects they will remove.
- Clear Cache is now Purge Unused Data (safe: it no longer deletes Blender's temporary folder).
- Optimize Viewport is now Light Viewport: uses Simplify and changes nothing in your objects.
- Align to Z Axis is now Drop to Floor (the object rests on the floor instead of moving its origin).
- Renaming and grouping act on the selection or the current scene only, never on the whole file.
- Geometry tools work in Object and Edit Mode. New panel with icons, tooltips and Spanish.

Free. Questions: https://hirohirosenpai.gumroad.com
