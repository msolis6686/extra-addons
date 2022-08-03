from odoo import models, api, fields, _
import mercadopago
import logging
from odoo.http import request
from werkzeug import urls

_logger = logging.getLogger(__name__)


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
    
    def mercadopago_form_generate_values(self):
        if self.env['ir.config_parameter'].sudo().get_param('mercadopago_external_reference', default='obj') == 'obj':
            external_reference = self._name
        else:
            external_reference = 'res.partner'
            
        #mercadopago_api_prod = "APP_USR-8145848978624836-070422-8745a8af5a55e7886380d86fa9cfcd3b-162428224"
        mercadopago_api = "TEST-8145848978624836-070422-40be156812b33426e211388d4070e80c-162428224"
        
        base_url = self.env["ir.config_parameter"].get_param("web.base.url")
        _logger.info("PREFERENCIAS mercado api %r"%mercadopago_api)
        if self.env['ir.config_parameter'].sudo().get_param('mercadopago_external_reference', default='obj') == 'obj':
            external_reference = self._name
        else:
            external_reference = 'res.partner'
        if self.env['ir.config_parameter'].sudo().get_param('mercadopago_sandbox', default=False):
            init_point = 'sandbox_init_point'
        else:
            init_point = 'init_point'
        for obj in self:
            if external_reference == 'res.partner':
                ref_id = self[self._mercadopago_partner_field].id
            else :
                ref_id = obj.id
            preference = {
                'external_reference': '%s-%s' % (external_reference, ref_id),
                'payer': obj.mercadopago_payer_dict(),
                "auto_return": "all",
                "back_urls": {
                    "success": urls.url_join(
                        base_url, "/mercadopago/notificacao/approved"
                    ),
                    "pending": urls.url_join(
                        base_url, "/mercadopago/notificacao/pending"
                    ),
                    "failure": urls.url_join(
                        base_url, "/mercadopago/notificacao/failure"
                    ),
                },
                'items': obj.mercadopago_items(),
            }

        mp = mercadopago.SDK(mercadopago_api)

        result = mp.preference().create(preference)

        url = result["response"]["init_point"]
        acquirer_reference = result["response"]["id"]
        
        vals = {
                    'date': '2022-07-07 02:01:23',
                    'acquirer_id': 13,
                    'type': 'form',
                    'state': 'draft',
                    'amount': 1.00,
                    'currency_id': 19,
                    "reference": '%s-%s' % (external_reference, ref_id),
                    "partner_id": 3,
                    "partner_name": "Administrador",
                    "partner_lang": "es_AR",
                    "partner_email": "guille@pon.com",
                    "partner_address": "aaa",
                    "partner_city": "buenos aires",
                    "partner_country_id": "10",
                    "partner_phone": "3123874",
                    "return_url": "/shop/payment/validate",
                    }
        #preference.update(obj.mercadopago_expires_dict())
        _logger.info("TRANSACTION TEST: %r"%vals)
        payment_transaction = self.env['payment.transaction'].create(vals)
        _logger.info("TRANSACTION ID: %r"%payment_transaction)
        
        
       
        payment_transaction_id = self.env["payment.transaction"].search(
            [("reference", "=", '%s-%s' % (external_reference, ref_id))]
        )

        payment_transaction_id.write(
            {"acquirer_reference": acquirer_reference}
        )
        if 'status' in result and result['status'] == 201:
            self.mercadopago_url = result[
                'response'][init_point]
            self.mercadopago_id = result['response']['id']
            _logger.info("EXITO %r"%self.mercadopago_url)
        _logger.info("PREFERENCIAS mercado api %r"%preference)
        _logger.info("PREFERENCIAS result %r"%result)
        _logger.info("PREFERENCIAS url %r"%url)
        _logger.info("PREFERENCIAS payment_transaction %r"%payment_transaction_id)
        
        
        return {
            "checkout_url": urls.url_join(
                base_url, "/mercadopago/checkout/redirect"
            ),
            "secure_url": url,
        }
    def mercadopago_create_preference(self):
        # preference api description
        # https://www.mercadopago.com.ar/developers/es/reference/preferences/_checkout_preferences/post/
        # to-do: add suport to back_urls expires
        mercadopago_client = self.env['ir.config_parameter'].get_param(
            'mercadopago_client', default=False)
        mercadopago_key = self.env['ir.config_parameter'].get_param(
            'mercadopago_key', default=False)
        mercadopago_api = self.env['ir.config_parameter'].get_param(
            'mercadopago_api', default=False)
        
        #mercadopago_api_prod = "APP_USR-8145848978624836-070422-8745a8af5a55e7886380d86fa9cfcd3b-162428224"
        
        mercadopago_api = "TEST-8145848978624836-070422-40be156812b33426e211388d4070e80c-162428224"
        
        
        base_url = self.env["ir.config_parameter"].get_param("web.base.url")

        _logger.info("PREFERENCIAS mercado api %r"%mercadopago_api)
        
        
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
                    "auto_return": "all",
                    "back_urls": {
                        "success": urls.url_join(
                            base_url, "/mercadopago/notificacao/approved"
                        ),
                        "pending": urls.url_join(
                            base_url, "/mercadopago/notificacao/pending"
                        ),
                        "failure": urls.url_join(
                            base_url, "/mercadopago/notificacao/failure"
                        ),
                    },
                }
                #preference.update(obj.mercadopago_expires_dict())
                _logger.info("preference %r"%preference)
                preferenceResult = sdk.preference().create(preference)


                vals = {
                    'date': '2022-07-07 02:01:23',
                    'acquirer_id': 13,
                    'type': 'form',
                    'state': 'draft',
                    'amount': 1.00,
                    'currency_id': 19,
                    "reference": ref_id,
                    "partner_id": "3",
                    "partner_name": "Administrador",
                    "partner_lang": "es_AR",
                    "partner_email": "guille@pon.com",
                    "partner_address": "aaa",
                    "partner_city": "buenos aires",
                    "partner_country_id": "10",
                    "partner_phone": "3123874",
                    "return_url": "/shop/payment/validate",
                    "payment_id": "",
                    }
                #preference.update(obj.mercadopago_expires_dict())
                _logger.info("TRANSACTION TEST: %r"%vals)
                payment_transaction = self.env['payment_transaction'].create(vals)
                _logger.info("TRANSACTION ID: %r"%payment_transaction)


                if 'status' in preferenceResult and preferenceResult['status'] == 201:
                    self.mercadopago_url = preferenceResult[
                        'response'][init_point]
                    self.mercadopago_id = preferenceResult['response']['id']
                    _logger.info("EXITO %r"%self.mercadopago_url)
                
                acquirer_reference = preferenceResult['response']['id']
       
                payment_transaction_id = self.env["payment.transaction"].search(
                    [("reference", "=", ref_id)]
                )

                payment_transaction_id.write(
                    {"acquirer_reference": acquirer_reference}
                )

        return {
                    "checkout_url": urls.url_join(
                        base_url, "/mercadopago/checkout/redirect"
                    ),
                    "secure_url": self.mercadopago_url,
                }
        
        #return True  # for xmlrcp
