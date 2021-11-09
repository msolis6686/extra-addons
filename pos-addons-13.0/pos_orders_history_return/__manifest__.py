# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# Copyright 2018 Ilmir Karamov <https://it-projects.info/team/ilmir-k>
# License MIT (https://opensource.org/licenses/MIT).
{
    "name": """POS Orders Return""",
    "summary": """The module allows to make order returns from POS interface by quick & easy way""",
    "category": "Point of Sale",
    # "live_test_url": "http://apps.it-projects.info/shop/product/pos-orders-return?version=13.0",
    "images": ["images/pos_orders_return_main.jpg"],
    "version": "13.0.1.0.6",
    "application": False,
    "author": "IT-Projects LLC, Dinar Gabbasov",
    "support": "pos@it-projects.info",
    "website": "https://apps.odoo.com/apps/modules/13.0/pos_orders_history_return/",
    "license": "Other OSI approved licence",  # MIT
    "price": 20.00,
    "currency": "EUR",
    "depends": ["pos_orders_history"],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views/pos_orders_history_return_view.xml",
        "views/pos_orders_history_return_template.xml",
    ],
    "demo": [],
    "qweb": ["static/src/xml/pos.xml"],
    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,
    "auto_install": False,
    "installable": False,
    "demo_title": "POS Orders Refund",
    "demo_addons": [],
    "demo_addons_hidden": [],
    "demo_url": "pos-orders-return",
    "demo_summary": "The module allows to make order returns from POS interface by convenient way",
    "demo_images": ["images/pos_orders_return_main.jpg"],
}
