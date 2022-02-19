# from odoo import models, fields, api
# from odoo.exceptions import UserError, ValidationError,AccessError
#
#
#
# class membership_form(models.Model):
#     _name = 'real.estate.membership.form'
#     _description = 'Real estate membership form'
#
#     # member_partner = fields.Many2one('res.partner', 'Partner', index=True, ondelete='cascade')
#     member_partner_id = fields.Many2one('res.partner', string='Customer', readonly=True)
#     # member_partner_name = fields.Char('Name', related='member_partner_id.name')
#     member_partner_name = fields.Char('Name', related='member_partner_id.name')
#     member_partner_street = fields.Char('Street', related='member_partner_id.street')
#     member_partner_phone = fields.Char('Phone', related='member_partner_id.phone')
#     member_partner_mobile = fields.Char('Mobile', related='member_partner_id.mobile')
#     member_partner_cnic = fields.Text('CNIC', related='member_partner_id.cnic_no')
#
#     kin_name = fields.Char(string='Next of kin', required=True)
#     kine_relationship = fields.Char(string='Relationship', required=True)
#     kin_cnic = fields.Char('CNIC no', copy=False, company_dependent=True)
#     kin_mobile = fields.Char(string='Mobile')
#     type = fields.Selection([('install', 'Installment'), ('lump_sum', 'Lump sum')])
#
#     installment_plan = fields.One2many('real.estate.installment.plan', 'membership_form_id', 'Installment plan', copy=True)
#     installment_type = fields.Selection([('yearly', 'Yearly'), ('monthly', 'Monthly')], string='Frequency')
#     installment_payment_type = fields.Selection([('down', 'Down Payment'), ('token', 'Token Money')], string='Payment method')
#     lump_sum_amount = fields.Float(string='Lump sum amount')
#     project_id = fields.Many2one(
#         'real.estate.project', 'Project')
#     building_id = fields.Many2one(
#         'real.estate.building', 'Building')
#     floor_id = fields.Many2one(
#         'real.estate.floor', 'Floor')
#     property_id = fields.Many2one(
#         'real.estate.property', 'Property')
#     property_value = fields.Float('Property Value', related='property_id.property_value')
#     installment_id = fields.One2many('real.estate.installment', 'membership_form_id')
#     first_installment_date = fields.Date(string='Installment due date')
#
#
#
#     @api.onchange('project_id')
#     def _onchange_project(self):
#         for rec in self:
#             return {'domain': {'building_id': [('real_estate_project', '=', rec.project_id.id)]}}
#
#     @api.onchange('building_id')
#     def _onchange_building(self):
#         for rec in self:
#             return {'domain': {'floor_id': [('real_estate_building', '=', rec.building_id.id)]}}
#
#     @api.onchange('floor_id')
#     def _onchange_floor(self):
#         for rec in self:
#             return {'domain': {'property_id': [('real_estate_floor', '=', rec.floor_id.id)]}}
#
#     @api.onchange('kin_cnic')
#     def add_validation(self):
#         if self.kin_cnic:
#             if len(self.kin_cnic) < 13:
#                 raise ValidationError('Invalid CNIC \n Enter 13 digit CNIC number')
#
#
#     @api.onchange('type')
#     def select_installment_plan(self):
#         if self.type == 'install':
#             print('from type install')
#             vals = {
#                 'property_id': self.property_id.id,
#                 'total_amount': self.property_id.property_value,
#                 'paid_installments': 0,
#                 'customer_id': self.member_partner_id.id,
#                 'frequency': self.installment_type,
#                 'down_payment': 12,
#                 'membership_form_id': self.id,
#                 'down_payment': (self.property_value * 40)/100,
#
#             }
#             try:
#                 self.installment_plan.sudo().create(vals)
#             except AccessError:
#                 print('create exception')
#
#     @api.onchange('installment_payment_type')
#     def generate_installment_schedule(self):
#         if self.installment_payment_type == 'down':
#             self.installment_plan.down_payment = (self.property_value * 40)/100
#             payment_residual = self.property_value - self.installment_plan.down_payment
#             single_installment = (payment_residual * 20 )/100
#             no_of_installments = payment_residual/single_installment
#             vals = {
#                 'property_id': self.property_id.id,
#                 'total_amount': self.property_id.property_value,
#                 'paid_installments': 0,
#                 'customer_id': self.member_partner_id.id,
#                 'frequency': self.installment_type,
#                 'down_payment': self.installment_plan.down_payment,
#                 'membership_form_id': self.id,
#                 'down_payment': (self.property_value * 40) / 100,
#                 'total_installments': no_of_installments,
#                 'single_installment_price': single_installment,
#
#             }
#             try:
#                 self.installment_plan.sudo().update(vals)
#             except AccessError:
#                 print('update exception')
#         if self.installment_payment_type == 'token':
#             print('token money')
#
#
#
#
#     @api.onchange('installment_payment_type')
#     def onchange_installment_payment_type(self):
#         print('onchange installment payment')
#
#
#
#
#
#
#
#
#
#
#
#
#
#
