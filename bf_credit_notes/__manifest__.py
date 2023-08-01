# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Black Fish Credit Notes',
    'version': '1.0',
    'category': 'Accounting/Accounting',
    'summary': 'Credit Notes',
    'description': """
        Edit of the module debit notes to allow the creation and validation of credit notes against AFIP.
    """,
    'data': [
        'views/bf_account_move_reversal_inherit.xml',
    ],
    'depends': ['account'],
    'installable': True,
    'auto_install': False,
}
