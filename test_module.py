# -*- coding: utf-8 -*-
"""Test completo via JSON-RPC (evita problemas de XML-RPC con None)."""
import json, urllib.request, sys
from datetime import date

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

URL = 'http://localhost:8069'
DB = 'odoo16'
USER = 'admin'
PASS = 'admin'

_id = 0
def jsonrpc(url, method, params):
    global _id
    _id += 1
    data = json.dumps({'jsonrpc': '2.0', 'method': method, 'params': params, 'id': _id}).encode()
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    resp = json.loads(urllib.request.urlopen(req).read().decode())
    if resp.get('error'):
        raise Exception(resp['error']['data']['message'])
    return resp.get('result')

# Authenticate
uid = jsonrpc(f'{URL}/jsonrpc', 'call', {
    'service': 'common', 'method': 'authenticate',
    'args': [DB, USER, PASS, {}]
})

def call(model, method, args, kwargs=None):
    return jsonrpc(f'{URL}/jsonrpc', 'call', {
        'service': 'object', 'method': 'execute_kw',
        'args': [DB, uid, PASS, model, method, args, kwargs or {}]
    })

passed = failed = 0
def test(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1; print(f"  [PASS] {name}")
    else:
        failed += 1; print(f"  [FAIL] {name} -- {detail}")

print("=" * 70)
print("TEST COMPLETO: product_sample_management (JSON-RPC)")
print("=" * 70)

# T1: CONEXION
print("\n--- TEST 1: Conexion y modulo ---")
test("Conexion", uid and uid > 0)
mods = call('ir.module.module', 'search', [[('name', '=', 'product_sample_management'), ('state', '=', 'installed')]])
test("Modulo instalado", len(mods) > 0)

# T2: CAMPOS
print("\n--- TEST 2: Campos product.sample.request ---")
fl = call('product.sample.request', 'fields_get', [], {'attributes': ['type']})
for f, t in {'name':'char','partner_id':'many2one','product_id':'many2one','quantity':'float',
             'request_date':'date','user_id':'many2one','notes':'text','state':'selection',
             'total_requests':'integer'}.items():
    test(f"'{f}' ({t})", f in fl and fl[f]['type'] == t)
test("message_ids (chatter)", 'message_ids' in fl)
test("activity_ids", 'activity_ids' in fl)

# T3: HERENCIA PARTNER
print("\n--- TEST 3: Herencia res.partner ---")
pfl = call('res.partner', 'fields_get', [], {'attributes': ['type']})
test("sample_request_ids", 'sample_request_ids' in pfl)
test("sample_count", 'sample_count' in pfl)

# T4: SECUENCIA
print("\n--- TEST 4: Secuencia ---")
sids = call('ir.sequence', 'search', [[('code', '=', 'product.sample.request')]])
test("Secuencia definida", len(sids) > 0)
if sids:
    seq = call('ir.sequence', 'read', sids, {'fields': ['prefix', 'padding']})
    test("Prefijo MUESTRA/%(year)s/", seq[0]['prefix'] == 'MUESTRA/%(year)s/')
    test("Padding=4", seq[0]['padding'] == 4)

# T5: DATOS PRUEBA
print("\n--- TEST 5: Datos de prueba ---")
pid = call('res.partner', 'create', [{'name': 'ClienteTestJsonRPC'}])
test("Partner creado", pid > 0)
prods = call('product.product', 'search', [[]], {'limit': 1})
prid = prods[0] if prods else call('product.product', 'create', [{'name': 'ProdTest', 'type': 'product'}])
test("Producto ok", prid > 0)

# T6: FLUJO COMPLETO
print("\n--- TEST 6: draft->confirmed->sent->received ---")
s1 = call('product.sample.request', 'create', [{'partner_id': pid, 'product_id': prid, 'quantity': 5.0, 'request_date': str(date.today())}])
test("Creada", s1 > 0)
r = call('product.sample.request', 'read', [s1], {'fields': ['name', 'state']})[0]
test("draft", r['state'] == 'draft')
test("Nuevo", r['name'] == 'Nuevo')

call('product.sample.request', 'action_confirm', [s1])
r = call('product.sample.request', 'read', [s1], {'fields': ['name', 'state']})[0]
test("confirmed", r['state'] == 'confirmed')
test("MUESTRA/...", r['name'].startswith('MUESTRA/'))
yr = str(date.today().year)
test(f"Year {yr}", yr in r['name'])
print(f"     Secuencia: {r['name']}")

call('product.sample.request', 'action_send', [s1])
r = call('product.sample.request', 'read', [s1], {'fields': ['state']})[0]
test("sent", r['state'] == 'sent')

call('product.sample.request', 'action_receive', [s1])
r = call('product.sample.request', 'read', [s1], {'fields': ['state']})[0]
test("received", r['state'] == 'received')

# T7: RECHAZO
print("\n--- TEST 7: Rechazo via wizard ---")
s2 = call('product.sample.request', 'create', [{'partner_id': pid, 'product_id': prid, 'quantity': 3.0, 'request_date': str(date.today())}])
call('product.sample.request', 'action_confirm', [s2])
call('product.sample.request', 'action_send', [s2])
w = call('product.sample.reject.wizard', 'create', [{'sample_request_id': s2, 'reject_reason': 'Producto defectuoso - test'}])
test("Wizard creado", w > 0)
call('product.sample.reject.wizard', 'action_reject', [w])
r2 = call('product.sample.request', 'read', [s2], {'fields': ['state', 'notes']})[0]
test("rejected", r2['state'] == 'rejected')
test("Motivo en notes", r2['notes'] == 'Producto defectuoso - test')

# T8: CANCELACION
print("\n--- TEST 8: Cancelacion ---")
s3 = call('product.sample.request', 'create', [{'partner_id': pid, 'product_id': prid, 'quantity': 2.0, 'request_date': str(date.today())}])
call('product.sample.request', 'action_cancel', [s3])
test("draft->cancelled", call('product.sample.request', 'read', [s3], {'fields': ['state']})[0]['state'] == 'cancelled')

s4 = call('product.sample.request', 'create', [{'partner_id': pid, 'product_id': prid, 'quantity': 1.0, 'request_date': str(date.today())}])
call('product.sample.request', 'action_confirm', [s4])
call('product.sample.request', 'action_cancel', [s4])
test("confirmed->cancelled", call('product.sample.request', 'read', [s4], {'fields': ['state']})[0]['state'] == 'cancelled')

s5 = call('product.sample.request', 'create', [{'partner_id': pid, 'product_id': prid, 'quantity': 1.0, 'request_date': str(date.today())}])
call('product.sample.request', 'action_confirm', [s5])
call('product.sample.request', 'action_send', [s5])
try:
    call('product.sample.request', 'action_cancel', [s5])
    test("sent NO cancelable", False)
except:
    test("sent NO cancelable (error ok)", True)

# T9: VOLVER BORRADOR
print("\n--- TEST 9: Volver a borrador ---")
s6 = call('product.sample.request', 'create', [{'partner_id': pid, 'product_id': prid, 'quantity': 1.0, 'request_date': str(date.today())}])
call('product.sample.request', 'action_confirm', [s6])
call('product.sample.request', 'action_draft', [s6])
test("confirmed->draft", call('product.sample.request', 'read', [s6], {'fields': ['state']})[0]['state'] == 'draft')

# T10: VALIDACION CANTIDAD
print("\n--- TEST 10: Validacion cantidad ---")
s7 = call('product.sample.request', 'create', [{'partner_id': pid, 'product_id': prid, 'quantity': 0, 'request_date': str(date.today())}])
try:
    call('product.sample.request', 'action_confirm', [s7])
    test("qty=0 NO confirmable", False)
except:
    test("qty=0 NO confirmable (error ok)", True)

s8 = call('product.sample.request', 'create', [{'partner_id': pid, 'product_id': prid, 'quantity': -5, 'request_date': str(date.today())}])
try:
    call('product.sample.request', 'action_confirm', [s8])
    test("qty=-5 NO confirmable", False)
except:
    test("qty=-5 NO confirmable (error ok)", True)

# T11: CAMPOS CALCULADOS
print("\n--- TEST 11: Campos calculados ---")
cnt = call('product.sample.request', 'search_count', [[('partner_id', '=', pid)]])
tr = call('product.sample.request', 'read', [s1], {'fields': ['total_requests']})[0]
test(f"total_requests={cnt}", tr['total_requests'] == cnt)
pc = call('res.partner', 'read', [pid], {'fields': ['sample_count']})[0]
test(f"sample_count={cnt}", pc['sample_count'] == cnt)

# T12: STAT BUTTON
print("\n--- TEST 12: Stat button ---")
act = call('res.partner', 'action_view_sample_requests', [pid])
test("act_window", act.get('type') == 'ir.actions.act_window')
test("model correcto", act.get('res_model') == 'product.sample.request')
test("domain partner", ['partner_id', '=', pid] in act.get('domain', []))

# T13: ELIMINAR
print("\n--- TEST 13: Eliminar ---")
sd = call('product.sample.request', 'create', [{'partner_id': pid, 'product_id': prid, 'quantity': 1.0, 'request_date': str(date.today())}])
try:
    call('product.sample.request', 'unlink', [sd])
    rem = call('product.sample.request', 'search', [[('id', '=', sd)]])
    test("Eliminacion ok", len(rem) == 0)
except Exception as e:
    test("Eliminacion ok", False, str(e))

# T14: SEGURIDAD
print("\n--- TEST 14: Seguridad ---")
gids = call('res.groups', 'search', [[('name', '=', 'Responsable de Muestras')]])
test("Grupo existe", len(gids) > 0)
if gids:
    g = call('res.groups', 'read', gids, {'fields': ['users']})[0]
    test("Admin en grupo", uid in g['users'])

# T15: VISTAS
print("\n--- TEST 15: Vistas ---")
for vt in ['form', 'tree', 'kanban', 'search']:
    test(f"Vista {vt}", len(call('ir.ui.view', 'search', [[('model', '=', 'product.sample.request'), ('type', '=', vt)]])) > 0)
test("Herencia partner", len(call('ir.ui.view', 'search', [[('model', '=', 'res.partner'), ('name', 'like', 'sample')]])) > 0)

# T16: MENUS
print("\n--- TEST 16: Menus ---")
test("Menu Muestras", len(call('ir.ui.menu', 'search', [[('name', '=', 'Muestras')]])) > 0)
test("Submenu Solicitudes", len(call('ir.ui.menu', 'search', [[('name', '=', 'Solicitudes de muestra')]])) > 0)

# RESUMEN
tot = passed + failed
print("\n" + "=" * 70)
if failed == 0:
    print(f"RESULTADO: {passed}/{tot} TODOS LOS TESTS PASARON!")
else:
    print(f"RESULTADO: {passed}/{tot} pasaron, {failed} FALLARON")
print("=" * 70)
