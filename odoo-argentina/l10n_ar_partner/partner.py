# -*- coding: utf-8 -*-

from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    internal_reference = fields.Char('Nombre de Fantasía')

    def name_get(self):
        result = []
        for record in self:
            if record.internal_reference:
                if record.parent_id:
                    result.append((record.id, record.parent_id.name + ', ' + record.internal_reference + ' - [' + record.name + ']'))
                else:
                    result.append((record.id, record.internal_reference + ' - [' + record.name + ']'))
            else:
                if record.parent_id:
                    result.append((record.id, str(record.parent_id.name) + ', ' + str(record.name)))
                else:    
                    result.append((record.id, record.name))
        return result
