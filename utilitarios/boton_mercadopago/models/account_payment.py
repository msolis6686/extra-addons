from odoo import models, api, fields
import mercadopago
import logging

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    mercadopago_id = fields.Char(
        'MercadoPago Id',
    )

    @api.model
    def mercadopago_search_payment(self):
        mercadopago_client = self.env['ir.config_parameter'].get_param(
            'mercadopago_client', default=False)
        mercadopago_key = self.env['ir.config_parameter'].get_param(
            'mercadopago_key', default=False)

        if mercadopago_client and mercadopago_key:

            mp = mercadopago.SDK.payment(mercadopago_client,
                                mercadopago_key)
            filters = {
                "range": "date_created",
                "begin_date": "NOW-1MONTH",
                "end_date": "NOW",
                "status": "approved",
            }
            journal_id = int(self.env['ir.config_parameter'].get_param(
                'mercadopago_journal_id', default=False))
            searchResult = mp.search_payment(filters, 0, 100)
            for result in searchResult["response"]["results"]:
                #_logger.info(result)
                #model, res_id =result['external_reference'].split('-')
                res_id = '11'
                model = 'res.partner'
                if model == 'res.partner':
                    partner_id = self.env['res.partner'].browse(int(res_id))
                else:
                    partner_id = self.env[model].browse(
                        res_id)[self.env[model]._mercadopago_partner_field]

                exist = self.search(
                    [('mercadopago_id', '=', result['authorization_code'])])
                if not len(exist):
                    payment = {
                        'communication': result['authorization_code'],
                        'mercadopago_id': result['authorization_code'],
                        'partner_type': 'customer',
                        'payment_type': 'inbound',
                        'partner_id': partner_id.id,
                        'journal_id': journal_id,
                        'payment_date': result['money_release_date'][:10],
                        'amount': result['transaction_amount'],
                        'payment_method_id': self.env.ref('payment.account_payment_method_electronic_in').id
                    }
                    payment_id = self.create(payment)
                    payment_id.post()
                    if model != 'res.partner':
                        self.env[model].search([('id','=',int(res_id))]).mercadopago_payment_receipt(payment_id,result)
