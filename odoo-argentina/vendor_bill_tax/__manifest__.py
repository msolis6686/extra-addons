{
    'name': 'Vendor Bill Tax',
    'version': "1.0",
    'description': """Agrega botones en facturas de proveedor para agregar manualmente impuestos.""",
    'author': 'ADHOC SA, Moldeo Interactive',
    'category': 'Localization',
    'depends': [
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/account_invoice_tax_view.xml',
        'views/account_move_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
