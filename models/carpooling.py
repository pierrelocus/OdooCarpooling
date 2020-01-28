#-*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime


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

    @api.depends('pooler_ids', 'seats')
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
