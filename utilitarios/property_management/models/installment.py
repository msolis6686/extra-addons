from odoo import models, fields, api
from odoo import _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)



class AccountMove(models.Model):
    _inherit = 'account.move'

    property_id = fields.Many2one(
        'real.estate.property', 'Property', readonly=True, force_save=True)

    @api.depends('property_id')
    def name_get(self):
        result = []
        name = ' '
        for line in self:
            if line.property_id:
                name = line.property_id.project_name +'/'+line.property_id.name
                result.append((line.id, name))
            else:
                result.append((line.id, name))
            return result

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    payment_option = fields.Selection([('cheque','Cheque No'),('pay_order','Pay Order')])
    payment_reference = fields.Char('Payment Reference')

    def _create_payment_vals_from_wizard(self):
        payment_vals = {
            'date': self.payment_date,
            'amount': self.amount,
            'payment_type': self.payment_type,
            'partner_type': self.partner_type,
            'ref': self.communication,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'partner_bank_id': self.partner_bank_id.id,
            'payment_method_id': self.payment_method_id.id,
            'destination_account_id': self.line_ids[0].account_id.id,
            'payment_reference': self.payment_reference,
            'payment_option': self.payment_option
        }

        if not self.currency_id.is_zero(self.payment_difference) and self.payment_difference_handling == 'reconcile':
            payment_vals['write_off_line_vals'] = {
                'name': self.writeoff_label,
                'amount': self.payment_difference,
                'account_id': self.writeoff_account_id.id,
            }
        return payment_vals



class AccountPayment(models.Model):
    _inherit = 'account.payment'

    payment_option = fields.Selection([('cheque', 'Cheque No'), ('pay_order', 'Pay Order')])
    payment_reference = fields.Char('Payment Reference')

class Installment(models.Model):
    _name = 'real.estate.installment'
    _description = 'Real estate installment'

    name = fields.Char(related='contract_id.property_id.name')
    property_id = fields.Many2one(
        'real.estate.property', 'Property', readonly=True, force_save=True, rec_name='property')
    contract_id = fields.Many2one('real.estate.contract', string='Installments')
    installment_no = fields.Integer(string='Installment no')
    amount = fields.Float(string='Amount')
    payment_status = fields.Char(string='Status')
    frequency = fields.Char(string='Frequency')
    due_date = fields.Date(string='Installment due date')
    product_id = fields.Many2one('product.product', 'Installment product')
    move_id = fields.Many2one('account.move', string='Invoice', ondelete="cascade")
    installment_discount = fields.Float(default=0)
    invoice_status = fields.Boolean(default=False, string='invoice status')
    installment_type = fields.Char()
    receipt_type = fields.Char(default='invoice')
    profit_on_buyback = fields.Float()
    buyback_product = fields.Many2one('product.product', 'Product Variant')
    profit_buyback_product = fields.Many2one('product.product', 'Product Variant')

    def create_invoice_hx(self):
        invoice_type = ''
        """ Create invoice for fee payment process of student """
        inv_obj = self.env['account.move']
        partner_id = self.contract_id.contract_partner_id.id
        account_id = False
        product = self.product_id

        if product.property_account_income_id:
            account_id = product.property_account_income_id.id
        if not account_id:
            account_id = product.categ_id.property_account_income_categ_id.id
        if not account_id:
            raise UserError(
                _('There is no income account defined for this product: "%s".'
                  'You may have to install a chart of account from Accounting'
                  ' app, settings menu.') % product.name)
        if self.amount <= 0.00:
            raise UserError(
                _('The value of the deposit amount must be positive.'))
        else:
            amount = self.amount
            name = product.name

        installment_label = self.name + " (Installment " + str(self.installment_no) + ")"
        move_line_temp = {
            'name': installment_label,
            'price_unit': self.amount,
            'quantity': 1.0,
            'discount': 0.0,
            'product_uom_id': self.product_id.uom_id.id,
            'product_id': self.product_id.id,
        }
        if self.receipt_type == 'bill':
            invoice_type = 'in_invoice'
            move_line_profit_on_buyback = {
                'name': 'Profit on buyback',
                'price_unit': self.profit_on_buyback,
                'quantity': 1.0,
                'discount': 0.0,
                'product_uom_id': self.product_id.uom_id.id,
                'product_id': self.profit_buyback_product.id,
                # 'account_id': 37,
            }
            invoice = inv_obj.create({
                # 'partner_id': partner_id.name,
                'journal_id': self.env['account.journal'].search(args=[('code', '=', 'BILL')], limit=1).id,
                'move_type': invoice_type,
                'partner_id': partner_id,
                'invoice_date': datetime.today().date(),
                'invoice_date_due': self.due_date,
                'property_id': self.property_id.id,
                'invoice_line_ids': [(0, 0, move_line_temp), (0, 0, move_line_profit_on_buyback)]

            })
        if self.receipt_type == 'invoice':
            invoice_type = 'out_invoice'
            invoice = inv_obj.create({
                'journal_id': self.env['account.journal'].search(args=[('code', '=', 'INV')], limit=1).id,
                'move_type': invoice_type,
                'partner_id': partner_id,
                'invoice_date': datetime.today().date(),
                'property_id': self.property_id.id,
                'invoice_date_due': self.due_date,
                'invoice_line_ids': [(0, 0, move_line_temp)]

            })
        self.invoice_status = True
        self.move_id = invoice.id
        # invoice.write({})
        # invoice._compute_invoice_taxes_by_group()
        return invoice

    def view_invoice_hx(self):
        # print('view invoice')
        value = True
        if self.move_id:
            form_view = self.env.ref('account.view_move_form')
            tree_view = self.env.ref('account.view_invoice_tree')
            value = {
                'domain': str([('id', '=', self.move_id.id)]),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.move',
                'view_id': False,
                'views': [(form_view and form_view.id or False, 'form'),
                          (tree_view and tree_view.id or False, 'tree')],
                'type': 'ir.actions.act_window',
                'res_id': self.move_id.id,
                'target': 'current',
                'nodestroy': True
            }
        else:
            _logger.warning("Access error")
        return value
