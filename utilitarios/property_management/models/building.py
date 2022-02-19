from odoo import models, fields, api


class Building(models.Model):
    _name = 'real.estate.building'
    _description = 'Building'


    map = fields.Char(string='Map')
    name = fields.Char(string='Building name', required=True)
    location = fields.Char('Location')
    city = fields.Char('City')
    approval_authority = fields.Char('Approval authority')
    size = fields.Char()
    # benefits = fields.Selection(string='Type', selection=[('parking', 'Parking'),
    #                                                       ('open_roof', 'Open Roof'), ('electric', 'Electricity')])

    parking = fields.Boolean(string='Parking')
    open_roof = fields.Boolean(string='Open Roof')
    electric = fields.Boolean(string='Electricity')

    # <field name="benefits" widget="many2many_checkboxes"/>

    floor_ids = fields.One2many(
        'real.estate.floor', 'real_estate_building', 'Floor',
        copy=True)

    real_estate_project = fields.Many2one('real.estate.project', 'Project', index=True, ondelete='cascade')
    project_name = fields.Char('Project Name', related='real_estate_project.name')
    # record = fields.Integer()
    image = fields.Binary(string='Image')
    contract_id = fields.One2many('real.estate.contract', 'building_id', 'Contract', copy=True)


