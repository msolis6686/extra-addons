from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)



class BfMailTemplateInherit(models.Model):
    _inherit = "mail.template"
    _description = "Mail Template WhatsApp Inherit"

    is_wa_template = fields.Boolean(default=False)

    @api.model
    def create(self, vals):
        res = super(BfMailTemplateInherit, self).create(vals)
        if self.env.context.get('whats_app_module'):
            _logger.info("Creating a WhatsApp Template.")
            res.is_wa_template = True
        return res