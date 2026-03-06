# -*- coding: utf-8 -*-
{
    'name': 'Gestión de Muestras de Producto',
    'version': '16.0.1.0.0',
    'category': 'Sales',
    'summary': 'Gestión de solicitudes de muestras de producto para clientes',
    'description': """
        Módulo para gestionar las solicitudes de muestras de producto
        que realizan los clientes antes de hacer un pedido real.
    """,
    'author': 'Renzo',
    'depends': ['base', 'mail', 'product', 'stock'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'wizard/reject_wizard_views.xml',
        'views/sample_request_views.xml',
        'views/res_partner_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
