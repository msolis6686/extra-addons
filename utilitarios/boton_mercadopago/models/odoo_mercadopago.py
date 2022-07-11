# -*- coding: utf-'8' "-*-"

import base64
try:
    import simplejson as json
except ImportError:
    import json
import logging
from urllib.parse import urlparse
from urllib.parse import urljoin
import werkzeug.urls
from urllib.request import urlopen
from datetime import date
import requests
import re
import mercadopago

from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.addons.boton_mercadopago.controllers.main import MercadoPagoController
from odoo import osv, fields, models, api, _
from odoo.tools.float_utils import float_compare
from odoo import SUPERUSER_ID

_logger = logging.getLogger(__name__)
from dateutil.tz import *

dateformat="%Y-%m-%dT%H:%M:%S."
dateformatmilis="%f"
dateformatutc="%z"

class OdooMercadopago(models.AbstractModel):
    _name = "odoo_mercadopago"
    _mercadopago_partner_field = 'partner_id'
    _mercadopago_amount_field = 'amount_total'

    mercadopago_url = fields.Char(
        'MercadoPago URL',
    )
    mercadopago_id = fields.Char(
        'MercadoPago Id',
    )
    
    def mercadopago_payment_receipt(self,payment_id,result):
        pass

    def mercadopago_payer_dict(self):
        partner_id = self[self._mercadopago_partner_field]
        return {
            #'surname': partner_id.name,
            'email': partner_id.email,

        }

    def mercadopago_shipments_dict(self):
        return {
            'mode': 'not_specified',

        }

    def mercadopago_payment_methods_dict(self):
        return {}

    def mercadopago_notification_url(self):
        return ''

    def mercadopago_items(self):
        # to-do: currency_id

        return [{
            'title': self.display_name,
            'quantity': 1,
            'currency_id': 'ARS',
            'unit_price': self[self._mercadopago_amount_field]
        }]

    def mercadopago_expires_dict(self):
        return {
            'expires': False,
        }

    def mercadopago_create_preference(self):
        # preference api description
        # https://www.mercadopago.com.ar/developers/es/reference/preferences/_checkout_preferences/post/
        # to-do: add suport to back_urls expires
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        acquirer = self

        #tx_values = dict(values)
        #_logger.info(tx_values)
        #saleorder_obj = self.env['sale.order']
        #saleorderline_obj = self.env['sale.order.line']

        saleorder_obj = self.env['account.move']
        saleorderline_obj = self.env['account.move.line']
        print(saleorder_obj)
        print(saleorderline_obj)

        mercadopago_client = self.env['ir.config_parameter'].get_param(
            'mercadopago_client', default=False)
        mercadopago_key = self.env['ir.config_parameter'].get_param(
            'mercadopago_key', default=False)
        mercadopago_api = self.env['ir.config_parameter'].get_param(
            'mercadopago_api', default=False)

        if self.env['ir.config_parameter'].sudo().get_param('mercadopago_external_reference', default='obj') == 'obj':
            external_reference = self._name
        else:
            external_reference = 'res.partner'

        if self.env['ir.config_parameter'].sudo().get_param('mercadopago_sandbox', default=False):
            init_point = 'sandbox_init_point'
        else:
            init_point = 'init_point'

        if mercadopago_api:
            #mp = mercadopago.MP(mercadopago_client, mercadopago_key)
            sdk = mercadopago.SDK(mercadopago_api)

            for obj in self:
                if external_reference == 'res.partner':
                    ref_id = self[self._mercadopago_partner_field].id
                else :
                    ref_id = obj.id
                preference = {
                    'external_reference': '%s-%s' % (external_reference, ref_id),
                    'payer': obj.mercadopago_payer_dict(),
                    'shipments': obj.mercadopago_shipments_dict(),
                    'payment_methods': obj.mercadopago_payment_methods_dict(),
                    'notification_url': obj.mercadopago_notification_url(),
                    'items': obj.mercadopago_items(),
                    "back_urls": {
                                    "success": '%s' % urljoin( base_url, MercadoPagoController._return_url),
                                    "failure": '%s' % urljoin( base_url, MercadoPagoController._cancel_url),
                                    "pending": '%s' % urljoin( base_url, MercadoPagoController._return_url)
                                },
                    "auto_return": "approved",
                    "notification_url": '%s' % urljoin( base_url, MercadoPagoController._notify_url),
                    "expires": True,
                    #"expiration_date_from": obj.mercadopago_dateformat( datetime.datetime.now(tzlocal())-datetime.timedelta(days=1) ),
                    #"expiration_date_to": obj.mercadopago_dateformat( datetime.datetime.now(tzlocal())+datetime.timedelta(days=31) )
                }
                #preference.update(obj.mercadopago_expires_dict())
                _logger.info("preference %r"%preference)
                preferenceResult = sdk.preference().create(preference)

                if 'status' in preferenceResult and preferenceResult['status'] == 201:
                    self.mercadopago_url = preferenceResult[
                        'response'][init_point]
                    self.mercadopago_id = preferenceResult['response']['id']

        return True  # for xmlrcp
    
    """ def create_payment(self, post, fact_id):
        _logger.info('ENTRE A LA FUNCION')
        _logger.info('ENTRE A LA FUNCION')
        _logger.info('ENTRE A LA FUNCION')
        _logger.info('ENTRE A LA FUNCION')
        _logger.info('ENTRE A LA FUNCION')
        factura = self.env['account.move'].sudo().search([('id','=',fact_id)])
        _logger.info(f"FACTURA: {factura}")
        #COSAS DE LA FOCA PARA SIMULAR MERCADOPAGO.
        move_line = self.env['account.move.line'].sudo().search([('move_id','=',fact_id),('account_internal_type','=','receivable')])
        payment_receipt_data = {
                                'localization': 'argentina',
                                'receiptbook_id': 1,
                                'name': 'Cobro Automatico Mercadopago: ' + factura.name,
                                'company_id': 1,
                                'partner_type': 'customer',
                                'partner_id': factura.partner_id.id,
                                'currency_id': factura.currency_id.id,
                                'payment_date': date.today(),
                                'state': 'draft',
                                'has_outstanding': False,
                                'sent': False,
                                'payment_ids': [(0, 0, {
                                    'state': 'draft',
                                    'payment_type': 'inbound',
                                    'payment_method_id': 1,
                                    'partner_type': 'customer',
                                    'partner_id': factura.partner_id.id,
                                    'amount': factura.amount_total,
                                    'currency_id': factura.currency_id.id,
                                    'payment_date': date.today(),
                                    'journal_id': 13,
                                    'payment_difference_handling': 'open',
                                    'writeoff_label': 'Write-Off',
                                })]
                                }
        temp_payment = self.env['account.payment.group']
        _logger.info(f"TEMP PAYMENT: {temp_payment}")
        temp_payment.sudo().create(payment_receipt_data)
        #payment = request.env['account.payment.group'].sudo().create(payment_receipt_data)
        temp_payment.write({'debt_move_line_ids': [(4,move_line.id)]})# = [(4,[move_line.id])]
        temp_payment.post() """
