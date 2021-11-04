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
  "name"                 :  "Support Theme Shopoint",
  "category"             :  "Theme/eCommerce",
  "version"              :  "1.0.5",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "description"          :  """Support Shopoint theme""",
  "depends"              :  [
                             'website_sale',
                             'website_sale_wishlist',
                            ],
  "data"                 :  [
                             'views/assets_template.xml',
                             'views/product_attributes.xml',
                            ],
  "demo"                 :  [],
  "images"               :  [
                             'static/description/Banner.png',
                             'static/description/main_screenshot.png',
                            ],
  "application"          :  False,
  "installable"          :  True,
  "price"                :  0,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}