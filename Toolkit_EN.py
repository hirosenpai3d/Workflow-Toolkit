bl_info = {
    "name": "Workflow Toolkit",
    "author": "Hiro",
    "version": (1, 1, 0),
    "blender": (2, 80, 0),
    "location": "3D View > Sidebar > Toolkit",
    "description": "Professional addon to improve Blender workflow",
    "category": "3D View",
}

import bpy
import os
import shutil

# ------------------------ PANEL PRINCIPAL ------------------------

class UWT_PT_MainPanel(bpy.types.Panel):
    bl_label = "🧰 Workflow"
    bl_idname = "UWT_PT_main_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Toolkit"

    def draw(self, context):
        layout = self.layout

        layout.label(text="🔧 Modifiers and Geometry")
        layout.operator("uwt.apply_modifiers")
        layout.operator("uwt.remove_modifiers")
        layout.operator("uwt.triangulate_mesh")
        layout.operator("uwt.convert_to_quads")
        layout.operator("uwt.merge_by_distance")
        layout.operator("uwt.recalculate_normals")
        layout.operator("uwt.origin_to_geometry")
        layout.operator("uwt.align_z_axis")

        layout.separator()
        layout.label(text="🧼 Cleanup and Optimization")
        layout.operator("uwt.remove_unused_materials")
        layout.operator("uwt.remove_hidden_or_empty")
        layout.operator("uwt.clear_scene")
        layout.operator("uwt.clear_cache")
        layout.operator("uwt.optimize_viewport")

        layout.separator()
        layout.label(text="📦 Organization and Renaming")
        layout.operator("uwt.rename_sequential")
        layout.operator("uwt.rename_with_prefix")
        layout.operator("uwt.group_selected_collection")
        layout.operator("uwt.group_by_type")

# ------------------------ OPERADORES ------------------------

class UWT_OT_ApplyModifiers(bpy.types.Operator):
    bl_idname = "uwt.apply_modifiers"
    bl_label = "Apply Modifiers"
    bl_description = "Applies all modifiers of selected objects"
    def execute(self, context):
        for obj in context.selected_objects:
            for mod in obj.modifiers:
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.modifier_apply(modifier=mod.name)
        return {'FINISHED'}

class UWT_OT_RemoveModifiers(bpy.types.Operator):
    bl_idname = "uwt.remove_modifiers"
    bl_label = "Remove Modifiers and Constraints"
    bl_description = "Removes all modifiers and constraints from selected objects"
    def execute(self, context):
        for obj in context.selected_objects:
            obj.modifiers.clear()
            obj.constraints.clear()
        return {'FINISHED'}

class UWT_OT_Triangulate(bpy.types.Operator):
    bl_idname = "uwt.triangulate_mesh"
    bl_label = "Triangulate Mesh"
    bl_description = "Converts meshes to triangles"
    def execute(self, context):
        for obj in context.selected_objects:
            if obj.type == "MESH":
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.quads_convert_to_tris()
                bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}

class UWT_OT_ConvertToQuads(bpy.types.Operator):
    bl_idname = "uwt.convert_to_quads"
    bl_label = "Convert to Quads"
    bl_description = "Converts triangles to quads where possible"
    def execute(self, context):
        for obj in context.selected_objects:
            if obj.type == "MESH":
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.tris_convert_to_quads()
                bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}

class UWT_OT_MergeByDistance(bpy.types.Operator):
    bl_idname = "uwt.merge_by_distance"
    bl_label = "Merge by Distance"
    bl_description = "Removes duplicate vertices"
    def execute(self, context):
        for obj in context.selected_objects:
            if obj.type == "MESH":
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.remove_doubles()
                bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}
class UWT_OT_RecalculateNormals(bpy.types.Operator):
    bl_idname = "uwt.recalculate_normals"
    bl_label = "Recalculate Normals"
    bl_description = "Fixes odd shading by recalculating normals"
    def execute(self, context):
        for obj in context.selected_objects:
            if obj.type == "MESH":
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.normals_make_consistent(inside=False)
                bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}

class UWT_OT_OriginToGeometry(bpy.types.Operator):
    bl_idname = "uwt.origin_to_geometry"
    bl_label = "Origin to Geometry"
    bl_description = "Sets object origin to geometry center"
    def execute(self, context):
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        return {'FINISHED'}

class UWT_OT_AlignZAxis(bpy.types.Operator):
    bl_idname = "uwt.align_z_axis"
    bl_label = "Align to Z Axis"
    bl_description = "Places all selected objects on Z=0 axis"
    def execute(self, context):
        for obj in context.selected_objects:
            obj.location.z = 0
        return {'FINISHED'}

class UWT_OT_RemoveUnusedMaterials(bpy.types.Operator):
    bl_idname = "uwt.remove_unused_materials"
    bl_label = "Remove Unused Materials"
    bl_description = "Removes unused materials from the scene"
    def execute(self, context):
        for mat in bpy.data.materials:
            if not mat.users:
                bpy.data.materials.remove(mat)
        return {'FINISHED'}

class UWT_OT_RemoveHiddenEmpty(bpy.types.Operator):
    bl_idname = "uwt.remove_hidden_or_empty"
    bl_label = "Remove Hidden/Empty"
    bl_description = "Removes hidden or empty objects without geometry"
    def execute(self, context):
        for obj in bpy.data.objects:
            if obj.hide_viewport or (obj.type == 'MESH' and len(obj.data.vertices) == 0):
                bpy.data.objects.remove(obj)
        return {'FINISHED'}

class UWT_OT_ClearScene(bpy.types.Operator):
    bl_idname = "uwt.clear_scene"
    bl_label = "Clear Scene"
    bl_description = "Deletes all objects in the scene"
    def execute(self, context):
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        return {'FINISHED'}

class UWT_OT_ClearCache(bpy.types.Operator):
    bl_idname = "uwt.clear_cache"
    bl_label = "Clear Cache"
    bl_description = "Cleans Blender's temporary folder"
    def execute(self, context):
        temp = bpy.app.tempdir
        if os.path.exists(temp):
            shutil.rmtree(temp)
        return {'FINISHED'}

class UWT_OT_OptimizeViewport(bpy.types.Operator):
    bl_idname = "uwt.optimize_viewport"
    bl_label = "Optimize Viewport"
    bl_description = "Reduces subdivision, shadows, and overlays for better performance"
    def execute(self, context):
        for obj in bpy.data.objects:
            for mod in obj.modifiers:
                if mod.type == 'SUBSURF':
                    mod.levels = 1
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.show_shadows = False
                        space.overlay.show_overlays = False
        return {'FINISHED'}
class UWT_OT_RenameSequential(bpy.types.Operator):
    bl_idname = "uwt.rename_sequential"
    bl_label = "Sequential Rename"
    bl_description = "Renames selected objects sequentially"
    def execute(self, context):
        for i, obj in enumerate(context.selected_objects, 1):
            obj.name = f"Object_{i:03}"
        return {'FINISHED'}

class UWT_OT_RenameWithPrefix(bpy.types.Operator):
    bl_idname = "uwt.rename_with_prefix"
    bl_label = "Prefix MESH_"
    bl_description = "Renames MESH type objects with prefix MESH_"
    def execute(self, context):
        count = 1
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                obj.name = f"MESH_{count:03}"
                count += 1
        return {'FINISHED'}

class UWT_OT_GroupSelectedCollection(bpy.types.Operator):
    bl_idname = "uwt.group_selected_collection"
    bl_label = "Group into New Collection"
    bl_description = "Groups selected objects into a new collection"
    def execute(self, context):
        col = bpy.data.collections.new("New_Collection")
        bpy.context.scene.collection.children.link(col)
        for obj in context.selected_objects:
            for c in obj.users_collection:
                c.objects.unlink(obj)
            col.objects.link(obj)
        return {'FINISHED'}

class UWT_OT_GroupByType(bpy.types.Operator):
    bl_idname = "uwt.group_by_type"
    bl_label = "Group by Type"
    bl_description = "Groups objects by type into collections"
    def execute(self, context):
        def move(obj, name):
            col = bpy.data.collections.get(name)
            if not col:
                col = bpy.data.collections.new(name)
                bpy.context.scene.collection.children.link(col)
            for c in obj.users_collection:
                c.objects.unlink(obj)
            col.objects.link(obj)
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                move(obj, "Meshes")
            elif obj.type == 'CAMERA':
                move(obj, "Cameras")
            elif obj.type == 'LIGHT':
                move(obj, "Lights")
        return {'FINISHED'}

# ------------------------ REGISTRO ------------------------

classes = [
    UWT_PT_MainPanel,
    UWT_OT_ApplyModifiers, UWT_OT_RemoveModifiers, UWT_OT_Triangulate, UWT_OT_ConvertToQuads,
    UWT_OT_MergeByDistance, UWT_OT_RecalculateNormals, UWT_OT_OriginToGeometry, UWT_OT_AlignZAxis,
    UWT_OT_RemoveUnusedMaterials, UWT_OT_RemoveHiddenEmpty, UWT_OT_ClearScene, UWT_OT_ClearCache,
    UWT_OT_OptimizeViewport, UWT_OT_RenameSequential, UWT_OT_RenameWithPrefix,
    UWT_OT_GroupSelectedCollection, UWT_OT_GroupByType,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
