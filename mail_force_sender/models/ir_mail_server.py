from odoo import api, fields, models, tools, _


class IrMailServer(models.Model):

    _inherit = "ir.mail_server"

    force_sender = fields.Boolean()
    sender_address = fields.Char()
    force_reply_to = fields.Boolean()
    replay_to_address = fields.Char()
