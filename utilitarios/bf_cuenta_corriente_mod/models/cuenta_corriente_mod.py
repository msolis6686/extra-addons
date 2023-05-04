# -*- coding: utf-8 -*-

from odoo import models, fields, _
from icecream import ic

class bf_cuenta_corriente_mod(models.Model):
    #_name = 'bf.cuenta.corriente'
    _inherit = 'res.partner'
    _description = 'Modulo para mostrar las cuentas corrientes de los clientes'

    debe_m = fields.Float(string="Debe", related="debe_c", default = 0.0, store=True)
    haber_m = fields.Float(string="Haber", related="haber_c", default = 0.0,  store=True)
    saldo_m = fields.Float(string="Saldo", related="saldo_c", default = 0.0, store=True)

    debe_c = fields.Float(compute='_get_debe_computed', default = 0.0, string="Debe")
    haber_c = fields.Float(compute='_get_haber_computed', default = 0.0, string="Haber")
    saldo_c = fields.Float(compute='_get_saldo_computed', default = 0.0, string="Saldo")
    
    def _get_debe_computed(self):
        for r in self:
            facturas = self.env['account.move'].search([('partner_id', '=', r.id),('state', '=', 'posted'),'|',('type', '=', 'out_invoice'),('type','=','out_refund')])
            total_debe = 0
            ##### AL ENCONTRAR UNA NOTA DE CREDITO, TOMA EL VALOR COMO NEGATIVO, SI LO QUERES RESTAR, LO SUMA (-*- = +)
            for x in facturas:
                total_debe = total_debe + x.amount_total_signed
            r.debe_c = total_debe
            diff = abs(r.debe_c - r.debe_m)
            """ if diff > 0.01: """
            vals = {'debe_m': r.debe_c}
            r.sudo().write(vals)
                #self.reload_page()
        self.reload_page()
        
    def _get_haber_computed(self):
        for r in self:
            payment = self.env['account.payment'].search([('partner_id', '=', r.id),('state', '=', 'posted'),('payment_type', '=', 'inbound')])
            total_haber = 0
            for x in payment:
                total_haber = total_haber + x.amount
            r.haber_c = total_haber
            diff = abs(r.haber_c - r.haber_m)
            """ if diff > 0.01: """
            vals = {'haber_m': r.haber_c}
            r.sudo().write(vals)
                #self.reload_page()
        self.reload_page()
        
    def _get_saldo_computed(self):
        for r in self:
            total_saldo = r.debe_m - r.haber_m
            r.saldo_c = total_saldo
            diff = abs(r.saldo_m - r.saldo_c)
            """ if diff >= 0.01: """
            new_value = round(r.saldo_c,2)
            vals = {'saldo_m': new_value}
            r.sudo().write(vals)
        self.reload_page()
        
    def action_show_invoices(self):
        invoices = self.env["account.move"].search([('partner_id', '=', self.id),('state', '=', 'posted'),'|',('type', '=', 'out_invoice'),('type','=','out_refund')])
        #for contract in self.contract_to_invoice_ids:
            #invoices |= contract.recurring_create_invoice()
        return {
            "type": "ir.actions.act_window",
            "name": _(f"Facturas de {self.name}"),
            "res_model": "account.move",
            "domain": [("id", "in", invoices.ids)],
            "view_mode": "tree,form",
            "context": self.env.context,
        }
              
    def action_show_payments(self):
        payments = self.env["account.payment.group"].search([('partner_id', '=', self.id),('state', '=', 'posted'),('partner_type','=','customer')])
        #for contract in self.contract_to_invoice_ids:
            #invoices |= contract.recurring_create_invoice()
        return {
            "type": "ir.actions.act_window",
            "name": _(f"Recibos de Pagos de {self.name}"),
            "res_model": "account.payment.group",
            "domain": [("id", "in", payments.ids)],
            "view_mode": "tree,form",
            "context": self.env.context,
        }
    
    #Funcion para que el boton llame directamente al wizard del partner statement
    def button_export_pdf(self):
        view_id = self.env.ref('partner_statement.activity_statement_wizard_view').id#Este dato lo sacamos de Ajustes/Tecnico/Vistas. Es el ID externo
        return {'type': 'ir.actions.act_window',#El type tiene que ser el mismo que usa el wizard (act_window)
                'name': _('Estado de la cuenta del cliente'),#Nombre que va a tener el wizard.
                'res_model': 'activity.statement.wizard',#El modelo del wizard o de la vista (se lo puede sacar del codigo, es el campo _name="nombre")
                'target': 'new',#New para que se abra una nueva ventana (el wizard)
                'view_mode': 'form',#Modo de vista (formulario para el wizard)
                'views': [[view_id, 'form']],#El id externo de la vista que definimos en la variable mas arriba y el 'form' o tree segun necesitemos
                }
    
    def reload_page(self):
        model_obj = self.env['ir.model.data']
        data_id = model_obj._get_id('bf_cuenta_corriente_mod', 'bf_cuenta_corriente_mod_view')
        view_id = model_obj.browse(data_id).res_id
        return {
            'type': 'ir.actions.act_window',
            'name': _('Cuenta corriente de clientes'),
            'res_model': 'bf_cuenta_corriente_mod',
            'view_type' : 'tree',
            'view_mode' : 'form',
            'view_id' : view_id,
            'target' : 'current',
            'nodestroy' : False,
        }