from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import html2text
from odoo.tools.safe_eval import safe_eval
#import urllib.parse as parse

#import os
#import re
import base64
import logging

_logger = logging.getLogger(__name__)


class SendMessage(models.TransientModel):
    _name = 'whatsapp.wizard'
    _description = 'WhatsApp Message Wizard'

    user_id = fields.Many2one('res.partner', string="Recipient Name", default=lambda self: self.env[self._context.get('active_model')].browse(self.env.context.get('active_ids')).partner_id)
    mobile_number = fields.Char()
    message = fields.Text(string="Message")
    model = fields.Char('mail.template.model_id')
    template_id = fields.Many2one('mail.template', 'Use template', index=True)
    attachment = fields.Many2many(comodel_name='ir.attachment')

    @api.onchange('template_id')
    def onchange_template_id_wrapper(self):
        self.ensure_one()
        res_id = self._context.get('active_id') or 1
        values = self.onchange_template_id(self.template_id.id, self.model, res_id)['value']
        for fname, value in values.items():
            setattr(self, fname, value)

    @api.onchange('user_id')
    def get_partner_number(self):
        if self.user_id.wa_mobile:
            self.mobile_number = self.user_id.wa_mobile

    def onchange_template_id(self, template_id, model, res_id):
        if template_id:
            values = self.generate_email_for_composer(template_id, [res_id])[res_id]
            if self.template_id.report_template:
                to_attach_data, to_attach_extension = self.template_id.report_template.render_qweb_pdf([self.env.context.get('active_id')])
                attachment = self.generate_preview_attachment(
                    to_attach_data,
                    to_attach_extension,
                    self.env.context.get('active_model'),
                    self.env.context.get('active_id')
                )
                self.attachment = attachment
        else:
            default_values = self.with_context(default_model=model, default_res_id=res_id).default_get(
                ['model', 'res_id', 'partner_ids', 'message'])
            values = dict((key, default_values[key]) for key in
                        ['body', 'partner_ids']
                        if key in default_values)
        values = self._convert_to_write(values)
        return {'value': values}

    def generate_preview_attachment(self, att_data, att_extension, active_model, active_id):
        """ This funciton generates the main attachment for the WhatsApp message. PARAMS:
        att_data: File to encode. It will be encoded to base64.
        att_extension: (str). The extension of the base64 encoded file (example: .pdf, .xlsx, etc).
        active_model: (str) The model that will generate the file. example: 'account.move'.
        active_id: (int). The ID of the active record. Example: 1540 """
        data = base64.b64encode(att_data)
        atta_id = self.env.context.get('active_id')
        if self.template_id.report_template.print_report_name:
            reg = self.env[active_model].browse(active_id)
            res_name = safe_eval(self.template_id.report_template.print_report_name, {'object': reg}) + '.' + att_extension
        else:
            temp_res_name = self.env[active_model].browse(active_id).name
            res_name = f"{self.user_id.name} {temp_res_name}"
        attachment = self.env['ir.attachment'].create({
                    'name': res_name,
                    'type': 'binary',
                    'datas': data,
                    'res_model': self._name,
                    #'res_id': atta_id,
                    'mimetype': f"application/{att_extension}"
                })
        return attachment

    def generate_email_for_composer(self, template_id, res_ids, fields=None):
        multi_mode = True
        if isinstance(res_ids, int):
            multi_mode = False
            res_ids = [res_ids]
        if fields is None:
            fields = ['body_html']
        returned_fields = fields + ['partner_ids']
        values = dict.fromkeys(res_ids, False)
        template_values = self.env['mail.template'].with_context(tpl_partners_only=True).browse(template_id).generate_email(res_ids, fields=fields)
        for res_id in res_ids:
            res_id_values = dict((field, template_values[res_id][field]) for field in returned_fields if
                                    template_values[res_id].get(field))
            res_id_values['message'] = html2text.html2text(res_id_values.pop('body_html', ''))
            values[res_id] = res_id_values
        return multi_mode and values or values[res_ids[0]]

    def prepare_messages(self):
        if self.message:
            active_model = self.env.context.get('active_model')
            active_id = self.env.context.get('active_id')
            model_has_mail = self.check_model_mail(self.env.context.get('active_model'))
            phone = self.user_id.wa_mobile
            if phone and len(phone) >= 8:
                phone = str(phone)
                phone = phone.replace(" ", "").replace("+","").replace("-","")
                #PREGUNTO SI EL NÚMERO TIENE EL CÓDIGO DEL PAIS, SINO LO TIENE LO AGREGA.
                cod_pais = phone[:2]
                if cod_pais != "54":
                    phone = "54" + phone
                if not phone:
                    raise ValidationError(_(f"El cliente {self.user_id.name} no")
                        ("tiene un numero de telefono de WhatsApp definido."))
                wa_record = self.env['bf.whatsapp.message'].create({
                    'name':self.user_id.id,
                    'message':self.message,
                    'phone':phone,
                    #'attachment_ids': atta
                    'attachment_ids': self.attachment
                })
                if model_has_mail:
                    self.post_message_to_model(
                        active_model,
                        active_id,
                        (f"Se creo un mensaje de WhatsApp exitosamente para ser enviado.<a href='#' data-oe-model='{wa_record._name}' data-oe-id='{wa_record.id}'>Link</a>"),
                        "WhatsApp"
                    )

    def post_message_to_model(self, model, record_id, msg, msg_subject):
        """ Posts a message to the chatter of the selected model.
        model: (str) the model to post the message. Example: 'account.move'.
        record: (int) the id of the record to post the message.
        message: (str) the message to post in the chatter.
        msg_subject: (str) the subject of the message to post."""
        self.env[model].browse(record_id).message_post(body=msg, subject=msg_subject)

    def check_model_mail(self, model_to_check):
        """ Check if a given model has chatter. Returns (bool). 
        model_to_check: (str). Model to check, example: 'account.move'."""
        model_has_mail = False
        if "message_ids" in self.env[model_to_check]._fields:
            model_has_mail = True
        else:
            _logger.info(f"The model {model_to_check} has no message_post attribute.")
            _logger.info("Skipping the creation of a message post.")
        return model_has_mail