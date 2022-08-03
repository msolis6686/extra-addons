from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form
from odoo.tools.translate import _


class ContractContract(models.Model):
    _inherit = "contract.contract"

    def recurring_create_invoice(self):
        """
        This method triggers the creation of the next invoices of the contracts
        even if their next invoicing date is in the future.
        """
        invoice = self._recurring_create_invoice()
        if invoice:
            self.message_post(
                body=_(
                    "Contract manually invoiced: "
                    '<a href="#" data-oe-model="%s" data-oe-id="%s">Invoice'
                    "</a>"
                )
                % (invoice._name, invoice.id)
            )
        #invoice.post()
        #invoice.mercadopago_create_preference()
        #mail_template_id = self.env.ref('boton_mercadopago.email_template_mercadopago_invoice').id
        #mail_template = self.env['mail.template'].browse(mail_template_id)
        #mail_template.send_mail(invoice.id,force_send=True)
        #notif_layout = self._context.get('custom_layout')
        return invoice
