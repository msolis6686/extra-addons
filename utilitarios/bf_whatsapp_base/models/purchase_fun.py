from odoo import models, fields, api, _
import urllib.parse as parse
from odoo.exceptions import ValidationError

class PurchaseOrderModule(models.Model):
    _inherit = 'purchase.order'

    def purchase_whatsapp(self):
        record_phone = self.partner_id.wa_mobile
        if not record_phone:
            raise ValidationError("El socio no tiene un número de celular")
        if not record_phone[0] == "+":
            raise ValidationError("El socio no tiene bien configurado el codigo del pais en el telefono.")
        else:
            return {'type': 'ir.actions.act_window',
                    'name': _('Whatsapp Message'),
                    'res_model': 'whatsapp.wizard',
                    'target': 'new',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'context': {
                        'default_template_id': self.env.ref('bf_whatsapp_base.whatsapp_purchase_template').id},
                    }