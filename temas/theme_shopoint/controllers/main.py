# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################
from odoo import fields, http, tools, _
from odoo.http import request, Controller
from odoo.addons.website_sale.controllers.main import WebsiteSale,TableCompute
from odoo.addons.website.controllers.main import QueryURL, Website
from odoo.addons.http_routing.models.ir_http import slug
import base64
import os
from odoo.tools import config
import logging

_logger = logging.getLogger(__name__)

class Website(Website):

    @http.route()
    def get_switchable_related_views(self, key):
        views = super(Website, self).get_switchable_related_views(key)
        for index, data in enumerate(views):
            if data.get('key').startswith('support_theme_shopoint') and request.website.theme_id.name not in ['theme_shopoint', 'theme_marketplace_shopoint']:
                views.pop(index)
        return views
    
    # @http.route()
    # def toggle_switchable_view(self, view_key):
    #     super(Website, self).toggle_switchable_view(view_key)
    #     if request.website.sudo().theme_id.name in ["theme_shopoint", "theme_marketplace_shopoint"] and view_key == 'website_sale.products_list_view' :
    #         request.website.viewref(view_key).toggle()

class WebsiteSale(WebsiteSale):

    def checkout_redirection(self, order):
        res = super(WebsiteSale, self).checkout_redirection(order)
        if request.httprequest.args.getlist('my_address_book') and bool(request.httprequest.args.getlist('my_address_book')[0]):
            return False
        else:
            return res

    def _get_search_domain(self, search, category, attrib_values, search_in_description=True):
        domain = super(WebsiteSale, self)._get_search_domain(search, category, attrib_values)
        theme_id = request.website.sudo().theme_id
        if theme_id and theme_id.name in ["theme_shopoint", "theme_marketplace_shopoint"]:
            min_price = request.httprequest.args.getlist('min_price')
            max_price = request.httprequest.args.getlist('max_price')

            if min_price or max_price:
                date = fields.Date.today()
                company = request.env.user.company_id
                to_currency = request.website.pricelist_id.currency_id
                from_currency = request.website.company_id.currency_id

                min_price = from_currency._convert(float(min_price[0]), to_currency, company, date)
                max_price = from_currency._convert(float(max_price[0]), to_currency, company, date)
                domain += [('lst_price','>=',min_price), ('lst_price','<=',max_price)]
        return domain

    def _sp_get_view_id(self, views, key):
        view_id = views.filtered(lambda v: v.key == key and v.active == False and v.website_id.id == request.website.id)
        if not view_id:
            view_id = views.filtered(lambda v: v.key == key and v.active == False and v.website_id.id == False)
        return view_id
    
    def _sp_get_view_id_2(self, views, key):
        view_id = views.filtered(lambda v: v.key == key and v.website_id.id == request.website.id)
        if not view_id:
            view_id = views.filtered(lambda v: v.key == key and v.website_id.id == False)
        return view_id

    @http.route([
        '''/shop''',
        '''/shop/page/<int:page>''',
        '''/shop/category/<model("product.public.category", "[('website_id', 'in', (False, current_website_id))]"):category>''',
        '''/shop/category/<model("product.public.category", "[('website_id', 'in', (False, current_website_id))]"):category>/page/<int:page>'''
    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        res = super(WebsiteSale, self).shop(page, category, search, ppg, **post)
        request.env['ir.ui.view'].sudo().browse(request.env.ref('website_sale.products_list_view').id).active = True
        #Always trigger list view
        theme_id = request.website.sudo().theme_id
        if theme_id and theme_id.name in ["theme_shopoint", "theme_marketplace_shopoint"]:
            views = request.env['ir.ui.view'].search([('key','in',['website_sale.products_list_view', 'support_theme_shopoint.sp_filter_category_fixed_view']),'|',('active','=',True),('active','=', False)])
            # try:
            #     products_list_view = self._sp_get_view_id(views, 'website_sale.products_list_view')
            #     products_list_view.sudo().active = True
            # except Exception as e:
            #     _logger.info('=== Error due to product list view == {}'.format(e))

            sp_filter_category_fixed_view = False
            try:
                sp_filter_category_fixed_view = views.filtered( lambda v: v.key == 'support_theme_shopoint.sp_filter_category_fixed_view' and v.website_id.id == request.website.id )
                if not sp_filter_category_fixed_view:
                    sp_filter_category_fixed_view = views.filtered(lambda v: v.key == 'support_theme_shopoint.sp_filter_category_fixed_view' and v.website_id.id == False)
                res.qcontext['sp_filter_category_fixed_view'] = sp_filter_category_fixed_view.sudo().active
            except Exception as E:
                _logger.info('=== Error due to sp_filter_category_fixed_view ==')

            try:
                product_comment = request.env['ir.default'].sudo().get('res.config.settings', 'show_rating')
                res.qcontext['product_comment'] = True if product_comment else False

            except Exception as E:
                _logger.info('=== Error due to Discussion & Rating ==')

            res.qcontext['page'] = page
            res.qcontext['ppg'] = ppg
            res.qcontext['order'] = post.get('order', '')

            date = fields.Date.today()
            company = request.env.user.company_id

            try:
                to_currency = request.website.pricelist_id.currency_id
                from_currency = request.website.company_id.currency_id

                default_min_price  = from_currency._convert(request.env['ir.default'].sudo().get('res.config.settings', 'min_price') or 200, to_currency, company, date)
                default_max_price  = from_currency._convert(request.env['ir.default'].sudo().get('res.config.settings', 'max_price') or 12000, to_currency, company, date)
                res.qcontext['default_min_price'] = default_min_price
                res.qcontext['default_max_price'] = default_max_price

                min_price, max_price = post.get('min_price'), post.get('max_price')
                if min_price or max_price:
                    res.qcontext['min_price'] = min_price
                    res.qcontext['max_price'] = max_price
            except Exception as e:
                _logger.info('==Error== Price range filter {}'.format(e))

            if post.get('lazy_load'):
                data_grid = request.env['ir.ui.view'].render_template("theme_shopoint.wk_lazy_list_product_item", res.qcontext)
                return data_grid

            for p in res.qcontext['products']:
                p.sudo().website_size_x = 1
                p.sudo().website_size_y = 1
        return res

    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        res = super(WebsiteSale, self).product(product, category, search, **kwargs)

        theme_id = request.website.sudo().theme_id
        if theme_id and theme_id.name in ["theme_shopoint", "theme_marketplace_shopoint"]:
            try:
                view_ids = request.env['ir.ui.view'].search([('key','in',['website_sale.product_comment', 'website_sale.recommended_products']),'|',('active','=',True),('active','=',False)])
                
                is_product_comment = self._sp_get_view_id_2(view_ids, 'website_sale.product_comment').sudo().active
                res.qcontext.update({'is_product_comment':is_product_comment})

                is_recommended_products = self._sp_get_view_id_2(view_ids, 'website_sale.product_comment').sudo().active
                res.qcontext['is_recommended_products'] = is_recommended_products

            except Exception as e:
                _logger.info('==is_product_comment== {}'.format(e))

        return res

    @http.route(['/website/sp/get_info'], type='json', auth="public", website=True)
    def sp_getInfo(self):
        return {
            'is_redirect': request.website.is_redirect
        }

    @http.route(['/delete/partner'], type='json', auth="public", website=True)
    def delete_partner(self, partner_id):
        partner_id = request.env['res.partner'].sudo().browse(int(partner_id))
        order_id = request.env['sale.order'].sudo().search([('partner_shipping_id', '=', partner_id.id)])
        if order_id:
            partner_id.active = False
            return True
        if partner_id:
            res = partner_id.unlink()
        return res or False

    @http.route(['/shop/product/data/'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def product_data(self, product_id,  category='', search='', **kwargs):
        add_qty = int(kwargs.get('add_qty', 1))
        product = request.env['product.template'].browse(int(product_id))
        product_context = dict(request.env.context, quantity=add_qty,
                               active_id=product.id,
                               partner=request.env.user.partner_id)
        ProductCategory = request.env['product.public.category']

        if category:
            category = ProductCategory.browse(int(category)).exists()

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attrib_set = {v[1] for v in attrib_values}

        keep = QueryURL('/shop', category=category and category.id, search=search, attrib=attrib_list)

        categs = ProductCategory.search([('parent_id', '=', False)])

        pricelist = request.website.get_current_pricelist()

        def compute_currency(price):
            return product.currency_id._convert(price, pricelist.currency_id, product._get_current_company(pricelist=pricelist, website=request.website), fields.Date.today())

        if not product_context.get('pricelist'):
            product_context['pricelist'] = pricelist.id
            product = product.with_context(product_context)

        try:
            add_to_cart = request.env['ir.ui.view'].search([('key','=','website_sale.products_add_to_cart'),('website_id','in',[request.website.id])]).sudo().active
            add_to_wishlist = request.env['ir.ui.view'].search([('key','=','website_sale_wishlist.add_to_wishlist'),('website_id','in',[request.website.id])]).sudo().active
            quantity = request.env['ir.ui.view'].search([('key','=','website_sale.product_quantity'),('website_id','in',[request.website.id])]).sudo().active
        except Exception as e:
            _logger.info(e)

        return request.env['ir.ui.view'].render_template("theme_shopoint.sp_eye_view_modal", {
            'search': search,
            'category': category,
            'pricelist': pricelist,
            'attrib_values': attrib_values,
            'compute_currency': compute_currency,
            'attrib_set': attrib_set,
            'keep': keep,
            'categories': categs,
            'main_object': product,
            'product': product,
            'add_qty': add_qty,
            'add_to_cart': add_to_cart,
            'add_to_wishlist': add_to_wishlist,
            'quantity': quantity,
            # 'optional_product_ids': [p.with_context({'active_id': p.id}) for p in product.optional_product_ids],
            # 'get_attribute_exclusions': self._get_attribute_exclusions,
        })

    @http.route(['/shop/optional_products/data'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def optional_products(self, product_id=None, type=None, **kwargs):
        try:
            add_to_cart = request.env['ir.ui.view'].search([('key','=','website_sale.products_add_to_cart'),('website_id','in',[request.website.id])]).sudo().active
            add_to_wishlist = request.env['ir.ui.view'].search([('key','=','website_sale_wishlist.add_to_wishlist'),('website_id','in',[request.website.id])]).sudo().active
        except Exception as e:
            _logger.info(e)
        if product_id:
            product_id = request.env['product.template'].browse(int(product_id))
            if type == 'a':
                products = product_id.accessory_product_ids
                type_name = "Accessory Products"
                type = 'product'
            else:
                products = product_id.alternative_product_ids
                type_name = "Alternative Products"
                type = 'template'
            return request.env['ir.ui.view'].render_template("theme_shopoint.modal_other_products", {
                'products': products,
                'type_name': type_name,
                'type' : type,
                'add_to_cart': add_to_cart,
                'add_to_wishlist': add_to_wishlist,
            })
        return False

    @http.route(['/dynamic/data'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def dynamic_data(self, data_of, **kwargs):
        MultiCarousel = request.env['multi.carousel']
        view_ids = request.env['ir.ui.view'].search([('key','in',['website_sale.products_add_to_cart', 'website_sale_wishlist.add_to_wishlist', 'support_theme_shopoint.quick_view', 'website_sale_comparison.add_to_compare']),'|',('active','=',True),('active','=',False)])

        add_to_cart = self._sp_get_view_id_2(view_ids, 'website_sale.products_add_to_cart').sudo().active
        add_to_wishlist = self._sp_get_view_id_2(view_ids, 'website_sale_wishlist.add_to_wishlist').sudo().active
        quick_view = self._sp_get_view_id_2(view_ids, 'support_theme_shopoint.quick_view').sudo().active
        compare = self._sp_get_view_id_2(view_ids, 'website_sale_comparison.add_to_compare').sudo().active

        try:
            product_comment = request.env['ir.default'].sudo().get('res.config.settings', 'show_rating') or False
            res.qcontext['product_comment'] = product_comment
        except Exception as E:
            _logger.info('=== Error due to Discussion & Rating ==')

        if data_of == 'multi_carousel':

            multi_carousel_dict = {}
            active_types = MultiCarousel.search([('published','=',True),('is_single_carousel','!=',True)])

            data = b''
            multi_carousel_dict.update({
                'tabs': {}
            })

            tab_count, link_count = 0, 0
            for mc_type in active_types:
                if len(mc_type.product_ids) > 0:
                    data += request.env['ir.ui.view'].render_template("theme_shopoint.multi_carousel_links", {
                        'type': mc_type,
                        'active': True if link_count == 0 else False
                    })
                    multi_carousel_dict.get('tabs').update({mc_type.type: request.env['ir.ui.view'].render_template("theme_shopoint.multi_carousel_products", {
                        'products': mc_type.product_ids,
                        'type': mc_type.type,
                        'active': True if tab_count == 0 else False,
                        'add_to_cart': add_to_cart,
                        'add_to_wishlist': add_to_wishlist,
                        'quick_view': quick_view,
                        'compare': compare,
                        'product_comment':product_comment
                    })})
                    link_count, tab_count = 1, 1

            multi_carousel_dict.update({'links': data})
            multi_carousel_dict.update({'items_number': request.website.multi_product_carousel_items_no})

            return multi_carousel_dict
        # elif data_of == "dynamic_brands":
        #     return request.env['ir.ui.view'].render_template("theme_shopoint.dynamic_brands", {
        #         'brands': request.env['sp.brands'].search([('published','=',True)])
        #     })
        elif data_of == "single_carousel":
            carousel_id = MultiCarousel.search([('is_single_carousel','=',True),('published','=',True)])
            products = carousel_id.product_ids
            single_carousel_products = request.env['ir.ui.view'].render_template("theme_shopoint.single_carousel_products", {
                'products': products,
                'add_to_cart': add_to_cart,
                'add_to_wishlist': add_to_wishlist,
                'quick_view': quick_view,
                'compare': compare,
                'product_comment':product_comment
            })

            href = carousel_id.category_id.url
            single_carousel_content = request.env['ir.ui.view'].render_template("theme_shopoint.single_carousel_content", {
                'carousel_id': carousel_id,
                'href': href,
            })
            return {
                'single_carousel_products': single_carousel_products,
                'single_carousel_content': single_carousel_content
            }
        elif data_of == "blog":
            posts = request.env['blog.post'].search([('is_published','=',True)])
            return request.env['ir.ui.view'].render_template("theme_shopoint.sp_dynamic_blogs", {
                'posts': posts
            })

    @http.route(['/website/set/view'], type='json', auth="public", website=True)
    def set_view(self, name, **kwargs):
        request.session['sp_view_type'] = name

    @http.route(['/website/get/view'], type='json', auth="public", website=True)
    def get_view(self, **kwargs):
        return request.session.get('sp_view_type', 'shopoint_view_main')

    @http.route(['/my/address/book'], type='http', auth="public", website=True)
    def addressBook(self, **kwargs):
        partner_id = request.env['res.users'].browse(request.env.uid).partner_id
        Partner = partner_id.with_context(show_address=1).sudo()
        shippings = Partner.search([
            ("id", "child_of", partner_id.commercial_partner_id.ids),
            '|', ("type", "in", ["delivery", "other"]), ("id", "=", partner_id.commercial_partner_id.id)
        ], order='id desc')
        return request.render('theme_shopoint.my_address_book', {
            'partner_id': partner_id,
            'only_services':  False,
            'shippings': shippings
        })

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True)
    def address(self, **kw):
        res = super(WebsiteSale, self).address(**kw)
        if kw.get('my_address_book'):
            res.qcontext['from_my_add_book'] = True
        if 'submitted' in kw:
            if res.qcontext.get('response_template') == None and bool(kw.get('from_my_add_book')):
                return request.redirect('/my/address/book')
        return res

    @http.route()
    def checkout(self, **post):
        res = super(WebsiteSale, self).checkout(**post)
        referer = request.httprequest.headers.get('Referer')
        if 'my_address_book' in referer:
            return request.redirect('/my/address/book')
        return res

    @http.route(['/reset/my/password/'], type='http', auth='user', website=True)
    def reset_my_password(self, redirect=None, **post):
        partner = request.env.user.partner_id

        values = {
            'partner': partner,
            'user':request.env.user,
            'redirect': redirect,
            'error': '',
            'error_message': '',
            'sucess_message':'',
        }

        if post and post.get('submitted'):
        # error, error_message = self.details_form_validate(post)
            if post.get('password') != post.get('confirm_password'):
                values['error_message'] = "Password and Confirm password does not match. Please enter correct passwords"
                values['error'] = 'error'
            else:
                try:
                    current_password = str(post.get('current_password'))
                    password = str(post.get('password'))
                    if password and current_password:
                        dbname = request._cr.dbname
                        uid = request._uid
                        request.env['res.users'].check(dbname, uid, current_password)
                        res = request.env['res.users'].change_password(current_password, password)
                        if res:
                            return request.render("theme_shopoint.user_success_password", values)
                        else:
                            values['error_message'] = "There is an error in changing the password. Please try again."
                    else:
                        values['error_message'] = "Please enter the password!!"
                except Exception as e:
                    values['error_message'] = "Your Current Password did not match the password in our records. Please try again."
                    values['error'] = 'error'
        return request.render("theme_shopoint.user_reset_password", values)

    @http.route(['/shop/wishlist'], type='http', auth="public", website=True)
    def get_wishlist(self, count=False, **kw):
        res = super(WebsiteSale ,self).get_wishlist(count, **kw)
        theme_id = request.website.sudo().theme_id
        if theme_id and theme_id.name == "theme_shopoint":
            try:
                stock_qty = request.env['ir.ui.view'].sudo().search([('key','=','support_theme_shopoint.sp_support_show_quantity'),('website_id','in',[request.website.id])])
                res.qcontext['stock_qty'] = stock_qty.active
            except Exception as E:
                _logger.info('=== Error due to stock_qty ==')
        return res


class ChooseImageWebsite(Controller):

    @http.route("/change/image", type='json', auth="public", method='POST')
    def delete_image(self, **kw):
        user_id = request.env['res.users'].search([('id','=',request.env.user.id)])
        if kw.get('action') == 'edit':
            user_id.sudo().image_1024 =  kw.get('data').split(',')[1].strip()
        else:
            for path in tools.config['addons_path'].split(','):
                try:
                    user_id.sudo().image_1024 = base64.b64encode(open(os.path.join(path, 'theme_shopoint', 'static', 'src', 'images', 'unknown.png'), 'rb') .read()).decode("utf-8")
                except Exception as e:
                    continue
