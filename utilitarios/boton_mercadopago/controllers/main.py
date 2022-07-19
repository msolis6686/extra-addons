# -*- coding: utf-8 -*-

try:
    import simplejson as json
except ImportError:
    import json
import logging
import pprint
from datetime import date

from urllib.request import urlopen
try:
    #python2
    import urlparse as parse
except ImportError:
    #python3
    from urllib import parse

import werkzeug

from odoo import http, SUPERUSER_ID
from odoo.http import request
from odoo.http import JsonRequest
from odoo.addons import web
import requests
from requests.structures import CaseInsensitiveDict

_logger = logging.getLogger(__name__)

#from odoo.addons.payment_mercadopago.mercadopago import mercadopago
from odoo.addons.portal.controllers.portal import _build_url_w_params

class MercadoPagoController(http.Controller):
    _notify_url = '/payment/mercadopago/ipn/'
    #_notify_url = '/test_route'
    _return_url = '/payment/mercadopago/dpn/'
    _cancel_url = '/payment/mercadopago/cancel/'

    def create_payment(self, factura, post):
        mp_payment_group_receiptbook = request.env['ir.config_parameter'].sudo().search([('key','=','mercadopago_payment_group_journal_id')])
        mp_journal = request.env['ir.config_parameter'].sudo().search([('key','=','mercadopago_journal_id')])
        payment_method = request.env['ir.config_parameter'].sudo().search([('key','=','mercadopago_payment_method')])
        #Esta funcion crea el recibo de pago y lo postea.
        payment_receipt_data = {
                                'localization': 'argentina',
                                'receiptbook_id': int(mp_payment_group_receiptbook.value),
                                'name': f"Cobro Automatico Mercadopago:{factura.name}",
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
                                    'payment_method_id': int(payment_method.value),
                                    'partner_type': 'customer',
                                    'partner_id': factura.partner_id.id,
                                    'amount': factura.amount_total,
                                    'currency_id': factura.currency_id.id,
                                    'payment_date': date.today(),
                                    'journal_id': int(mp_journal.value),
                                    'payment_difference_handling': 'open',
                                    'writeoff_label': 'Write-Off',
                                })]
                                }
        temp_payment = request.env['account.payment.group']
        payment = temp_payment.sudo().create(payment_receipt_data)
        if post.get('pago_repetido') == False:
            move_line = request.env['account.move.line'].sudo().search([('move_id','=',factura.id),('account_internal_type','=','receivable')])
            payment.write({'debt_move_line_ids': [(4,move_line.id)]})
        payment.post()
        post = self.create_mercadopago_data(payment, factura, post)
        return post
    
    def create_mercadopago_data(self, payment, factura, post):
        #Esta funcion es solo accionada si se creo un recibo de pago, aqui se crea un registro de los datos de MercadoPago, el recibo y la factura.
        nota = False
        post['factura'] = factura
        post['recibo'] = payment
        post['error_critico'] = False
        post['error_description'] = False
        if post.get('pago_repetido') == True:
            nota = f"El cliente {factura.partner_id.name} ha realizado un pago repetido de la factura: {factura.name}, se acredito el pago con el nombre: {payment.name}."
            post['error_description'] = f"Ha realizado un pago repetido de la factura {factura.name}, se acredito el pago con el nombre {payment.name} y se le otorgo el saldo del mismo a favor. Si tiene alguna pregunta no dude en contactarnos."
        mp_data_temp = request.env['mp.data']
        mp_data = mp_data_temp.sudo().create(
            {
                'payment_group_id': payment.id,
                'invoice_id': factura.id,
                'collection_id': post.get('collection_id'),
                'collection_status': post.get('collection_status'),
                'external_reference': post.get('external_reference'),
                'merchant_account_id': post.get('merchant_account_id'),
                'merchant_order_id': post.get('merchant_order_id'),
                'payment_id': post.get('payment_id'),
                'payment_type': post.get('payment_type'),
                'preference_id': post.get('preference_id'),
                'processing_mode': post.get('processing_mode'),
                'state_id': post.get('state_id'),
                'status': post.get('status'),
                'note': nota if nota != False else ''
            }
        )
        _logger.info(f"PASO DE POST FINAL A RETURN: {post}")
        return post
    
    def get_approval(self, post):
        #En esta funcion se busca validar los datos contra mercadopago y aprobar el pago o rechazarlo en nuestro sistema.
        if post.get('collection_status') == 'approved':
            mp_api_key = request.env['ir.config_parameter'].sudo().search([('key','=','mercadopago_api')])
            mp_request = requests.get(F"https://api.mercadopago.com/v1/payments/{post.get('payment_id')}",headers={'Authorization': f'Bearer {mp_api_key.value}'})
            mp_response = mp_request.json()
            if mp_response.get('status') == 404:
                post['error_critico'] = True
                post['error_description'] = f"No se encontro el pago en MercadoPago. ID de Pago: {post.get('payment_id')}"
                return post
            if str(mp_response.get('id')) == post.get('payment_id'):
                payment_existence = request.env['mp.data'].sudo().search([('payment_id','=',post.get('payment_id'))])
                if payment_existence:
                    post['payment_existence'] = payment_existence
                    post['error_critico'] = True
                    post['error_description'] = f"Este pago ya fue realizado. Si se debito dinero de su cuenta mas de una vez, porfavor, contactenos e informenos este numero: {post.get('payment_id')}"
                    _logger.info(f"Se detecto un pago existente en mercadopago y en nuestra DB, rechazando. {post}")
                    return post
                _logger.info(f"Pago listo para procesar: {post}")
                post['payment_existence'] = False
                post['error_critico'] = False
                return post
        elif post.get('collection_status') == 'pending':
            return werkzeug.utils.redirect('/pendiente')
        elif post.get('collection_status') == 'cancelled':
            post['error_critico'] = True
            post['error_description'] = 'Ha cancelado manualmente el pago.'
            return post

    def mercadopago_validate_data(self, post):
        """ MercadoPago IPN: three steps validation to ensure data correctness

         - step 1: return an empty HTTP 200 response -> will be done at the end
           by returning ''
         - step 2: POST the complete, unaltered message back to MercadoPago (preceded
           by cmd=_notify-validate), with same encoding
         - step 3: mercadopago send either VERIFIED or INVALID (single word)

        Once data is validated, process it. """
        res = False
        reference = post.get('external_reference')
        _logger.info('MercadoPago REFERENCIA:'+str(reference))
        #Se busca la referencia del POST, si tiene referencia se verifica que el pago sea valido en mercadopago con la funcion get_approval, si devuelve error_critico TRUE
        #se cancela la creacion del pago, si no se crea el pago y se renderiza la vista con la informacion correspondiente.
        if reference:
            post = self.get_approval(post)
            if post.get('error_critico') == False:
                _logger.info('PAGO ACEPTADO')
                fact_id = int(reference.split('-')[1])
                factura = request.env['account.move'].sudo().search([('id','=',fact_id)])
                #Se revisa si ya hay un pago realizado para la factura, si es asi, se crea un saldo a favor y se le informa a finalizar la transaccion.
                if factura.invoice_payment_state == 'paid':
                    post['pago_repetido'] = True
                    _logger.info("PAGO REPETIDO DETECTADO")
                    post = self.create_payment(factura, post)
                    return post
                else:
                    post['pago_repetido'] = False
                    #Si todo salio bien y tampoco hay pago repetido sobre la factura se crea un pago normalmente.
                    post = self.create_payment(factura, post)
                    return post
            else:
                #Aqui se entra solo si hubo un error critico (no se pudo procesar el pago.)
                _logger.info(f"NO SE APROBO UN PAGO: {post}")
                post['error_critico'] = True
                post['factura'] = False
                post['recibo'] = False
                return post
        return post

    @http.route('/payment/mercadopago/dpn', type='http', auth="public", website=True)
    def mercadopago_dpn(self, **post):
        """ MercadoPago DPN """
        _logger.info('Beginning MercadoPago DPN form_feedback with post data %s', pprint.pformat(post))  # debug
        new_post = self.mercadopago_validate_data(post)
        return http.request.render('boton_mercadopago.aceptado_process',new_post)

    @http.route('/payment/mercadopago/cancel', type='http', auth="public", website=True)
    def mercadopago_cancel(self, **post):
        """ When the user cancels its MercadoPago payment: GET on this route """
        post['collection_status'] = 'cancelled'
        new_post = self.mercadopago_validate_data(**post)
        return http.request.render('boton_mercadopago.aceptado_process',new_post)
    