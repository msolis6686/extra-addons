# Copyright 2020 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.addons.queue_job.job import job


class AccountInvoiceSend(models.TransientModel):
    _inherit = "account.invoice.send"

    def _send_email(self):
        if self.composition_mode == 'mass_mail' and self.template_id and\
           not self.env.context.get('delay'):
            for x in self.env.context.get('active_ids'):
                self.with_delay(priority=30, max_retries=5, description='Envio de factura al cliente por correo electrónico', channel='root.invoice_email').delay_send_email(
                    x,
                    self.env.context.get('lang'),
                    self.template_id
                )
        else:
            super(AccountInvoiceSend, self)._send_email()

    #@job(default_channel='root.invoice_email')
    def delay_send_email(self, invoice_ids, lang, template):
        self_lang = self.with_context(
            active_ids=invoice_ids,
            lang=lang,
            delay=True
        )
        self_lang.composer_id.template_id = template.id
        self_lang.composer_id.onchange_template_id_wrapper()
        self_lang._send_email()
