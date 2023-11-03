from odoo import models, _
from odoo.exceptions import ValidationError

class InventoryTransferDone(models.Model):
    _inherit = 'stock.picking'

    def inventory_whatsapp(self):
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
                        'default_template_id': self.env.ref('bf_whatsapp_base.whatsapp_inventory_template').id},
                    }