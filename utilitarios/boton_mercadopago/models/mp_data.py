from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _name = 'mp.data'
    _description = 'Modelo para guardar datos de pagos de mercadopago'

    payment_group_id = fields.Many2one('account.payment.group', string='ID de Grupo de Pago')
    invoice_id = fields.Many2one('account.move', string='ID de Factura')
    partner_id = fields.Char(string='Cliente',related='invoice_id.partner_id.name')
    collection_id = fields.Char(string='ID de Collection')
    collection_status = fields.Char(string='Estado de Collection')
    external_reference = fields.Char(string='Referencia Externa')
    merchant_account_id = fields.Char(string='ID de Cuenta de Mercader')
    merchant_order_id = fields.Char(string='ID de Orden de Mercader')
    payment_id = fields.Char(string='ID de Pago')
    payment_type = fields.Char(string='Tipo de Pago')
    preference_id = fields.Char(string='ID de Preferencia')
    processing_mode = fields.Char(string='Modo de Procesamiento')
    state_id = fields.Char(string='ID de Estado')
    status = fields.Char(string='Estado')
    note = fields.Text(string='Notas Adicionales')
