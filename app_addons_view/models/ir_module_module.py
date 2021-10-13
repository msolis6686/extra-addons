# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.modules.module import get_module_path


class IrModule(models.Model):
    _inherit = "ir.module.module"

    addons_path_id = fields.Many2one('ir.module.addons.path', string='Addons Path', readonly=True)
    addons_path = fields.Char(string='Addons Path', related='addons_path_id.path', readonly=True)


class BaseModuleUpdate(models.TransientModel):
    _inherit = "base.module.update"

    def update_addons_paths(self):
        from odoo.modules.module import ad_paths
        addons_path_obj = self.env['ir.module.addons.path']

        for path in ad_paths:
            if not addons_path_obj.search([('path', '=', path)]):
                path_temp = path

                if len(path_temp) > 42:
                    path_temp = '%s......%s' % (path[:12], path[-19:])

                addons_path_obj.sudo().create({
                    'name': path.split('/')[-1],
                    'path': path,
                    'path_temp': path_temp,
                })

        for addons_path_id in addons_path_obj.search([]):
            if addons_path_id.path not in ad_paths:
                addons_path_id.unlink()

    def update_module_addons_paths(self):
        addons_path_obj = self.env['ir.module.addons.path']

        for module_id in self.env['ir.module.module'].search([]):
            module_path = get_module_path(module_id.name)
            if not module_path:
                continue
            addons_path = module_path.rstrip(module_id.name).rstrip('/')
            addons_path_id = addons_path_obj.search([('path', '=', addons_path)])

            if addons_path_id:
                module_id.addons_path_id = addons_path_id.id

    def update_module(self):
        result = super(BaseModuleUpdate, self).update_module()
        self.sudo().update_addons_paths()
        self.sudo().update_module_addons_paths()
        return result

