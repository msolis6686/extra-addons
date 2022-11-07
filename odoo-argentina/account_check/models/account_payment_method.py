# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import UserError


class AccountPaymentMethod(models.Model):
    _inherit = "account.payment.method"


    @api.model
    def _get_payment_method_information(self):
        """
        Contains details about how to initialize a payment method with the code x.
        The contained info are:
            mode: Either unique if we only want one of them at a single time (payment acquirers for example)
                   or multi if we want the method on each journal fitting the domain.
            domain: The domain defining the eligible journals.
            currency_id: The id of the currency necessary on the journal (or company) for it to be eligible.
            country_id: The id of the country needed on the company for it to be eligible.
            hidden: If set to true, the method will not be automatically added to the journal,
                    and will not be selectable by the user.
        """
        return {
            'manual': {'mode': 'multi', 'domain': [('type', 'in', ('bank', 'cash'))]},
            'received_third_check': {'mode': 'multi', 'domain': [('type', 'in', ('bank', 'cash'))]},
            'delivered_third_check': {'mode': 'multi', 'domain': [('type', 'in', ('bank', 'cash'))]},
            'issue_check': {'mode': 'multi', 'domain': [('type', 'in', ('bank', 'cash'))]},
        }



