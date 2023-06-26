from email.policy import default
import os
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date, datetime
#from icecream import ic
import logging
_logger = logging.getLogger(__name__)

class DeleteFileBulkWizard(models.TransientModel):
    _name = "delete.file.bulk.wizard"
    _description = "Eliminar archivo por lote de backups."

    def get_backups_to_delete(self):
        return self.env.context.get("bulk_id")
    
    def get_qty_to_delete(self):
        counter = 0
        record = self.env['db.backupform'].search([('id','=',self.env.context.get("bulk_id"))])
        for checked in record.list_files:
            if checked.checkbox == True:
                counter = counter + 1
        return counter

    bulk_delete_id = fields.Integer(string='Id de Record', default=get_backups_to_delete)
    archivos = fields.Integer(string='Cantidad de Archivos', default=get_qty_to_delete)
    
    #En el modelo de la vista formulario lista, la variable de la caja de seleccion para revisar si se va a borrar el registro se llama "checkbox"
    def bulk_delete(self):
        record = self.env['db.backupform'].search([('id','=',self.bulk_delete_id)])
        for to_delete in record.list_files:
            if to_delete.checkbox == True:#Si checkbox esta como True, se borra el archivo.
                file_path = to_delete.file_path
                _logger.info("------------ %r ----------------"%file_path)
                try:
                    os.remove(file_path)
                except Exception as e:
                    print (e)
                    raise ValidationError(f'Error: {e}')

        aux = self.env["db.backupform"].search([('id','=',self.env.context.get("bulk_id"))])
        view_id = self.env.ref('auto_backup.view_backup_list_form').id#Este dato lo sacamos de Ajustes/Tecnico/Vistas. Es el ID externo
        return {'type': 'ir.actions.act_window',#El type tiene que ser el mismo que usa el wizard (act_window)
                'name': _('Ver y Descargar Backups'),#Nombre que va a tener el wizard.
                'res_model': 'db.backupform',#El modelo del wizard o de la vista (se lo puede sacar del codigo, es el campo _name="nombre")
                'target': 'current',#New para que se abra una nueva ventana (el wizard)
                'view_mode': 'form',#Modo de vista (formulario para el wizard)
                'views': [[view_id, 'form']],#El id externo de la vista que definimos en la variable mas arriba y el 'form' o tree segun necesitemos
                },aux.list_db_file(),aux.check_bulk_delete()
                #Se llama a la funcion list_db_file para actualizar el listado de las DBs u el check_bulk_delete para que se vuelvan a falso todos los 
                #archivos tildados anteriormente para evitar confusiones.