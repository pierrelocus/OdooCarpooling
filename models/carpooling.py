#-*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime


class Carpooling(models.Model):
    _inherit        = ['mail.thread', 'mail.activity.mixin']
    _name           = 'carpooling.carpooling'
    _description    = """Represents a carpooling, composed by:
        - driver//as name               : Many2many res.partner
        - departure                     : address model Many2one
        - departure date                : datetime
        - arrival                       : address model Many2one
        - is return                     : boolean
        - return date                   : datetime
        - steps                         : address model Many2many
        - repeat                        : boolean
        - dates repeat                  : 
        - seats                         : integer
        - taken seats                   : integer
        - money economy                 : float(6,2)
        - avg CO2 footprint economy     : float(6,2)
        - cost                          : float(5,2)
        - estimated distance in km      : integer
        - info                          : text
        - State (new, still places, full): selection, header buttons
        - poolers                       : Many2many res.partner extended
    """

    name                = fields.Char()
    driver_id           = fields.Many2one('res.partner', required=True,
                                        string="Driver",
                                        domain="[('is_company', '=', False)]")
    _rec_name           = 'driver_id'

    description         = fields.Text()
    pooler_ids          = fields.Many2many('res.partner',
                                            required=True,
                                            string="Took a place")
    departure_id        = fields.Many2one('carpooling.address', 
                                            string="Pickup point",
                                            required=True)
    departure_date      = fields.Datetime(string="Departure time", 
                                            default=(datetime.date.today() 
                                            + datetime.timedelta(days=1)),
                                            required=True
                                        )
    departure_tree      = fields.Char(string="Departure",
                                        compute='_compute_departure_arrival',
                                        default="Address",
                                        store=True)
    arrival_tree        = fields.Char(string="Arrival",
                                        compute='_compute_departure_arrival',
                                        default="Address",
                                        store=True)
    arrival_id          = fields.Many2one('carpooling.address',
                                            string="Dropoff point",
                                            required=True)
    is_return           = fields.Boolean(default=True, string="Has return")
    return_date         = fields.Datetime(string="Return time", 
                                            default=(datetime.date.today() 
                                            + datetime.timedelta(days=1)),
                                            required=True
                                        )
    steps_ids           = fields.Many2many('carpooling.address',
                                            string="Steps")

    seats               = fields.Integer(required=True, default=3)
    taken_seats         = fields.Integer(string="Taken seats",
                                        compute='_on_pooler_manage_seats',
                                        default=0,
                                        store=True)
    taken_seats_tree    = fields.Char(string="Taken seats",
                                        compute='_on_pooler_manage_seats',
                                        default="0 / 0",
                                        store=True)
    distance            = fields.Integer(string="Estimated distance in km")
    money_economy       = fields.Float(string="Estimated money economy per seat in euros",
                                        digits=(5,2),
                                        readonly=True,
                                        compute='_on_distance_calculate',
                                        store=True)
    avg_cotwo_economy   = fields.Float(string="Estimated CO2 footprint economy per seat in grams",
                                        digits=(5,2),
                                        readonly=True,
                                        compute='_avg_cotwo_calculate',
                                        store=True)
    cost                = fields.Float(string="Cost",
                                        digits=(5,2))
    info                = fields.Text(string="Additional information")
    states              = [('new', "New"),
                            ('available', "Has seats available"),
                            ('full', "Full")]
    state               = fields.Selection(selection=states, default='new')


    @api.depends('distance')
    def _on_distance_calculate(self):
        for pool in self:
            pool.money_economy = pool.distance * 0.27

    @api.depends('distance')
    def _avg_cotwo_calculate(self):
        for pool in self:
            pool.avg_cotwo_economy = pool.distance * 118.5

    @api.depends('pooler_ids')
    def _on_pooler_manage_seats(self):
        for pool in self:
            if pool.seats <= len(pool.pooler_ids) - 1:
                return {
                    'warning': {
                        'title': "No more seats available",
                        'message': "Not enough seats for you to join the ride !",
                    }
                }
            pool.taken_seats = len(pool.pooler_ids)
            pool.taken_seats_tree = str(len(pool.pooler_ids)) + ' / ' + str(pool.seats)
            if pool.taken_seats:
                if pool.taken_seats == pool.seats:
                    pool.state = 'full'
                else :
                    pool.state = 'available'
            else:
                pool.state = 'new'

    @api.depends('arrival_id', 'departure_id')
    def _compute_departure_arrival(self):
        for pool in self:
            if pool.departure_id != False:
                pool.departure_tree = str(pool.departure_id.name) + ': ' + str(pool.departure_id.street) + ', ' + str(pool.departure_id.zipcode) + ' ' + str(pool.departure_id.city)
            if pool.arrival_id != False:
                pool.arrival_tree   = str(pool.arrival_id.name) + ': ' + str(pool.arrival_id.street) + ', ' + str(pool.arrival_id.zipcode) + ' ' + str(pool.arrival_id.city)

    ### Smart Buttons
    def smart_button_poolers(self):
        action = self.env.ref('carpooling.pooler_action').read()[0]
        action['domain'] = [('carpooling_ids.id', '=', self.id)]
        return action

class Address(models.Model):
    _name           = 'carpooling.address'
    _description    = 'Addresses for carpooling: Street, Zip, City'

    name   = fields.Char()
    description = fields.Char()

    street  = fields.Char()
    zipcode = fields.Integer()
    city    = fields.Char()

class Pooler(models.Model):
    _inherit = 'res.partner'

    carpooling_ids  = fields.Many2many('carpooling.carpooling',
                                        string="Carpoolings",
                                        default=0)