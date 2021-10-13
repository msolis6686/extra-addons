# -*- coding: utf-8 -*-
from odoo import models, api, fields


class AccountMove(models.Model):
	_inherit = "account.move"

	def _get_tax_factor(self):
		tax_factor = (self.amount_untaxed / self.amount_total) or 1.0
		doc_letter = self.l10n_latam_document_type_id.l10n_ar_letter
		# if we receive B invoices, then we take out 21 of vat
	        # this use of case if when company is except on vat for eg.
		if tax_factor == 1.0 and doc_letter == 'B':
			tax_factor = 1.0 / 1.21
		return tax_factor

    #@api.multi
    #def get_taxes_values(self):
    #    """
    #    Hacemos esto para disponer de fecha de factura y cia para calcular
    #    impuesto con código python (por ej. para ARBA).
    #    Aparentemente no se puede cambiar el contexto a cosas que se llaman
    #    desde un onchange (ver https://github.com/odoo/odoo/issues/7472)
    #    entonces usamos este artilugio
   #     """
  #      date_invoice = self.date_invoice or fields.Date.context_today(self)
        # hacemos try porque al llamarse desde acciones de servidor da error
 #       try:
  #self.env.context.date_invoice = date_invoice
#            self.env.context.invoice_company = self.company_id
#        except Exception:
#            pass
 #       return super(AccountInvoice, self).get_taxes_values()
#
#
#
