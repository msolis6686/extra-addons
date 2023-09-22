from odoo import models, fields, api, _
from odoo.exceptions import UserError

class BfMassiveWaSendWizard(models.TransientModel):
    _name = "bf.massive.wa.send.wizard"
    _description = "Massive Whats App Messages Wizard"
    
    
    def get_default_wa_template(self):
        template = self.get_whatsapp_template()
        if template:
            return template
    
    wa_template = fields.Many2one(comodel_name="bf.whatsapp.templates", default=get_default_wa_template)
    error = fields.Boolean(default=True)

    @api.onchange("wa_template")
    def check_for_errors(self):
        no_wa_clients = ""
        record_active_ids = self.env.context.get('active_ids')
        res_partners = self.env['account.move'].search([('id', 'in', record_active_ids)]).mapped("partner_id")
        for partner in res_partners:
            if not partner.wa_mobile:
                if partner.l10n_latam_identification_type_id.name != "Sigd":
                    no_wa_clients = no_wa_clients + partner.name + ", "
        if len(no_wa_clients) > 1:
            # Remove the ", " in the error message.
            no_wa_clients = no_wa_clients[:-2]
            raise UserError(_(f"Los siguientes contactos no tienen un número de WhatsApp asignado: {no_wa_clients}"))
        self.error = False

    def massive_prepare(self):
        to_create = self.env['bf.whatsapp.create.messages'].create({
            'template_id': self.wa_template.id
        })
        to_create.prepare_messages()
    
    def get_whatsapp_template(self):
        context_model = self._context.get('active_model')
        if context_model:
            wa_template = self.env['bf.whatsapp.templates'].search([('model', '=', context_model)], limit=1)
            if wa_template:
                return wa_template.id