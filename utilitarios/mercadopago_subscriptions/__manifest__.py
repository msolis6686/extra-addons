# -*- coding: utf-8 -*-
{
    'name': "mercadopago_subscriptions",

    'summary': """
        Modulo para subscripciones de mercadopago""",

    'description': """
        Modulo para poder administrar y realizar las facturas automaticamente de las subscripciones de los clientes a travez de mercadopago.
    """,

    'author': "BlackFish",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','contacts','website','account'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/templates.xml',
        'wizards/mass_subscription.xml',
        'website_views/subscription_success.xml',
        'security/ir.model.access.csv',
    ],
}
