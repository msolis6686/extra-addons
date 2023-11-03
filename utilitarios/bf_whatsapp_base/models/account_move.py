# -*- coding: utf-8 -*-
from odoo import models, _
from odoo.exceptions import ValidationError

class bf_whatsapp_account_move(models.Model):
    _inherit = 'account.move'
    _description = 'Account move buttons'

    def invoice_whatsapp(self):
        record_phone = self.partner_id.wa_mobile
        if not record_phone:
            raise ValidationError("El socio no tiene un numero de celular definido.")
        if not record_phone[0] == "+":
            raise ValidationError("El socio no tiene bien configurado el codigo del pais en el telefono.")
        else:
            return {'type': 'ir.actions.act_window',
                    'name': _('Mensaje de WhatsApp'),
                    'res_model': 'whatsapp.wizard',
                    'target': 'new',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'context': {
                        'default_template_id': self.env.ref('bf_whatsapp_base.whatsapp_invoice_template').id},
                    }
