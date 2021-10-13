# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################
from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)

class ThemeShopoint(models.TransientModel):
    _inherit = 'res.config.settings'

    min_price = fields.Float(string="Min Price")
    max_price = fields.Float(string="Max Price")
    show_rating = fields.Boolean(string="Show Rating")
    is_bck_img = fields.Boolean(related='website_id.is_bck_img', readonly=False)
    login_bck_img = fields.Binary(related='website_id.login_bck_img', readonly=False)
    is_signup_bck_img = fields.Boolean(related='website_id.is_signup_bck_img', readonly=False)
    signup_bck_img = fields.Binary(related='website_id.signup_bck_img', readonly=False)
    is_footer_bck_img = fields.Boolean(related='website_id.is_footer_bck_img', readonly=False)
    footer_bck_img = fields.Binary(related='website_id.footer_bck_img', readonly=False)
    is_redirect = fields.Boolean(related='website_id.is_redirect', readonly=False)
    multi_product_carousel_items_no = fields.Integer(related='website_id.multi_product_carousel_items_no', readonly=False)

    # @api.multi
    def set_values(self):
        super(ThemeShopoint, self).set_values()
        IrDefault = self.env['ir.default'].sudo()
        IrDefault.set('res.config.settings', 'min_price', self.min_price)
        IrDefault.set('res.config.settings', 'max_price', self.max_price)
        IrDefault.set('res.config.settings', 'show_rating', self.show_rating)
        return True

    @api.model
    def get_values(self):
        res = super(ThemeShopoint, self).get_values()
        IrDefault = self.env['ir.default'].sudo()
        min_price = IrDefault.get('res.config.settings', 'min_price') if  IrDefault.get('res.config.settings', 'min_price') else 200
        max_price = IrDefault.get('res.config.settings', 'max_price') if  IrDefault.get('res.config.settings', 'max_price') else 12000
        show_rating = IrDefault.get('res.config.settings', 'show_rating') if  IrDefault.get('res.config.settings', 'show_rating') == False else True
        res.update({
            'min_price': min_price,
            'max_price': max_price,
            'show_rating': show_rating,
        })
        return res
