# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo.tools.float_utils import float_round as round
from odoo import api, fields, models, _
from datetime import datetime, time, date
from dateutil.relativedelta import relativedelta
from lxml import etree
import base64
import re
from odoo import tools
#import odoo.report
import calendar


class account_move(models.Model):
	
	_inherit = 'account.move'
	_order = 'invoice_date_due'
	
	def _get_result(self):
		for aml in self:
			aml.result = 0.0
			aml.result = aml.amount_total_signed - aml.credit_amount 

	def _get_credit(self):
		for aml in self:
			aml.credit_amount = 0.0
			aml.credit_amount = aml.amount_total_signed - aml.amount_residual_signed

	def _get_credit_custom(self):
		payment = self.env['account.payment'].search([('partner_id', '=', self.id),('state', '=', 'posted'),('payment_type', '=', 'inbound')])
		total_haber = 0
		for x in payment:
			total_haber = total_haber + x.amount
			#vals = {'haber_m': r.haber_c}
			#self.write(vals)


	credit_amount = fields.Float(compute ='_get_credit',   string="Credit/paid")
	result = fields.Float(compute ='_get_result',   string="Balance") #'balance' field is not the same


class Res_Partner(models.Model):
	_inherit = 'res.partner'
	
	#attachment_ids = fields.Many2many('ir.attachment', string='Attachments')

	def _get_amounts_and_date_amount(self):
		user_id = self._uid
		company = self.env['res.users'].browse(user_id).company_id
		
		current_date = datetime.now().date()

		for partner in self:
			partner.do_process_monthly_statement_filter()
			amount_due = amount_overdue = 0.0
			supplier_amount_due = supplier_amount_overdue = 0.0
			for aml in partner.balance_invoice_ids:
				if (aml.company_id == company):
					date_maturity = aml.invoice_date_due or aml.date
					amount_due += aml.result
				   
					if (date_maturity <= current_date):
						amount_overdue += aml.result
			partner.payment_amount_due_amt= amount_due
			partner.payment_amount_overdue_amt =  amount_overdue
			for aml in partner.supplier_invoice_ids:
				if (aml.company_id == company):
					date_maturity = aml.invoice_date_due or aml.date
					supplier_amount_due += aml.result
					if (date_maturity <= current_date):
						supplier_amount_overdue += aml.result
			partner.payment_amount_due_amt_supplier= supplier_amount_due
			partner.payment_amount_overdue_amt_supplier =  supplier_amount_overdue
			
			monthly_amount_due_amt = monthly_amount_overdue_amt = 0.0
			for aml in partner.monthly_statement_line_ids:
				date_maturity = aml.invoice_date_due
				monthly_amount_due_amt += aml.result
				if date_maturity and (date_maturity <= current_date):
					monthly_amount_overdue_amt += aml.result
			partner.monthly_payment_amount_due_amt = monthly_amount_due_amt
			
			partner.monthly_payment_amount_overdue_amt = monthly_amount_overdue_amt

			
	

	start_date = fields.Date('Start Date', compute='get_dates')
	month_name = fields.Char('Month', compute='get_dates')
	end_date = fields.Date('End Date', compute='get_dates')

	monthly_statement_line_ids = fields.One2many('monthly.statement.line', 'partner_id', 'Monthly Statement Lines')
	supplier_invoice_ids = fields.One2many('account.move', 'partner_id', 'Customer move lines', domain=[('type', 'in', ['in_invoice','in_refund']),('state', 'in', ['posted'])]) 
	balance_invoice_ids = fields.One2many('account.move', 'partner_id', 'Customer move lines', domain=[('type', 'in', ['out_invoice','out_refund']),('state', 'in', ['posted'])]) 
	
	payment_amount_due_amt=fields.Float(compute = '_get_amounts_and_date_amount', string="Balance Due")
	payment_amount_overdue_amt = fields.Float(compute='_get_amounts_and_date_amount',
												  string="Total Overdue Amount"  )
	payment_amount_due_amt_supplier=fields.Float(compute = '_get_amounts_and_date_amount', string="Supplier Balance Due")
	payment_amount_overdue_amt_supplier = fields.Float(compute='_get_amounts_and_date_amount',
												  string="Total Supplier Overdue Amount"  )
	
	monthly_payment_amount_due_amt = fields.Float(compute='_get_amounts_and_date_amount', string="Balance Due")
	monthly_payment_amount_overdue_amt = fields.Float(compute='_get_amounts_and_date_amount',
												  string="Total Overdue Amount")                                                  
	current_date = fields.Date(default=fields.date.today())

	first_thirty_day = fields.Float(string="0-30",compute="compute_days")
	thirty_sixty_days = fields.Float(string="30-60",compute="compute_days")
	sixty_ninty_days = fields.Float(string="60-90",compute="compute_days")
	ninty_plus_days = fields.Float(string="90+",compute="compute_days")
	total = fields.Float(string="Total",compute="compute_total")

	def get_dates(self):
		for record in self:
			today = date.today()
			d = today - relativedelta(months=1)

			start_date = date(d.year, d.month,1)
			end_date = date(today.year, today.month,1) - relativedelta(days=1)
			
			record.month_name = calendar.month_name[start_date.month] or False
			record.start_date = str(start_date) or False
			record.end_date = str(end_date) or False

	@api.depends('balance_invoice_ids')
	def compute_days(self):
		today = fields.date.today()
		for partner in self:
			partner.first_thirty_day = 0
			partner.thirty_sixty_days = 0
			partner.sixty_ninty_days = 0
			partner.ninty_plus_days = 0
			if partner.balance_invoice_ids :
				for line in partner.balance_invoice_ids :				
					diff = today- line.invoice_date_due
					if diff.days <= 30 and diff.days > 0:
						partner.first_thirty_day = partner.first_thirty_day + line.result
					elif diff.days > 30 and diff.days<=60:
						partner.thirty_sixty_days = partner.thirty_sixty_days + line.result
					elif diff.days > 60 and diff.days<=90:
						partner.sixty_ninty_days = partner.sixty_ninty_days + line.result
					else:
						if diff.days > 90  :
							partner.ninty_plus_days = partner.ninty_plus_days + line.result
		return

	@api.depends('ninty_plus_days','sixty_ninty_days','thirty_sixty_days','first_thirty_day')
	def compute_total(self):
		for partner in self:
			partner.total = 0.0
			partner.total = partner.ninty_plus_days + partner.sixty_ninty_days + partner.thirty_sixty_days + partner.first_thirty_day
		return	

	def _cron_send_customer_statement(self):
		partners = self.env['res.partner'].search([])
		# partner_search_mode = self.env.context.get('res_partner_search_mode')
		# if partner_search_mode == 'customer':
		if self.env.user.company_id.period == 'monthly':
			partners.do_process_monthly_statement_filter()
			partners.customer_monthly_send_mail()
		else:
			partners.customer_send_mail()
		return True

	def customer_monthly_send_mail(self):
		unknown_mails = 0
		for partner in self:
			partners_to_email = [child for child in partner.child_ids if child.type == 'invoice' and child.email]
			if not partners_to_email and partner.email:
				partners_to_email = [partner]
			if partners_to_email:
				for partner_to_email in partners_to_email:
					mail_template_id = self.env['ir.model.data'].xmlid_to_object('account_statement.email_template_customer_monthly_statement')
					if mail_template_id:
						mail_template_id.send_mail(partner_to_email.id)
				if partner not in partner_to_email:
					self.message_post([partner.id], body=_('Customer Monthly Statement email sent to %s' % ', '.join(['%s <%s>' % (partner.name, partner.email) for partner in partners_to_email])))
		return unknown_mails

	def do_process_monthly_statement_filter(self):
		account_invoice_obj = self.env['account.move']
		account_payment_obj = self.env['account.payment']
		statement_line_obj = self.env['monthly.statement.line']
		for record in self: 
			today = date.today()
			d = today - relativedelta(months=1)

			start_date = date(d.year, d.month,1)
			end_date = date(today.year, today.month,1) - relativedelta(days=1)
			
			from_date = str(start_date)
			to_date = str(end_date)
			
			domain = [('type', 'in', ['out_invoice','out_refund']), ('state', 'in', ['posted']), ('partner_id', '=', record.id)]
			if from_date:
				domain.append(('invoice_date', '>=', from_date))
			if to_date:
				domain.append(('invoice_date', '<=', to_date))
			lines_to_be_delete = statement_line_obj.search([('partner_id', '=', record.id)])
			lines_to_be_delete.unlink()
			invoices = account_invoice_obj.search(domain)
			for invoice in invoices.sorted(key=lambda r: r.name):
				vals = {
						'partner_id':invoice.partner_id.id or False,
						'state':invoice.state or False,
						'invoice_date':invoice.invoice_date,
						'invoice_date_due':invoice.invoice_date_due,
						'result':invoice.result or 0.0,
						'name':invoice.name or '',
						'amount_total':invoice.amount_total or 0.0,
						'credit_amount':invoice.credit_amount or 0.0,
						'invoice_id' : invoice.id,
					}
				ob = statement_line_obj.create(vals) 
			
			""" #AGREGO TODOS LOS PAGOS DEL CLIENTE
			domain = [('partner_id', '=', record.id),('state', '=', 'posted'),('payment_type', '=', 'inbound')]
			if from_date:
				domain.append(('payment_date', '>=', from_date))
			if to_date:
				domain.append(('payment_date', '<=', to_date))
			payment = account_payment_obj.search(domain)
			for pay in payment.sorted(key=lambda r: r.name):
				vals = {
						'partner_id':pay.partner_id.id or False,
						'state':pay.state or False,
						'invoice_date':pay.payment_date,
						'invoice_date_due': False,
						'result': False,
						'name':pay.name or '',
						'amount_total':False,
						'credit_amount':pay.amount or 0.0,
						#'invoice_id' : pay.id,
					}
				ob = statement_line_obj.create(vals)  """
   
   
	def customer_send_mail(self):
		unknown_mails = 0
		for partner in self:
			partners_to_email = [child for child in partner.child_ids if child.type == 'invoice' and child.email]
			if not partners_to_email and partner.email:
				partners_to_email = [partner]
			if partners_to_email:
				for partner_to_email in partners_to_email:
					mail_template_id = self.env['ir.model.data'].xmlid_to_object('account_statement.email_template_customer_statement')
					mail_template_id.send_mail(partner_to_email.id)
				if partner not in partner_to_email:
					self.message_post([partner.id], body=_('Customer Statement email sent to %s' % ', '.join(['%s <%s>' % (partner.name, partner.email) for partner in partners_to_email])))
		return unknown_mails
	
	def supplier_send_mail(self):
		unknown_mails = 0
		for partner in self:
			partners_to_email = [child for child in partner.child_ids if child.type == 'invoice' and child.email]
			if not partners_to_email and partner.email:
				partners_to_email = [partner]
			if partners_to_email:
				for partner_to_email in partners_to_email:
					mail_template_id = self.env['ir.model.data'].xmlid_to_object('account_statement.email_template_supplier_statement')
					mail_template_id.send_mail(partner_to_email.id)
				#if partner not in partner_to_email:
					#self.message_post([partner.id], body=_('Customer Statement email sent to %s' % ', '.join(['%s <%s>' % (partner.name, partner.email) for partner in partners_to_email])))
		return unknown_mails
	

	def do_button_print_statement(self):
		return self.env.ref('account_statement.report_customert_print').report_action(self)
		
	def do_button_print_statement_vendor(self) : 
		return self.env.ref('account_statement.report_supplier_print').report_action(self)