# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json
import base64
from icecream import ic

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    def _get_name_invoice(self):
        aux = self.name
        ic(self.l10n_latam_document_type_id)
        if (self.l10n_latam_document_type_id.id in [3,8,13,35]):
            name = f"{aux} ({self.invoice_origin})"
        else:
            name=aux
        return name

    def _get_tax_details(self):
        taxs = self.env['account.tax'].search([('type_tax_use','=','sale'),('amount_type','=','percent')],order='amount desc')
        tax_data = []
        for t in taxs:
            tax_data.append(0)
        for t in self.move_tax_ids:
            i = 0
            for j in taxs:
                if j.id == t.tax_id.id:
                    tax_data[i] = t.tax_amount
                i += 1
        return tax_data

    def _compute_json_qr(self):
        for rec in self:
            dict_invoice = ''
            if rec.type in ['out_invoice','out_refund'] and rec.state == 'posted' and rec.afip_auth_code != '':
                try:
                    dict_invoice = {
                        "ver": 1,
                        "fecha": str(rec.invoice_date),
                        "cuit": int(rec.company_id.partner_id.vat),
                        "ptoVta": rec.journal_id.l10n_ar_afip_pos_number,
                        "tipoCmp": int(rec.l10n_latam_document_type_id.code),
                        "nroCmp": int(rec.name.split('-')[2]),
                        "importe": rec.amount_total,
                        "moneda": rec.currency_id.l10n_ar_afip_code,
                        "ctz": rec.l10n_ar_currency_rate,
                        "tipoDocRec": int(rec.partner_id.l10n_latam_identification_type_id.l10n_ar_afip_code),
                        "nroDocRec": int(rec.partner_id.vat),
                        "tipoCodAut": 'E',
                        "codAut": rec.afip_auth_code,
                        }
                except:
                    dict_invoice = 'ERROR'
                    pass
                res = str(dict_invoice).replace("", "")
            else:
                res = 'N/A'
            rec.json_qr = res
            if type(dict_invoice) == dict:
                enc = res.encode('utf-8')
                b64 = base64.b64encode(enc)
                rec.texto_modificado_qr = 'https://www.afip.gob.ar/fe/qr/?p=' + str(b64, 'utf-8')
                self.qr_boleta_servicio = rec.texto_modificado_qr
            else:
                rec.texto_modificado_qr = 'https://www.afip.gob.ar/fe/qr/?ERROR'
                self.qr_boleta_servicio = rec.texto_modificado_qr

    json_qr = fields.Char("JSON QR AFIP",compute=_compute_json_qr)
    texto_modificado_qr = fields.Char('Texto Modificado QR',compute=_compute_json_qr)   
    
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _compute_price_subtotal_vat(self):
        for line in self:
            if line.tax_ids:
                for tax_id in line.tax_ids:
                    if tax_id.tax_group_id.tax_type == 'vat':
                        line.price_subtotal_vat = line.price_subtotal * \
                            (1 + tax_id.amount / 100)
                    else:
                        line.price_subtotal_vat = line.price_subtotal
            else:
                line.price_subtotal_vat = 0

    price_subtotal_vat = fields.Float(
        'price_subtotal_vat', compute=_compute_price_subtotal_vat)