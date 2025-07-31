{
    "author": "BlackFishTeam",
    "website": "https://blackfishweb.com/",
    "summary": """
    Este modulo modifica la localizacion de codize para mandar dos nuevos campos requeridos por ARCA en (RG:5616/2024)
    """,
    "category": "black-addons",
    "depends": ['account', 'l10n_ar_afipws_fe'],
    "installable": True,
    "version": "14.0.0.0.1",
    "license": "AGPL-3",
    "name": "bf_arca_rg5616_2024",
    'data':[
        'views/move_view_inherit.xml',
        'views/res_config_settings_view.xml'
        ],
    "demo": [],
}
