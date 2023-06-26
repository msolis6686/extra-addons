# -*- coding: utf-8 -*-
from email.policy import default
from odoo import models, fields, api,_
import json
import requests
import base64
import io
from odoo.exceptions import UserError
from datetime import datetime
import html2text
from odoo.tools import html2plaintext, plaintext2html


class bf_whatsapp_templates(models.Model):
    _name = 'bf.whatsapp.templates'
    _description = 'Whatsapp Message Template'
    
    name = fields.Char('Nombre')
    model_id = fields.Many2one('ir.model', 'Aplicar a', help="The type of document this template can be used with")
    model = fields.Char('Related Document Model', related='model_id.model', index=True, store=True, readonly=True)
    
    header_message = fields.Text(string = 'Header Message', default="Nombre de la Compañía", required=True)
    footer_message = fields.Text(string = 'Footer Message', default="Responder a https://wa.me/549xxx", required=True)
    message = fields.Text()
    
    
    attachment_ids = fields.Many2many(
        'ir.attachment', 'bf_whatsapp_templates_ir_attachments_rel',
        'wizard_id', 'attachment_id', 'Attachments')
    
    attachment_file = fields.Boolean('Adjuntar Reporte')
    report_template = fields.Many2one('ir.actions.report', 'Reporte relacionado')
    
    
    
    @api.onchange('model_id')
    def onchange_model_id(self):
        # TDE CLEANME: should'nt it be a stored related ?
        if self.model_id:
            self.model = self.model_id.model
        else:
            self.model = False
            
            
    @api.model
    def generate_email_for_composer(self, template_id, res_ids, fields=None):
        """ Call email_template.generate_email(), get fields relevant for
            whatsapp.compose.message, transform email_cc and email_to into partner_ids """
        multi_mode = True
        if isinstance(res_ids, int):
            multi_mode = False
            res_ids = [res_ids]

        if fields is None:
            fields = ['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc',  'reply_to', 'attachment_ids', 'mail_server_id']
        returned_fields = fields + ['partner_ids', 'attachments']
        values = dict.fromkeys(res_ids, False)

        template_values = self.env['mail.template'].with_context(tpl_partners_only=True).browse(template_id).generate_email(res_ids, fields=fields)
        for res_id in res_ids:
            res_id_values = dict((field, template_values[res_id][field]) for field in returned_fields if template_values[res_id].get(field))
            #res_id_values['body'] = res_id_values.pop('body_html', '')
            res_id_values['message'] = html2text.html2text(res_id_values.pop('body_html', ''))
            values[res_id] = res_id_values

        return multi_mode and values or values[res_ids[0]]
    