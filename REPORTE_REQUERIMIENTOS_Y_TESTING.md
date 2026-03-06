# Reporte de requerimientos y testing - product_sample_management

Fecha: 2026-03-06
Proyecto: `PruebaTecnicaOdoo`
Modulo: `product_sample_management`
Documento fuente: `prueba_tecnica_odoo16 (1).docx.pdf`

## 1. Resumen ejecutivo

Se ejecuto una prueba integral de la app con 2 bloques:

1. Test funcional E2E por JSON-RPC (`test_module.py`): 52/52 pruebas OK.
2. Validacion adicional de cumplimiento estricto del enunciado (`extra_validation.py`): detecta 3 brechas frente al documento.

Conclusiones:

- El modulo esta funcional en flujo principal y vistas base.
- Existen requerimientos del enunciado que no estan cerrados al 100%.

## 2. Evidencia de pruebas ejecutadas

Comandos ejecutados:

```powershell
C:/Users/renzo/AppData/Local/Microsoft/WindowsApps/python3.13.exe test_module.py
C:/Users/renzo/AppData/Local/Microsoft/WindowsApps/python3.13.exe extra_validation.py
```

Resultado principal:

- `test_module.py`: `52/52 TODOS LOS TESTS PASARON`.

Resultado validacion extra:

- Statusbar visible actual: `draft,confirmed,sent,received`
- Estados faltantes en statusbar: `rejected`, `cancelled`
- Usuario interno sin grupo manager puede confirmar: `False` en "Confirmar bloqueado" (es decir, SI puede confirmar)
- Usuario no admin puede cancelar una solicitud confirmada: `False` en "Cancelar confirmed bloqueado" (es decir, SI puede cancelar)

## 3. Checklist completo de requerimientos del documento

### 3.1 Contexto y objetivo

- [x] Modulo en Odoo 16 para gestion de solicitudes de muestras.
- [x] Estructura y enfoque alineados a practicas Odoo.

### 3.2 Modelo de datos

Modelo `product.sample.request`:

- [x] `name` (Char, auto secuencia) implementado.
- [x] `partner_id` (Many2one) implementado.
- [x] `product_id` (Many2one) implementado.
- [x] `quantity` (Float) implementado.
- [x] `request_date` (Date, default hoy) implementado.
- [x] `user_id` (Many2one) implementado.
- [x] `notes` (Text) implementado.
- [x] `state` (Selection) implementado.
- [x] `total_requests` (Integer compute) implementado.

Extension `res.partner`:

- [x] `sample_request_ids` (One2many) implementado.
- [x] `sample_count` (Integer compute) implementado.
- [x] Stat button en ficha de cliente implementado.

### 3.3 Flujo de estados

- [x] `draft -> confirmed` (boton confirmar) implementado.
- [x] `confirmed -> sent` (boton enviar) implementado.
- [x] `sent -> received` implementado.
- [x] `sent -> rejected` por wizard implementado.
- [x] `confirmed -> draft` (volver a borrador) implementado.
- [x] `draft/confirmed -> cancelled` implementado.
- [x] Estados finales en readonly a nivel vista implementado.
- [ ] Statusbar visible con TODOS los estados (faltan `rejected`, `cancelled`).

### 3.4 Vistas requeridas

- [x] Form view con campos, botones contextuales y chatter.
- [x] Tree view con columnas solicitadas.
- [x] Decoraciones en tree por estado (`success`, `danger`, `muted`).
- [x] Kanban view con agrupacion por estado y campos clave.
- [x] Search view con filtros predefinidos.
- [x] Group by predefinidos (cliente, estado, comercial).

### 3.5 Logica de negocio

- [x] Secuencia generada al confirmar (no al crear).
- [x] En borrador se muestra `Nuevo`.
- [x] Validacion: no confirmar cantidad <= 0.
- [x] Rechazo via wizard guarda motivo en `notes`.
- [x] `total_requests` calcula total por cliente.
- [x] Advertencia de stock en envio sin bloqueo (implementada con `display_notification`).

Nota de validacion:

- [~] El enunciado indica actualizar correctamente al crear/cancelar; el compute actual cuenta todos los estados y en pruebas de integracion responde correctamente, pero no hay test unitario dedicado a recomputacion por transicion especifica.

### 3.6 Seguridad y acceso

- [x] Grupo `Responsable de Muestras` existe.
- [x] ACL base para usuarios internos y managers existe en `ir.model.access.csv`.
- [ ] Solo grupo `Responsable de Muestras` puede confirmar/enviar/rechazar (en backend no se bloquea; solo se limita por botones en vista).
- [ ] Solo managers/admin pueden cancelar solicitudes ya confirmadas (no se bloquea en backend; usuario no admin puede cancelar por RPC).

### 3.7 Menu y navegacion

- [x] Menu raiz `Muestras` fuera de Ventas/Inventario.
- [x] Submenu `Solicitudes de muestra` implementado.
- [x] Stat button abre solicitudes filtradas por cliente.
- [x] Menu `Configuracion` no requerido al no haber parametros configurables.

### 3.8 Estructura esperada del modulo

- [x] `__manifest__.py` presente.
- [x] `models/sample_request.py` presente.
- [x] `models/res_partner.py` presente.
- [x] `views/sample_request_views.xml` presente.
- [x] `views/res_partner_views.xml` presente.
- [x] `views/menus.xml` presente.
- [x] `wizard/reject_wizard.py` presente.
- [x] `security/ir.model.access.csv` presente.
- [x] `data/sequences.xml` presente.

### 3.9 Criterios de evaluacion (lectura tecnica)

- [x] Estructura y manifest: correcto.
- [x] Modelo de datos completo.
- [x] Flujo funcional base.
- [x] Vistas requeridas implementadas.
- [x] Herencia de partner y contador implementados.
- [~] Seguridad parcialmente cumplida (falta enforcement backend de permisos por accion).
- [x] Wizard de rechazo y validaciones base implementadas.

## 4. Hallazgos principales

1. Requerimiento no cumplido: statusbar no muestra todos los estados.
2. Riesgo funcional/seguridad: acciones `confirm/send/reject` no restringidas por grupo a nivel backend.
3. Riesgo funcional/seguridad: cancelacion de `confirmed` no restringida a managers/admin en backend.

## 5. Archivos revisados

- `test_module.py`
- `extra_validation.py`
- `addons/product_sample_management/models/sample_request.py`
- `addons/product_sample_management/models/res_partner.py`
- `addons/product_sample_management/views/sample_request_views.xml`
- `addons/product_sample_management/views/res_partner_views.xml`
- `addons/product_sample_management/views/menus.xml`
- `addons/product_sample_management/security/security.xml`
- `addons/product_sample_management/security/ir.model.access.csv`
- `addons/product_sample_management/data/sequences.xml`
- `addons/product_sample_management/wizard/reject_wizard.py`
- `addons/product_sample_management/wizard/reject_wizard_views.xml`

## 6. Resultado final

Estado general: FUNCIONAL CON OBSERVACIONES.

- Cobertura funcional ejecutada: completa segun suite disponible + validacion extra.
- Cumplimiento estricto del enunciado: parcial (3 puntos abiertos indicados arriba).
