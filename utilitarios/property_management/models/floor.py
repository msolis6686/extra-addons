from odoo import models, fields, api


class Floor(models.Model):
    _name = 'real.estate.floor'
    _description = 'Real estate floor'

    name = fields.Char(string='Floor name', required=True)
    code = fields.Text()
    area = fields.Char('Covered area')
    property_ids = fields.One2many(
        'real.estate.property', 'real_estate_floor', 'Property',
        copy=True)

    real_estate_building = fields.Many2one('real.estate.building', 'Building', index=True, ondelete='cascade')
    building_name = fields.Char('Building Name', related='real_estate_building.name')
    building_id = fields.Integer('Building Id', related='real_estate_building.id', store=True)
    image = fields.Binary(string='Image')

    contract_id = fields.One2many('real.estate.contract', 'floor_id', 'Contract', copy=True)
