# -*- coding: utf:8 -*-
from odoo import api, models, fields, _


class ResPartner(models.Model):
    _inherit = 'res.partner'
    mobile_2 = fields.Char(string="Móvil 2")
    wa_mobile = fields.Char(string="Núm. Whatsapp")


    @api.onchange('wa_mobile', 'country_id', 'company_id')
    def onchange_mobile_validation(self):
        print(self.wa_mobile)
        if self.wa_mobile:
            self.wa_mobile = self.phone_format(self.wa_mobile)
            print("Validado...",self.wa_mobile)


    def cron_copy_mobiles(self):
        partners = self.env['res.partner'].search([("mobile","!=",False)])
        for reg in partners:
            reg.wa_mobile = reg.mobile            