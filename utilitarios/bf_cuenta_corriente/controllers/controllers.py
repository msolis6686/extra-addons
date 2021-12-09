# -*- coding: utf-8 -*-
# from odoo import http


# class BfAntanetUnreconciled(http.Controller):
#     @http.route('/bf_antanet_unreconciled/bf_antanet_unreconciled/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bf_antanet_unreconciled/bf_antanet_unreconciled/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bf_antanet_unreconciled.listing', {
#             'root': '/bf_antanet_unreconciled/bf_antanet_unreconciled',
#             'objects': http.request.env['bf_antanet_unreconciled.bf_antanet_unreconciled'].search([]),
#         })

#     @http.route('/bf_antanet_unreconciled/bf_antanet_unreconciled/objects/<model("bf_antanet_unreconciled.bf_antanet_unreconciled"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bf_antanet_unreconciled.object', {
#             'object': obj
#         })
