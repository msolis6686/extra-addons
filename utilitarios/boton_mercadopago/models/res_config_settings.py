from odoo import fields, models



class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    mercadopago_sandbox = fields.Boolean(
        string='Sanbox',
    )
    mercadopago_invoice_on_post = fields.Boolean(
        string='Create preference on post invoice'
    )
    mercadopago_external_reference = fields.Selection(
        [('obj','To object'),('partner','To partner')],
        string='External reference',
    )

    mercadopago_client = fields.Char(
        string='Client id',
    )
    mercadopago_key = fields.Char(
        string='Client secret',
    )
    mercadopago_api = fields.Char(
        string='API secret',
    )
    mercadopago_journal_id = fields.Many2one(
        'account.journal',
        string='mercadopago journal',
    )



    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['mercadopago_client'] = self.env['ir.config_parameter'].sudo(
        ).get_param('mercadopago_client', default=False)
        res['mercadopago_key'] = self.env['ir.config_parameter'].sudo(
        ).get_param('mercadopago_key', default=False)
        res['mercadopago_api'] = self.env['ir.config_parameter'].sudo(
        ).get_param('mercadopago_api', default=False)
        res['mercadopago_sandbox'] = self.env['ir.config_parameter'].sudo(
        ).get_param('mercadopago_sandbox', default=False)
        res['mercadopago_invoice_on_post'] = self.env['ir.config_parameter'].sudo(
        ).get_param('mercadopago_invoice_on_post', default=False)
        res['mercadopago_external_reference'] = self.env['ir.config_parameter'].sudo(
        ).get_param('mercadopago_external_reference', default=False)
        res['mercadopago_journal_id'] = int(self.env['ir.config_parameter'].sudo(
        ).get_param('mercadopago_journal_id', default=False))

        return res


    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param(
            'mercadopago_client', self.mercadopago_client)
        self.env['ir.config_parameter'].sudo().set_param(
            'mercadopago_key', self.mercadopago_key)
        self.env['ir.config_parameter'].sudo().set_param(
            'mercadopago_api', self.mercadopago_api)
        self.env['ir.config_parameter'].sudo().set_param(
            'mercadopago_sandbox', self.mercadopago_sandbox)
        self.env['ir.config_parameter'].sudo().set_param(
            'mercadopago_invoice_on_post', self.mercadopago_invoice_on_post)
        self.env['ir.config_parameter'].sudo().set_param(
            'mercadopago_external_reference', self.mercadopago_external_reference)
        self.env['ir.config_parameter'].sudo().set_param(
            'mercadopago_journal_id', self.mercadopago_journal_id.id)
        super(ResConfigSettings, self).set_values()
