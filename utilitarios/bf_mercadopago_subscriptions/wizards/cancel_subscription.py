# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
from odoo.exceptions import ValidationError, UserError

class bf_mercadopago_cancel_subscription_wizard(models.TransientModel):
    _name = 'bf.mercadopago.cancel.subscription.wizard'
    _description = 'Wizard para actualizar los datos de una subscripción.'

    def get_mp_id(self):
        if self.env.context.get('mp_id'):
            return self.env.context.get('mp_id')
        else:
            raise ValidationError("No se pudo encontrar la ID en el sistema. Esto no deberia pasar, porfavor contacte a soporte tecnico.")
    
    mp_id = fields.Char(string='ID de Subscripción', help='Identificador único del plan de suscripción.', default=get_mp_id)
    reason = fields.Char(string='Nombre de Subscripción', help='Es una breve descripción que el suscriptor verá durante el checkout y en las notificaciones.')

    @api.onchange('mp_id')
    def fill_fields(self):
        subscription_data = self.env['bf.mercadopago.subscriptions'].search([('mp_id','=', self.mp_id)])
        self.mp_id = subscription_data.mp_id
        self.reason = subscription_data.reason
    
    def send_and_cancel_subscription(self):
        subscription_record = self.env['bf.mercadopago.subscriptions'].search([('mp_id','=', self.mp_id)])
        if subscription_record:
            mp_dict = {
                "reason": subscription_record.reason,
                "auto_recurring": {
                "frequency": subscription_record.frequency,
                "frequency_type": subscription_record.frequency_type,
                "repetitions": subscription_record.repetitions,
                "billing_day": subscription_record.billing_day,
                "billing_day_proportional": subscription_record.billing_day_proportional,
                "free_trial": {
                    "frequency": subscription_record.free_trial_frequency,
                    "frequency_type": subscription_record.free_trial_frequency_type
                },
                "transaction_amount": subscription_record.transaction_amount,
                "currency_id": subscription_record.currency_id
                },
                "payment_methods_allowed": {
                    "payment_types": [
                    {}
                    ],
                    "payment_methods": [
                    {}
                    ]
                },
                "back_url": subscription_record.back_url,
                "status": 'cancelled'
            }
        if subscription_record.has_repetitions == False:
            mp_dict['auto_recurring'].pop('repetitions')
        if subscription_record.has_free_trial == False:
            mp_dict['auto_recurring'].pop('free_trial')
        #Si la frecuencia de cobro se distina de 1 mes (mensual), no se puede definir un billing day.
        if subscription_record.frequency != 1 or subscription_record.frequency != 'months':
            mp_dict['auto_recurring'].pop('billing_day')
        mp_api_key = self.env['ir.config_parameter'].search([('key','=','mercadopago_api')])
        mp_header = {
                'Authorization': f'Bearer {mp_api_key.value}',
                'Content_Type': 'application/json'
            }
        mp_request = requests.put(f"https://api.mercadopago.com/preapproval_plan/{self.mp_id}",headers=mp_header, json=mp_dict).json()
        if mp_request:
            if mp_request.get('status') != 'cancelled':
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