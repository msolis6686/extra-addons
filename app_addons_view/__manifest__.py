# -*- coding: utf-8 -*-
{
    'name': 'Display Addons Paths',
    'version': '1.0',
    'summary': """Displaying Addons Paths""",
    'description': """Displays all addons paths and filter modules""",
    'category': 'Base',
    'author': 'iKreative',
    'website': "",
    'license': 'AGPL-3',

    'depends': ['base'],

    'data': [
        'security/ir.model.access.csv',
        'views/ir_module_module_view.xml',
        'views/ir_module_addons_path_view.xml',
    ],
    'demo': [

    ],
    'images': ['static/description/banner.png'],
    'qweb': [],

    'installable': True,
    'auto_install': False,
    'application': False,
}
