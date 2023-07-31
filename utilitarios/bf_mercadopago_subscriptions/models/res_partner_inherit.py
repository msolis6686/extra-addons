# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class bf_mercadopago_subscriptions(models.Model):
    _inherit = 'res.partner'
    _description = 'Append subscriptions tiers to partners'

    subscription_type = fields.Many2one('bf.mercadopago.subscriptions', string='Tipo de Subscripcion:')
    mail_counter = fields.Integer(string='Intentos de Contacto', help='''Numero de correos de subscripcion enviados. Este numero vuelve a 0 si se confirma una 
        subscripción.''')
    subscription_confirmed = fields.Boolean(string='Subscripcion Confirmada')

    def compose_subscription_mercadopago(self):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
        """
        if not self.subscription_type:
            raise ValidationError('El cliente no tiene asignada una subscripción.')
        self.ensure_one()
        template = self.env.ref(
            'bf_mercadopago_subscriptions.email_template_mercadopago_subscription', False)
        if not template:
            template_id = False
        else:
            template_id = template.id
        compose_form = self.env.ref(
            'mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model='res.partner',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template_id,
            default_composition_mode='comment',
            #mark_invoice_as_sent=True,
        )
        self.mail_counter = self.mail_counter + 1
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    #Funcion para buscar, separar y mandar al wizard corresponsiente los partners que no tengan una subscripcion seleccionada
    def prepare_mass_subscription(self):
        found = []#Clientes que tienen subscripcion seleccionada
        not_found = []#Clientes que no tienen subscripcion seleccionada
        for partner in self:
            if partner.subscription_type:
                found.append(partner.id)
            else:
                not_found.append(partner.id)
        print(f"Encontrados: {found}, no encontrados: {not_found}")
        view_id = self.env.ref('bf_mercadopago_subscriptions.bf_mp_mass_subscription').id#Este dato lo sacamos de Ajustes/Tecnico/Vistas. Es el ID externo
        return {'type': 'ir.actions.act_window',#El type tiene que ser el mismo que usa el wizard (act_window)
                'name': _('Enviar Subscripciones'),#Nombre que va a tener el wizard.
                'res_model': 'mercadopago.mass.subscription',#El modelo del wizard o de la vista (se lo puede sacar del codigo, es el campo _name="nombre")
                'target': 'new',#New para que se abra una nueva ventana (el wizard)
                'view_mode': 'form',#Modo de vista (formulario para el wizard)
                'views': [[view_id, 'form']],#El id externo de la vista que definimos en la variable mas arriba y el 'form' o tree segun necesitemos
                'context': {'found': found, 'not_found': not_found}#Envio de contexto hacia el wizard
                }
    
    @api.onchange('subscription_confirmed')
    def reset_mail_counter(self):
        if self.subscription_confirmed == True:
            self.mail_counter = 0