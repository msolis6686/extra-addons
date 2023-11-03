from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleOrderValidation(models.Model):
    _inherit = 'res.partner'

    def contact_whatsapp(self):
        record_phone = self.wa_mobile
        if not record_phone[0] == "+":
            raise ValidationError("El socio no tiene bien configurado el codigo del pais en el telefono.")
        else:
            return {'type': 'ir.actions.act_window',
                    'name': _('Whatsapp Message'),
                    'res_model': 'whatsapp.wizard.contact',
                    'target': 'new',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'context': {
                        'default_template_id': self.env.ref('bf_whatsapp_base.whatsapp_contacts_template').id},
                    }