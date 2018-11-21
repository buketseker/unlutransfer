# -*- coding: utf-8 -*-
from odoo import http

# class NitroDevelopment(http.Controller):
#     @http.route('/nitro_development/nitro_development/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/nitro_development/nitro_development/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('nitro_development.listing', {
#             'root': '/nitro_development/nitro_development',
#             'objects': http.request.env['nitro_development.nitro_development'].search([]),
#         })

#     @http.route('/nitro_development/nitro_development/objects/<model("nitro_development.nitro_development"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('nitro_development.object', {
#             'object': obj
#         })