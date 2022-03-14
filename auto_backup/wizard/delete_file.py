import os
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date, datetime
from icecream import ic
import logging
_logger = logging.getLogger(__name__)

class DeleteFileWizard(models.TransientModel):
    _name = "delete.file.wizard"
    _description = "Eliminar archivo de copias de base de datos"

    def get_file_path(self):
        return self.env.context.get("file_path")
    
    def get_name(self):
        return self.env.context.get("name")
    
    def get_folder(self):
        return self.env.context.get("folder")
    
    def get_aviso(self):
        return f"{self.env.context.get('name')}"
    
    name = fields.Char(string='Nombre de Archivo', default=get_name)
    file_path = fields.Char(string='Ruta', default=get_file_path)
    folder = fields.Char(string='Carpeta', default=get_folder)
    aviso = fields.Char(string='aviso', default=get_aviso)
    
    def action_done(self):
        file_path = self.file_path
        _logger.info("------------ %r ----------------"%file_path)
        try:
            os.remove(file_path)
        except Exception as e:
            print (e)
            raise ValidationError(f'Error: {e}')

        aux = self.env["db.backupform"].search([('id','=',self.env.context.get("parent_id"))])
        view_id = self.env.ref('auto_backup.view_backup_list_form').id#Este dato lo sacamos de Ajustes/Tecnico/Vistas. Es el ID externo
        return {'type': 'ir.actions.act_window',#El type tiene que ser el mismo que usa el wizard (act_window)
                'name': _('Ver y Descargar Backups'),#Nombre que va a tener el wizard.
                'res_model': 'db.backupform',#El modelo del wizard o de la vista (se lo puede sacar del codigo, es el campo _name="nombre")
                'target': 'current',#New para que se abra una nueva ventana (el wizard)
                'view_mode': 'form',#Modo de vista (formulario para el wizard)
                'views': [[view_id, 'form']],#El id externo de la vista que definimos en la variable mas arriba y el 'form' o tree segun necesitemos
                },aux.list_db_file()
                