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

_logger = logging.getLogger(__name__)

#from odoo.addons.payment_mercadopago.mercadopago import mercadopago

class MercadoPagoController(http.Controller):
    _notify_url = '/payment/mercadopago/ipn/'
    _return_url = '/payment/mercadopago/dpn/'
    _cancel_url = '/payment/mercadopago/cancel/'

    def _get_return_url(self, **post):
        """ Extract the return URL from the data coming from MercadoPago. """
#        return_url = post.pop('return_url', '')
#        if not return_url:
#            custom = json.loads(post.pop('custom', False) or '{}')
#            return_url = custom.get('return_url', '/')
        if post.get('collection_status') == 'approved':
            return_url = '/aceptado'
            if post.get('pago_repetido') == 'True':
                return_url = '/repetido'
        else:
            return_url = '/cancelado'
        return return_url

    def mercadopago_validate_data(self, **post):
        """ MercadoPago IPN: three steps validation to ensure data correctness

         - step 1: return an empty HTTP 200 response -> will be done at the end
           by returning ''
         - step 2: POST the complete, unaltered message back to MercadoPago (preceded
           by cmd=_notify-validate), with same encoding
         - step 3: mercadopago send either VERIFIED or INVALID (single word)

        Once data is validated, process it. """
        res = False

#       topic = payment
#       id = identificador-de-la-operación
        topic = post.get('topic')
        op_id = post.get('id') or post.get('data.id')

        reference = post.get('external_reference')
        _logger.info('MercadoPago REFERENCIA:'+str(reference))

        if (not reference and (topic and str(topic) in ["payment"] and op_id) ):
            _logger.info('MercadoPago topic:'+str(topic))
            _logger.info('MercadoPago payment id to search:'+str(op_id))
            reference = request.env["payment.acquirer"].sudo().mercadopago_get_reference(payment_id=op_id)

        tx = None
        if reference:
            if post.get('collection_status') == 'approved':
                _logger.info('PAGO ACEPTADO')
                fact_id = int(reference.split('-')[1])
                factura = request.env['account.move'].sudo().search([('id','=',fact_id)])
                #Se revisa si ya hay un pago realizado para la factura recibida.
                if factura.invoice_payment_state == 'paid':
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
                                            'journal_id': 18,
                                            'payment_difference_handling': 'open',
                                            'writeoff_label': 'Write-Off',
                                        })]
                                        }
                    temp_payment = request.env['account.payment.group']
                    payment = temp_payment.sudo().create(payment_receipt_data)
                    payment.post()
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
                            'note': f"El cliente {factura.partner_id.name} ha realizado un pago repetido de la factura: {factura.name}, se acredito el pago con el nombre: {payment.name}."
                        }
                    )
                    post['pago_repetido'] = 'True'
                else:
                    _logger.info(f"FACTURA: {factura}")
                    #COSAS DE LA FOCA PARA SIMULAR MERCADOPAGO.
                    move_line = request.env['account.move.line'].sudo().search([('move_id','=',fact_id),('account_internal_type','=','receivable')])
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
                                                'journal_id': 18,
                                                'payment_difference_handling': 'open',
                                                'writeoff_label': 'Write-Off',
                                            })]
                                            }
                    temp_payment = request.env['account.payment.group']
                    payment = temp_payment.sudo().create(payment_receipt_data)
                    payment.write({'debt_move_line_ids': [(4,move_line.id)]})
                    payment.post()
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
                            'note': False
                        }
                    )
                    post['pago_repetido'] = 'False'
        #COSAS DE LA FOCA PARA SIMULAR MERCADOPAGO.
            elif post.get('collection_status') == 'pending':
                _logger.info('PAGO PENDIENTE')
            elif post.get('collection_status') == 'null':
                _logger.info('PAGO RECHAZADO')
            tx = request.env['payment.transaction'].sudo().search( [('reference', '=', reference)])
            txx = request.env['payment.transaction'].sudo().search([])
            _logger.info('TODAS LAS REFERENCIAS DE PAGO:  %s' % txx)
            print(request)
            _logger.info('mercadopago_validate_data() > payment.transaction founded: %s' % tx.reference)

        _logger.info('MercadoPago: validating data')
        #print "new_post:", new_post
        _logger.info('MercadoPago Post: %s' % post)

        if (tx):
            post.update( { 'external_reference': reference } )
            _logger.info('MercadoPago Post Updated: %s' % post)
            res = request.env['payment.transaction'].sudo().form_feedback( post, 'mercadopago')

        return post

    @http.route('/payment/mercadopago/ipn/', type='json', auth='none')
    def mercadopago_ipn(self, **post):
        """ MercadoPago IPN. """
        # recibimo algo como http://www.yoursite.com/notifications?topic=payment&id=identificador-de-la-operación
        #segun el topic: # luego se consulta con el "id"
        _logger.info('Beginning MercadoPago IPN form_feedback with post data %s', pprint.pformat(post))  # debug
        querys = parse.urlsplit(request.httprequest.url).query
        params = dict(parse.parse_qsl(querys))
        _logger.info(params)
        if (params and ('topic' in params or 'type' in params) and ('id' in params or 'data.id' in params)):
            self.mercadopago_validate_data( **params )
        else:
            self.mercadopago_validate_data(**post)
        return ''

    @http.route('/payment/mercadopago/dpn', type='http', auth="public")
    def mercadopago_dpn(self, **post):
        """ MercadoPago DPN """
        _logger.info('Beginning MercadoPago DPN form_feedback with post data %s', pprint.pformat(post))  # debug
        #return_url = self._get_return_url(**post)
        new_post = self.mercadopago_validate_data(**post)
        _logger.info(f'POST DE MERCADOPAGO: {new_post}')
        _logger.info(f'POST DE MERCADOPAGO: {new_post}')
        _logger.info(f'POST DE MERCADOPAGO: {new_post}')
        _logger.info(f'POST DE MERCADOPAGO: {new_post}')
        _logger.info(f'POST DE MERCADOPAGO: {new_post}')
        _logger.info(f'POST DE MERCADOPAGO: {new_post}')
        if post.get('collection_status') == 'approved':
            return_url = '/aceptado'
            if new_post.get('pago_repetido') == 'True':
                return_url = '/repetido'
        else:
            return_url = '/cancelado'
        return werkzeug.utils.redirect(return_url)

    @http.route('/payment/mercadopago/cancel', type='http', auth="public")
    def mercadopago_cancel(self, **post):
        """ When the user cancels its MercadoPago payment: GET on this route """
        _logger.info('Beginning MercadoPago cancel with post data %s', pprint.pformat(post))  # debug
        return_url = self._get_return_url(**post)
        status = post.get('collection_status')
        if status=='null':
            post['collection_status'] = 'cancelled'
        self.mercadopago_validate_data(**post)
        return werkzeug.utils.redirect(return_url)