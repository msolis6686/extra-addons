# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
from odoo.exceptions import ValidationError, UserError

class bf_mercadopago_update_subscription_wizard(models.TransientModel):
    _name = 'bf.mercadopago.update.subscription.wizard'
    _description = 'Wizard para actualizar los datos de una subscripción.'

    def get_mp_id(self):
        if self.env.context.get('mp_id'):
            return self.env.context.get('mp_id')
        else:
            raise ValidationError("No se pudo encontrar la ID en el sistema. Esto no deberia pasar, porfavor contacte a soporte tecnico.")

    mp_id = fields.Char(string='ID de Subscripción', help='Identificador único del plan de suscripción.', default=get_mp_id)
    reason = fields.Char(string='Nombre de Subscripción', help='Es una breve descripción que el suscriptor verá durante el checkout y en las notificaciones.')
    transaction_amount = fields.Float(string='Monto', help='Suma que se cobrará en cada factura.')
    frequency_type = fields.Selection([('days', 'Días'), ('months', 'Meses')])
    frequency = fields.Integer(string='Frecuencia', help='Indica el valor de la frecuencia. Junto con frequency_type definen el ciclo de facturación que tendrá una suscripción.')
    has_free_trial = fields.Boolean(string='Prueba Gratuita')
    free_trial_frequency_type = fields.Selection([('months', 'Meses'),('days', 'Días')])
    free_trial_frequency = fields.Integer(string='Frecuencia', help='Indica el valor de la frecuencia. Junto con frequency_type definen el ciclo de facturación que tendrá una suscripción.')
    has_repetitions = fields.Boolean(string='Subscripción Limitada')
    repetitions = fields.Integer(string='Repeticiones', help='Es opcional y se utiliza para crear una suscripción limitada. Indica el número de veces que repetiremos el ciclo de recurrencia. Si no se define este param, la suscripción no finaliza hasta que alguna de las partes la cancela.')
    billing_day = fields.Integer(string='Día de Facturacion', help='Día del mes en que siempre se cobrará la suscripción. Solo acepta valores entre 1 y 28.')
    billing_day_proportional = fields.Boolean(string='Facturacion Proporcional', help="Cobra una suma proporcional al día de facturación en el momento del registro. 'true': Cobra un valor proporcional basado en los dias restantes del siguiente ciclo de facturación. Los ciclos de facturación son calculados en base de 30 días. 'false': Cobrar el monto total de la subscripcion sin importar en cuando se inscribe el cliente.")
    back_url = fields.Char(string='URL de Redireccion', help='URL a la que se redirigira al cliente una vez concretado el pago.')
    external_reference = fields.Char(string='Referencia Externa', help='Referencia para sincronizar con tu sistema. Este es un campo de texto libre para ayudarte con tu integración para vincular las entidades.')
    currency_id = fields.Char(string='Moneda', help='Identificador de la moneda utilizada en el pago.', default='ARS')

    @api.onchange('mp_id')
    def fill_fields(self):
        subscription_data = self.env['bf.mercadopago.subscriptions'].search([('mp_id','=', self.mp_id)])
        self.reason = subscription_data.reason
        self.has_repetitions = subscription_data.has_repetitions
        self.repetitions = subscription_data.repetitions
        self.transaction_amount = subscription_data.transaction_amount
        self.frequency_type = subscription_data.frequency_type
        self.frequency = subscription_data.frequency
        self.has_free_trial = subscription_data.has_free_trial
        if subscription_data.has_free_trial == True:
            self.free_trial_frequency_type = subscription_data.free_trial_frequency_type
            self.free_trial_frequency = subscription_data.free_trial_frequency
        self.billing_day = subscription_data.billing_day
        self.billing_day_proportional = subscription_data.billing_day_proportional
        self.back_url = subscription_data.back_url
        self.external_reference = subscription_data.external_reference
        self.currency_id = subscription_data.currency_id
    
    @api.onchange('has_free_trial')
    def reset_trial_values(self):
        if self.has_free_trial == False:
            self.free_trial_frequency_type = False
            self.free_trial_frequency = False
    
    @api.onchange('has_repetitions')
    def reset_repetition_value(self):
        if self.has_repetitions == False:
            self.repetitions = False

    def send_and_update_subscription(self):
        subscription_record = self.env['bf.mercadopago.subscriptions'].search([('mp_id','=', self.mp_id)])
        if subscription_record:
            mp_dict = {
                "reason": self.reason,
                "auto_recurring": {
                "frequency": self.frequency,
                "frequency_type": self.frequency_type,
                "repetitions": self.repetitions,
                "billing_day": self.billing_day,
                "billing_day_proportional": self.billing_day_proportional,
                "free_trial": {
                    "frequency": self.free_trial_frequency,
                    "frequency_type": self.free_trial_frequency_type
                },
                "transaction_amount": self.transaction_amount,
                "currency_id": self.currency_id
                },
                "payment_methods_allowed": {
                    "payment_types": [
                    {}
                    ],
                    "payment_methods": [
                    {}
                    ]
                },
                "back_url": self.back_url
            }
            print(mp_dict)
            #Controles de diccionario
            if self.has_repetitions == False:
                mp_dict['auto_recurring'].pop('repetitions')
            if self.has_free_trial == False:
                mp_dict['auto_recurring'].pop('free_trial')
            #Si la frecuencia de cobro se distina de 1 mes (mensual), no se puede definir un billing day.
            if self.frequency != 1 or self.frequency != 'months':
                mp_dict['auto_recurring'].pop('billing_day')
            #Envio de los datos a MercadoPago
            mp_api_key = self.env['ir.config_parameter'].search([('key','=','mercadopago_api')])
            mp_header = {
                    'Authorization': f'Bearer {mp_api_key.value}',
                    'Content_Type': 'application/json'
                }
            mp_request = requests.put(f"https://api.mercadopago.com/preapproval_plan/{self.mp_id}",headers=mp_header, json=mp_dict).json()
            if mp_request:
                if mp_request.get('status') != 'active':
                    raise ValidationError(f"Ocurrion un error de validacion con MercadoPago y esto es lo que devolvio: {mp_request.get('message')}")
                else:
                    update_vals = {}
                    update_vals['mp_id'] = mp_request.get('id')
                    update_vals['reason'] = mp_request.get('reason')
                    update_vals['application_id'] = mp_request.get('application_id')
                    update_vals['status'] = mp_request.get('status')
                    update_vals['subscribed'] = mp_request.get('subscribed')
                    update_vals['back_url'] = mp_request.get('back_url')
                    update_vals['collector_id'] = mp_request.get('collector_id')
                    update_vals['init_point'] = mp_request.get('init_point')
                    update_vals['date_created'] = self.env['bf.mercadopago.subscriptions'].mp_convert_date(mp_request.get('date_created'))
                    update_vals['last_modified'] = self.env['bf.mercadopago.subscriptions'].mp_convert_date(mp_request.get('last_modified'))
                    update_vals['external_reference'] = mp_request.get('external_reference')
                    update_vals['transaction_amount'] = mp_request.get('transaction_amount')
                    #FREQUENCY
                    update_vals['frequency'] = mp_request.get('auto_recurring').get('frequency')
                    update_vals['repetitions'] = mp_request.get('auto_recurring').get('repetitions')
                    update_vals['currency_id'] = mp_request.get('auto_recurring').get('currency_id')
                    update_vals['transaction_amount'] = mp_request.get('auto_recurring').get('transaction_amount')
                    update_vals['frequency_type'] = mp_request.get('auto_recurring').get('frequency_type')
                    update_vals['billing_day'] = mp_request.get('auto_recurring').get('billing_day')
                    update_vals['billing_day_proportional'] = mp_request.get('auto_recurring').get('billing_day_proportional')
                    update_vals['mp_validated'] = True
                    #FREE TRIAL
                    try:
                        if mp_request.get('auto_recurring').get('free_trial'):
                            update_vals['has_free_trial'] = True
                            update_vals['free_trial_frequency'] = mp_request.get('auto_recurring').get('free_trial').get('frequency')
                            update_vals['free_trial_frequency_type'] = mp_request.get('auto_recurring').get('free_trial').get('frequency_type')
                    except:
                        print(f"La subscripcion {mp_request.get('reason')} no tiene un periodo de prueba.")
                        update_vals['has_free_trial'] = False
                        update_vals['free_trial_frequency'] = False
                        update_vals['free_trial_frequency_type'] = False
                    subscription_record.write(update_vals)
    #TODO
    #Si se pone una fecha de pureba es imposible sacarla desde odoo por el diccionario de datos y hay que hacerlo directamente desde mercadopago
    #Si se pone una fecha de repeticion es imposible sacarla desde odoo por el diccionario de datos y hay que hacerlo directamente desde mercadopago
    #REVISAR ESTOS DOS CON LA RESPUESTA QUE DE EL SOPORTE DE MERCADOPAGO Y CORREGIR SI ES POSIBLE