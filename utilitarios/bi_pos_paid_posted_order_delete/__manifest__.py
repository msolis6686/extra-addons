# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "POS Order Delete/ Delete POS Paid Order",
    "version" : "13.0.0.0",
    "category" : "Point of Sale",
    'summary': 'Delete POS order Delete point of sales order delete paid order on pos delete posted order delete pos posted order delete paid pos order cancel pos order reset to draft cancel point of sales order cancel pos paid order delete from pos completed prder delete',
    "description": """
    
         POS Delete Order in Odoo,
         Paid/Posted Delete POS orders in odoo,
         Delete Single POS order in odoo,
         Delete Multiple POS orders in odoo,
         Set security code for delete POS order in odoo,
         Allow delete POS order in odoo,
         Delete POS Order Without Code in odoo,
         Delete POS Order With Code in odoo,
    
    """,
    "author": "BrowseInfo",
    "website" : "https://www.browseinfo.in",
    "price": 12,
    "currency": 'EUR',
    "depends" : ['base','point_of_sale'],
    "data": [
        'security/pos_delete_paid_order.xml',
        'views/res_users.xml',
        'wizard/delete_order_wiz.xml',
    ],
    
    "auto_install": False,
    "installable": True,
    "live_test_url":'https://youtu.be/B7thB99LinI',
    "images":['static/description/Banner.png'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: