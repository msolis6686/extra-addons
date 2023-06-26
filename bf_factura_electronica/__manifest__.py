# -*- coding: utf-8 -*-
{
    'author': "BlackFishTeam",
    'website': "http://www.blackfishweb.com/",
    'summary': """
    Este módulo es una personalización de las facturas electrónicas.""",
    'description': """
    Con este módulo perzonalizamos las facturas en un formato mas limpio y presentable. Se puede adaptar a las necesidades de cada cliente.
    """,
    'category': 'black-addons',
    'depends': [
        'l10n_ar_afipws_fe',
    ],
    'external_dependencies': {'python':['icecream']},
    'installable': True,
    'license': 'AGPL-3',
    'name': 'bf_factura_electronica',
    'data': [
        'layouts.xml',
        'report_move_fe.xml',
    ],
    'demo': [

    ],
    'images':['static/img/afip.svg',]
}
