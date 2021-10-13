# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Website Theme: Shopoint",
  "category"             :  "Theme/eCommerce",
  "version"              :  "1.0.20",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo.html",
  "description"          :  "https://webkul.com/blog/odoo-website-theme-shopoint/",
  "live_test_url"        :  "https://shopoint_13.odoothemes.webkul.com",
  "depends"              :  [
                             'website_theme_install',
                             'support_theme_shopoint',
                             'website_sale_comparison',
                             'website_mail',
                             'website_blog',
                             'website'
                            ],
  "data"                 :  [
                             'views/lazy_loading.xml',
                             'views/inherit_products.xml',
                             'views/inherit_product.xml',
                             'views/assets_template.xml',
                             'views/inherit_404.xml',
                             'views/inherit_cart.xml',
                             'views/inherit_wishlist.xml',
                             'views/inherit_login_signup.xml',
                             'views/checkout.xml',
                             'views/contact_us.xml',
                             'views/snippets.xml',
                             'views/shopoint.xml',
                             'views/inherit_payment.xml',
                             'views/inherit_confirmation.xml',
                             'views/inherit_pager.xml',
                             'views/inherit_portal.xml',
                             'views/inherit_footer.xml',
                             'views/res_config.xml',
                             'views/mega_menu.xml',
                             'views/my_account.xml',
                             'views/change_password.xml',
                             'security/ir.model.access.csv',
                             'demo/demo_data.xml',
                            ],
  # "demo"                 :  ['demo/demo_data.xml'],
  "qweb"                 :  ['static/src/xml/*.xml'],
  "images"               :  [
                             'static/description/Banner.png',
                             'static/description/main_screenshot.gif',
                            ],
  "application"          :  False,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  99,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}