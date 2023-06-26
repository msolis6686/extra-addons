# -*- coding: utf:8 -*-
import string
from odoo import api, models, fields, _
from odoo.addons.phone_validation.tools import phone_validation


class ResPartner(models.Model):
    _inherit = 'res.partner'
    mobile_2 = fields.Char(string="Móvil 2")


@api.onchange('mobile_2', 'country_id', 'company_id')
def onchange_mobile_validation(self):
    print(self.mobile_2)
    if self.mobile_2:
        self.mobile_2 = self.phone_format(self.mobile_2)
        print("Validado...",self.mobile_2)