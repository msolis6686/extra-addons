# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError,ValidationError
from dateutil.relativedelta import relativedelta
import datetime
from datetime import date


class AccountTax(models.Model):
    _inherit = "account.tax"

    amount_type = fields.Selection(
        selection_add=([
            ('partner_tax', 'Alícuota en el Partner'),
        ])
    )
    withholding_type = fields.Selection(
        selection_add=([
            ('tabla_ganancias', 'Tabla Ganancias'),
            ('partner_tax', 'Alícuota en el Partner'),
        ])
    )
    # default_alicuot = fields.Float(
    #     'Alícuota por defecto',
    #     help="Alícuota por defecto para los partners que no figuran en el "
    #     "padrón"
    # )
    # default_alicuot_copy = fields.Float(
    #     related='default_alicuot',
    # )

    @api.constrains('amount_type', 'withholding_type')
    def check_partner_tax_tag(self):
        recs = self.filtered(lambda x: ((
                x.type_tax_use in ['sale', 'purchase'] and
                x.amount_type == 'partner_tax') or (
                x.type_tax_use in ['customer', 'supplier'] and
                x.withholding_type == 'partner_tax')) and not x.tag_ids)
        if recs:
            raise UserError(_(
                'Si utiliza Cálculo de impuestos igual a "Alícuota en el '
                'Partner", debe setear al menos una etiqueta en el impuesto y'
                ' utilizar esa misma etiqueta en las alícuotas configuradas en'
                ' el partner. Revise los impuestos con id: %s') % recs.ids)

    def get_period_payments_domain(self, payment_group):
        previos_payment_groups_domain, previos_payments_domain = super(
            AccountTax, self).get_period_payments_domain(payment_group)
        if self.withholding_type == 'tabla_ganancias':
            previos_payment_groups_domain += [
                ('regimen_ganancias_id', '=',
                    payment_group.regimen_ganancias_id.id)]
            previos_payments_domain += [
                ('payment_group_id.regimen_ganancias_id', '=',
                    payment_group.regimen_ganancias_id.id)]
        return (
            previos_payment_groups_domain,
            previos_payments_domain)

    def get_withholding_vals(self, payment_group):
        commercial_partner = payment_group.commercial_partner_id

        force_withholding_amount_type = None
        if self.withholding_type == 'partner_tax':
            alicuot_line = self.get_partner_alicuot(
                commercial_partner,
                payment_group.payment_date or fields.Date.context_today(self),
            )
            alicuota = alicuot_line.alicuota_retencion / 100.0
            force_withholding_amount_type = alicuot_line.withholding_amount_type

        vals = super(AccountTax, self).get_withholding_vals(
            payment_group, force_withholding_amount_type)
        base_amount = vals['withholdable_base_amount']

        if self.withholding_type == 'partner_tax':
            amount = base_amount * (alicuota)
            vals['comment'] = "%s x %s" % (
                base_amount, alicuota)
            vals['period_withholding_amount'] = amount
        elif self.withholding_type == 'tabla_ganancias':
            regimen = payment_group.regimen_ganancias_id
            imp_ganancias_padron = commercial_partner.imp_ganancias_padron
            if (
                    payment_group.retencion_ganancias != 'nro_regimen' or
                    not regimen):
                # if amount zero then we dont create withholding
                amount = 0.0
            elif not imp_ganancias_padron:
                raise UserError(
                    'El partner %s no tiene configurada inscripcion en '
                    'impuesto a las ganancias' % commercial_partner.name)
            elif imp_ganancias_padron in ['EX', 'NC']:
                # if amount zero then we dont create withholding
                amount = 0.0
            # TODO validar excencion actualizada
            elif imp_ganancias_padron == 'AC':
                if base_amount == 0:
                    base_amount = payment_group.to_pay_amount
                # alicuota inscripto
                non_taxable_amount = (
                    regimen.montos_no_sujetos_a_retencion)
                vals['withholding_non_taxable_amount'] = non_taxable_amount
                prev_payments = []
                if self.withholding_accumulated_payments:
                    payment_date = str(payment_group.payment_date)[:8]
                    payment_date = payment_date + '00'
                    payments = self.env['account.payment'].search([('payment_type','=','outbound'),('state','=','posted'),('payment_group_id','!=',payment_group.id),\
                                        ('partner_id','=',payment_group.partner_id.id),('used_withholding','=',False),('payment_group_id.retencion_ganancias','=','nro_regimen')])
                    previous_amount = 0
                    for payment in payments:
                        if payment_group.payment_date.month == payment.payment_group_id.payment_date.month and payment_group.payment_date.year == payment.payment_group_id.payment_date.year:
                            if payment_group.payment_date.day >= payment.payment_group_id.payment_date.day:
                                if payment.payment_group_id and payment.payment_group_id.matched_move_line_ids:
                                    for matched_line in payment.payment_group_id.matched_move_line_ids:
                                        matched_amount = matched_line.move_id._get_tax_factor() * (-1) * matched_line.with_context({'payment_group_id': payment.payment_group_id.id}).payment_group_matched_amount
                                    previous_amount += matched_amount
                                else:
                                    previous_amount += payment.amount
                                    # esta linea MGO
                                prev_payments.append(str(payment.id))
                    base_amount += previous_amount
                    payment_group.write({'temp_payment_ids': ','.join(prev_payments)})

                if base_amount < non_taxable_amount and not prev_payments:
                    base_amount = 0.0
                elif not prev_payments:
                    #raise ValidationError('estamos aca #2')
                    base_amount -= non_taxable_amount
                elif prev_payments:
                    flag_substract = True
                    for idx in prev_payments:
                        prev_pay_obj = self.env['account.payment'].browse(int(idx))
                        if prev_pay_obj.tax_withholding_id:
                            flag_substract = False
                    if flag_substract:
                        #raise ValidationError('estamos aca #3')
                        base_amount -= non_taxable_amount

                vals['withholdable_base_amount'] = base_amount
                escala = self.env['afip.tabla_ganancias.escala'].search([
                        ('importe_desde', '<=', base_amount),
                        ('importe_hasta', '>', base_amount),
                ], limit=1)
                importe_excedente = escala.importe_excedente
                #today = date.today()
                today = payment_group.payment_date
                prev_date = date(today.year,today.month,1)
                prev_payments = self.env['account.payment'].search([('payment_type','=','outbound'),('state','=','posted'),('payment_group_id.payment_date','>=',str(prev_date)),\
                                        ('payment_group_id.payment_date','<=',today),('partner_id','=',payment_group.partner_id.id),('tax_withholding_id','=',self.id)])
                if prev_payments:
                    vals['withholding_non_taxable_amount'] = 0
                    if vals['withholdable_base_amount'] == 0:
                        vals['withholdable_base_amount'] = vals['total_amount']
                    else:
                        vals['withholdable_base_amount'] = vals['withholdable_base_amount'] + payment_group.partner_id.default_regimen_ganancias_id.montos_no_sujetos_a_retencion
                    vals['period_withholding_amount'] = vals['withholdable_base_amount'] * payment_group.partner_id.default_regimen_ganancias_id.porcentaje_inscripto / 100
                    vals['previous_withholding_amount'] = 0
                    base_amount = vals['withholdable_base_amount']
                #raise ValidationError('estamos aca %s %s'%(prev_payments,vals))

                # Changes MGO - base imponible
                withholdable_base_amount = 0
                if not payment_group.debt_move_line_ids:
                    withholdable_base_amount += payment_group.to_pay_amount
                else:
                    for matched_move in payment_group.debt_move_line_ids:
                        matched_amount = matched_move.move_id._get_tax_factor() * (-1) * matched_move.with_context({'payment_group_id': payment_group.id}).amount_residual
                        withholdable_base_amount += matched_amount
                prev_payments = self.env['account.payment'].search([('payment_type','=','outbound'),('state','=','posted'),('payment_group_id.payment_date','>=',str(prev_date)),\
                                        ('payment_group_id.payment_date','<=',today),('partner_id','=',payment_group.partner_id.id)])

                if prev_payments:
                    for prev_payment in prev_payments:
                        if prev_payment.payment_group_id.matched_move_line_ids and prev_payment.payment_group_id.prev_invoices:
                            withholdable_base_amount += prev_payment.amount * prev_payment.payment_group_id.matched_move_line_ids[0].move_id._get_tax_factor()
                            #withholdable_base_amount += prev_payment.amount
                        else:
                            withholdable_base_amount += prev_payment.amount
                non_taxable_amount = payment_group.partner_id.default_regimen_ganancias_id.montos_no_sujetos_a_retencion
                withholdable_base_amount = withholdable_base_amount - non_taxable_amount
                if withholdable_base_amount > 0:
                    period_withholding_amount = withholdable_base_amount * payment_group.partner_id.default_regimen_ganancias_id.porcentaje_inscripto / 100
                else:
                    period_withholding_amount = 0
                prev_payments_with_withholding = self.env['account.payment'].search([('payment_type','=','outbound'),('state','=','posted'),('payment_group_id.payment_date','>=',str(prev_date)),\
                                        ('payment_group_id.payment_date','<=',today),('partner_id','=',payment_group.partner_id.id),('tax_withholding_id','=',self.id)])
                prev_withholdings = 0
                for prev_payment_with_withholding in prev_payments_with_withholding:
                    prev_withholdings += prev_payment_with_withholding.amount
                if period_withholding_amount > 0:
                    period_withholding_amount = period_withholding_amount - prev_withholdings
                if period_withholding_amount < self.withholding_non_taxable_minimum and not prev_payments_with_withholding:
                    period_withholding_amount = 0

                """
                if not payment_group.debt_move_line_ids:
                    withholdable_base_amount += payment_group.to_pay_amount
                else:
                    for matched_move in payment_group.debt_move_line_ids:
                        matched_amount = matched_move.move_id._get_tax_factor() * (-1) * matched_move.with_context({'payment_group_id': payment_group.id}).amount_residual
                        withholdable_base_amount += matched_amount
                #raise ValidationError('estamos aca %s'%(withholdable_base_amount))
                period_withholding_amount = 0
                non_taxable_amount = 0
                non_taxable_amount = payment_group.partner_id.default_regimen_ganancias_id.montos_no_sujetos_a_retencion
                # Agregar soporte a montos netos de facturas
                prev_payments_no_withholding = self.env['account.payment'].search([('payment_type','=','outbound'),('state','=','posted'),('payment_group_id.payment_date','>=',str(prev_date)),\
                                        ('payment_group_id.payment_date','<=',today),('partner_id','=',payment_group.partner_id.id),('tax_withholding_id','!=',self.id)])
                prev_payments_with_withholding = self.env['account.payment'].search([('payment_type','=','outbound'),('state','=','posted'),('payment_group_id.payment_date','>=',str(prev_date)),\
                                        ('payment_group_id.payment_date','<=',today),('partner_id','=',payment_group.partner_id.id),('tax_withholding_id','=',self.id)])
                if not prev_payments_with_withholding :
                    if prev_payments_no_withholding:
                        for prev_payments in prev_payments_no_withholding:
                            if prev_payments.payment_group_id.matched_move_line_ids:
                                withholdable_base_amount += prev_payments.amount * prev_payments.payment_group_id.matched_move_line_ids[0].move_id._get_tax_factor()
                            else:
                                withholdable_base_amount += prev_payments.amount
                    withholdable_base_amount = withholdable_base_amount - non_taxable_amount
                if withholdable_base_amount > 0:
                    period_withholding_amount = withholdable_base_amount * payment_group.partner_id.default_regimen_ganancias_id.porcentaje_inscripto / 100
                if period_withholding_amount < self.withholding_non_taxable_minimum and not prev_payments_with_withholding:
                    period_withholding_amount = 0
                """
                vals['withholdable_base_amount'] = withholdable_base_amount
                vals['period_withholding_amount'] = period_withholding_amount



                if regimen.porcentaje_inscripto == -1:
                    # hacemos <= porque si es 0 necesitamos que encuentre
                    # la primer regla (0 es en el caso en que la no
                    # imponible sea mayor)
                    escala = self.env['afip.tabla_ganancias.escala'].search([
                        ('importe_desde', '<=', base_amount),
                        ('importe_hasta', '>', base_amount),
                    ], limit=1)
                    if not escala:
                        raise UserError(
                            'No se encontro ninguna escala para el monto'
                            ' %s' % (base_amount))
                    amount = escala.importe_fijo
                    #amount += (escala.porcentaje / 100.0) * (
                    #    base_amount - escala.importe_excedente)
                    amount += (escala.porcentaje / 100.0) * (
                        base_amount - importe_excedente)
                    #vals['comment'] = "%s + (%s x %s)" % (
                    #    escala.importe_fijo,
                    #    base_amount - escala.importe_excedente,
                    #    escala.porcentaje / 100.0)
                    vals['comment'] = "%s + (%s x %s)" % (
                        escala.importe_fijo,
                        base_amount - importe_excedente,
                        escala.porcentaje / 100.0)
                else:
                    # raise ValidationError('llegamos aca')
                    #amount = base_amount * (
                    #    regimen.porcentaje_inscripto / 100.0)
                    amount = period_withholding_amount
                    vals['comment'] = "%s x %s" % (
                        base_amount, regimen.porcentaje_inscripto / 100.0)
            elif imp_ganancias_padron == 'NI':
                # alicuota no inscripto
                amount = base_amount * (
                    regimen.porcentaje_no_inscripto / 100.0)
                vals['comment'] = "%s x %s" % (
                    base_amount, regimen.porcentaje_no_inscripto / 100.0)
            # TODO, tal vez sea mejor utilizar otro campo?
            vals['communication'] = "%s - %s" % (
                regimen.codigo_de_regimen, regimen.concepto_referencia)
            #if amount < self.withholding_non_taxable_minimum:
            #    amount = 0

            # vals['period_withholding_amount'] = amount
        # raise ValidationError('estamos aca %s'%(vals))
        return vals

    def get_partner_alicuota_percepcion(self, partner, date):
        if partner and date:
            arba = self.get_partner_alicuot(partner, date)
            return arba.alicuota_percepcion / 100.0
        return 0.0

    def get_partner_alicuot(self, partner, date):
        self.ensure_one()
        commercial_partner = partner.commercial_partner_id
        company = self.company_id
        alicuot = partner.arba_alicuot_ids.search([
            ('tag_id', 'in', self.tag_ids.ids),
            ('company_id', '=', company.id),
            ('partner_id', '=', commercial_partner.id),
            '|',
            ('from_date', '=', False),
            ('from_date', '<=', date),
            '|',
            ('to_date', '=', False),
            ('to_date', '>=', date),
        ], limit=1)
        # solo buscamos en padron para estas responsabilidades
        if not alicuot and \
                commercial_partner.afip_responsability_type_id.code in \
                ['1', '1FM', '2', '3', '4', '6', '11', '13']:
            date_date = fields.Date.from_string(date)
            from_date = (date_date + relativedelta(day=1)).strftime('%Y%m%d')
            to_date = (date_date + relativedelta(
                day=1, days=-1, months=+1)).strftime('%Y%m%d')

            agip_tag = self.env.ref('l10n_ar_account.tag_tax_jurisdiccion_901')
            arba_tag = self.env.ref('l10n_ar_account.tag_tax_jurisdiccion_902')
            if arba_tag and arba_tag.id in self.tag_ids.ids:
                arba_data = company.get_arba_data(
                    commercial_partner,
                    from_date, to_date,
                )

                # si no hay numero de comprobante entonces es porque no
                # figura en el padron, aplicamos alicuota no inscripto
                if not arba_data['numero_comprobante']:
                    arba_data['numero_comprobante'] = \
                        'Alícuota no inscripto'
                    arba_data['alicuota_retencion'] = \
                        company.arba_alicuota_no_sincripto_retencion
                    arba_data['alicuota_percepcion'] = \
                        company.arba_alicuota_no_sincripto_percepcion

                arba_data['partner_id'] = commercial_partner.id
                arba_data['company_id'] = company.id
                arba_data['tag_id'] = arba_tag.id
                alicuot = partner.arba_alicuot_ids.sudo().create(arba_data)
            elif agip_tag and agip_tag.id in self.tag_ids.ids:
                agip_data = company.get_agip_data(
                    commercial_partner,
                    date,
                )
                # si no hay numero de comprobante entonces es porque no
                # figura en el padron, aplicamos alicuota no inscripto
                if not agip_data['numero_comprobante']:
                    agip_data['numero_comprobante'] = \
                        'Alícuota no inscripto'
                    agip_data['alicuota_retencion'] = \
                        company.agip_alicuota_no_sincripto_retencion
                    agip_data['alicuota_percepcion'] = \
                        company.agip_alicuota_no_sincripto_percepcion
                agip_data['from_date'] = from_date
                agip_data['to_date'] = to_date
                agip_data['partner_id'] = commercial_partner.id
                agip_data['company_id'] = company.id
                agip_data['tag_id'] = agip_tag.id
                alicuot = partner.arba_alicuot_ids.sudo().create(agip_data)
        return alicuot

    def _compute_amount(
            self, base_amount, price_unit, quantity=1.0, product=None,
            partner=None):
        if self.amount_type == 'partner_tax':
            # TODO obtener fecha de otra manera?
            try:
                date = self._context.date_invoice
            except Exception:
                date = fields.Date.context_today(self)
            return base_amount * self.get_partner_alicuota_percepcion(
                partner, date)
        else:
            return super(AccountTax, self)._compute_amount(
                base_amount, price_unit, quantity, product, partner)
