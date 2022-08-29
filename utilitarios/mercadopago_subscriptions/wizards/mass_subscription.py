# -*- coding: utf-8 -*-

from odoo import models, fields, api


class mercadopago_mass_subscriptions(models.TransientModel):
    _name = 'mercadopago.mass.subscription'
    _description = 'Wizard para preparar el envio de correos de varias subscripciones.'

    def get_message(self):
        self.fill_wizard()
        return 'Cargando. . .'

    message = fields.Text(string='Atencion', default=get_message)
    clients_not_found = fields.Many2many('res.partner', string='Clientes sin Subscripcion', help='''Estos son clientes a los que no se 
        les va a enviar un mail ya que no tienen una subscripcion seleccionada.''')
    
    @api.onchange('message')
    def fill_wizard(self):
        found = self.env['res.partner'].search([('id','in',self.env.context['found'])])
        not_found = self.env['res.partner'].search([('id','in',self.env.context['not_found'])])
        self.clients_found = found
        self.clients_not_found = not_found
        self.message = f"Hay {len(not_found)} clientes sin una subscripcion asignada y no se les va a enviar un correo. Se los detalla mas abajo."
    
    def send_mass_subscriptions(self):
        found = self.env['res.partner'].search([('id','in',self.env.context['found'])])
        for partner in found:
            mail_template_id = self.env.ref('mercadopago_subscriptions.email_template_mercadopago_subscription').id
            mail_template = self.env['mail.template'].browse(mail_template_id)
            mail_template.send_mail(partner.id,force_send=True)
            notif_layout = self._context.get('custom_layout')