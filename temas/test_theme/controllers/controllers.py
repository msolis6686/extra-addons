from odoo import http
from odoo.http import request

class TestTheme(http.Controller):
    @http.route(['/tema'], type="http", auth="user", website=True)
    def index(self, **kw):
        #return "Hello, world"
        return http.request.render('test_theme.product_attributes',{})

#     @http.route('/test_theme/test_theme/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('test_theme.listing', {
#             'root': '/test_theme/test_theme',
#             'objects': http.request.env['test_theme.test_theme'].search([]),
#         })

#     @http.route('/test_theme/test_theme/objects/<model("test_theme.test_theme"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('test_theme.object', {
#             'object': obj
#         })
