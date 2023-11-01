# -*- coding: utf-8 -*-
from email.policy import default
from odoo import models, fields, api,_
import requests
import os
import re
import logging
import random
from odoo.tools import config
from datetime import datetime
import time

_logger = logging.getLogger(__name__)
I_SERV = 0

class bf_whatsapp_message(models.Model):
    _name = 'bf.whatsapp.message'
    _description = 'bf.whatsapp.message'

    id_w = fields.Char(string = 'ID Whatsapp', copy=False, readonly=True)
    name = fields.Many2one(string="Cliente", comodel_name='res.partner')
    message = fields.Text(string = 'Message')
    media = fields.Char(string = 'file')
    
    phone = fields.Char(string = 'Phone')
    
    server_name = fields.Char(string = 'Server Name', copy=False, readonly=True)
    server_phone = fields.Char(string = 'Server Phone', copy=False, readonly=True)
    
    sent_date = fields.Datetime(string = "Date Sent", copy=False, readonly=True)
    send_state = fields.Boolean(string = 'Sent', default=False, copy=False, readonly=True)
    
    attachment_ids = fields.Many2many(
        'ir.attachment', 'bf_whatsapp_message_ir_attachments_rel',
        'wizard_id', 'attachment_id', 'Attachments')
    
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
            pass
            _logger.info("_read_file reading %s", full_path, exc_info=True)
        return b''
    
    @api.onchange('name')
    def set_phone_partner(self):
        if self.name:
            phone = self.name.wa_mobile
            if phone:
                phone = phone.replace(" ", "").replace("+","").replace("-","")
                #PREGUNTO SI EL NÚMERO TIENE EL CÓDIGO DEL PAIS, SINO LO TIENE LO AGREGA.
                cod_pais = phone[:2]
                if cod_pais != "54":
                    phone = "549" + phone
                self.phone = phone

    def notifications(self,title,message):
        resp = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _(title),
                'message': message,
                'sticky': False,
            }
        }
        return resp

    def selectServer(self):
        config = self.env['bf.whatsapp.config'].sudo().search([("active_conf","=",True)])
        cant_servers = len(config)
        global I_SERV
        I_SERV=(I_SERV+1)%(cant_servers)
        return(config[I_SERV])
    
    def connect_api(self):
        config = self.env['bf.whatsapp.config'].sudo().search([("active_conf","=",True)])
        for c in config:
            api_link = c.link_api          
        return(api_link)

    def send_command(self,command,data,config=False):
        if config:
            api_link = config.link_api
        else:
            api_link = self.connect_api()
        api_serv = api_link + "/" + command
        
        try:
            resp = requests.post(api_serv, json=data)
            return resp
        except:
            title = "SERVER OFFLINE"
            mess = "El servidor no responde."
            message = self.notifications(title,mess)
            return message

    def cron_send_message(self):
        messages = self.env['bf.whatsapp.message'].search([("send_state","=",False)], order="id", limit=10)
        config = self.env['bf.whatsapp.config'].sudo().search([("active_conf","=",True)])
        cant_servers = len(config)
        count = 0
        for reg in messages:
            print('Send menssage: ', count)
            self.send_message(reg)
            count+=1
            if (count%cant_servers==0):
                rnd = random.randint(10, 12)
                time.sleep(rnd)
            else:
                time.sleep(1)

    #ESTA FUNCIÓN DE CRON MARCA LOS MENSAJES COMO ENVIADOS, PARA QUE NO SE VUELVAN A ENVIAR EN CASO DE FALLO...
    def cron_send_status_true(self):
        messages = self.env['bf_whatsapp_message'].search([("send_state","=",False)], order="id", limit=50)
        for reg in messages:
            now = datetime.now()
            reg.id_w = '3EB0107861536C6785DB'
            reg.server_name = "Notifications-Server-00"
            reg.server_phone = "5493875036093"
            reg.sent_date = now
            reg.send_state = True