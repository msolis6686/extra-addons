# -*- coding: utf-8 -*-
from email.policy import default
from odoo import models, fields, api,_
import json
import requests
from odoo.tools.mimetypes import guess_mimetype
import qrcode
from PIL import Image
import base64
import io
import os
import re
import logging
import random

from odoo.tools import config, human_size, ustr, html_escape

from odoo.exceptions import UserError
from datetime import datetime
import time

#from odoo.addons.queue_job.job import Job

_logger = logging.getLogger(__name__)
I_SERV = 0

class bf_whatsapp_message(models.Model):
    _name = 'bf.whatsapp.message'
    _description = 'bf.whatsapp.message'

    id_w = fields.Char(string = 'ID Whatsapp', copy=False, readonly=True)
    name = fields.Many2one(string="Cliente", comodel_name='res.partner', required=True)
    message = fields.Text(string = 'Message', required=True)
    media = fields.Char(string = 'file')
    
    #phone = fields.Char(string = 'Phone', related='name.mobile', required=True)
    phone = fields.Char(string = 'Phone', required=True)
    
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
            phone = self.name.mobile
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
        #print(I_SERV)
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
    
    
    def send_message(self,reg=False):
        if not reg:
            reg = self
        
        #config = self.env['bf.whatsapp.config'].sudo().search([("active_conf","=",True)])
        # SELECCIONO EL SERVER SECUENCIALMENTE
        config = self.selectServer()

        if config.header_message and config.footer_message:
            mess = "*" + config.header_message + "* \n\n" +  reg.message + "\n\n" + config.footer_message
        else:
            mess = reg.message
        
        phone = reg.phone.replace(" ", "").replace("+","").replace("-","")
        
        #PREGUNTO SI EL NÚMERO TIENE EL CÓDIGO DEL PAIS, SINO LO TIENE LO AGREGA.
        cod_pais = phone[:2]
        if cod_pais != "54":
            phone = "54" + phone
        #media = False
        if reg.attachment_ids:
            media = []
            attachment_new_ids = []
            for attach in reg.attachment_ids:
                full_path = self._full_path(attach.store_fname)
                encoded_string = base64.b64encode(open(full_path, 'rb').read())
                base64_message = encoded_string.decode('utf-8')
                mimetype = attach.mimetype
                if mimetype == 'application/octet-stream':
                    mimetype = 'video/mp4'
                vals = {
                        'filename': attach.name,
                        'type': mimetype,
                        'data': base64_message                        
                        }
                media.append(vals)
        else:
            media = False
        
        data_message = json.dumps(media)
        logo=False
        logo_url=False
        if config.logo:
            binary = self.env["ir.attachment"].sudo().search([("res_model", "=", "bf.whatsapp.config"),("res_id", "=", config.id),("res_field", "=", "logo"),],limit=1)
            if binary:
                logo = []
                full_path = self._full_path(binary.store_fname)
                encoded_string = base64.b64encode(open(full_path, 'rb').read())
                base64_message = encoded_string.decode('utf-8')
                mimetype = binary.mimetype
                if mimetype == 'application/octet-stream':
                    mimetype = 'video/mp4'
                vals = {
                        'filename': config.logo_name,
                        'type': mimetype,
                        'data': base64_message                        
                        }
                logo.append(vals)
        if config.logo_url:
            logo_url = config.logo_url
        data = {
            'messages':
                [{
                    'id':reg.id,
                    'message':mess,
                    'phone':phone,
                    'media':data_message,
                    'logo':logo,
                    'logo_url':logo_url,
                }]
            }
        #print(media[:20])
        if not reg.send_state:
            try:
                resp = self.send_command("send_message",data)
                resp = resp.json()
                band = True
            except Exception as e:
                print("Oops!", e.__class__, "occurred.")
                title = "SERVER OFFLINE"
                mess = "El servidor no responde."
                message = self.notifications(title,mess)
                band = False
                return message
        
            logging.info("RESPUESTA DEL SERVIDOR")
            logging.info(resp)
            if resp!=[None] and band:
                for item in resp:
                    if item:
                        reg = self.env['bf.whatsapp.message'].search([("id","=",item["id_externo"])])
                        now = datetime.now()
                        reg.id_w = item['id']
                        reg.server_name = item['server_name']
                        reg.server_phone = item['server_phone']
                        reg.sent_date = now
                        reg.send_state = True
                        reg.message = mess
                
                title = "Mensajes enviados"
                mess = "Se envió su mensaje correctamente"
                message = self.notifications(title,mess)
                #return message
            else:
                title = "SERVIDOR DESCONECTADO"
                mess = "El servidor no responde. Reintente mas tarde."
                message = self.notifications(title,mess)
                return message
        else:
            title = "Error al enviar"
            mess = "No puede reenviar este mensaje.\nEn su lugar, intente duplicarlo."
            message = self.notifications(title,mess)
            return message
        
    def cron_send_message(self):
        messages = self.env['bf.whatsapp.message'].search([("send_state","=",False)], order="id", limit=10)
        config = self.env['bf.whatsapp.config'].sudo().search([("active_conf","=",True)])
        cant_servers = len(config)
        
        count = 1
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