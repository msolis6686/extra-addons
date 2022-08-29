# -*- coding: utf-8 -*-

from odoo import models, fields, api


class mercadopago_subscriptions(models.Model):
    _name = 'mercadopago.subscriptions'
    _description = 'Subscriptions Tiers'

    name = fields.Char(string='Subscripción', help='Nombre de la subscripción')
    description = fields.Text(string='Descripcion de la Subscripcion', help='Descripcion de la subscripción')
    mp_link = fields.Char(string='Link de MercadoPago', help='Coloca aqui el link que generaste en mercadopago para este tipo de subscripción.')
    #internal_note = fields.Text(string='Nota Interna', help='''Este campo es para poner una nota interna de la subscripcion que no puede ser vista por los clientes.
    #    Puede usarse para poner recordatorios o notas especiales para la subscripcion, por ejemplo un rango de precios, etc.''')