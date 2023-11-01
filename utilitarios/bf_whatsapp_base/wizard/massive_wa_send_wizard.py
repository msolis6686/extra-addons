from odoo import models, fields, api, _
from odoo.exceptions import UserError

class BfMassiveWaSendWizard(models.TransientModel):
    _name = "bf.massive.wa.send.wizard"
    _description = "Massive Whats App Messages Wizard"

    wa_template = fields.Many2one(comodel_name="mail.template")
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
            raise UserError(_(f"Los siguientes clientes no tienen telefono de WhatsApp asignado: {no_wa_clients}"))
        self.error = False
        # RETURN A DOMAIN ACCORDING TO THE ACTIVE MODEL
        if not self.wa_template:
            model_id = self.env['ir.model'].search([('model', '=', self.env.context.get('active_model'))])
            if model_id:
                templates = self.env['mail.template'].search([('model_id', '=', model_id.id)])
                if templates:
                    return {'domain': {'wa_template': [('id', 'in', templates.ids)]}}

    def massive_prepare(self):
        to_create = self.env["whatsapp.wizard"]
        for id in self.env.context.get('active_ids'):
            current_data = self.env[self.env.context.get('active_model')].browse(id)
            """ data = dict(
                user_id=current_data.partner_id,
                #mobile_number=current_data.partner_id.wa_mobile,
                template_id=self.template_id
                #attachment=
            ) """
            temp_record = self.env["whatsapp.wizard"].create(
                {
                    'user_id': current_data.partner_id.id,
                    'template_id': self.wa_template.id
                }
            )
            temp_record.onchange_template_id(self.wa_template.id, self.env.context.get('active_model'), id)
            temp_record.prepare_messages()
            to_create = to_create + temp_record
        #for created in to_create:
        #    created.prepare_messages()