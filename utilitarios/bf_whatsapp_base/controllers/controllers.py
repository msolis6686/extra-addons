# -*- coding: utf-8 -*-
# from odoo import http


# class BfAntanetCards(http.Controller):
#     @http.route('/bf_antanet_cards/bf_antanet_cards/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bf_antanet_cards/bf_antanet_cards/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bf_antanet_cards.listing', {
#             'root': '/bf_antanet_cards/bf_antanet_cards',
#             'objects': http.request.env['bf_antanet_cards.bf_antanet_cards'].search([]),
#         })

#     @http.route('/bf_antanet_cards/bf_antanet_cards/objects/<model("bf_antanet_cards.bf_antanet_cards"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bf_antanet_cards.object', {
#             'object': obj
#         })
