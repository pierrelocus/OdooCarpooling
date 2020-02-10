# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from geopy import distance
import datetime

class Carpooling(http.Controller):

    

    @http.route('/carpooling/find', methods=['GET', 'POST'], type='http', auth='public', website=True)
    def find(self):        
        if request.httprequest.method == 'GET':
            return request.render('carpooling.finder', {})
        if request.httprequest.method == 'POST':
            street  = request.params.get('street')
            zipcode = request.params.get('zipcode')
            city    = request.params.get('city')
            country = request.params.get('country')

            resp = request.env['carpooling.address']._geo_localize(street, zipcode, city, '', country)
            if resp:
                latlon = (resp[0], resp[1])
                carpools = request.env['carpooling.carpooling'].search([('departure_date', '<', datetime.date.today() + datetime.timedelta(days=1))])
                nearby_carpools = []
                for pool in carpools:
                    dst = distance.distance(latlon, (pool.departure_id.latitude, pool.departure_id.longitude)).km
                    print("Distance : ", dst)
                    if dst < 10:
                        nearby_carpools.append(pool)

                return request.render('carpooling.finder', {
                    'carpools': nearby_carpools
                })
            return request.render('carpooling.finder', {})