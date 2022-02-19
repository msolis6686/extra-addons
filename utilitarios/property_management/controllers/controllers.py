# -*- coding: utf-8 -*-
# from odoo import http


# class HxRealEstate(http.Controller):
#     @http.route('/Property management/Property management/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/Property management/Property management/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('Property management.listing', {
#             'root': '/Property management/Property management',
#             'objects': http.request.env['Property management.Property management'].search([]),
#         })

#     @http.route('/Property management/Property management/objects/<model("Property management.Property management"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('Property management.object', {
#             'object': obj
#         })
