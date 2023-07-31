# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
import requests


class bf_mercadopago_subscriptions(models.Model):
    _name = 'bf.mercadopago.subscriptions'
    _description = 'Subscriptions Tiers'

    #CAMPOS BASICOS DE LA SUBSCRIPCION#
    mp_id = fields.Char(string='ID de Suscripción', help='Identificador único del plan de suscripción.')
    reason = fields.Char(string='Nombre de Suscripción', help='Es una breve descripción que el suscriptor verá durante el checkout y en las notificaciones.')
    application_id = fields.Char(string='ID de Aplicación', help='ID único que identifica tu aplicación/integración. Una de las claves del par que componen las credenciales que identifican una aplicación/integración en tu cuenta.')
    #name = fields.Char(string='Suscripción', help='Nombre de la Suscripción.')
    status = fields.Char(string='Estado', help="Estado del plan. ('active': Plan disponible y aceptando subscripciones. 'cancelled': Plan NO disponible para crear subscripciones.)")
    subscribed = fields.Integer(string='Subscriptores', help='Número de clientes suscritos al plan.')
    back_url = fields.Char(string='URL de Redireccion', help='URL a la que se redirigira al cliente una vez concretado el pago.')
    collector_id = fields.Char(string='ID de Vendedor', help='ID único que identifica a tu usuario como vendedor. Este ID coincide con tu User ID en nuestro ecosistema.')
    init_point = fields.Char(string='Link MercadoPago', help='URL para comenzar el flujo de suscripción.')
    date_created = fields.Datetime(string='Fecha de Creación')
    last_modified = fields.Datetime(string='Fecha de Última Modificación.')
    external_reference = fields.Char(string='Referencia Externa', help='Referencia para sincronizar con tu sistema. Este es un campo de texto libre para ayudarte con tu integración para vincular las entidades.')
    transaction_amount = fields.Float(string='Monto', help='Suma que se cobrará en cada factura.')
    currency_id = fields.Char(string='Moneda', help='Identificador de la moneda utilizada en el pago.', default='ARS')


    #AUTO RECURRING#
    frequency = fields.Integer(string='Frecuencia', help='Indica el valor de la frecuencia. Junto con frequency_type definen el ciclo de facturación que tendrá una suscripción.')
    frequency_type = fields.Selection([('days', 'Días'), ('months', 'Meses')])
    has_repetitions = fields.Boolean(string='Suscripción Limitada')
    repetitions = fields.Integer(string='Repeticiones', help='Es opcional y se utiliza para crear una suscripción limitada. Indica el número de veces que repetiremos el ciclo de recurrencia. Si no se define este param, la suscripción no finaliza hasta que alguna de las partes la cancela.')
    billing_day = fields.Integer(string='Día de Facturacion', help='Día del mes en que siempre se cobrará la suscripción. Solo acepta valores entre 1 y 28.')
    billing_day_proportional = fields.Boolean(string='Facturacion Proporcional', help="Cobra una suma proporcional al día de facturación en el momento del registro. 'true': Cobra un valor proporcional basado en los dias restantes del siguiente ciclo de facturación. Los ciclos de facturación son calculados en base de 30 días. 'false': Cobrar el monto total de la subscripcion sin importar en cuando se inscribe el cliente.")

    #FREE TRIAL
    free_trial_frequency = fields.Integer(string='Frecuencia', help='Indica el valor de la frecuencia. Junto con frequency_type definen el ciclo de facturación que tendrá una suscripción.')
    free_trial_frequency_type = fields.Selection([('months', 'Meses'),('days', 'Días')])
    has_free_trial = fields.Boolean(string='Prueba Gratuita')
    first_invoice_offset = fields.Integer(string='Compensación de la Primera Factura', help='Numero de días para cobrar la primera factura.')

    #METODOS DE PAGO
    payment_method_id = fields.Text(string='Metodo de Pago')

    mp_validated = fields.Boolean(string='Validado', help='Suscripción validada por MercadoPago')

    def get_subscriptions(self, user):
        """ Gets all the subscriptions from MercadoPago with the associated API_KEY and creates a dict with all it's values """
        mp_api_key = self.env['ir.config_parameter'].search([('key','=','mercadopago_api')])
        mp_request = requests.get(F"https://api.mercadopago.com/preapproval_plan/search",headers={'Authorization': f'Bearer {mp_api_key.value}'}).json()
        for subscription in mp_request.get('results'):
            vals = {
                'mp_id': subscription.get('id'),
                'reason': subscription.get('reason'),
                'application_id': subscription.get('application_id'),
                'status': subscription.get('status'),
                'subscribed': subscription.get('subscribed'),
                'back_url': subscription.get('back_url'),
                'collector_id': subscription.get('collector_id'),
                'init_point': subscription.get('init_point'),
                'date_created': self.mp_convert_date(subscription.get('date_created')),
                'last_modified': self.mp_convert_date(subscription.get('last_modified')),
                'external_reference': subscription.get('external_reference'),
                'transaction_amount': subscription.get('transaction_amount'),
                #FREQUENCY
                'frequency': subscription.get('auto_recurring').get('frequency'),
                'repetitions': subscription.get('auto_recurring').get('repetitions'),
                'currency_id': subscription.get('auto_recurring').get('currency_id'),
                'transaction_amount': subscription.get('auto_recurring').get('transaction_amount'),
                'frequency_type': subscription.get('auto_recurring').get('frequency_type'),
                'billing_day': subscription.get('auto_recurring').get('billing_day'),
                'mp_validated': True,
                #FREE TRIAL
            }
            try:
                if subscription.get('auto_recurring').get('free_trial'):
                    vals['has_free_trial'] = True
                    vals['free_trial_frequency'] = subscription.get('auto_recurring').get('free_trial').get('frequency')
                    vals['free_trial_frequency_type'] = subscription.get('auto_recurring').get('free_trial').get('frequency_type')
            except:
                print(f"La subscripcion {subscription.get('reason')} no tiene un periodo de prueba.")
                vals['has_free_trial'] = False
                vals['free_trial_frequency'] = subscription.get('auto_recurring').get('free_trial').get('frequency')
                vals['free_trial_frequency_type'] = subscription.get('auto_recurring').get('free_trial').get('frequency_type')
            self.mp_compare_subscriptions(vals)

    def mp_convert_date(self, mp_date):
        """ Recieves a date from MercadoPago and returns a %Y-%m-%d %H:%M:%S datetime """
        date = mp_date.split('T')[0]
        time = mp_date.split('T')[1].split('.')[0]
        mp_converted_date = date+' '+time
        return datetime.strptime(mp_converted_date, '%Y-%m-%d %H:%M:%S')
    
    def mp_compare_subscriptions(self, vals):
        """ Recieves a dict with the values obtained from MercadoPago and it will try to find and update a subscription in the system. If a subscrption is not
            found it will create a new record."""
        system_subscription = self.env['bf.mercadopago.subscriptions'].search([('mp_id','=',vals['mp_id'])])
        #Si encuentra una subscripcion en el sistema con el mismo ID, hay que comparar los datos para revisar si tiene cambios desde mercadolibre y actualizar
        #si es necesario, de lo contrario hay que crearla.
        if system_subscription:
            if vals['last_modified'] != system_subscription.last_modified:
                print(f"Suscripción {system_subscription.reason} con datos distintos, actualizando.")
                system_subscription.write(vals)
            elif vals['last_modified'] == system_subscription.last_modified:
                print(f"Subscripcion { system_subscription.reason} sin cambios.")
        else:
            print(f"Suscripción {vals['reason']} no encontrada en el sistema, creando registro")
            vals['automated'] = 1
            self.mp_create_subscription(vals)

    def mp_create_subscription(self, vals):
        """ Recieves a dict of vals to create a new record on the system """
        subscription_record = self.env['bf.mercadopago.subscriptions'].create(vals)
        if subscription_record:
            print(f"Suscripción {subscription_record.reason} creada con exito.")
    
    def mp_update_subscription_wizard(self):
        if self.status == 'cancelled':
            raise ValidationError('No se pueden actualizar los datos de una subscripcion cancelada.')
        view_id = self.env.ref('bf_mercadopago_subscriptions.bf_mp_update_subscription').id#Este dato lo sacamos de Ajustes/Tecnico/Vistas. Es el ID externo
        return {'type': 'ir.actions.act_window',#El type tiene que ser el mismo que usa el wizard (act_window)
                'name': _('Actualizar Datos de Suscripción'),#Nombre que va a tener el wizard.
                'res_model': 'bf.mercadopago.update.subscription.wizard',#El modelo del wizard o de la vista (se lo puede sacar del codigo, es el campo _name="nombre")
                'target': 'new',#New para que se abra una nueva ventana (el wizard)
                'view_mode': 'form',#Modo de vista (formulario para el wizard)
                'views': [[view_id, 'form']],#El id externo de la vista que definimos en la variable mas arriba y el 'form' o tree segun necesitemos
                'context': {'mp_id': self.mp_id}
                }
    
    def mp_cancel_subscription_wizard(self):
        if self.status == 'cancelled':
            raise ValidationError('No se puede cancelar una subscripcion ya cancelada.')
        view_id = self.env.ref('bf_mercadopago_subscriptions.bf_mp_cancel_subscription').id#Este dato lo sacamos de Ajustes/Tecnico/Vistas. Es el ID externo
        return {'type': 'ir.actions.act_window',#El type tiene que ser el mismo que usa el wizard (act_window)
                'name': _('Cancelar Suscripción'),#Nombre que va a tener el wizard.
                'res_model': 'bf.mercadopago.cancel.subscription.wizard',#El modelo del wizard o de la vista (se lo puede sacar del codigo, es el campo _name="nombre")
                'target': 'new',#New para que se abra una nueva ventana (el wizard)
                'view_mode': 'form',#Modo de vista (formulario para el wizard)
                'views': [[view_id, 'form']],#El id externo de la vista que definimos en la variable mas arriba y el 'form' o tree segun necesitemos
                'context': {'mp_id': self.mp_id}
                }

    @api.model
    def create(self, vals):
        print(vals)
        try:
            if vals['automated']:
                vals.pop('automated')
                return super(bf_mercadopago_subscriptions, self).create(vals)
        except:
            print('Creacion manual de plan desde Odoo.')
            mp_api_key = self.env['ir.config_parameter'].search([('key','=','mercadopago_api')])
            if vals['transaction_amount'] < 5:
                raise UserError(f"El monto de la subscripcion no puede ser menor a 5 Pesos. Ingresado: {vals.tansaction_amount}")
            if vals['frequency_type'] == 'months' and vals['frequency'] == 1:
                if vals['billing_day'] < 1 or vals['billing_day'] > 28:
                    raise UserError(f"El Día de Facturacion no puede ser menor que 1 o mayor que 28")
            mp_header = {
                'Authorization': f'Bearer {mp_api_key.value}',
                'Content_Type': 'application/json'
            }
            #Diccionario de datos que se envia a MercadoPago para crear una nueva Suscripción
            try:
                vals['billing_day_proportional']
            except:
                vals['billing_day_proportional'] = False
            mp_json = {
                    "reason": vals['reason'],
                    "external_reference": vals['external_reference'],
                    "auto_recurring": {
                        "frequency": vals['frequency'],
                        "frequency_type": vals['frequency_type'],
                        #"repetitions": '' if vals['repetitions'] == False else vals['repetitions'],
                        "billing_day": vals['billing_day'],
                        "billing_day_proportional": vals['billing_day_proportional'],
                        "transaction_amount": vals['transaction_amount'],
                        "currency_id": vals['currency_id']
                        },
                    "payment_methods_allowed": {
                        "payment_types": [
                            {}
                        ],
                        "payment_methods": [
                            {}
                        ]
                        },
                    "back_url": vals['back_url']
                }
            #if vals['has_free_trial'] == True:
            #    mp_json['free_trial'] = {
            #        "frequency": vals['free_trial_frequency'],
            #        "frequency_type": vals['free_trial_frequency_type']
            #    }
            if vals['frequency_type'] == 'days':
                mp_json['auto_recurring'].pop('billing_day')
            mp_request = requests.post("https://api.mercadopago.com/preapproval_plan",headers=mp_header, json=mp_json)
            mp_request = mp_request.json()
            if mp_request:
                if mp_request.get('status') != 'active':
                    raise ValidationError(f"Ocurrion un error de validacion con MercadoPago y esto es lo que devolvio: {mp_request.get('message')}")
                else:
                    vals['mp_id'] = mp_request.get('id')
                    vals['reason'] = mp_request.get('reason')
                    vals['application_id'] = mp_request.get('application_id')
                    vals['status'] = mp_request.get('status')
                    vals['subscribed'] = mp_request.get('subscribed')
                    vals['back_url'] = mp_request.get('back_url')
                    vals['collector_id'] = mp_request.get('collector_id')
                    vals['init_point'] = mp_request.get('init_point')
                    vals['date_created'] = self.mp_convert_date(mp_request.get('date_created'))
                    vals['last_modified'] = self.mp_convert_date(mp_request.get('last_modified'))
                    vals['external_reference'] = mp_request.get('external_reference')
                    vals['transaction_amount'] = mp_request.get('transaction_amount')
                    #FREQUENCY
                    vals['frequency'] = mp_request.get('auto_recurring').get('frequency')
                    vals['repetitions'] = mp_request.get('auto_recurring').get('repetitions')
                    vals['currency_id'] = mp_request.get('auto_recurring').get('currency_id')
                    vals['transaction_amount'] = mp_request.get('auto_recurring').get('transaction_amount')
                    vals['frequency_type'] = mp_request.get('auto_recurring').get('frequency_type')
                    vals['billing_day'] = mp_request.get('auto_recurring').get('billing_day')
                    vals['billing_day_proportional'] = mp_request.get('auto_recurring').get('billing_day_proportional')
                    vals['mp_validated'] = True
                    #FREE TRIAL
                try:
                    if mp_request.get('auto_recurring').get('free_trial'):
                        vals['has_free_trial'] = True
                        vals['free_trial_frequency'] = mp_request.get('auto_recurring').get('free_trial').get('frequency')
                        vals['free_trial_frequency_type'] = mp_request.get('auto_recurring').get('free_trial').get('frequency_type')
                except:
                    print(f"La subscripcion {mp_request.get('reason')} no tiene un periodo de prueba.")
                    vals['has_free_trial'] = False
                    vals['free_trial_frequency'] = mp_request.get('auto_recurring').get('free_trial').get('frequency')
                    vals['free_trial_frequency_type'] = mp_request.get('auto_recurring').get('free_trial').get('frequency_type')
                return super(bf_mercadopago_subscriptions, self).create(vals)
            else:
                raise ValidationError("No se recibio respuesta de MercadoPago")
        #return super(bf_mercadopago_subscriptions, self).create(vals)
        
    
    #TODO
    #TRANSFORMAR LAS FECHAS A LA ZONA HORARIA, CREO QUE LO PUEDE HACER EL ODOO SOLO, HAY QUE REVISAR.
    #Dejar que pase el constraint de "Dia de Facturacion" si es que el tipo de frecuencia no esta en "meses" o si esta en "meses" y frecuencia es mayor a 1