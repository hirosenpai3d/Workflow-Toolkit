================
WORKFLOW TOOLKIT
================

Herramientas de limpieza, geometría y organización para Blender en un solo panel. Ordená una escena en
pocos clics en vez de buscar en los menús.

Por Hiro Hiro Senpai · https://hirohirosenpai.gumroad.com · https://github.com/hirosenpai3d/Workflow-Toolkit

1. INSTALACIÓN
--------------

1. Editar > Preferencias > Complementos > (v) > Instalar desde disco... y elegí Toolkit_EN.py.
2. Activá Workflow Toolkit en la lista.
3. En el Viewport 3D pulsá N y abrí la pestaña Toolkit.

Hecho y probado para Blender 5.2 LTS (funciona desde 4.2).
Si tenías la 1.1: instalá el archivo nuevo encima del viejo (mismo nombre).

2. LAS HERRAMIENTAS
-------------------

Modificadores y Geometría (objetos seleccionados)
- Aplicar Modificadores: aplica todos, de arriba hacia abajo.
- Quitar Modificadores y Restricciones: los saca todos. Pregunta antes.
- Triangular / Tris a Quads.
- Fusionar por Distancia: suelda vértices duplicados (podés cambiar la distancia).
- Recalcular Normales: arregla sombreado oscuro o raro.
- Origen a Geometría: centra el origen en la malla.
- Apoyar en el Piso: el punto más bajo de cada objeto queda en Z = 0.

Limpieza y Optimización
- Quitar Materiales sin Uso (se conservan los que tienen usuario falso).
- Quitar Ocultos / Vacíos: objetos ocultos y mallas sin geometría de esta escena. Pregunta antes.
- Purgar Datos sin Uso: borra datos que nada usa para aligerar el archivo. Pregunta antes.
- Viewport Liviano: activa Simplificar (subdivisión máxima 1). Pulsalo otra vez para apagarlo.
- Vaciar Escena: borra todos los objetos de esta escena. Pregunta antes.

Organización y Nombres
- Renombrar en Serie: Nombre_001, Nombre_002... con el nombre base que escribas.
- Prefijo por Tipo: MESH_, CAM_, LGT_... en los objetos seleccionados.
- Agrupar en Colección Nueva: mueve la selección a una colección nueva con el nombre que elijas.
- Agrupar por Tipo: ordena la escena en colecciones Mallas, Cámaras, Luces, Curvas...

Todo se puede deshacer con Ctrl+Z, y todos los controles tienen descripción.

3. IDIOMA
---------

Inglés y español: la interfaz sigue el idioma de Blender (Editar > Preferencias > Interfaz > Traducción).

4. NOVEDADES DE LA 1.2
----------------------

- Ctrl+Z funciona en todas las herramientas.
- Las herramientas que borran preguntan antes y dicen cuántos objetos van a quitar.
- Limpiar Caché ahora es Purgar Datos sin Uso (seguro: ya no borra la carpeta temporal de Blender).
- Optimizar Viewport ahora es Viewport Liviano: usa Simplificar y no cambia nada de tus objetos.
- Alinear al Eje Z ahora es Apoyar en el Piso (el objeto se apoya en el piso en vez de mover su origen).
- Renombrar y agrupar actúan solo sobre la selección o la escena actual, nunca sobre todo el archivo.
- Las herramientas de geometría funcionan en Modo Objeto y Modo Edición. Panel nuevo con íconos,
  descripciones y español.

Gratis. Consultas: https://hirohirosenpai.gumroad.com
