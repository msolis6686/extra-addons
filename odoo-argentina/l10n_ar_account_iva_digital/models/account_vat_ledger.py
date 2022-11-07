##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from ast import literal_eval
import base64
import logging
import re
_logger = logging.getLogger(__name__)


class AccountVatLedger(models.Model):
    _inherit = "account.vat.ledger"

    digital_skip_invoice_tests = fields.Boolean(
        string='Saltear tests a facturas?',
        help='If you skip invoice tests probably you will have errors when '
        'loading the files in digital.'
    )
    digital_skip_lines = fields.Char(
        string="Lista de lineas a saltear con los archivos del digital",
        help="Enter a list of lines, for eg '1, 2, 3'. If you skip some lines "
        "you would need to enter them manually"
    )
    REGDIGITAL_CV_ALICUOTAS = fields.Text(
        'REGDIGITAL_CV_ALICUOTAS',
        readonly=True,
    )
    REGDIGITAL_CV_COMPRAS_IMPORTACIONES = fields.Text(
        'REGDIGITAL_CV_COMPRAS_IMPORTACIONES',
        readonly=True,
    )
    REGDIGITAL_CV_CBTE = fields.Text(
        'REGDIGITAL_CV_CBTE',
        readonly=True,
    )
    REGDIGITAL_CV_CABECERA = fields.Text(
        'REGDIGITAL_CV_CABECERA',
        readonly=True,
    )
    digital_vouchers_file = fields.Binary(
        compute='_compute_digital_files',
        readonly=True
    )
    digital_vouchers_filename = fields.Char(
        compute='_compute_digital_files',
    )
    digital_aliquots_file = fields.Binary(
        compute='_compute_digital_files',
        readonly=True
    )
    digital_aliquots_filename = fields.Char(
        readonly=True,
        compute='_compute_digital_files',
    )
    digital_import_aliquots_file = fields.Binary(
        compute='_compute_digital_files',
        readonly=True
    )
    digital_import_aliquots_filename = fields.Char(
        readonly=True,
        compute='_compute_digital_files',
    )
    prorate_tax_credit = fields.Boolean(
    )

    def format_amount(self, amount, padding=15, decimals=2, invoice=False):
        # get amounts on correct sign despite conifiguration on taxes and tax
        # codes
        # TODO
        # remove this and perhups invoice argument (we always send invoice)
        # for invoice refund we dont change sign (we do this before)
        # if invoice:
        #     amount = abs(amount)
        #     if invoice.type in ['in_refund', 'out_refund']:
        #         amount = -1.0 * amount
        # Al final volvimos a agregar esto, lo necesitabamos por ej si se pasa
        # base negativa de no gravado
        # si se usa alguno de estos tipos de doc para rectificativa hay que pasarlos restando
        # seguramente para algunos otros tambien pero realmente no se usan y el digital tiende a depreciarse
        # y el uso de internal_type a cambiar
        if invoice and invoice.l10n_latam_document_type_id.code in ['39', '40', '41', '66', '99'] \
           and invoice.type in ['in_refund', 'out_refund']:
            amount = -amount

        if amount < 0:
            template = "-{:0>%dd}" % (padding - 1)
        else:
            template = "{:0>%dd}" % (padding)
        return template.format(
            int(round(abs(amount) * 10**decimals, decimals)))

    def _compute_digital_files(self):
        self.ensure_one()
        # segun vimos aca la afip espera "ISO-8859-1" en vez de utf-8
        # http://www.planillasutiles.com.ar/2015/08/
        # como-descargar-los-archivos-de.html
        if self.REGDIGITAL_CV_ALICUOTAS:
            self.digital_aliquots_filename = _('Alicuots_%s_%s.txt') % (
                self.type,
                self.date_to,
                # self.period_id.name
            )
            #self.digital_aliquots_file = base64.encodestring(
            #    self.REGDIGITAL_CV_ALICUOTAS.encode('ISO-8859-1'))
            self.digital_aliquots_file = base64.encodebytes(
                self.REGDIGITAL_CV_ALICUOTAS.encode('ISO-8859-1'))
        else:
            self.digital_aliquots_file = False
            self.digital_aliquots_filename = False
        if self.REGDIGITAL_CV_COMPRAS_IMPORTACIONES:
            self.digital_import_aliquots_filename = _('Import_Alicuots_%s_%s.txt') % (
                self.type,
                self.date_to,
                # self.period_id.name
            )
            self.digital_import_aliquots_file = base64.encodestring(
                self.REGDIGITAL_CV_COMPRAS_IMPORTACIONES.encode('ISO-8859-1'))
        else:
            self.digital_import_aliquots_file = False
            self.digital_import_aliquots_filename = False
        if self.REGDIGITAL_CV_CBTE:
            self.digital_vouchers_filename = _('Vouchers_%s_%s.txt') % (
                self.type,
                self.date_to,
                # self.period_id.name
            )
            self.digital_vouchers_file = base64.encodebytes(
                self.REGDIGITAL_CV_CBTE.encode('ISO-8859-1'))
        else:
            self.digital_vouchers_file = False
            self.digital_vouchers_filename = False


    def compute_digital_data(self):
        # computamos comprobantes = self.get_REGDIGITAL_CV_CBTE()
        cbtes = self.get_REGDIGITAL_CV_CBTE()
        self.REGDIGITAL_CV_CBTE = '\r\n'.join(cbtes)

        alicuotas = self.get_REGDIGITAL_CV_ALICUOTAS()
        # sacamos todas las lineas y las juntamos
        self.REGDIGITAL_CV_ALICUOTAS = '\r\n'.join(alicuotas)

    def get_partner_document_code(self, partner):
        # se exige cuit para todo menos consumidor final.
        # TODO si es mayor a 1000 habria que validar reportar
        # DNI, LE, LC, CI o pasaporte
        if partner.l10n_ar_afip_responsibility_type_id.code == '5':
            #return "{:0>2d}".format(partner.l10n_latam_identification_type_id.l10n_ar_afip_code)
            res = str(partner.l10n_latam_identification_type_id.l10n_ar_afip_code).zfill(2)
            return res
        return '80'

    @api.model
    def get_partner_document_number(self, partner):
        # se exige cuit para todo menos consumidor final.
        # TODO si es mayor a 1000 habria que validar reportar
        # DNI, LE, LC, CI o pasaporte
        #if partner.l10n_ar_afip_responsibility_type_id.l10n_ar_afip_code == '5':
        if partner.l10n_ar_afip_responsibility_type_id.code == '5':
            number = partner.vat or ''
            # por las dudas limpiamos letras
            number = re.sub("[^0-9]", "", number)
        else:
            #number = partner.cuit_required()
            number = partner.vat
        return number.rjust(20, '0')

    def action_see_skiped_invoices(self):
        invoices = self.get_digital_invoices(return_skiped=True)
        raise ValidationError(_('Facturas salteadas:\n%s') % ', '.join(invoices.mapped('display_name')))

    @api.constrains('digital_skip_lines')
    def _check_digital_skip_lines(self):
        for rec in self.filtered('digital_skip_lines'):
            try:
                res = literal_eval(rec.digital_skip_lines)
                if not isinstance(res, int):
                    assert isinstance(res, tuple)
            except Exception as e:
                raise ValidationError(_(
                    'Bad format for Skip Lines. You need to enter a list of '
                    'numbers like "1, 2, 3". This is the error we get: %s') % (
                        repr(e)))

    def get_digital_invoices(self, return_skiped=False):
        self.ensure_one()
        invoices = self.env['account.move'].search([
            ('l10n_latam_document_type_id.export_to_digital', '=', True),
            ('id', 'in', self.invoice_ids.ids)], order='invoice_date asc')
        if self.digital_skip_lines:
            skip_lines = literal_eval(self.digital_skip_lines)
            if isinstance(skip_lines, int):
                skip_lines = [skip_lines]
            to_skip = invoices.browse()
            for line in skip_lines:
                to_skip += invoices[line - 1]
            if return_skiped:
                return to_skip
            invoices -= to_skip
        return invoices

    def get_REGDIGITAL_CV_CBTE(self):
        self.ensure_one()
        res = []
        for inv in self.invoice_ids:
            line = ''
            if self.type == 'sale':
                # Fecha de comprobante
                line = line + inv.invoice_date.strftime('%Y%m%d')
                # Tipo de comprobante
                line = line + inv.l10n_latam_document_type_id.code.zfill(3)
                # Punto de venta
                pos, number = inv.name[5:].split('-')
                line = line + pos
                # Numero de comprobante
                line = line + number.zfill(20)
                # Numero de comprobante hasta
                line = line + number.zfill(20)
                # Codigo de documento del comprador
                line = line + self.get_partner_document_code(inv.partner_id)
                # Apellido y nombre o denominación del comprador
                line = line + inv.partner_id.name.encode('ascii', 'replace').decode('ascii').ljust(30,' ')
                # Importe total de la operacion
                line = line + self.format_amount(inv.amount_total)
                # Importe total de conceptos que no integran el precio neto gravado
                net_amount = 0
                for inv_line in inv.invoice_line_ids:
                    if not inv_line.tax_ids:
                        net_amount = net_amount + inv_line.price_subtotal
                line = line + self.format_amount(net_amount)
                # Percepción a no categorizados
                line = line + self.format_amount(0)
                # Importe de operaciones exentas
                exempt_amount = sum(inv.move_tax_ids.filtered(lambda l: l.tax_id.tax_group_id.tax_type == 'vat' and l.tax_id.amount == 0).mapped('base_amount'))
                line = line + self.format_amount(exempt_amount)
                # Importe de percepciones o pagos a cuenta de impuestos Nacionales
                perception_amount = sum(inv.move_tax_ids.filtered(lambda l: l.tax_id.tax_group_id.tax_type == 'withholdings' \
                        and l.tax_id.tax_group_id.l10n_ar_tribute_afip_code in ['01','06']).mapped('tax_amount'))
                line = line + self.format_amount(perception_amount)
                # Importe de percepciones de Ingresos Brutos 
                perception_amount = sum(inv.move_tax_ids.filtered(lambda l: l.tax_id.tax_group_id.tax_type == 'withholdings' \
                        and l.tax_id.tax_group_id.l10n_ar_tribute_afip_code in ['07']).mapped('tax_amount'))
                line = line + self.format_amount(perception_amount)
                # Importe de percepciones de Impuestos Municipales
                perception_amount = sum(inv.move_tax_ids.filtered(lambda l: l.tax_id.tax_group_id.tax_type == 'withholdings' \
                        and l.tax_id.tax_group_id.l10n_ar_tribute_afip_code in ['03']).mapped('tax_amount'))
                line = line + self.format_amount(perception_amount)
                # Importe de percepciones de Impuestos Internos
                perception_amount = sum(inv.move_tax_ids.filtered(lambda l: l.tax_id.tax_group_id.tax_type == 'withholdings' \
                        and l.tax_id.tax_group_id.l10n_ar_tribute_afip_code in ['04']).mapped('tax_amount'))
                line = line + self.format_amount(perception_amount)
                # Codigo de moneda
                line = line + inv.currency_id.afip_code
                # Tipo de cambio 
                if inv.l10n_ar_currency_rate > 0:
                    line = line + self.format_amount(1 / inv.l10n_ar_currency_rate)
                else:
                    line = line + self.format_amount(0)
                # Cantidad de alícuotas de IVA
                cantidad = len(inv.move_tax_ids.filtered(lambda l: l.tax_id.tax_group_id.tax_type == 'vat'))
                line = line + str(cantidad)
                # Codigo de operacion
                line = line + '0'
                # Otros Tributos
                line = line + self.format_amount(0)
                # Fecha de vencimiento 
                line = line + inv.invoice_date_due.strftime('%Y%m%d')

            if line != '':
                res.append(line)
        return res

    def get_REGDIGITAL_CV_ALICUOTAS(self, impo=False):
        """
        Devolvemos un dict para calcular la cantidad de alicuotas cuando
        hacemos los comprobantes
        """
        self.ensure_one()
        res = []
        # only vat taxes with codes 3, 4, 5, 6, 8, 9
        # segun: http://contadoresenred.com/regimen-de-informacion-de-
        # compras-y-ventas-rg-3685-como-cargar-la-informacion/
        # empezamos a contar los codigos 1 (no gravado) y 2 (exento)
        # si no hay alicuotas, sumamos una de esta con 0, 0, 0 en detalle
        # usamos mapped por si hay afip codes duplicados (ej. manual y
        # auto)
        for inv in self.invoice_ids:
            line = ""
            if self.type == 'sale':
                for move_tax in inv.move_tax_ids.filtered(lambda l: l.tax_id.tax_group_id.tax_type == 'vat').sorted(lambda l: l.tax_id.tax_group_id.l10n_ar_vat_afip_code):
                    # Tipo de comprobante
                    line = line + inv.l10n_latam_document_type_id.code.zfill(3)
                    # Punto de venta
                    pos, number = inv.name[5:].split('-')
                    line = line + pos
                    # Numero de comprobante
                    line = line + number.zfill(20)
                    # Importe neto gravado
                    line = line + self.format_amount(move_tax.base_amount)
                    # Alicuota de IVA
                    line = line + move_tax.tax_id.tax_group_id.l10n_ar_vat_afip_code.zfill(4)
                    # Impuesto liquidado
                    line = line + self.format_amount(move_tax.tax_amount)
            if self.type == 'purchase':
                for move_tax in inv.move_tax_ids.filtered(lambda l: l.tax_id.tax_group_id.tax_type == 'vat').sorted(lambda l: l.tax_id.tax_group_id.l10n_ar_vat_afip_code):
                    # Tipo de comprobante
                    line = line + inv.l10n_latam_document_type_id.code.zfill(3)
                    # Punto de venta
                    pos, number = inv.name[5:].split('-')
                    line = line + pos
                    # Numero de comprobante
                    line = line + number.zfill(20)
                    # Codigo de documento del comprador
                    line = line + self.get_partner_document_code(inv.partner_id)
                    # Nro de identificacion del comprador
                    line = line + inv.partner_id.vat.zfill(20)
                    # Importe neto gravado
                    line = line + self.format_amount(move_tax.base_amount)
                    # Alicuota de IVA
                    line = line + move_tax.tax_id.tax_group_id.l10n_ar_vat_afip_code.zfill(4)
                    # Impuesto liquidado
                    line = line + self.format_amount(move_tax.tax_amount)
            res.append(line)
        return res
