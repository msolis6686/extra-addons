# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import api, fields, models, _

class sh_message_wizard(models.TransientModel):
    _name="sh.message.wizard"
    _description = "Message wizard to display warnings, alert ,success messages"      
    
    def get_default(self):
        if self.env.context.get("message",False):
            return self.env.context.get("message")
        return False 

    def get_link(self):
        if self.env.context.get("link",False):
            return self.env.context.get("link")
        return False 

    def get_title(self):
        if self.env.context.get("title",False):
            return self.env.context.get("title")
        return False 
    name=fields.Text(string="Message",readonly=True,default=get_default)
    link=fields.Text(string="link",readonly=True, default=get_link)
    title=fields.Text(string="title",readonly=True, default=get_title)#Canpo para pasarle el texto que necesitamos que tenga el link.
    