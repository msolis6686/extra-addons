from odoo import models, fields, api


class Project(models.Model):
    _name = 'real.estate.project'
    _description = 'Real estate project'

    name = fields.Char(string='Project name', required=True)
    description = fields.Text()
    location = fields.Char('Location')
    city = fields.Char('City')
    type = fields.Char('Type')
    building_ids = fields.One2many(
        'real.estate.building', 'real_estate_project', 'Building',
        copy=True)
    image = fields.Binary(string='Image')
    contract_id = fields.One2many('real.estate.contract', 'project_id','Contract',copy=True)