# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################
import logging
import math
import operator
import collections

from odoo import models, fields, api, exceptions, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    image_hover = fields.Binary(string='On Hover Image')
    # website_price = fields.Float('Website price', compute='_website_price', digits=dp.get_precision('Product Price'),store=True)

    # @api.multi
    def get_rating(self):
        prod_rating = sum(self.rating_ids.mapped('rating'))/(2*self.rating_count) if self.rating_count else 0
        rating_integer = math.floor(prod_rating)
        rating_decimal = prod_rating - rating_integer
        empty_start = 5 - (rating_integer + math.ceil(rating_decimal))
        return [rating_integer, rating_decimal, empty_start]


class SPMenu(models.Model):
    _inherit = 'website.menu'

    # sp_is_mega_menu = fields.Boolean(string='Mega Menu')
    category_ids = fields.Many2many(comodel_name='product.public.category')
    mega_menu_type = fields.Selection([('type_1', 'Type A'), ('type_2', 'Type B'), ('type_3', 'Type C'), ('type_4', 'Type D')], string='Type', required=True, default='type_1')


class Website(models.Model):
    _inherit = "website"

    is_bck_img = fields.Boolean(string='Enable/Disable Login Page Background Image')
    login_bck_img = fields.Binary(string='Login Page background Image')
    is_signup_bck_img = fields.Boolean(string='Enable/Disbale SignUp Page Background Image')
    signup_bck_img = fields.Binary(string='Login Page background Image')
    is_footer_bck_img = fields.Boolean(string='Enable/Disable Footer Background Image')
    footer_bck_img = fields.Binary(string='Footer background Image')
    is_redirect = fields.Boolean(string='Redirection to cart page', default=True)
    multi_product_carousel_items_no = fields.Integer(string="No. of items in Multi Carousel", default=4)

class SPProductPublicCategory(models.Model):
    _inherit = 'product.public.category'

    url = fields.Text(string="Url", compute="_build_url")

    def _recursive_url(self):
        url = ''
        if self.parent_id:
            url = self.parent_id._recursive_url() + '-'
        return url + '-'.join(self.name.lower().split(' '))

    # @api.multi
    def _build_url(self):
        for rec in self:
            rec.url = '/shop/category/%s-%s'%(rec._recursive_url(), str(rec.id))


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    def action_confirm(self):
        self.ensure_one()
        order_lines = self.order_line
        for line in order_lines:
            product_id = line.product_id
            product_id.product_tmpl_id.selling_count = product_id.product_tmpl_id.selling_count + line.product_uom_qty
        rec = super(SaleOrder, self).action_confirm()
        return rec


class Product(models.Model):

    _inherit = 'product.template'

    # @api.multi
    def _get_selling_count(self):
        sale_order_line = self.env['sale.order.line']
        for rec in self:
            sale_order_line_ids = sale_order_line.search([('product_id','in',rec.product_variant_ids.ids)])
            count = sum(sale_order_line_ids.mapped('product_uom_qty'))
            rec.selling_count = count

    selling_count = fields.Integer(string='Total Sold Count', compute="_get_selling_count", store=True)


class MutliCarousel(models.Model):
    _name = "multi.carousel"

    name = fields.Text('Name', required=True, translate=True)
    product_ids = fields.Many2many(comodel_name="product.template", string="Products")
    type = fields.Selection([('top_selling','Top Selling Products'),('new','New Products'),('featured','Featured Products'),('rated','Top Rated Products')], default="top_selling", required=True)
    limit = fields.Integer(string="Limit", default="6", required=True)
    published = fields.Boolean(string="published")
    is_single_carousel = fields.Boolean(string="Single carousel")
    category_id = fields.Many2one(comodel_name="product.public.category")
    _sql_constraints=[('type_constraint','unique(type)','This type is already exists'),('is_single_carousel_constraint','unique(type)','Single Value is allowed for this carousel')]

    @api.onchange('category_id', 'is_single_carousel')
    def _onchange_productids(self):
        if not self.is_single_carousel:
            self.category_id = False
            return {
                'domain':{'product_ids':[]}
            }
        else:
            self.product_ids = False
            return {
                'domain':{'product_ids':[('public_categ_ids.id','=',self.category_id.id)]}
            }

    @api.onchange('type')
    def _default_name(self):
        if self.type == 'top_selling':
            self.name = 'Top Selling'
        elif self.type == 'rated':
            self.name = 'Top Rated'
        elif self.type == 'new':
            self.name = 'New'
        elif self.type == 'featured':
            self.name = 'Featured'

    @api.model
    def create(self, vals):
        if vals.get('is_single_carousel'):
            is_single_carousel = self.env['multi.carousel'].search([('is_single_carousel','=',True)])
            if len(is_single_carousel):
                raise UserError(_('Only one single carousel record can be created at a time!'))
        return super(MutliCarousel, self).create(vals)

    # @api.multi
    def write(self, vals):
        if vals.get('is_single_carousel'):
            is_single_carousel = self.env['multi.carousel'].search([('is_single_carousel','=',True)])
            if len(is_single_carousel):
                raise UserError(_('Only one single carousel record can be created at a time!'))
        return super(MutliCarousel, self).write(vals)

    # @api.multi
    def toggle_published(self):
        self.published = not self.published
        return True

    def _set_random(self, limit):
        return self.env['product.template'].search([], limit = limit).ids

    #@api.multi
    def auto_compute(self):
        type = self.type
        lst = []
        count = 0
        Product = self.env['product.template']
        # if self.is_single_carousel:
        #     categ = self.env['product.public.category'].browse(self.category_id)
        #     Product.search([('')])
        if type == 'rated':
            prod_rating = {}
            product_ids = Product.search([])
            for product in product_ids:
                if product.rating_count > 0:
                    avg_rating = sum(product.rating_ids.mapped('rating'))/product.rating_count
                    prod_rating.update({str(product.id): avg_rating })
            sorted_x = sorted(prod_rating.items(), key=lambda kv: kv[1])
            for value in sorted_x:
                if count >= self.limit:
                    break
                lst.append(int(value[0]))
                count += 1
            if not prod_rating:
                lst = self._set_random(self.limit)
        elif type == 'new':
            product_ids = Product.search([], order="create_date desc, id desc")
            for product in product_ids:
                if count >= self.limit:
                    break
                lst.append(product.id)
                count += 1
        elif type == 'top_selling':
            product_ids = Product.search([('selling_count','!=',0)], order="selling_count desc")
            for product in product_ids:
                if count >= self.limit:
                    break
                lst.append(product.id)
                count += 1
            if not product_ids:
                lst = self._set_random(self.limit)
        else:
            pass
        self.product_ids = [(6,0,lst)]
        return True


class Brands(models.Model):
    _name = 'sp.brands'
    _description = 'Product Brands'

    # name = fields.Char(required=True)
    # image = fields.Binary(required=True)
    # published = fields.Boolean()

    # # @api.multi
    # def toggle_is_publish(self):
    #     if self.published:
    #         self.published = False
    #     else:
    #         self.published = True
    #     return True

    @api.model
    def set_demo_config(self):
        self.env['ir.ui.view'].browse(self.env.ref('website_sale.products_add_to_cart').id).active = True
        self.env['ir.ui.view'].browse(self.env.ref('website_sale_comparison.add_to_compare').id).active = True
        self.env['ir.ui.view'].browse(self.env.ref('website_sale.products_categories').id).active = True

        self.env['ir.ui.view'].browse(self.env.ref('website_sale.option_collapse_products_categories').id).active = True
        self.env['ir.ui.view'].browse(self.env.ref('website_sale.products_attributes').id).active = True
        self.env['ir.ui.view'].browse(self.env.ref('website_sale.products_list_view').id).active = True

        self.env['ir.ui.view'].browse(self.env.ref('website_sale.products_description').id).active = True
        self.env['ir.ui.view'].browse(self.env.ref('website_sale_wishlist.add_to_wishlist').id).active = True
        self.env['ir.ui.view'].browse(self.env.ref('website_sale.recommended_products').id).active = True

        self.env['ir.ui.view'].browse(self.env.ref('website_sale.product_picture_magnify_auto').id).active = True
        self.env['ir.ui.view'].browse(self.env.ref('website_sale.product_comment').id).active = True
        self.env['ir.ui.view'].browse(self.env.ref('website_sale.product_picture_magnify').id).active = True
        self.env['ir.ui.view'].browse(self.env.ref('website_sale.product_quantity').id).active = True

        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('auth_signup.allow_uninvited', True)
        set_param('auth_signup.reset_password', True)
        set_param('auth_oauth.module_auth_oauth', True)
        self.env['ir.ui.view'].browse(self.env.ref(
            'website.layout_logo_show').id).active = True
        self.env['ir.ui.view'].browse(self.env.ref(
            'portal.portal_show_sign_in').id).active = True
        return True
