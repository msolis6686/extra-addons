from odoo import models, api, _, fields
from odoo.exceptions import UserError
from odoo.tools import html2plaintext, plaintext2html
from odoo.tools.mimetypes import guess_mimetype
from odoo.tools import config, human_size, ustr, html_escape

import os
import re
import base64
import logging

_logger = logging.getLogger(__name__)

class bf_whatsapp_create_messages(models.TransientModel):
    _name = 'bf.whatsapp.create.messages'
    _description = 'Whatsapp envio de facturas'

    def get_model(self):
        return self.env.context.get('model')
    
    message = fields.Text(string='Mensaje a enviar...')
    template_id = fields.Many2one('bf.whatsapp.templates', 'Use template')
    model = fields.Char('Related Document Model',default=get_model)
    
    @api.model
    def _storage(self):
        return self.env['ir.config_parameter'].sudo().get_param('ir_attachment.location', 'file')

    @api.model
    def _filestore(self):
        return config.filestore(self._cr.dbname)

    @api.model
    def _full_path(self, path):
        # sanitize 
        pathpath = re.sub('[.]', '', path)
        path = path.strip('/\\')
        return os.path.join(self._filestore(), path)

    @api.model
    def _file_read(self, fname):
        full_path = self._full_path(fname)
        try:
            with open(full_path, 'rb') as f:
                return f.read()
        except (IOError, OSError):
            _logger.info("_read_file reading %s", full_path, exc_info=True)
        return b''    
    
    @api.onchange('template_id')
    def onchange_template_id_wrapper(self):
        #self.ensure_one()
        self.message = self.template_id.message        
            
            
    def _model_context(self):
        self._context.get('active_model')
            
    def prepare_messages(self):
        if self._context.get('active_model') == 'account.move':
            domain = [('id', 'in', self._context.get('active_ids', []))]
        elif self._context.get('active_model') == 'account.journal':
            domain = [('journal_id', '=', self._context.get('active_id'))]
        else:
            raise UserError(_("Missing 'active_model' in context."))

        moves = self.env['account.move'].search(domain).filtered('line_ids')

        if not moves:
            raise UserError(_('There are no journal items in the draft state to post.'))
        
        self.message = self.template_id.message
        client_omitted = []
        mobile_omitted = []
        i=0
        j=0
        for reg in moves:
            client = reg.partner_id.name.strip()
            phone = reg.partner_id.wa_mobile
            invoice = reg.name.strip()
            reference = reg.invoice_origin.strip() if reg.invoice_origin else False
            total = reg.amount_total
            symbol = reg.currency_id.symbol
            company = reg.company_id.name
            mensaje = self.message
            #Recupero el reporte que hay que enviar en caso de que exista
            is_attachment_exists = False
            if self.template_id.attachment_file:
                Attachment = self.env['ir.attachment']
                res_name = 'Factura_' + reg.name.replace('/', '_')
                domain = [('res_id', '=', reg.id), ('name', 'like', res_name + '%'), ('res_model', '=', self.model)]
                is_attachment_exists = Attachment.search(domain, limit=1)
            #Si existe el reporte, lo appendeo a los archivos a enviar
            atta = self.env['ir.attachment']
            atta = self.template_id.attachment_ids

            logging.info("Reporte existe?: " + str(is_attachment_exists))
            if is_attachment_exists:
                atta += is_attachment_exists
            else:
                #pass
                logging.info("El reporte no existe, creando...")
                template = self.template_id
                report = template.report_template
                report_service = report.report_name
                if report.report_type not in ['qweb-html', 'qweb-pdf']:
                    raise UserError(_('Unsupported report type %s found.') % report.report_type)
                res, format = report.render_qweb_pdf([reg.id])
                b64_pdf = base64.b64encode(res)
                if not res_name:
                    res_name = 'report.' + report_service
                ext = "." + format
                if not res_name.endswith(ext):
                    res_name += ext
                
                att_id = self.env['ir.attachment'].create({
                'name': res_name,
                'type': 'binary',
                'datas': b64_pdf,
                'res_model': 'account.move',
                'res_id': reg.id,
                'mimetype': 'application/x-pdf'
                })
                
                atta += att_id
            
            mensaje = mensaje.replace('{company_name}',company)
            mensaje = mensaje.replace('{partner_name}',client)
            mensaje = mensaje.replace('{invoice}',invoice) 
            mensaje = mensaje.replace('{reference}',reference) if reference else mensaje.replace('{reference}',"")
            mensaje = mensaje.replace('{total}',str(total)) 
            mensaje = mensaje.replace('{symbol}',str(symbol))
                
            if phone and len(phone) >= 8:
                phone = str(phone)
                phone = phone.replace(" ", "").replace("+","").replace("-","")
                
                #PREGUNTO SI EL NÚMERO TIENE EL CÓDIGO DEL PAIS, SINO LO TIENE LO AGREGA.
                cod_pais = phone[:2]
                if cod_pais != "54":
                    phone = "54" + phone
                
                msj_wa = self.env['bf.whatsapp.message']
                r = msj_wa.create({
                    'name':reg.partner_id.id,
                    'message':mensaje,
                    'phone':phone,
                    'attachment_ids': atta                    
                })     
                i=i+1           
            else:
                j=j+1
                client_omitted.append(client)
                mobile_omitted.append(phone)
                #raise UserError(_(f'El cliente {client} no tiene un número de celular asignado o es incorrecto - Móvil: {phone}'))
        s_mjs = f"Mensajes creados correctamente: {i}\n"
        e_mjs = f"Mensajes Omitidos: {j} (núm. False)\n"
        c_mjs = "Clientes: "
        for c in client_omitted:
            c_mjs = c_mjs + f"{c}" + ", "        
        if j == 0:
            message = s_mjs
        else:
            message = s_mjs + e_mjs + c_mjs

        """ return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Mensajes Creados"),
                "message": message,
                "sticky": True,
                }
            } """