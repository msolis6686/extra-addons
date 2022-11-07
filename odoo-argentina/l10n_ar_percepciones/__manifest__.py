# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Percepciones Ventas - Argentina',
    'version': '11.0.1.0.0',
    'category': 'Accounting',
    'summary': "Percepciones en Ventas - Argentina",
    'depends': ['base','account','l10n_ar','account_move_tax','account_tax_python','product'],
    "data": [
	"account_view.xml",
        "security/ir.model.access.csv"
    ],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
}

