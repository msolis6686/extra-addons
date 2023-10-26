# -*- coding: utf-8 -*-
{
    'name': "bf_whatsapp_base",

    'summary': """
        Este módulo se conecta con un servicio de API de whatsapp y permite enviar mensajes a sus clientes.
        """,

    'description': """
        Este módulo se conecta con un servicio de API de whatsapp y permite enviar mensajes a sus clientes.
    """,

    'author': "BlackFishTeam",
    'website': "https://www.blackfish.com.ar/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'black-addons',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'web', 'stock', 'purchase','account','contacts'],
    
    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        #'views/templates.xml',
        #'views/template.xml',
        #'views/account_invoice.xml',
        'views/res_partner.xml',
        'wizard/create_message.xml',
        'wizard/massive_wa_send_wizard.xml',
        'wizard/message_wizard.xml',
        'wizard/wizard_contact.xml',
        'wizard/wizard.xml',
        'data/template.xml',
        'data/registros.xml',
    ],
    # only loaded in demonstration mode
    #'demo': [
    #    'demo/demo.xml',
    #],
}
