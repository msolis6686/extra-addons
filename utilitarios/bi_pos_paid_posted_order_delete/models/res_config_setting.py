# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class ResConfigSettings_Inherit(models.TransientModel):
	_inherit = 'res.config.settings'

	delete_paid_order = fields.Boolean('Delete POS Order',related="company_id.delete_paid_order",readonly=False)
	
	set_paid_delete_order = fields.Selection([
        ('without_code', 'Delete POS Order Without Code'),
        ('with_code', 'Delete POS order with Code')
        ], string="POS Pricelists",related="company_id.set_paid_delete_order",readonly=False)

	code = fields.Char(
	    string='Code',related="company_id.code",readonly=False, 
	)


class Res_company_inherit(models.Model):
	_inherit = 'res.company'

	delete_paid_order = fields.Boolean('Apply POS Commission')
	set_paid_delete_order = fields.Selection([
        ('without_code', 'Delete POS Order Without Code'),
        ('with_code', 'Delete POS order with Code')
        ], string="POS Pricelists",default='without_code')


	code = fields.Char(
	    string='Code',
	)