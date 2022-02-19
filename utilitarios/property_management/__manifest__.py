# -*- coding: utf-8 -*-
{
    'name': "property_management",

    'summary': """
        Manage your buildings, floors, properties and contract""",

    'description': """
        System with in-depth management of Projects, Buildings, Floors, Properties 
    """,

    'author': "Sana",
    'website': "http://www.sanakhurram.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','contacts','account'],
    'license': 'LGPL-3',
    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/real_estate_views.xml',
        'views/templates.xml',
        # 'views/member.xml',
    ],
    'qweb': [
        'static/src/xml/partner_autocomplete.xml',
    ],
    'images': ['static/description/banner.gif',],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

}
