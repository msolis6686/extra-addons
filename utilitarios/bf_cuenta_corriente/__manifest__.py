# -*- coding: utf-8 -*-
{
    'name': "bf_cuenta_corriente",

    'summary': """
        Mostrar cuenta corriente de clientes""",

    'description': """
        Modulo para mostrar las cuentas corrientes de todos los clientes. Los datos figuran en la misma vista del cliente o en la parte de facturacion y contabilidad/Clientes/Cuenta Corriente de Clientes.
        Los datos figuran como Debe: Haber: y Saldo. Tambien habilita dos botones en la misma vista para poder ver los pagos y facturas de los clientes.
    """,

    'author': "BlackFish",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account_payment_group','partner_statement'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/cuenta_corriente_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
