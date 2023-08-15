# -*- coding: utf-8 -*-
from email.policy import default
from odoo import models, fields, api,_
import json
import requests
import qrcode
from PIL import Image
import base64
import io
from odoo.exceptions import UserError
from datetime import datetime

class bf_whatsapp_qrs(models.Model):
    _name = 'bf.whatsapp.qrs'
    _description = 'bf.whatsapp.qrs'

    id_qrs = fields.Many2one('bf.whatsapp.config','ok')
    name = fields.Text(string = 'QR STRING')
    qr_image = fields.Binary()
    #qr_string = fields.Char(string = 'Qr String', required=True)

class bf_whatsapp_config(models.Model):
    _name = 'bf.whatsapp.config'
    _description = 'bf.whatsapp.config'

    name = fields.Char(string = 'Name Service', default="Api Whatsapp Web",  required=True)
    link_api = fields.Char(string = 'Link Api', required=True)
    user_name = fields.Char(string= 'User Name', required=True)
    user_pass = fields.Char(string = 'User Pass',  required=True)

    num_msg = fields.Integer(required=True,default=10)
    
    phone_company = fields.Char(string = 'Phone Company', default="Company Phone")
    header_message = fields.Text(string = 'Header Message', default="Company Name")
    footer_message = fields.Text(string = 'Footer Message', default="Responder a https://wa.me/549")
    logo = fields.Image(string= 'Logo Company', max_width=600, max_height=600)
    logo_name = fields.Char('File Name')    
    logo_url = fields.Char(string= 'URL Logo Company')
    qr_w = fields.Text(string = 'QR Conect', readonly=True)
    qrs_strings = fields.One2many(comodel_name='bf.whatsapp.qrs', inverse_name='id_qrs', string='Qrs Strings')    
    active_conf = fields.Boolean(string="Active")
    
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
    
    def active_config(self):
        config = self.env['bf.whatsapp.config'].search([])
        for c in config:
            c.active_conf = False
        self.active_conf = True
    
    def connect_api(self):
        """ config = self.env['bf.whatsapp.config'].search([("active_conf","=",True)])
        for c in config:
            api_link = c.link_api"""
        api_link = self.link_api       
        return(api_link)
        
    def send_command(self,command):
        api_link = self.connect_api()
        api_serv = api_link + "/" + command
        try:
            resp = requests.post(api_serv)
            return resp
        except:
            title = "SERVER OFFLINE"
            mess = "El servidor no responde."
            message = self.notifications(title,mess)
            return message
    
    def connected_services(self):
        resp = self.send_command("getqr")
        resp = resp.json().get('QRS')
        self.qr_w = resp
        
        #ELIMINO TODOS LOS REGISTROS DEL MODELO
        regs = self.env["bf.whatsapp.qrs"].search([])
        for item in regs:
            item.unlink()
        
        #AGREGO NUEVOS REGISTROS AL MODELO
        for item in resp:
            if item:
                img = qrcode.make(item)
                buf = io.BytesIO()
                img.save(buf)
                image_stream = buf.getvalue()
                qr_image = base64.b64encode(image_stream)
                new_item = self.env['bf.whatsapp.qrs'].create({'name': item,'qr_image':qr_image})
                #self.qrs_strings = [(0,0,{'name':item})]
        
        
        regs = self.env["bf.whatsapp.qrs"].search([])
        self.qrs_strings = regs
        
    def status(self):
        try:
            resp = self.send_command("status")
            resp = resp.json().get('server_status')
        except:
            resp = False
        return resp
    
    def status_services(self):
        resp = self.status()
        if resp:
            title = "Server Status"
            mess = ""
            for item in resp:
                mess = mess + item + "</br>"
            message = self.notifications(title,mess)
        else:
            title = "SERVER OFFLINE"
            mess = "El servidor no responde."
            message = self.notifications(title,mess)
        return message
            
    def destroy_services(self):
        state = self.status()
        if state:
            logout = self.send_command("logout")
            resp = logout.json().get('logout')
        else:
            resp=False
        
        title = "Result - Logout: "
        mess = (resp)
        if resp:
            mess = str(resp)
        else:
            mess = "Servidor fuera de línea"
        
        message = self.notifications(title,mess)
        return message
    
    def initializing_services(self):
        state = self.status()
        if state:
            init_ser = self.send_command("initializing")
            resp = init_ser.json().get('init_service')
        else:
            resp=False
        
        title = "Result - Init: "
        mess = str(resp)
        message = self.notifications(title,mess)
        return message
    