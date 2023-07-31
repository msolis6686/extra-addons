# -*- coding: utf-8 -*-

from odoo import models, fields, api


class bf_mercadopago_active_subscriptions(models.Model):
    _name = 'bf.mercadopago.active.subscriptions'
    _description = 'Active Subscriptions'

    partner_id = fields.Many2one('res.partner',string='Cliente')
    subscription_id = fields.Many2one('bf.mercadopago.subscriptions',string='Subscripcion')
    status = fields.Char(string='Estado de Subscripción')
    active_since = fields.Date(string='Activo Desde')
    ended_in = fields.Date(string='Finalizado Desde')
    active_months = fields.Integer(string='Meses Activo')
    notes = fields.Text(string='Notas Internas')
    total_recaudado = fields.Float(string='Total Recaudado')
    #internal_note = fields.Text(string='Nota Interna', help='''Este campo es para poner una nota interna de la subscripcion que no puede ser vista por los clientes.
    #    Puede usarse para poner recordatorios o notas especiales para la subscripcion, por ejemplo un rango de precios, etc.''')