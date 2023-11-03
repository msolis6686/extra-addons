from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class BfMassiveWaSendWizard(models.TransientModel):
    _name = "bf.massive.wa.send.wizard"
    _description = "Massive Whats App Messages Wizard"
<<<<<<< HEAD
    
    
    def get_default_wa_template(self):
        template = self.get_whatsapp_template()
        if template:
            return template
    
    wa_template = fields.Many2one(comodel_name="bf.whatsapp.templates", default=get_default_wa_template)
=======

    wa_template = fields.Many2one(comodel_name="mail.template")
>>>>>>> origin/dev_wa
    error = fields.Boolean(default=True)

    @api.onchange("wa_template")
    def check_for_errors(self):
        no_wa_clients = ""
        record_active_ids = self.env.context.get('active_ids')
        res_partners = self.env['account.move'].search([
                ('id', 'in', record_active_ids)
            ]).mapped("partner_id")
        for partner in res_partners:
            if not partner.wa_mobile:
                #if partner.l10n_latam_identification_type_id.name != "Sigd":
                no_wa_clients = no_wa_clients + partner.name + ", "
        if len(no_wa_clients) > 1:
            # Remove the ", " in the error message.
            no_wa_clients = no_wa_clients[:-2]
<<<<<<< HEAD
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
=======
            raise UserError(
                    _("Los siguientes clientes no tienen telefono de WhatsApp" 
                        f"asignado: {no_wa_clients}")
                )
        # RETURN A DOMAIN ACCORDING TO THE ACTIVE MODEL
        if not self.wa_template:
            model_id = self.env['ir.model'].search([
                    ('model', '=', self.env.context.get('active_model'))
                ])
            if model_id:
                templates = self.env['mail.template'].search([
                        ('model_id', '=', model_id.id),
                        ('is_wa_template', '=', True),
                    ])
                if templates:
                    self.error = False
                    return {'domain': {'wa_template': [('id', 'in', templates.ids)]}}
                else:
                    raise UserError(
                            _("No se pudo encontrar ninguna plantilla para el "
                                f"modelo '{model_id.name},' puede crear una "
                                "en el modulo de WhatsApp->Plantillas->Crear"
                                " y en el campo 'Aplica a' seleccione: "
                                f"{model_id.name}.")
                            )
        else:
            if self.wa_template.model_id.model != self.env.context.get('active_model'):
                raise UserError("La plantilla seleccionada no es " 
                                f"aplicable para el modelo activo.")
            else:
                self.error = False


    def massive_prepare(self):
        for id in self.env.context.get('active_ids'):
            current_data = self.env[self.env.context.get('active_model')].browse(id)
            temp_record = self.env["whatsapp.wizard"].create(
                {
                    'user_id': current_data.partner_id.id,
                    'template_id': self.wa_template.id
                }
            )
            temp_record.with_context(active_id=id).onchange_template_id_wrapper()
            temp_record.prepare_messages()
>>>>>>> origin/dev_wa
