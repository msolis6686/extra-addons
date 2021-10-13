# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, _, fields, api, tools
from odoo.exceptions import UserError,ValidationError
from odoo.tools.safe_eval import safe_eval
import datetime


class AccountCheck(models.Model):
        _inherit = 'account.check'

        payment_date = fields.Date(readonly=True,states={'draft': [('readonly', False)],'holding': [('readonly', False)]},index=True,)


class AccountPadron(models.Model):
	_name = 'account.padron'
	_description = 'account.padron'

	date_from = fields.Date('Fecha Desde')
	date_to = fields.Date('Fecha Hasta')
	cuit = fields.Char('CUIT',index=True)
	tax = fields.Char('Impuesto')
	percent = fields.Float('Porcentaje')

class ResPartnerPerception(models.Model):
	_name = "res.partner.perception"
	_description = "Perception Defined in Partner"

	tax_id = fields.Many2one('account.tax',string='Impuesto',required=True)
	percent = fields.Float('Percent', required=True)
	date_from = fields.Date('Fecha Desde')
	partner_id = fields.Many2one('res.partner', 'Cliente')

class ResPartner(models.Model):
        _name = "res.partner"
        _inherit = "res.partner"

        @api.model
        def update_percepciones(self):
            partners = self.env['res.partner'].search([])
            for partner in partners:
                for perception in partner.perception_ids:
                    perception.unlink()
                padron_ids = self.env['account.padron'].search([('cuit','=',partner.vat)])
                for padron in padron_ids:
                    tax_id = self.env['account.tax'].search([('padron_prefix','=',padron.tax)])
                    if not tax_id:
                        raise ValidationError('Impuesto no determinado %s'%(padron.tax))
                    perception_ids = self.env['res.partner.perception'].search([('partner_id','=',partner.id),('tax_id','=',tax_id.id)],order='date_from desc')
                    #perception_id = None
                    #for perception in perception_ids:
                    #    if perception.date_from > padron.date_from:
                    #        perception_id = perception_id
                    if not perception_ids:
                        vals = {'partner_id': partner.id,'percent': padron.percent,'tax_id': tax_id.id,'date_from': padron.date_from}
                        perception_id = self.env['res.partner.perception'].create(vals)

        def partner_update_percepciones(self):
            self.ensure_one()
            for partner in self:
                for perception in partner.perception_ids:
                    perception.unlink()
                padron_ids = self.env['account.padron'].search([('cuit','=',partner.vat)],order='date_from desc')
                for padron in padron_ids:
                    tax_id = self.env['account.tax'].search([('padron_prefix','=',padron.tax)])
                    if not tax_id:
                        raise ValidationError('Impuesto no determinado %s'%(padron.tax))
                    perception_ids = self.env['res.partner.perception'].search([('partner_id','=',partner.id),('tax_id','=',tax_id.id)])
                    #for perception in perception_ids:
                    #    if perception.date_from < padron.date_from:
                    #        perception_id = perception
                    if not perception_ids:
                        vals = {'partner_id': partner.id,'percent': padron.percent,'tax_id': tax_id.id,'date_from': padron.date_from}
                        perception_id = self.env['res.partner.perception'].create(vals)
                    #else:
                    #    perception_id.write({'percent': padron.percent,'date_from': padron.date_from})





#        			padron_ids = self.env['account.padron'].search([('cuit','=',partner.vat)],order='id desc')
#        			for padron in padron_ids:
#        				if padron.tax == 'RET_IIBB_AGIP':
#                                            tax_id = self.env['account.tax'].browse(32)
#        				else:
#                                            tax_id = self.env['account.tax'].search([('padron_prefix','=',padron.tax)])
#        				#perception_id = self.env['res.partner.perception'].search([('partner_id','=',partner.id),('tax_id','=',tax_id.id),('date_from','=>',str(padron.date_from))])
#        				perception_ids = self.env['res.partner.perception'].search([('partner_id','=',partner.id),('tax_id','=',tax_id.id)])
#        				perception_id = None
#        				for perception_id in perception_ids:
#        				if not perception_id:
#        					vals = {'partner_id': partner.id,'percent': padron.percent,'tax_id': tax_id.id,'date_from': padron.date_from}
#        					perception_id = self.env['res.partner.perception'].create(vals)

        perception_ids = fields.One2many('res.partner.perception', 'partner_id', 'Percepciones Definidas')


class AccountMove(models.Model):
        _inherit = "account.move"
        

        def compute_taxes(self):
            self.ensure_one()
            if self.state == 'draft':
                if self.type in ['out_invoice','out_refund']:
                    for move_tax in self.move_tax_ids:
                        move_tax.unlink()
                    if self.partner_id.perception_ids:
                        for perception in self.partner_id.perception_ids:
                            if perception.tax_id.type_tax_use != 'sale':
                                continue
                            for invoice_line in self.invoice_line_ids:
                                if perception.tax_id.id not in invoice_line.tax_ids.ids:
                                    invoice_line.tax_ids = [(4,perception.tax_id.id)] 
                    for invoice_line in self.invoice_line_ids:
                        if invoice_line.tax_ids:
                            for tax in invoice_line.tax_ids.ids:
                                account_tax = self.env['account.tax'].browse(tax)
                                move_tax_id = self.env['account.move.tax'].search([('move_id','=',self.id),('tax_id','=',tax)])
                                if not move_tax_id:
                                    vals = {
                                            'move_id': self.id,
                                            'tax_id': tax
                                            }
                                    move_tax_id = self.env['account.move.tax'].create(vals)
                                move_tax_id.base_amount = move_tax_id.base_amount + invoice_line.price_subtotal
                                tax_id = self.env['account.tax'].browse(tax)
                                if not tax_id.is_padron:
                                    move_tax_id.tax_amount = move_tax_id.tax_amount + invoice_line.price_subtotal * (account_tax.amount / 100)
                                else:
                                    amount = 0
                                    for perception in self.partner_id.perception_ids:
                                        if perception.tax_id.id == tax_id.id:
                                            amount = perception.percent
                                    move_tax_id.tax_amount = move_tax_id.tax_amount + invoice_line.price_subtotal * (amount / 100)




"""
        @api.depends(
                'line_ids.debit',
                'line_ids.credit',
                'line_ids.currency_id',
                'line_ids.amount_currency',
                'line_ids.amount_residual',
                'line_ids.amount_residual_currency',
                'move_tax_ids',
                'line_ids.payment_id.state')
        def _compute_amount(self):
            res = super(AccountMove, self)._compute_amount()
            for move in self:
                if move.is_invoice(include_receipts=True):
                    if move.move_tax_ids:
                        amount_total = move.amount_untaxed
                        amount_residual = move.amount_untaxed
                        if move.amount_residual_signed < 0:
                            sign = -1
                        else:
                            sign = 1
                        for move_tax in move.move_tax_ids:
                            amount_total = amount_total + move_tax.tax_amount
                            amount_residual = amount_residual + move_tax.tax_amount
                        move.amount_total = amount_total
                        move.amount_residual = amount_residual
                        move.amount_residual_signed = amount_residual * sign
            return res


        def compute_taxes(self):
            if self.state == 'draft':
                if self.type in ['out_invoice','out_refund']:
                    for move_tax in self.move_tax_ids:
                        move_tax.unlink()
                    for invoice_line in self.invoice_line_ids:
                        if invoice_line.tax_ids:
                            for tax in invoice_line.tax_ids.ids:
                                account_tax = self.env['account.tax'].browse(tax)
                                move_tax_id = self.env['account.move.tax'].search([('move_id','=',self.id),('tax_id','=',tax)])
                                if not move_tax_id:
                                    vals = {
                                            'move_id': self.id,
                                            'tax_id': tax
                                            }
                                    move_tax_id = self.env['account.move.tax'].create(vals)
                                move_tax_id.base_amount = move_tax_id.base_amount + invoice_line.price_subtotal
                                move_tax_id.tax_amount = move_tax_id.tax_amount + invoice_line.price_subtotal * (account_tax.amount / 100)
                if self.partner_id.perception_ids:
                    for perception in self.partner_id.perception_ids:
                            if perception.percent > 0:
                                vals = {
                                        'tax_id': perception.tax_id.id,
                                        'base_amount': self.amount_untaxed_signed,
                                        'tax_amount': self.amount_untaxed_signed * (perception.percent / 100),
                                        'move_id': self.id}
                                move_tax_id = self.env['account.move.tax'].create(vals)


        @api.multi
        def compute_taxes(self):
        	account_invoice_tax = self.env['account.invoice.tax']
	        ctx = dict(self._context)
	        for invoice in self:
        	    # Delete non-manual tax lines
	            self._cr.execute("DELETE FROM account_invoice_tax WHERE invoice_id=%s AND manual is False", (invoice.id,))
        	    if self._cr.rowcount:
                	self.invalidate_cache()

	            # Generate one tax line per tax, however many invoice lines it's applied to
        	    tax_grouped = invoice.get_taxes_values()

	            # Create new tax lines
        	    for tax in tax_grouped.values():
                	account_invoice_tax.create(tax)

        	    if invoice.type in ['out_invoice','out_refund']:
        	    	if invoice.partner_id.perception_ids:
        	    		for perception in invoice.partner_id.perception_ids:
        	    			if perception.percent > 0:
        	    				vals = {'name': perception.tax_id.name,'tax_id': perception.tax_id.id,'account_id': perception.tax_id.account_id.id,'base': invoice.amount_untaxed,'amount': invoice.amount_untaxed * (perception.percent / 100),'invoice_id': invoice.id,'sequence': 100,'account_analytic_id': False,'manual': False}
        	    				account_invoice_tax.create(vals)

	        # dummy write on self to trigger recomputations
        	return self.with_context(ctx).write({'invoice_line_ids': []})
"""
