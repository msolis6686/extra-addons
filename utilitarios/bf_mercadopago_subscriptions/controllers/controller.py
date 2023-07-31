# -*- coding: utf-8 -*-

from odoo import models, fields, api, http
from odoo import http
from odoo.http import request, JsonRequest
import mercadopago
import requests
from datetime import date

class MyController(http.Controller):
    @http.route('/json_test', type='json', auth='none', methods=['POST'])
    def json(self, **kw):
        json_data = request.jsonrequest
        print(json_data)

    @http.route('/subscripcion_exitosa', auth='public', website=True)
    def return_subscription_success(self, **kw):
        post = request.params
        mp_api_key = request.env['ir.config_parameter'].sudo().search([('key','=','mercadopago_api')])
        mp_request = requests.get(F"https://api.mercadopago.com/preapproval/{post.get('preapproval_id')}",headers={'Authorization': f'Bearer {mp_api_key.value}'}).json()
        if mp_request.get('status') == 'authorized':
            if mp_request.get('payer_email'):
                odoo_partner = request.env['res.partner'].search([('email', '=', mp_request.get('payer_email'))])
                if odoo_partner:
                    #Checkeamos si el cliente tiene alguna subscripcion
                    if odoo_partner.subscription_type:
                        self.check_subscription(odoo_partner, mp_request)
                    else:
                        self.create_subscription(odoo_partner, mp_request)
            else:
                self.check_client(mp_request)
        return http.request.render('bf_mercadopago_subscriptions.mp_subscription_success')



    def check_subscription(self, partner, mp_data):
        subscription = request.env['bf.mercadopago.active.subscription'].search([('partner_id','=',partner.id),('state','=','Activa')])
        if subscription:
            #modify subscription values
            
            pass
    
    def create_subscription(self, partner, mp_data):
        internal_subscription = request.env['bf.mercadopago.subscriptions'].search([('name','=',mp_data.get('external_reference'))])
        if internal_subscription:
            partner.subscription_type = internal_subscription.id
            subscription_record = request.env['bf.mercadopago.active.subscriptions']
            vals = {
                'partner_id': partner.id,
                'subscription_id': internal_subscription.id,
                'status': 'Activa',
                'active_since': date.today(),
                'ended_in': False,
                'active_months': 1,
                'notes': 'test',
                'total_recaudado': 0
            }
            subscription_record.create(vals)
    
    def check_client(self, mp_data):
        client_check = request.env['res.partner'].search([('name','=',str(mp_data.get('payer_id')))])
        if client_check:
            if client_check.subscription_type:
                self.check_subscription(client_check, mp_data)
            else:
                self.create_subscription(client_check, mp_data)
        else:
            client_record = request.env['res.partner']
            vals = {
                'name': str(mp_data.get('payer_id')),
                'l10n_latam_identification_type_id': request.env['l10n_latam.identification.type'].search([('name','=','DNI')]).id,
            }
            created_client = client_record.create(vals)
            self.create_subscription(created_client, mp_data)