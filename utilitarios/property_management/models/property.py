from odoo import models, fields, api


class Property(models.Model):
    _name = 'real.estate.property'
    _description = 'Real estate property'

    name = fields.Char(string='Property name', required=True)
    type = fields.Selection([('room', 'Room'), ('apartment', 'Apartment'),
                             ('shop', 'Shop')])  # use this widget in F.E <field name="type" widget="radio"/>
    size = fields.Char('Size')
    image = fields.Binary(string='Image')
    # facilities = fields.Selection([('parking', 'Parking'),('open_roof', 'Open Roof'), ('electric', 'Electricity')])
    # for checkboxes
    parking = fields.Boolean(string='Parking')
    open_roof = fields.Boolean(string='Open Roof')
    electric = fields.Boolean(string='Electricity')


    detail = fields.Char('Detail')
    property_value = fields.Float(string='Property Value', digits='Product Price')
    currency_id = fields.Many2one('res.currency', help='The currency used to enter statement', string="Currency")
    status = fields.Selection([('booked', 'Booked'), ('available', 'Available'),
                             ('rented', 'Rented'), ('sold', 'Sold')], default='available')
    real_estate_floor = fields.Many2one('real.estate.floor', 'Floor', index=True, ondelete='cascade')
    floor_name = fields.Char('Floor Name', related='real_estate_floor.name')
    floor_id = fields.Integer('Floor id', related='real_estate_floor.id')
    image = fields.Binary(string='Image')
    contract_id = fields.One2many('real.estate.contract', 'floor_id', 'Contract', copy=True)
    owned_by = fields.Many2one('res.partner', string='Customer', readonly=True)
    project_name = fields.Char(compute='_find_project_id', string='Project Name')

    def _find_project_id(self):
        project_name= ''
        for line in self:
            project_name = line.real_estate_floor.real_estate_building.real_estate_project.name
        self.project_name = project_name






