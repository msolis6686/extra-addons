# from odoo import models, fields, api
# from odoo import _
# from odoo.exceptions import UserError, ValidationError
#
#
# class Installment_plan(models.Model):
#     _name = 'real.estate.installment.plan' #plan
#     _description = 'Real estate installment plan'
#     #
#     # property_id = fields.Many2one('real.estate.property', 'Property', index=True, ondelete='cascade') #_id correct
#     # total_installments = fields.Integer(string='Installment no')
#     # total_amount = fields.Float(string='Installment amount')
#     # paid_installments = fields.Integer(string='Payment status', default=0)
#     # customer_id = fields.Many2one('res.partner', 'Customer', index=True, ondelete='cascade')
#     # frequency = fields.Char(string='Installment type')
#     # down_payment = fields.Float(string='Down payment')
#     # single_installment_price = fields.Integer(string='Single installment Rs.', default=0)
#     #
#     #
#
#
#     contract_id = fields.Many2one('real.estate.contract', string='Installment plan', readonly=True)
#     installment_no = fields.Integer(string='Installment no')
#     amount = fields.Float(string='Amount')
#     payment_status = fields.Char(string='Status')
#
#
