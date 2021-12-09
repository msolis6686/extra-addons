# -*- coding: utf-8 -*-

from odoo import models, fields, _

class bf_cuenta_corriente(models.Model):
    #_name = 'bf.cuenta.corriente'
    _inherit = 'res.partner'
    _description = 'Modulo para mostrar las cuentas corrientes de los clientes'

    debe = fields.Float(compute='_get_debe', string="Debe")
    haber = fields.Float(compute='_get_haber', string="Haber")
    saldo = fields.Float(compute='_get_saldo', string="Saldo")
    

    def _get_debe(self):
        for r in self:
            facturas = self.env['account.move'].search([('partner_id', '=', r.id),('state', '=', 'posted'),'|',('type', '=', 'out_invoice'),('type','=','out_refund')])
            total_debe = 0
            ##### AL ENCONTRAR UNA NOTA DE CREDITO, TOMA EL VALOR COMO NEGATIVO, SI LO QUERES RESTAR, LO SUMA (-*- = +)
            for x in facturas:
                total_debe = total_debe + x.amount_total_signed
            
            """ for x in facturas:
                if x.type == 'out_refund':
                    total_debe = total_debe - x.amount_total_signed
                else:
                    total_debe = total_debe + x.amount_total_signed """
            r.debe = total_debe

    def _get_haber(self):
        for r in self:
            payment = self.env['account.payment'].search([('partner_id', '=', r.id),('state', '=', 'posted')])
            total_haber = 0
            for x in payment:
                total_haber = total_haber + x.amount
            r.haber = total_haber

    def _get_saldo(self):
        for r in self:
            total_debe = r.debe - r.haber
            r.saldo = total_debe

    def action_show_invoices(self):
        invoices = self.env["account.move"].search([('partner_id', '=', self.id),('state', '=', 'posted'),'|',('type', '=', 'out_invoice'),('type','=','out_refund')])
        #for contract in self.contract_to_invoice_ids:
            #invoices |= contract.recurring_create_invoice()
        return {
            "type": "ir.actions.act_window",
            "name": _("Invoices"),
            "res_model": "account.move",
            "domain": [("id", "in", invoices.ids)],
            "view_mode": "tree,form",
            "context": self.env.context,
        }
              
    def action_show_payments(self):
        payments = self.env["account.payment"].search([('partner_id', '=', self.id),('state', '=', 'posted')])
        #for contract in self.contract_to_invoice_ids:
            #invoices |= contract.recurring_create_invoice()
        return {
            "type": "ir.actions.act_window",
            "name": _("Invoices"),
            "res_model": "account.payment",
            "domain": [("id", "in", payments.ids)],
            "view_mode": "tree,form",
            "context": self.env.context,
        }
