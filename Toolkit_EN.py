bl_info = {
    "name": "Workflow Toolkit",
    "author": "Hiro Hiro Senpai",
    "version": (1, 2, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar (N) > Toolkit",
    "description": "Everyday cleanup, geometry and organization tools in one sidebar panel",
    "doc_url": "https://github.com/hirosenpai3d/Workflow-Toolkit",
    "category": "3D View",
}

import bpy
import bmesh
from bpy.props import FloatProperty, StringProperty

# Every operator supports Ctrl+Z. Anything that deletes asks first.


# ------------------------------------------------------------------ helpers
def _T(text):
    return bpy.app.translations.pgettext_iface(text)


def selected_meshes(context):
    """Selected mesh objects, one per mesh data block (linked duplicates are done once)."""
    seen, out = set(), []
    for ob in context.selected_objects:
        if ob.type == 'MESH' and ob.data not in seen and ob.data.library is None:
            seen.add(ob.data)
            out.append(ob)
    return out


def edit_bmesh(ob, fn):
    """Run fn(bm) on the object's mesh in Object or Edit Mode and write it back."""
    me = ob.data
    if ob.mode == 'EDIT':
        bm = bmesh.from_edit_mesh(me)
        fn(bm)
        bmesh.update_edit_mesh(me)
    else:
        bm = bmesh.new()
        bm.from_mesh(me)
        fn(bm)
        bm.to_mesh(me)
        bm.free()
        me.update()


def need_selection(self, context, meshes=False):
    obs = selected_meshes(context) if meshes else context.selected_objects
    if not obs:
        self.report({'WARNING'}, _T("Select some meshes first") if meshes else _T("Select some objects first"))
    return obs


class _Confirm:
    """Mixin: ask before running. Subclasses set confirm_title / confirm_message."""
    confirm_title = ""
    confirm_message = ""

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(
            self, event, title=_T(self.confirm_title), message=self.message(context),
            confirm_text=_T("Continue"), icon='WARNING')

    def message(self, context):
        return _T(self.confirm_message)


# ------------------------------------------------------------------ modifiers & geometry
class UWT_OT_ApplyModifiers(bpy.types.Operator):
    bl_idname = "uwt.apply_modifiers"
    bl_label = "Apply Modifiers"
    bl_description = "Apply every modifier on the selected objects, top to bottom"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        obs = need_selection(self, context)
        done = failed = 0
        for ob in obs:
            if not hasattr(ob, "modifiers"):
                continue
            for name in [m.name for m in ob.modifiers]:
                try:
                    with context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
                        bpy.ops.object.modifier_apply(modifier=name)
                    done += 1
                except RuntimeError:
                    failed += 1
        msg = _T("%d modifiers applied") % done
        if failed:
            msg += " · " + _T("%d could not be applied (disabled or shared mesh)") % failed
        self.report({'WARNING'} if failed else {'INFO'}, msg)
        return {'FINISHED'}


class UWT_OT_RemoveModifiers(_Confirm, bpy.types.Operator):
    bl_idname = "uwt.remove_modifiers"
    bl_label = "Remove Modifiers and Constraints"
    bl_description = "Remove every modifier and constraint from the selected objects (asks first)"
    bl_options = {'REGISTER', 'UNDO'}
    confirm_title = "Remove modifiers and constraints?"
    confirm_message = "They are removed from the selected objects. Ctrl+Z brings them back"

    def execute(self, context):
        n = 0
        for ob in need_selection(self, context):
            if hasattr(ob, "modifiers"):
                n += len(ob.modifiers)
                ob.modifiers.clear()
            n += len(ob.constraints)
            ob.constraints.clear()
        self.report({'INFO'}, _T("%d removed") % n)
        return {'FINISHED'}


class UWT_OT_Triangulate(bpy.types.Operator):
    bl_idname = "uwt.triangulate_mesh"
    bl_label = "Triangulate"
    bl_description = "Turn every face of the selected meshes into triangles"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for ob in need_selection(self, context, meshes=True):
            edit_bmesh(ob, lambda bm: bmesh.ops.triangulate(bm, faces=bm.faces[:]))
        return {'FINISHED'}


class UWT_OT_ConvertToQuads(bpy.types.Operator):
    bl_idname = "uwt.convert_to_quads"
    bl_label = "Tris to Quads"
    bl_description = "Join triangles into quads where the shape allows it"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        def fn(bm):
            bmesh.ops.join_triangles(bm, faces=bm.faces[:], angle_face_threshold=0.698,
                                     angle_shape_threshold=0.698)
        for ob in need_selection(self, context, meshes=True):
            edit_bmesh(ob, fn)
        return {'FINISHED'}


class UWT_OT_MergeByDistance(bpy.types.Operator):
    bl_idname = "uwt.merge_by_distance"
    bl_label = "Merge by Distance"
    bl_description = "Weld vertices that sit on top of each other"
    bl_options = {'REGISTER', 'UNDO'}

    distance: FloatProperty(name="Distance", description="Vertices closer than this are welded",
                            default=0.0001, min=0.0, soft_max=0.1, precision=5, unit='LENGTH')

    def execute(self, context):
        total = 0
        for ob in need_selection(self, context, meshes=True):
            before = len(ob.data.vertices)
            edit_bmesh(ob, lambda bm: bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=self.distance))
            if ob.mode != 'EDIT':
                total += before - len(ob.data.vertices)
        self.report({'INFO'}, _T("%d vertices removed") % total)
        return {'FINISHED'}


class UWT_OT_RecalculateNormals(bpy.types.Operator):
    bl_idname = "uwt.recalculate_normals"
    bl_label = "Recalculate Normals"
    bl_description = "Point every face outside. Fixes dark or odd shading"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for ob in need_selection(self, context, meshes=True):
            edit_bmesh(ob, lambda bm: bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]))
        return {'FINISHED'}


class UWT_OT_OriginToGeometry(bpy.types.Operator):
    bl_idname = "uwt.origin_to_geometry"
    bl_label = "Origin to Geometry"
    bl_description = "Move the origin of the selected objects to the center of their geometry"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        if need_selection(self, context):
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        return {'FINISHED'}


class UWT_OT_AlignZAxis(bpy.types.Operator):
    bl_idname = "uwt.align_z_axis"
    bl_label = "Drop to Floor"
    bl_description = "Move the selected objects up or down so their lowest point rests on Z = 0"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        from mathutils import Vector
        dg = context.evaluated_depsgraph_get()
        for ob in need_selection(self, context):
            ev = ob.evaluated_get(dg)
            low = min((ev.matrix_world @ Vector(c)).z for c in ev.bound_box) if ob.type in {
                'MESH', 'CURVE', 'SURFACE', 'FONT', 'META', 'CURVES', 'POINTCLOUD', 'VOLUME'} else ob.matrix_world.translation.z
            m = ob.matrix_world.copy()
            m.translation.z -= low
            ob.matrix_world = m
        return {'FINISHED'}


# ------------------------------------------------------------------ cleanup
class UWT_OT_RemoveUnusedMaterials(bpy.types.Operator):
    bl_idname = "uwt.remove_unused_materials"
    bl_label = "Remove Unused Materials"
    bl_description = "Delete materials nothing uses. Materials with a fake user (shield icon) are kept"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        dead = [m for m in bpy.data.materials if m.users == 0 and not m.library]
        for m in dead:
            bpy.data.materials.remove(m)
        self.report({'INFO'}, _T("%d materials removed") % len(dead))
        return {'FINISHED'}


def _hidden_or_empty(scene):
    return [ob for ob in scene.objects
            if ob.hide_get() or ob.hide_viewport
            or (ob.type == 'MESH' and len(ob.data.vertices) == 0)]


class UWT_OT_RemoveHiddenEmpty(_Confirm, bpy.types.Operator):
    bl_idname = "uwt.remove_hidden_or_empty"
    bl_label = "Remove Hidden / Empty"
    bl_description = "Delete hidden objects and meshes with no geometry in this scene (asks first)"
    bl_options = {'REGISTER', 'UNDO'}
    confirm_title = "Remove hidden and empty objects?"

    def message(self, context):
        n = len(_hidden_or_empty(context.scene))
        return _T("%d objects in this scene will be deleted. Ctrl+Z brings them back") % n

    def execute(self, context):
        obs = _hidden_or_empty(context.scene)
        for ob in obs:
            bpy.data.objects.remove(ob)
        self.report({'INFO'}, _T("%d objects removed") % len(obs))
        return {'FINISHED'}


class UWT_OT_ClearScene(_Confirm, bpy.types.Operator):
    bl_idname = "uwt.clear_scene"
    bl_label = "Clear Scene"
    bl_description = "Delete every object in this scene (asks first)"
    bl_options = {'REGISTER', 'UNDO'}
    confirm_title = "Delete every object in this scene?"

    def message(self, context):
        return _T("%d objects will be deleted. Ctrl+Z brings them back") % len(context.scene.objects)

    def execute(self, context):
        obs = list(context.scene.objects)
        for ob in obs:
            bpy.data.objects.remove(ob)
        self.report({'INFO'}, _T("%d objects removed") % len(obs))
        return {'FINISHED'}


class UWT_OT_ClearCache(_Confirm, bpy.types.Operator):
    bl_idname = "uwt.clear_cache"
    bl_label = "Purge Unused Data"
    bl_description = "Delete data blocks nothing uses (meshes, materials, images...) to make the file lighter (asks first)"
    bl_options = {'REGISTER', 'UNDO'}
    confirm_title = "Purge unused data?"
    confirm_message = "Meshes, materials, images and other data that nothing uses are deleted. Items with a fake user are kept"

    def execute(self, context):
        before = sum(len(c) for c in (bpy.data.meshes, bpy.data.materials, bpy.data.images,
                                      bpy.data.textures, bpy.data.node_groups, bpy.data.curves))
        bpy.data.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        after = sum(len(c) for c in (bpy.data.meshes, bpy.data.materials, bpy.data.images,
                                     bpy.data.textures, bpy.data.node_groups, bpy.data.curves))
        self.report({'INFO'}, _T("%d data blocks removed") % (before - after))
        return {'FINISHED'}


class UWT_OT_OptimizeViewport(bpy.types.Operator):
    bl_idname = "uwt.optimize_viewport"
    bl_label = "Light Viewport"
    bl_description = "Turn Simplify on (subdivision at most 1) for smoother navigation. Press again to turn it off. Nothing is changed in your objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        r = context.scene.render
        if r.use_simplify:
            r.use_simplify = False
            self.report({'INFO'}, _T("Light Viewport off"))
        else:
            r.use_simplify = True
            r.simplify_subdivision = min(r.simplify_subdivision, 1)
            self.report({'INFO'}, _T("Light Viewport on"))
        return {'FINISHED'}


# ------------------------------------------------------------------ organization
TYPE_PREFIX = {'MESH': "MESH_", 'CAMERA': "CAM_", 'LIGHT': "LGT_", 'CURVE': "CRV_", 'EMPTY': "EMP_",
               'ARMATURE': "RIG_", 'FONT': "TXT_", 'GREASEPENCIL': "GP_", 'LATTICE': "LAT_"}

TYPE_COLLECTION = {'MESH': "Meshes", 'CAMERA': "Cameras", 'LIGHT': "Lights", 'CURVE': "Curves",
                   'EMPTY': "Empties", 'ARMATURE': "Rigs", 'FONT': "Texts", 'GREASEPENCIL': "Grease Pencil"}


class UWT_OT_RenameSequential(bpy.types.Operator):
    bl_idname = "uwt.rename_sequential"
    bl_label = "Sequential Rename"
    bl_description = "Rename the selected objects Name_001, Name_002... in the order they sit in the scene"
    bl_options = {'REGISTER', 'UNDO'}

    base: StringProperty(name="Name", description="Base name for the selected objects", default="Object")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        obs = sorted(need_selection(self, context), key=lambda o: o.name)
        for ob in obs:                       # free the target names first
            ob.name = "_uwt_tmp_" + ob.name
        for i, ob in enumerate(obs, 1):
            ob.name = "%s_%03d" % (self.base.strip() or "Object", i)
        return {'FINISHED'}


class UWT_OT_RenameWithPrefix(bpy.types.Operator):
    bl_idname = "uwt.rename_with_prefix"
    bl_label = "Prefix by Type"
    bl_description = "Add a type prefix (MESH_, CAM_, LGT_...) to the selected objects. Names that already have it are skipped"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        n = 0
        for ob in need_selection(self, context):
            p = TYPE_PREFIX.get(ob.type)
            if p and not ob.name.startswith(p):
                ob.name = p + ob.name
                n += 1
        self.report({'INFO'}, _T("%d renamed") % n)
        return {'FINISHED'}


def _move_to(ob, col):
    if col not in ob.users_collection:
        col.objects.link(ob)
    for c in list(ob.users_collection):
        if c != col:
            c.objects.unlink(ob)


class UWT_OT_GroupSelectedCollection(bpy.types.Operator):
    bl_idname = "uwt.group_selected_collection"
    bl_label = "Group into New Collection"
    bl_description = "Move the selected objects into a new collection"
    bl_options = {'REGISTER', 'UNDO'}

    col_name: StringProperty(name="Name", description="Name of the new collection", default="New Collection")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        obs = need_selection(self, context)
        if not obs:
            return {'CANCELLED'}
        col = bpy.data.collections.new(self.col_name.strip() or "New Collection")
        context.scene.collection.children.link(col)
        for ob in obs:
            _move_to(ob, col)
        return {'FINISHED'}


class UWT_OT_GroupByType(bpy.types.Operator):
    bl_idname = "uwt.group_by_type"
    bl_label = "Group by Type"
    bl_description = "Sort the objects of this scene into collections by type (Meshes, Cameras, Lights...)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        sc = context.scene
        made = {}
        for ob in list(sc.objects):
            name = TYPE_COLLECTION.get(ob.type)
            if not name or ob.parent:          # children stay with their parent
                continue
            col = made.get(name)
            if col is None:
                col = next((c for c in sc.collection.children if c.name == name), None)
                if col is None:
                    col = bpy.data.collections.new(name)
                    sc.collection.children.link(col)
                made[name] = col
            _move_to(ob, col)
        return {'FINISHED'}


# ------------------------------------------------------------------ panels
class UWT_PT_MainPanel(bpy.types.Panel):
    bl_label = "Workflow Toolkit"
    bl_idname = "UWT_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Toolkit"

    def draw(self, context):
        n = len(context.selected_objects)
        self.layout.label(text=(_T("%d selected") % n) if n else _T("Nothing selected"), icon='RESTRICT_SELECT_OFF')


class _Sub:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Toolkit"
    bl_parent_id = "UWT_PT_main_panel"


class UWT_PT_Geometry(_Sub, bpy.types.Panel):
    bl_label = "Modifiers and Geometry"
    bl_idname = "UWT_PT_geometry"

    def draw_header(self, context):
        self.layout.label(icon='MODIFIER')

    def draw(self, context):
        col = self.layout.column(align=True)
        col.operator("uwt.apply_modifiers", icon='CHECKMARK')
        col.operator("uwt.remove_modifiers", icon='X')
        col.separator()
        row = col.row(align=True)
        row.operator("uwt.triangulate_mesh", icon='MOD_TRIANGULATE')
        row.operator("uwt.convert_to_quads", icon='MESH_PLANE')
        col.operator("uwt.merge_by_distance", icon='AUTOMERGE_ON')
        col.operator("uwt.recalculate_normals", icon='NORMALS_FACE')
        col.separator()
        col.operator("uwt.origin_to_geometry", icon='OBJECT_ORIGIN')
        col.operator("uwt.align_z_axis", icon='TRIA_DOWN_BAR')


class UWT_PT_Cleanup(_Sub, bpy.types.Panel):
    bl_label = "Cleanup and Optimization"
    bl_idname = "UWT_PT_cleanup"

    def draw_header(self, context):
        self.layout.label(icon='BRUSH_DATA')

    def draw(self, context):
        col = self.layout.column(align=True)
        col.operator("uwt.remove_unused_materials", icon='MATERIAL')
        col.operator("uwt.remove_hidden_or_empty", icon='HIDE_ON')
        col.operator("uwt.clear_cache", icon='ORPHAN_DATA')
        col.separator()
        col.operator("uwt.optimize_viewport", icon='VIEW_PERSPECTIVE',
                     depress=context.scene.render.use_simplify)
        col.separator()
        col.alert = True
        col.operator("uwt.clear_scene", icon='TRASH')


class UWT_PT_Organize(_Sub, bpy.types.Panel):
    bl_label = "Organization and Renaming"
    bl_idname = "UWT_PT_organize"

    def draw_header(self, context):
        self.layout.label(icon='OUTLINER')

    def draw(self, context):
        col = self.layout.column(align=True)
        col.operator("uwt.rename_sequential", icon='SORTALPHA')
        col.operator("uwt.rename_with_prefix", icon='SYNTAX_OFF')
        col.separator()
        col.operator("uwt.group_selected_collection", icon='COLLECTION_NEW')
        col.operator("uwt.group_by_type", icon='OUTLINER_COLLECTION')


# ------------------------------------------------------------------ Spanish
_ES = {
    "Workflow Toolkit": "Workflow Toolkit",
    "Modifiers and Geometry": "Modificadores y Geometría",
    "Cleanup and Optimization": "Limpieza y Optimización",
    "Organization and Renaming": "Organización y Nombres",
    "Apply Modifiers": "Aplicar Modificadores",
    "Apply every modifier on the selected objects, top to bottom": "Aplica todos los modificadores de los objetos seleccionados, de arriba hacia abajo",
    "Remove Modifiers and Constraints": "Quitar Modificadores y Restricciones",
    "Remove every modifier and constraint from the selected objects (asks first)": "Quita todos los modificadores y restricciones de los objetos seleccionados (pregunta antes)",
    "Remove modifiers and constraints?": "¿Quitar modificadores y restricciones?",
    "They are removed from the selected objects. Ctrl+Z brings them back": "Se quitan de los objetos seleccionados. Ctrl+Z los recupera",
    "Triangulate": "Triangular",
    "Turn every face of the selected meshes into triangles": "Convierte todas las caras de las mallas seleccionadas en triángulos",
    "Tris to Quads": "Tris a Quads",
    "Join triangles into quads where the shape allows it": "Une triángulos en quads donde la forma lo permite",
    "Merge by Distance": "Fusionar por Distancia",
    "Weld vertices that sit on top of each other": "Suelda los vértices que están uno encima del otro",
    "Distance": "Distancia",
    "Vertices closer than this are welded": "Se sueldan los vértices más cercanos que esto",
    "Recalculate Normals": "Recalcular Normales",
    "Point every face outside. Fixes dark or odd shading": "Apunta todas las caras hacia afuera. Arregla sombreado oscuro o raro",
    "Origin to Geometry": "Origen a Geometría",
    "Move the origin of the selected objects to the center of their geometry": "Lleva el origen de los objetos seleccionados al centro de su geometría",
    "Drop to Floor": "Apoyar en el Piso",
    "Move the selected objects up or down so their lowest point rests on Z = 0": "Sube o baja los objetos seleccionados para que su punto más bajo quede en Z = 0",
    "Remove Unused Materials": "Quitar Materiales sin Uso",
    "Delete materials nothing uses. Materials with a fake user (shield icon) are kept": "Borra los materiales que nada usa. Se conservan los que tienen usuario falso (ícono de escudo)",
    "Remove Hidden / Empty": "Quitar Ocultos / Vacíos",
    "Delete hidden objects and meshes with no geometry in this scene (asks first)": "Borra los objetos ocultos y las mallas sin geometría de esta escena (pregunta antes)",
    "Remove hidden and empty objects?": "¿Quitar objetos ocultos y vacíos?",
    "%d objects in this scene will be deleted. Ctrl+Z brings them back": "Se borrarán %d objetos de esta escena. Ctrl+Z los recupera",
    "Clear Scene": "Vaciar Escena",
    "Delete every object in this scene (asks first)": "Borra todos los objetos de esta escena (pregunta antes)",
    "Delete every object in this scene?": "¿Borrar todos los objetos de esta escena?",
    "%d objects will be deleted. Ctrl+Z brings them back": "Se borrarán %d objetos. Ctrl+Z los recupera",
    "Purge Unused Data": "Purgar Datos sin Uso",
    "Delete data blocks nothing uses (meshes, materials, images...) to make the file lighter (asks first)": "Borra los datos que nada usa (mallas, materiales, imágenes...) para aligerar el archivo (pregunta antes)",
    "Purge unused data?": "¿Purgar datos sin uso?",
    "Meshes, materials, images and other data that nothing uses are deleted. Items with a fake user are kept": "Se borran mallas, materiales, imágenes y otros datos que nada usa. Se conservan los que tienen usuario falso",
    "Light Viewport": "Viewport Liviano",
    "Turn Simplify on (subdivision at most 1) for smoother navigation. Press again to turn it off. Nothing is changed in your objects": "Activa Simplificar (subdivisión máxima 1) para navegar más fluido. Púlsalo otra vez para apagarlo. No cambia nada en tus objetos",
    "Light Viewport on": "Viewport Liviano activado",
    "Light Viewport off": "Viewport Liviano desactivado",
    "Sequential Rename": "Renombrar en Serie",
    "Rename the selected objects Name_001, Name_002... in the order they sit in the scene": "Renombra los objetos seleccionados Nombre_001, Nombre_002... en orden",
    "Name": "Nombre",
    "Base name for the selected objects": "Nombre base para los objetos seleccionados",
    "Prefix by Type": "Prefijo por Tipo",
    "Add a type prefix (MESH_, CAM_, LGT_...) to the selected objects. Names that already have it are skipped": "Agrega un prefijo por tipo (MESH_, CAM_, LGT_...) a los objetos seleccionados. Los que ya lo tienen se saltean",
    "Group into New Collection": "Agrupar en Colección Nueva",
    "Move the selected objects into a new collection": "Mueve los objetos seleccionados a una colección nueva",
    "Name of the new collection": "Nombre de la colección nueva",
    "Group by Type": "Agrupar por Tipo",
    "Sort the objects of this scene into collections by type (Meshes, Cameras, Lights...)": "Ordena los objetos de esta escena en colecciones por tipo (Mallas, Cámaras, Luces...)",
    "Continue": "Continuar",
    "Select some meshes first": "Selecciona alguna malla primero",
    "Select some objects first": "Selecciona algún objeto primero",
    "%d modifiers applied": "%d modificadores aplicados",
    "%d could not be applied (disabled or shared mesh)": "%d no se pudieron aplicar (desactivados o malla compartida)",
    "%d removed": "%d quitados",
    "%d vertices removed": "%d vértices quitados",
    "%d materials removed": "%d materiales quitados",
    "%d objects removed": "%d objetos quitados",
    "%d data blocks removed": "%d datos quitados",
    "%d renamed": "%d renombrados",
    "%d selected": "%d seleccionados",
    "Nothing selected": "Nada seleccionado",
}


def _translations():
    d = {}
    for en, es in _ES.items():
        for ctx in ("*", "Operator"):
            d[(ctx, en)] = es
    return {"es": d, "es_ES": d}


# ------------------------------------------------------------------ register
classes = (
    UWT_OT_ApplyModifiers, UWT_OT_RemoveModifiers, UWT_OT_Triangulate, UWT_OT_ConvertToQuads,
    UWT_OT_MergeByDistance, UWT_OT_RecalculateNormals, UWT_OT_OriginToGeometry, UWT_OT_AlignZAxis,
    UWT_OT_RemoveUnusedMaterials, UWT_OT_RemoveHiddenEmpty, UWT_OT_ClearScene, UWT_OT_ClearCache,
    UWT_OT_OptimizeViewport, UWT_OT_RenameSequential, UWT_OT_RenameWithPrefix,
    UWT_OT_GroupSelectedCollection, UWT_OT_GroupByType,
    UWT_PT_MainPanel, UWT_PT_Geometry, UWT_PT_Cleanup, UWT_PT_Organize,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    try:
        bpy.app.translations.register(__name__, _translations())
    except ValueError:
        pass


def unregister():
    try:
        bpy.app.translations.unregister(__name__)
    except Exception:
        pass
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
