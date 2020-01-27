# -*- coding: utf-8 -*-
# from odoo import http


# class Carpooling(http.Controller):
#     @http.route('/carpooling/carpooling/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/carpooling/carpooling/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('carpooling.listing', {
#             'root': '/carpooling/carpooling',
#             'objects': http.request.env['carpooling.carpooling'].search([]),
#         })

#     @http.route('/carpooling/carpooling/objects/<model("carpooling.carpooling"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('carpooling.object', {
#             'object': obj
#         })
