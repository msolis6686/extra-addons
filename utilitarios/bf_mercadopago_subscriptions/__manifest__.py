# -*- coding: utf-8 -*-
{
    'name': "bf_mercadopago_subscriptions",

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
    'depends': ['base','mail','contacts','website','account','boton_mercadopago'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/templates.xml',
        'views/active_subscriptions.xml',
        'wizards/mass_subscription.xml',
        'wizards/update_subscription.xml',
        'wizards/cancel_subscription.xml',
        'website_views/subscription_success.xml',
        'static/src/js/get_update_subscriptions.js',
        'security/ir.model.access.csv',
    ],
    'qweb': [
        "static/src/xml/js_buttons.xml",
    ],
}