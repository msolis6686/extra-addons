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

class SendContactMessage(models.TransientModel):
    _name = 'whatsapp.wizard.contact'

    user_id = fields.Many2one('res.partner', string="Recipient Name", default=lambda self: self.env[self._context.get('active_model')].browse(self.env.context.get('active_ids')))
    mobile_number = fields.Char(related='user_id.wa_mobile', required=True)
    message = fields.Text(string="Message", required=True)

    def send_custom_contact_message(self):
        if self.message:
            message_string = ''
            message = self.message.split(' ')
            for msg in message:
                message_string = message_string + msg + '%20'
            message_string = message_string[:(len(message_string) - 3)]
            number = self.user_id.mobile
            link = "https://web.whatsapp.com/send?phone=" + number
            send_msg = {
                'type': 'ir.actions.act_url',
                'url': link + "&text=" + message_string,
                'target': 'new',
                'res_id': self.id,
            }
            return send_msg

    def prepare_messages(self):
        if self.message:
            mensaje = self.message
            phone = self.user_id.wa_mobile
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
                    'attachment_ids': False                    
                })