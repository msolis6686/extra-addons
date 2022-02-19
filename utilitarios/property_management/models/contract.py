from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError, AccessError
from datetime import datetime
from dateutil import relativedelta
import logging
from datetime import date, timedelta

_logger = logging.getLogger(__name__)

class contract(models.Model):
    _name = 'real.estate.contract'
    _rec_name = 'contract_partner_name' # changes the name above edit and create button
    _description = 'Real estate contract'

    dealer_id = fields.Many2one('res.partner', string='Customer')
    dealer_name = fields.Char('Name', related='dealer_id.name', force_save=True)
    dealer_street = fields.Char('Street', related='dealer_id.street')
    dealer_phone = fields.Char('Phone', related='dealer_id.phone')
    dealer_mobile = fields.Char('Mobile', related='dealer_id.mobile')
    dealer_email = fields.Char('Email', related='dealer_id.email')



    contract_partner_id = fields.Many2one('res.partner', string='Customer')
    contract_partner_image_1920 = fields.Image(related='contract_partner_id.image_1920',store=True)
    contract_partner_name = fields.Char('Name', related='contract_partner_id.name', force_save=True)
    contract_partner_street = fields.Char('Street', related='contract_partner_id.street')
    contract_partner_phone = fields.Char('Phone', related='contract_partner_id.phone')
    contract_partner_mobile = fields.Char('Mobile', related='contract_partner_id.mobile')
    contract_partner_cnic = fields.Char('CNIC', related='contract_partner_id.cnic_no')
    contract_type = fields.Selection([('buy', 'Buy Back'), ('sell','Sell')])
    # contract_type = fields.Selection([('sell','Sell')])

    kin_name = fields.Char(string='Next of kin')
    kine_relationship = fields.Char(string='Relationship',)
    kin_cnic = fields.Char('CNIC no', copy=False, company_dependent=True)
    kin_mobile = fields.Char(string='Mobile')
    payment_plan_type = fields.Selection([('lump_sum', 'Lump sum'),
                                          ('install_down', 'Installment + Down Payment'),
                                          ('install', 'Installment'),])
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('active', 'Active'),
        ('inactive', 'Closed')
    ], string='State', readonly=True, default='draft')
    # installment_id = fields.One2many('real.estate.installment', 'contract_id', 'Installment plan', copy=True)
    frequency = fields.Selection([('monthly', 'Monthly'), ('quarterly', 'Quarterly')], string='Frequency')
    lump_sum_amount = fields.Float(string='Lump sum amount')
    down_payment = fields.Float('Down Payment', store=True)
    down_payment_amt = fields.Float(store=True)
    project_id = fields.Many2one(
        'real.estate.project', 'Project')
    building_id = fields.Many2one(
        'real.estate.building', 'Building')
    floor_id = fields.Many2one(
        'real.estate.floor', 'Floor')
    property_id = fields.Many2one(
        'real.estate.property', 'Property')
    property_value = fields.Float('Property Value', related='property_id.property_value')
    property_name = fields.Char('Property Name', related='property_id.name')
    installment_id = fields.One2many('real.estate.installment', 'contract_id')
    first_installment_date = fields.Date(string='First Installment due date')
    down_payment_date = fields.Date(string='Down payment due date')
    total_payment_date = fields.Date(string='Payment due date')
    total_installments = fields.Integer('Total installments')
    installment_product_id = fields.Many2one('product.product', string='Installment Product', readonly=False)
    token_money_product_id = fields.Many2one('product.product', string='Token money Product', readonly=False)
    down_payment_product_id = fields.Many2one('product.product', string='Down payment Product', readonly=False)
    buyback_product_id = fields.Many2one('product.product', string='Buyback Product', readonly=False)
    generate_installment_plan = fields.Boolean(default=False)
    buy_back_type = fields.Selection([('payback_full', 'Full Payment'),('payback_installments', 'Installments')])
    # buy_back_type = fields.Selection([('payback_full', 'Full Payment'), ('payback_installments', 'Installments'),
    #                                   ('payback_property_adjust','Adjust payment in other properties'), ('payback_payment_and_property','Partial payment and partial adjustment in property')])
    down_payment_type = fields.Selection([('lumpsum', 'Lumpsum'),('percentage', 'Percentage')])
    discount_hx = fields.Float('discount')
    amt_after_disc = fields.Float('Amount after discount',store=True, compute='_compute_amt_after_disc')
    buy_back_bill_due_date = fields.Date()
    contract_active = fields.Boolean(default=True)
    profit_on_buyback = fields.Float('Profit')
    buy_back_value = fields.Float()
    total_installments_buyback = fields.Integer()
    profit_on_buyback_product = fields.Many2one('product.product', string='Buyback Product', readonly=False)
    adjustment_property_id = fields.Many2one(
        'real.estate.property', 'Property for adjustment ')
    check_buyback_selection = fields.Boolean()
    check_readonly = fields.Boolean()
    effective_date = fields.Date(string='Effective date')
    total_without_down_payment = fields.Float(string='Installments Balance')
    resale_value = fields.Float()
    contract_date = fields.Date(default=fields.Date.context_today)

    @api.constrains('total_installments')
    def _check_total_installments_value(self):
        if self.total_installments < 1 and self.contract_type=='sell':
            raise UserError(
                    'Total Installments should be greater than 0')
    def unlink(self):
        for c in self:
            if c.state in ('confirm', 'active'):
                raise UserError(
                    'You cannot delete a confirmed or active contract')
        return super(contract, self).unlink()

    def action_balance_installments(self):
        installments = self.env['real.estate.installment'].search(args=[('contract_id', '=', self.id)])
        temp = 0
        for i in installments:
            temp = temp + i.amount
        if temp != self.amt_after_disc:
            raise UserError('Sum of installments must be equal')

    def action_confirm(self):
        self.state = 'confirm'

    def action_active(self):
        if self.generate_installment_plan is False:
            raise UserError('Generate installment plan before confirming contract')
        else:
            self.state = 'active'

    def action_inactive(self):
        return {
            'name': _("Select Property Status"),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'select.property.status',
            'view_id': self.env.ref('Property management.select_property_status_view_form').id,
            'target': 'new',
            'context': {
                'default_property_id': self.property_id.id,
                'default_contract_id': self.id,
            }}

    def _compute_amt_after_disc(self):
        for line in self:
            line.amt_after_disc = line.property_value - line.discount_hx
            if line.discount_hx:
                line.amt_after_disc = line.property_value - line.discount_hx
            else:
                line.amt_after_disc = line.property_value
            if line.down_payment !=0:
                if line.resale_value > 0:
                    line.total_without_down_payment = line.amt_after_disc - line.down_payment + line.resale_value
                else:
                    line.total_without_down_payment = line.amt_after_disc - line.down_payment

    @api.onchange('contract_type')
    def onchange_contract_type(self):
        if self.contract_type == 'buy':
            self.check_buyback_selection = True
            results = self.env['real.estate.property'].search([('status', '=', 'booked')])
            select_contract_type = True
            property_list = []
            for property in results:
                property_list.append(property.id)
            res = {}
            res['domain'] = {'property_id': [('id', 'in', property_list)]}
            return res
        if self.contract_type == 'sell':
            self.check_buyback_selection = False

    @api.onchange('property_value')
    def onchange_property_value(self):
        self.amt_after_disc = self.property_value - self.discount_hx

    @api.onchange('buy_back_type')
    def onchange_buy_back_type(self):
        if self.buy_back_type == 'payback_property_adjust':
            for rec in self:
                return {'domain': {'adjustment_property_id': [('owned_by', '=', rec.contract_partner_id.id),
                                                              ('id', '!=', rec.property_id.id)]}}
        if self.buy_back_type == 'payback_payment_and_property':
            for rec in self:
                return {'domain': {'adjustment_property_id': [('owned_by', '=', rec.contract_partner_id.id),
                                                              ('id', '!=', rec.property_id.id)]}}

    @api.onchange('floor_id')
    def onchange_floor_filter(self):
        results = ''
        select_contract_type = False
        if self.contract_type == 'sell':
            results = self.env['real.estate.property'].search([('status','=','available'),('floor_id','=',self.floor_id.id)])
            select_contract_type = True
            property_list = []
            for property in results:
                property_list.append(property.id)
            res = {}
            res['domain'] = {'property_id': [('id', 'in', property_list)]}
            return res
        if self.contract_type == 'buy':
            results = self.env['real.estate.property'].search([('status', '=', 'booked')])
            select_contract_type = True
            property_list = []
            for property in results:
                property_list.append(property.id)
            res = {}
            res['domain'] = {'property_id': [('id', 'in', property_list)]}
            return res

        # if self.contract_type is not 'sell' or 'buy':
        #     raise ValidationError('Select contract type')


    # Will be used project dropdown is required

    # @api.onchange('project_id')
    # def onchange_project(self):
    #     for rec in self:
    #         return {'domain': {'building_id': [('real_estate_project', '=', rec.project_id.id)]}}

    @api.onchange('building_id')
    def onchange_building(self):
        for rec in self:
            return {'domain': {'floor_id': [('real_estate_building', '=', rec.building_id.id)]}}

    @api.onchange('floor_id')
    def onchange_floor(self):
        for rec in self:
            if self.contract_type == 'sell':
                return {'domain': {'property_id': [('real_estate_floor', '=', rec.floor_id.id)]}}

    @api.onchange('property_id')
    def onchange_property(self):
        if self.contract_type == 'buy':
            self.check_buyback_selection = False
            self.check_readonly = True
            for line in self:
                line.floor_id = line.property_id.real_estate_floor.id
                line.building_id = line.property_id.real_estate_floor.real_estate_building.id
                line.project_id = line.property_id.real_estate_floor.real_estate_building.real_estate_project.id


    @api.onchange('kin_cnic')
    def add_validation(self):
        if self.kin_cnic:
            if len(self.kin_cnic) < 13:
                raise ValidationError('Invalid CNIC \n Enter 13 digit CNIC number')

    @api.onchange('down_payment_amt')
    def generate_down_payment(self):
        if self.down_payment_type == 'lumpsum':
            if self.down_payment_amt <= self.amt_after_disc:
                self.down_payment = self.down_payment_amt
            elif self.down_payment_amt < 0:
                raise ValidationError('Down payment is less than 0')
            else:
                raise ValidationError('Down payment is greater than Property Value')

        if self.down_payment_type == 'percentage':
            if self.down_payment_amt > 100:
                raise ValidationError('Down payment  percentage is greater than 100')
            elif self.down_payment_amt < 0:
                raise ValidationError('Down payment  percentage is less than 0')
            else:
                down_payment = (self.amt_after_disc * self.down_payment_amt) / 100
                self.down_payment = down_payment
        self.total_without_down_payment = self.amt_after_disc - self.down_payment
        if self.resale_value >0:
            self.total_without_down_payment = self.total_without_down_payment + self.resale_value

    @api.onchange('discount_hx')
    def generate_amt_after_discount(self):
        self._compute_amt_after_disc()

    def populate_installments(self):
        if not self.property_id:
            raise UserError('Select property first.')
        if self.resale_value > 0:
            self.amt_after_disc = self.amt_after_disc + self.resale_value
        self.property_id.owned_by = self.contract_partner_id.id
        if self.payment_plan_type == 'lump_sum':
            vals = {
                'installment_no': 1,
                'amount': self.amt_after_disc,
                'due_date': self.total_payment_date,
                'frequency': 'One time',
                'contract_id': self.id,
                'product_id': self.installment_product_id.id,
                'property_id': self.property_id.id,

            }
            try:
                self.installment_id.sudo().create(vals)
            except AccessError:
                _logger.warning("Access error")

        if self.payment_plan_type == 'install_down':
            amount_residual = (self.amt_after_disc - self.down_payment)
            single_installment = (amount_residual / self.total_installments)
            single_installment = round(single_installment,2)
            next_installment = self.first_installment_date
            var = self.total_installments-1
            last_installment = (amount_residual - (single_installment * var))
            # self.total_without_down_payment = amount_residual

            # Down payment installment generation
            down_vals = {
                'amount': self.down_payment,
                'due_date': self.down_payment_date,
                'frequency': 'one time',
                'contract_id': self.id,
                'product_id': self.down_payment_product_id.id,
                'property_id': self.property_id.id,
            }
            self.installment_id.sudo().create(down_vals)

            # Installments generation
            if self.frequency == 'monthly':
                for i in range(self.total_installments-1):
                    vals = {
                        'installment_no': i+1,
                        'amount': single_installment,
                        'due_date': next_installment,
                        'frequency': self.frequency,
                        'contract_id': self.id,
                        'product_id': self.installment_product_id.id,
                        'property_id': self.property_id.id,
                    }
                    next_installment = next_installment + relativedelta.relativedelta(months=1)
                    try:
                        self.installment_id.sudo().create(vals)
                    except AccessError:
                        _logger.warning("Access error")
                # next_installment = next_installment + relativedelta.relativedelta(months=1)
                last_installment_vals = {
                    'installment_no': self.total_installments,
                    'amount': last_installment,
                    'due_date': next_installment,
                    'frequency': self.frequency,
                    'contract_id': self.id,
                    'product_id': self.installment_product_id.id,
                    'property_id': self.property_id.id,
                }
                try:
                    self.installment_id.sudo().create(last_installment_vals)
                except AccessError:
                    _logger.warning("Access error")

            if self.frequency == 'quarterly':
                for i in range(self.total_installments-1):
                    vals = {
                        'installment_no': i+1,
                        'amount': single_installment,
                        'due_date': next_installment,
                        'frequency': self.frequency,
                        'contract_id': self.id,
                        'product_id': self.installment_product_id.id,
                        'property_id': self.property_id.id,
                    }
                    next_installment = next_installment + relativedelta.relativedelta(months=3)
                    try:
                        self.installment_id.sudo().create(vals)
                    except AccessError:
                        _logger.warning("Access error")
                # next_installment = next_installment + relativedelta.relativedelta(months=3)
                vals = {
                    'installment_no': self.total_installments,
                    'amount': last_installment,
                    'due_date': next_installment,
                    'frequency': self.frequency,
                    'contract_id': self.id,
                    'product_id': self.installment_product_id.id,
                    'property_id': self.property_id.id,
                }
                try:
                    self.installment_id.sudo().create(vals)
                except AccessError:
                    _logger.warning("Access error")

        self.property_id.update({
            'status': 'booked',
        })
        self.generate_installment_plan = True

        if self.payment_plan_type == 'install':
            single_installment = self.amt_after_disc / self.total_installments
            single_installment = round(single_installment,2)
            next_installment = self.first_installment_date
            var = self.total_installments - 1
            last_installment = (self.amt_after_disc - (single_installment * var))
            if self.frequency == 'monthly':
                for i in range(self.total_installments-1):
                    vals = {
                        'installment_no': i + 1,
                        'amount': single_installment,
                        'due_date': next_installment,
                        'frequency': self.frequency,
                        'contract_id': self.id,
                        'product_id': self.installment_product_id.id,
                        'property_id': self.property_id.id,
                    }
                    next_installment = next_installment + relativedelta.relativedelta(months=1)
                    try:
                        self.installment_id.sudo().create(vals)
                    except AccessError:
                        _logger.warning("Access error")
                # next_installment = next_installment + relativedelta.relativedelta(months=1)
                vals = {
                    'installment_no': self.total_installments,
                    'amount': last_installment,
                    'due_date': next_installment,
                    'frequency': self.frequency,
                    'contract_id': self.id,
                    'product_id': self.installment_product_id.id,
                    'property_id': self.property_id.id,
                }
                try:
                    self.installment_id.sudo().create(vals)
                except AccessError:
                    _logger.warning("Access error")
            if self.frequency == 'quarterly':
                for i in range(self.total_installments-1):
                    # next_installment = next_installment + relativedelta.relativedelta(months=3)
                    vals = {
                        'installment_no': i + 1,
                        'amount': single_installment,
                        'due_date': next_installment,
                        'frequency': self.frequency,
                        'contract_id': self.id,
                        'product_id': self.installment_product_id.id,
                        'property_id': self.property_id.id,
                    }
                    next_installment = next_installment + relativedelta.relativedelta(months=3)
                    try:
                        self.installment_id.sudo().create(vals)
                    except AccessError:
                        _logger.warning("Access error")
                # next_installment = next_installment + relativedelta.relativedelta(months=3)
                vals = {
                    'installment_no': self.total_installments,
                    'amount': last_installment,
                    'due_date': next_installment,
                    'frequency': self.frequency,
                    'contract_id': self.id,
                    'product_id': self.installment_product_id.id,
                    'property_id': self.property_id.id,
                }
                try:
                    self.installment_id.sudo().create(vals)
                except AccessError:
                    _logger.warning("Access error")

    def Populate_plan(self):
        temp = 0
        contracts = self.env['real.estate.contract'].search(
            [('property_id', '=', self.property_id.id), ('contract_type', '=', 'sell'),('contract_active', '=', True)])
        installments = self.env['real.estate.installment'].search([('contract_id', '=', contracts.id)])
        for i in installments:
            if i.move_id.payment_state == 'paid':
                temp = temp + i.move_id.amount_total
            if i.move_id.payment_state == 'partial':
                partial_payment = i.move_id.amount_total - i.move_id.amount_residual
                temp = temp + partial_payment
        self.buy_back_value = temp
        if self.buy_back_value > 0:
            if self.buy_back_type == 'payback_full':
                vals = {
                    'installment_no': 1,
                    'amount': self.buy_back_value,
                    'due_date': self.buy_back_bill_due_date,
                    'frequency': 'one-time',
                    'contract_id': self.id,
                    'receipt_type': 'bill',
                    'product_id': self.buyback_product_id.id,
                    'profit_on_buyback': self.profit_on_buyback,
                    'property_id': self.property_id.id,
                }
                try:
                    self.installment_id.sudo().create(vals)
                except AccessError:
                    _logger.warning("Access error")
            if self.buy_back_type == 'payback_installments':
                single_installment = self.buy_back_value / self.total_installments_buyback
                single_installment = round(single_installment, 2)
                single_profit_installment = self.profit_on_buyback / self.total_installments_buyback
                single_profit_installment = round(single_profit_installment, 2)
                # next_installment = self.first_installment_date
                # if self.frequency == 'monthly':
                for i in range(self.total_installments_buyback):
                    # next_installment = next_installment + relativedelta.relativedelta(months=1)
                    vals = {
                        'installment_no': i + 1,
                        'amount': single_installment,
                        # 'payment_status': 'Unpaid',
                        # 'due_date': next_installment,
                        # 'frequency': self.frequency,
                        'receipt_type': 'bill',
                        'contract_id': self.id,
                        'product_id': self.buyback_product_id.id,
                        'profit_on_buyback': single_profit_installment,
                        'property_id': self.property_id.id,
                    }
                    try:
                        self.installment_id.sudo().create(vals)
                    except AccessError:
                        _logger.warning("Access error")
            self.property_id.update({
                'status': 'available',
            })
        else:
            raise UserError('Invoices not created')

    def view_invoice_hx(self):
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



class SelectPropertyStatus(models.TransientModel):
    _name = 'select.property.status'

    property_id = fields.Many2one(
        'real.estate.property', 'Property', readonly=True, force_save=True)
    contract_id = fields.Many2one(
        'real.estate.contract', 'Contract', readonly=True, force_save=True)
    status = fields.Selection([('booked', 'Booked'), ('available', 'Available'),
                               ('rented', 'Rented'), ('sold', 'Sold'), ('legal_issue', 'Legal Issue')])

    def action_apply(self):
        self.property_id.update({
                    'status': self.status,
                })
        self.contract_id.update({
            'state': 'inactive',
        })