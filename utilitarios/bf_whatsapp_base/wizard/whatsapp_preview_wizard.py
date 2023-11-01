from odoo import models, fields, api


class BfWhatsAppBaseWizardPreview(models.TransientModel):
    _name = "bf.whats.app.base.wizard.preview"
    _description = "Whats App Message Preview Wizard"

    wa_template_id = fields.Many2one(comodel_name="mail.template")
    text_preview = fields.Html()

    @api.onchange('wa_template_id')
    def generate_wa_preview(self):
        if self.wa_template_id:
            self.text_preview = self.env['ir.qweb']._render('bf_whatsapp_base.template_message_preview', {
                    'body': self.wa_template_id.body_html._get_formatted_body(demo_fallback=True),
                    #'buttons': self.wa_template_id.button_ids,
                    'header_type': 'none',
                    #'footer_text': record.wa_template_id.footer_text,
                    #'language_direction': 'rtl' if record.wa_template_id.lang_code in ('ar', 'he', 'fa', 'ur') else 'ltr',
                })