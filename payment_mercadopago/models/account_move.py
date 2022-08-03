from odoo import models, api, fields, _


class AccountMove(models.Model):
    _name = "account.move"

    _inherit = ["account.move","odoo_mercadopago"]
    _mercadopago_partner_field = 'partner_id'
    _mercadopago_amount_field = 'amount_total'


    def mercadopago_payment_receipt(self,payment_id,result):
        for line_id in payment_id.move_line_ids :
            self.js_assign_outstanding_line( line_id)

    def action_post(self):

        res = super(AccountMove, self).action_post()
        if  self.env['ir.config_parameter'].sudo().get_param('mercadopago_invoice_on_post', default=False):
            self.mercadopago_create_preference()

        return res

    def action_invoice_mercadopago(self):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
        """
        self.ensure_one()
        #if len(self.mercadopago_id):
        #self.mercadopago_create_preference()
        self.mercadopago_form_generate_values()

        template = self.env.ref(
            'payment_mercadopago.email_template_mercadopago_invoice', False)
        if not template:
            template_id = False
        else:
            template_id = template.id
        compose_form = self.env.ref(
            'mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model='account.move',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template_id,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }
