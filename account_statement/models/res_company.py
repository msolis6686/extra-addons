# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class Company(models.Model):
    _inherit = 'res.company'
    
    send_statement = fields.Boolean("Send Customer Statement")
    period = fields.Selection([('monthly', 'Monthly'),('all', "All")],'Period',default='monthly')
    statement_days = fields.Integer("Statement Send Date")
    
    #overdue_days = fields.Integer("Overdue Statement Send Date")
    #send_overdue_statement = fields.Boolean("Send Overdue Customer Statement")

class AccountConfig(models.TransientModel):
    _inherit = "res.config.settings"
    
    send_statement = fields.Boolean(related='company_id.send_statement',string="Send Customer Statement",readonly=False)
    period = fields.Selection([('monthly', 'Monthly'),('all', "All")],'Period',related='company_id.period',readonly=False)
    statement_days = fields.Integer(related='company_id.statement_days',string="Statement Date",readonly=False)
    
    #overdue_days = fields.Integer(related='company_id.overdue_days',string="Overdue Date")
    #send_overdue_statement = fields.Boolean(related='company_id.send_overdue_statement',string="Send Overdue Customer Statement")
    
           
