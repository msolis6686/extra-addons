from odoo import tools,fields, models, api, _
from datetime import date
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero


class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'


    refund_method = fields.Selection(selection=[
            ('refund', 'Partial Refund'),
            ('cancel', 'Full Refund'),
            ('modify', 'Full refund and new draft invoice')
        ], string='Credit Method', required=True, default = 'refund',
        help='Choose how you want to credit this invoice. You cannot "modify" nor "cancel" if the invoice is already reconciled.')


