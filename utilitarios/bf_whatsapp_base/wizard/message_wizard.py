from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import html2plaintext, plaintext2html
from odoo.tools.mimetypes import guess_mimetype
from odoo.tools import config, human_size, ustr, html_escape
import html2text
import urllib.parse as parse

import os
import re
import base64
import logging

_logger = logging.getLogger(__name__)

class MessageError(models.TransientModel):
    _name='display.error.message'
    def get_message(self):
        if self.env.context.get("message", False):
            return self.env.context.get('message')
        return False
    name = fields.Text(string="Message", readonly=True, default=get_message)

class SendMessage(models.TransientModel):
    _name = 'whatsapp.wizard'

    user_id = fields.Many2one('res.partner', string="Recipient Name", default=lambda self: self.env[self._context.get('active_model')].browse(self.env.context.get('active_ids')).partner_id)
    mobile_number = fields.Char()
    message = fields.Text(string="Message")
    model = fields.Char('mail.template.model_id')
    template_id = fields.Many2one('mail.template', 'Use template', index=True)

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
        else:
            default_values = self.with_context(default_model=model, default_res_id=res_id).default_get(
                ['model', 'res_id', 'partner_ids', 'message'])
            values = dict((key, default_values[key]) for key in
                          ['body', 'partner_ids']
                          if key in default_values)
        values = self._convert_to_write(values)
        return {'value': values}

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

    """ def send_custom_message(self):
        if self.message and self.mobile_number:
            message_string = parse.quote(self.message)
            message_string = message_string[:(len(message_string) - 3)]
            number = self.user_id.mobile
            link = "https://web.whatsapp.com/send?phone=" + number
            send_msg = {
                'type': 'ir.actions.act_url',
                'url': link + "&text=" + message_string,
                'target': 'new',
                'res_id': self.id,
            }
            return send_msg """
    
    def prepare_messages(self):
        if self.message:
            mensaje = self.message
            phone = self.user_id.wa_mobile
            #Recupero el reporte que hay que enviar en caso de que exista
            atta = False
            res_id = self._context.get('active_id') or 1
            if self.template_id.report_template:
                model = self.template_id.model
                self.model = self.env[model]
                reg = self.env[model].browse(res_id)
                Attachment = self.env['ir.attachment']
                res_name = self.template_id.report_template.display_name + '_' + reg.name.replace('/', '_')
                domain = [('res_id', '=', res_id), ('name', 'like', res_name + '%'), ('res_model', '=', model)]
                is_attachment_exists = Attachment.search(domain, limit=1)
                
                atta = self.env['ir.attachment']
                if is_attachment_exists:
                    atta += is_attachment_exists
                else:
                    logging.info("El reporte no existe, creando...")
                    template = self.template_id
                    report = template.report_template
                    report_service = report.report_name
                    if report.report_type not in ['qweb-html', 'qweb-pdf']:
                        raise UserError(_('Unsupported report type %s found.') % report.report_type)
                    res, format = report.render_qweb_pdf([reg.id])
                    b64_pdf = base64.b64encode(res)
                    if not res_name:
                        res_name = 'report.' + report_service
                    ext = "." + format
                    if not res_name.endswith(ext):
                        res_name += ext
                    att_id = self.env['ir.attachment'].create({
                        'name': res_name,
                        'type': 'binary',
                        'datas': b64_pdf,
                        'res_model': model,
                        'res_id': res_id,
                        'mimetype': 'application/x-pdf'
                    })
                    atta += att_id
                

            """ res_name = False
            if self.template_id.report_template:
                atta = self.template_id.report_template.id """
            
            if phone and len(phone) >= 8:
                phone = str(phone)
                phone = phone.replace(" ", "").replace("+","").replace("-","")
                
                #PREGUNTO SI EL NÚMERO TIENE EL CÓDIGO DEL PAIS, SINO LO TIENE LO AGREGA.
                cod_pais = phone[:2]
                if cod_pais != "54":
                    phone = "54" + phone
                if not phone:
                    raise UserError(_(f"El cliente {self.user_id.name} no")
                        ("tiene un numero de telefono de WhatsApp definido."))
                self.env['bf.whatsapp.message'].create({
                    'name':self.user_id.id,
                    'message':mensaje,
                    'phone':phone,
                    'attachment_ids': atta                    
                })
                """ self.message_post(body="Se creo un mensaje de WhatsApp exitosamente para ser enviado.",
                                    subject="WhatsApp")   """

class bf_whatsapp_create_messages(models.TransientModel):
    _name = 'bf.whatsapp.create.messages'
    _description = 'Whatsapp envio de facturas'

    def get_model(self):
        return self.env.context.get('model')
    
    def get_default_wa_template(self):
        template = self.get_whatsapp_template()
        if template:
            return template

    message = fields.Text(string='Mensaje a enviar...')
    template_id = fields.Many2one('bf.whatsapp.templates', 'Use template', default=get_default_wa_template)
    model = fields.Char('Related Document Model',default=get_model)
    
    @api.model
    def _storage(self):
        return self.env['ir.config_parameter'].sudo().get_param('ir_attachment.location', 'file')

    @api.model
    def _filestore(self):
        return config.filestore(self._cr.dbname)

    @api.model
    def _full_path(self, path):
        # sanitize 
        pathpath = re.sub('[.]', '', path)
        path = path.strip('/\\')
        return os.path.join(self._filestore(), path)

    @api.model
    def _file_read(self, fname):
        full_path = self._full_path(fname)
        try:
            with open(full_path, 'rb') as f:
                return f.read()
        except (IOError, OSError):
            _logger.info("_read_file reading %s", full_path, exc_info=True)
        return b''    
    
    @api.onchange('template_id')
    def onchange_template_id_wrapper(self):
        #self.ensure_one()
        self.message = self.template_id.message        

    def get_whatsapp_template(self):
        context_model = self._context.get('active_model')
        if context_model:
            wa_template = self.env['bf.whatsapp.templates'].search([('model', '=', context_model)], limit=1)
            if wa_template:
                return wa_template.id

    def _model_context(self):
        self._context.get('active_model')

    