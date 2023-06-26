# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import UserError

class bf_whatsapp_account_move(models.Model):
    _inherit = 'account.move'
    _description = 'Account move buttons'


    def whatsapp_wizard(self):
        view_id = self.env.ref('bf_whatsapp_base.create_message_view').id#Este dato lo sacamos de Ajustes/Tecnico/Vistas. Es el ID externo
        return {'type': 'ir.actions.act_window',#El type tiene que ser el mismo que usa el wizard (act_window)
                'name': _('Enviar factura por whatsapp'),#Nombre que va a tener el wizard.
                'res_model': 'bf.whatsapp.create.messages',#El modelo del wizard o de la vista (se lo puede sacar del codigo, es el campo _name="nombre")
                'target': 'new',#New para que se abra una nueva ventana (el wizard)
                'view_mode': 'form',#Modo de vista (formulario para el wizard)
                'views': [[view_id, 'form']],#El id externo de la vista que definimos en la variable mas arriba y el 'form' o tree segun necesitemos
                }