# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################
from odoo import models

class ThemeShopoint(models.AbstractModel):
    _inherit = 'theme.utils'

    def _theme_shopoint_post_copy(self, mod):
        self.disable_view('website_theme_install.customize_modal')
