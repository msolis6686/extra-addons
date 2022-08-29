# -*- coding: utf-8 -*-

from odoo import models, fields, api, http

class MyController(http.Controller):
    @http.route('/subscripcion_exitosa', auth='public', website=True)
    def return_subscription_success(self):
        return http.request.render('mercadopago_subscriptions.mp_subscription_success')