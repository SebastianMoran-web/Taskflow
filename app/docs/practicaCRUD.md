# Práctica 1.6 — CRUD completo

## Decisión sobre el borrado

### Projects → CASCADA
Una tarea siempre pertenece a un proyecto (`project_id` NOT NULL). Si el proyecto
desaparece, sus tareas pierden el contexto y quedarían huérfanas, así que se borran con él.
Implementado en dos niveles:
- BD: `ForeignKey("projects.id", ondelete="CASCADE")`
- ORM: `relationship(..., cascade="all, delete-orphan", passive_deletes=True)`
- En SQLite se activa `PRAGMA foreign_keys=ON` en `database.py`.

### Categories → BLOQUEO (409 Conflict)
La categoría es solo una etiqueta; borrarla no debe destruir trabajo del usuario.
Si tiene tareas, `DELETE` responde `409` con el número de tareas afectadas.
- BD: `ForeignKey("categories.id", ondelete="RESTRICT")` como red de seguridad.
- API: comprobación previa con mensaje claro.

## Errores
| Código | Cuándo |
|---|---|
| 404 | Tarea, proyecto o categoría no existe (también `project_id`/`category_id` inexistentes al crear/editar tarea) |
| 409 | Categoría con tareas al borrar, o nombre de categoría duplicado |
| 422 | Validación de datos / parámetros (`skip<0`, `limit>100`...) |
