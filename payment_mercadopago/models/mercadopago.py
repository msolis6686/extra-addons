import re
import logging
import mercadopago

from odoo import api, fields, models
from odoo.http import request
from werkzeug import urls

_logger = logging.getLogger(__name__)
odoo_request = request


class MercadopagoBoleto(models.Model):
    _inherit = "payment.acquirer"
    provider = fields.Selection(
        selection_add=[("mercadopago", "Mercado Pago")]
    )
    mercadopago_public_key = fields.Char("Mercado Pago Public Key")
    mercadopago_access_token = fields.Char("Mercado Pago Access Token")

    def mercadopago_form_generate_values(self, values):
        """ Função para gerar HTML POST do mercadopago """
        base_url = (
            self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        )

        partner_id = values.get("billing_partner")
        commercial_partner_id = partner_id.commercial_partner_id

        items = [
            {
                "title": "Fatura Ref: %s" % values.get("reference"),
                "quantity": 1,
                "unit_price": int(values.get("amount")),
                "currency_id": "ARS",
            }
        ]

        payer = {
            "name": commercial_partner_id.name,
            "email": commercial_partner_id.email,
            "address": {
                "street_name": commercial_partner_id.street,
                "zip_code": commercial_partner_id.zip,
            },
        }

        preference = {
            "external_reference": values.get("reference"),
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
            "items": items,
            "payer": payer,
        }

        mp = mercadopago.SDK(self.mercadopago_access_token)

        result = mp.preference().create(preference)

        url = result["response"]["init_point"]
        acquirer_reference = result["response"]["id"]
       
        payment_transaction_id = self.env["payment.transaction"].search(
            [("reference", "=", values["reference"])]
        )

        payment_transaction_id.write(
            {"acquirer_reference": acquirer_reference}
        )

        return {
            "checkout_url": urls.url_join(
                base_url, "/mercadopago/checkout/redirect"
            ),
            "secure_url": url,
        }


class TransactionMercadopago(models.Model):
    _inherit = "payment.transaction"


    # ESTA FUNCIÓN HACE QUE ESCRIBA DONE A LA TRANSACCIÓN....
    
    #### FALTA DESCULAR DONDE SE GENERA EL TX .... 
    def _set_transaction_done(self):
        '''Move the transaction's payment to the done state(e.g. Paypal).'''
        allowed_states = ('draft', 'authorized', 'pending', 'error')
        target_state = 'done'
        (tx_to_process, tx_already_processed, tx_wrong_state) = self._filter_transaction_state(allowed_states, target_state)
        
        #_logger.warning('TRANSACTION DONE (ref: %s, target state: %s, previous state %s, expected previous states: %s)' % (tx.reference, target_state, tx.state, allowed_states))
        
        _logger.warning("TRANSACTION DONE TX PROCESSED %r"%tx_already_processed)
        
        
        
        for tx in tx_already_processed:
            _logger.info('Trying to write the same state twice on tx (ref: %s, state: %s' % (tx.reference, tx.state))
        for tx in tx_wrong_state:
            _logger.warning('Processed tx with abnormal state (ref: %s, target state: %s, previous state %s, expected previous states: %s)' % (tx.reference, target_state, tx.state, allowed_states))

        tx_to_process.write({
            'state': target_state,
            'date': fields.Datetime.now(),
            'state_message': '',
        })
    
    
    @api.model
    def _mercadopago_form_get_tx_from_data(self, data):
        acquirer_reference = data.get("preference_id")
        tx = self.search([("acquirer_reference", "=", acquirer_reference)])
        _logger.info("ACQUIRER REFERENCE %r"%acquirer_reference)
        _logger.info("TX FROM DATA %r"%tx[0])
        
        return tx[0]

    def _mercadopago_form_validate(self, data):
        status = data.get("status")
        
        _logger.info("ESTADO DEL PAGO %r"%status)
        
        if status in ("paid", "partially_paid", "approved", "authorized"):
            self._set_transaction_done()
            return True
        elif status == "pending":
            self._set_transaction_pending()
            return True
        else:
            self._set_transaction_cancel()
            return False
