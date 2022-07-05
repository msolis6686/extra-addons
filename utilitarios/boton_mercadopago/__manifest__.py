{
    'name': 'Button for MercadoPago',
    'category': 'Account',
    'version': '13.0.0.1',
    'author': 'Moldeo Interactive,Filoquin',
    'license': 'AGPL-3',
    'summary': '',

    'depends': ['account','base','payment'],
    'data': [
    'data/account_journal.xml',
    'data/ir_cron.xml',
    'data/payment_acquirer.xml',
	'views/invoice_view.xml',
	'views/invoice_action_data.xml',
    'views/res_config_settings.xml'
    ],
    'external_dependencies':{
            'python': ['mercadopago'],
        },
    'demo': [
    ],
    'qweb': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
