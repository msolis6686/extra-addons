from odoo import models, api, fields, _
from mercadopago import mercadopago
import logging

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
            'surname': partner_id.name,
            'email': partner_id.name,

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
        mercadopago_client = self.env['ir.config_parameter'].get_param(
            'mercadopago_client', default=False)
        mercadopago_key = self.env['ir.config_parameter'].get_param(
            'mercadopago_key', default=False)

        if self.env['ir.config_parameter'].sudo().get_param('mercadopago_external_reference', default='obj') == 'obj':
            external_reference = self._name
        else:
            external_reference = 'res.partner'

        if self.env['ir.config_parameter'].sudo().get_param('mercadopago_sandbox', default=False):
            init_point = 'sandbox_init_point'
        else:
            init_point = 'init_point'

        if mercadopago_client and mercadopago_key:
            mp = mercadopago.MP(mercadopago_client, mercadopago_key)

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
                }
                preference.update(obj.mercadopago_expires_dict())
                _logger.info("preference %r"%preference)
                preferenceResult = mp.create_preference(preference)

                if 'status' in preferenceResult and preferenceResult['status'] == 201:
                    self.mercadopago_url = preferenceResult[
                        'response'][init_point]
                    self.mercadopago_id = preferenceResult['response']['id']

        return True  # for xmlrcp
