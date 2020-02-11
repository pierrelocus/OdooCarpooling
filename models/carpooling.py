#-*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
import datetime
from geopy import distance


class Carpooling(models.Model):
    _inherit        = ['mail.thread', 'mail.activity.mixin', 'carpooling.journey']
    _name           = 'carpooling.carpooling'
    _description    = """Represents a carpooling"""
    _rec_name       = 'driver_id'

    name                = fields.Char()
    journey_id          = fields.Many2one('carpooling.journey', 
                                        string="Journey",
                                        ondelete='cascade')
    pooler_ids          = fields.Many2many('res.partner', string="Poolers")
    departure_date      = fields.Date(string="Departure date")
    departure_time      = fields.Float(string="Departure time")
    taken_seats         = fields.Integer(string="Taken seats",
                                        compute='_on_pooler_manage_seats',
                                        default=0,
                                        store=True)
    taken_seats_tree    = fields.Char(string="Taken seats",
                                        compute='_on_pooler_manage_seats',
                                        default="0 / 0",
                                        store=True)
    carpool_url         = fields.Char(compute='_compute_url')
    states              = [('new', "New"),
                            ('available', "Has seats available"),
                            ('full', "Full")]
    state               = fields.Selection(selection=states, default='new')


    def _compute_url(self):
        for rec in self:
            base_url = rec.env["ir.config_parameter"].sudo().get_param("web.base.url")
            action_id = rec.env.ref('carpooling.carpooling_action').id
            model_id = rec.id
            rec.carpool_url = base_url + '/web#action=%s&id=%s' % (str(action_id), str(model_id))


    @api.depends('distance')
    def _on_distance_calculate(self):
        for pool in self:
            pool.money_economy = pool.distance * 0.27

    @api.depends('distance')
    def _avg_cotwo_calculate(self):
        for pool in self:
            pool.avg_cotwo_economy = pool.distance * 118.5

    @api.depends('pooler_ids', 'seats')
    def _on_pooler_manage_seats(self):
        for pool in self:
            if pool.seats < len(pool.pooler_ids):
                raise exceptions.ValidationError("No more seat in this carpool")
            pool.taken_seats = len(pool.pooler_ids)
            pool.taken_seats_tree = str(pool.taken_seats) + ' / ' + str(pool.seats)
            if pool.taken_seats:
                if pool.taken_seats == pool.seats:
                    pool.state = 'full'
                else :
                    pool.state = 'available'
            else:
                pool.state = 'new'
    ### Smart Buttons
    def smart_button_poolers(self):
        action = self.env.ref('carpooling.pooler_action').read()[0]
        action['domain'] = [('carpooling_ids.id', '=', self.id)]
        return action

    def action_toggle_take_seat(self):
        self.ensure_one()
        if self.env.user.partner_id in self.pooler_ids:
            self.pooler_ids -= self.env.user.partner_id
        else:
            self.pooler_ids |= self.env.user.partner_id





class CarpoolingFinder(models.Model):
    _name = 'carpooling.finder'
    _description = "Looks for carpools at a maximum given distance of a given point"

    name = fields.Char()
    desccription = fields.Char()
    
    street  = fields.Char(required=True)
    zipcode = fields.Integer(required=True)
    city    = fields.Char(required=True)
    country_id = fields.Many2one('res.country', required=True)
    address_tree = fields.Char(string="Address", compute='_on_address_change', store=True)

    distance = fields.Integer(required=True, string="Distance from address")

    latitude    = fields.Float('Geo Latitude', digits=(16, 5))
    longitude   = fields.Float('Geo Longitude', digits=(16, 5))
    carpooling_ids = fields.Many2many('carpooling.carpooling', string="Nearby carpoolings", readonly=True, store=True, compute="_on_address_change")

    @api.depends('street', 'zipcode', 'city', 'country_id', 'distance', 'latitude', 'longitude', 'carpooling_ids')
    def _on_address_change(self):
        for rec in self:
            if rec.street and rec.zipcode and rec.city and rec.country_id:
                rec.address_tree = '%s, %s %s, %s' % (rec.street, rec.zipcode, rec.city, rec.country_id.name)
                resp = self.env['carpooling.address']._geo_localize(rec.street, rec.zipcode, rec.city, '', rec.country_id.name)
                if resp:
                    rec.latitude = resp[0]
                    rec.longitude = resp[1]
                    carpools = self.env['carpooling.carpooling'].search([('departure_date', '<', datetime.date.today() + datetime.timedelta(days=1))])
                    to_create = []
                    for pool in carpools:
                        dst = distance.distance((rec.latitude, rec.longitude), (pool.departure_id.latitude, pool.departure_id.longitude)).km
                        if dst < rec.distance:
                            to_create.append(pool.id)
                    
                    rec.carpooling_ids = [(6, 0, to_create)]




class CarpoolRequest(models.Model):
    _name = 'carpooling.request'
    _description = """
        Let users request carpools so people can check if they can help.
        When creating a request, existing carpools at less than 5km will be shown.
    """

    name = fields.Char()
    description = fields.Char()

    departure_id        = fields.Many2one('carpooling.address', 
                                            string="Pickup point",
                                            required=True)
    arrival_id          = fields.Many2one('carpooling.address', 
                                            string="Arrival point",
                                            required=True)
    day_ids             = fields.One2many('carpooling.days', 'journey_id',
                                        string="Days needed",
                                        required=True)