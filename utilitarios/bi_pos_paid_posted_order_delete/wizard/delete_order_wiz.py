# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models,fields,api,_
from datetime import datetime
from odoo.exceptions import UserError, ValidationError

class PosOrders(models.TransientModel):
	_name = 'pos.order.delete'


	validate_pin = fields.Char(
		string='Enter Code',
	)

	set_paid_delete_order = fields.Selection([
		('without_code', 'Delete POS Order Without Code'),
		('with_code', 'Delete POS order with Code')
		], string="POS Pricelists",related="company_id.set_paid_delete_order",readonly=False)
	company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)

	def call_delete_order(self,record):
		if record.state == 'done':
			for payment in record.payment_ids:

				draft_moves = self.env['account.move'].search([('ref', '=', record.session_id.name)])
				for journal_entry in draft_moves:
					journal_entry.button_draft()
					MoveLine = journal_entry.with_context(check_move_validity=False).line_ids
					for line in MoveLine:
						if payment.payment_method_id.cash_journal_id.id == line.journal_id.id:
							if line.credit >= payment.amount:
								line.credit -= payment.amount
							elif line.debit >= payment.amount:
								line.debit -= payment.amount
						else:
							if line.account_internal_type == 'receivable':
								if payment.payment_method_id.name in line.name:
									if record.config_id.journal_id.id == line.journal_id.id:
										if line.debit >= payment.amount :
											line.debit -= payment.amount
										elif line.credit >= payment.amount:
											line.credit -= payment.amount
							elif line.account_internal_type == 'other':
								if line.credit >= payment.amount:
									line.credit -= payment.amount
								elif line.debit >= payment.amount:
									line.debit -= payment.amount
								
					journal_entry.action_post()
		

		if record.state == 'invoiced':
			draft_moves = self.env['account.move'].search([('ref', '=', record.name)])
			for journal_entry in draft_moves:
				journal_entry.button_draft()
				journal_entry.button_cancel()

			draft_moves_entry = self.env['account.move'].search([('ref', '=', record.session_id.name)])
			moves_lines = self.env['account.move.line'].search([('name', '=', record.session_id.name)])

			for journal_entry in draft_moves_entry:
				journal_entry.button_draft()
				MoveLine = journal_entry.with_context(check_move_validity=False).line_ids
				for payment in record.payment_ids:
					for line in MoveLine:
						
						if line.account_internal_type == 'receivable':
							if line.partner_id:
								record_float = float("{:.2f}".format(record.amount_paid))
								if record.partner_id.parent_id:
									if line.partner_id.id == record.partner_id.parent_id.id:
										if line.debit >= record_float:
											line.debit -= record_float
										elif line.credit >= record_float:
											line.credit -= record_float
								else:
									if line.partner_id.id == record.partner_id.id:
										if line.debit >= record_float:
											line.debit -= record_float
										elif line.credit >= record_float:
											line.credit -= record.amount_paid
							elif payment.payment_method_id.name in line.name:
								format_float = float("{:.2f}".format(payment.amount))
								if line.debit >= format_float :
									line.debit -= format_float
								elif line.credit >= format_float:
									line.credit -= format_float

				journal_entry.action_post()
		
		record.action_pos_order_cancel()
		if record.picking_id:
			picking = self.env['stock.picking'].search([('name','=',record.picking_id.name)])
			for pick in picking.move_ids_without_package:
				pick.write({'state':'draft'})
			picking.action_cancel()
			picking.unlink()

		if record.payment_ids:
			for statement in record.payment_ids:
				statement.unlink()
		record.unlink()


	def delete_order(self):
		delete_paid_order = self.env.user.company_id.delete_paid_order
		active_ids = self.env['pos.order'].browse(self._context.get('active_ids'))
		if delete_paid_order == False:
			raise ValidationError("You Can't Delete order Please contact administrator")
		else:
			set_paid_delete_order = self.env.user.company_id.set_paid_delete_order
			code = self.env.user.company_id.code
			for i in self._context.get('active_ids'):
				if set_paid_delete_order == 'without_code':
					record = self.env['pos.order'].browse(i)
					if record:
						self.call_delete_order(record)		
				else:
					if self.validate_pin == code:
						record = self.env['pos.order'].browse(i)
						if record:
							self.call_delete_order(record)
					else:
						raise ValidationError("Enter Code Invalid")
								