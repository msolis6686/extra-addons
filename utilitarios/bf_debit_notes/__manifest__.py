# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'bf_debit_notes',
    'version': '1.0',
    'category': 'Accounting/Accounting',
    'summary': 'Correccion de Debit Notes',
    'description': """
        Este modulo hace que funcionen correctamente las notas de debito. Arregla un error que hacia que no ponga el documento de origen en la nota de debito, por lo que 
        no validaba la afip la misma. 
    """,
    'depends': ['account'],
    'data': [
        'wizard/account_debit_note_view.xml',
        'views/account_move_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
