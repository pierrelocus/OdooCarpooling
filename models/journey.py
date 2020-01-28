#-*- coding: utf-8 -*
import datetime
from odoo import models, api, fields

class Journey(models.Model):
    _name           = 'carpooling.journey'
    _description    = """Represents a journey. Once created, a journey can be converted
    into carpoolings."""

    driver_id           = fields.Many2one('res.partner', required=True,
                                        string="Driver",
                                        domain="[('is_company', '=', False)]")
    _rec_name           = 'driver_id'
    description         = fields.Text()
    departure_id        = fields.Many2one('carpooling.address', 
                                            string="Pickup point",
                                            required=True)
    departure_tree      = fields.Char(related='departure_id.full_address',
                                    string="Pickup point")
    arrival_id          = fields.Many2one('carpooling.address',
                                            string="Dropoff point",
                                            required=True)
    arrival_tree        = fields.Char(related='arrival_id.full_address',
                                    string="Dropoff point")
    steps_ids           = fields.Many2many('carpooling.address',
                                            string="Steps")
    seats               = fields.Integer(required=True, default=3)
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
    day_ids             = fields.One2many('carpooling.days', 'journey_id',
                                        string="Days available")
    until_date          = fields.Date(string="Available until")
    carpooling_ids      = fields.One2many('carpooling.carpooling', 'journey_id',
                                        string="Carpoolings")
    has_carpoolings     = fields.Boolean(default=False)

    def action_toggle_carpools(self):
        self.ensure_one()
        self.has_carpoolings = not self.has_carpoolings
        todayday    = datetime.date.today()
        untilday    = self.until_date
        dayz        = {
            0: 'monday',
            1: 'tuesday',
            2: 'wednesday',
            3: 'thursday',
            4: 'friday',
            5: 'saturday',
            6: 'sunday'
        }
        print("Hello world !")
        if self.has_carpoolings:
            if self.day_ids != False and untilday:
                try:
                    while todayday <= untilday:
                        for dday in self.day_ids:
                            cur_time    = dday.times
                            cur_day     = dday.day
                            if dayz[todayday.weekday()] == cur_day.lower():
                                self.env['carpooling.carpooling'].create({
                                    'journey_id': self.id,
                                    'driver_id': self.driver_id.id,
                                    'departure_id': self.departure_id.id,
                                    'departure_date': todayday,
                                    'departure_time': cur_time,
                                    'arrival_id': self.arrival_id.id,
                                    'steps_ids': [(6, 0, self.steps_ids.ids)],
                                    'seats': self.seats,
                                    'distance': self.distance,
                                    'cost': self.cost,
                                    'info': self.info
                                })
                        todayday += datetime.timedelta(days=1)
                    return {'warning': {'title': "Saved", 'message': "Saved !"}}
                except:
                    return {'warning': {'title': "Error", 'message': "An error occured"}}
        else:
            try:
                self.carpooling_ids.unlink()
            except:
                return {}
    @api.depends('distance')
    def _on_distance_calculate(self):
        for pool in self:
            pool.money_economy = pool.distance * 0.27

    @api.depends('distance')
    def _avg_cotwo_calculate(self):
        for pool in self:
            pool.avg_cotwo_economy = pool.distance * 118.5


class Address(models.Model):
    _name           = 'carpooling.address'
    _description    = 'Addresses for carpooling: Street, Zip, City'
    
    name   = fields.Char()
    description = fields.Char()

    street  = fields.Char()
    zipcode = fields.Integer()
    city    = fields.Char()
    full_address = fields.Char(compute="_compute_full_address")

    @api.depends('street', 'zipcode', 'city')
    def _compute_full_address(self):
        self.ensure_one()
        self.full_address = self.name + ': ' + self.street + ', ' + str(self.zipcode) + ' ' + self.city

class Pooler(models.Model):
    _inherit    = 'res.partner'
    _name       = 'res.partner'
    carpooling_ids  = fields.Many2many('carpooling.carpooling',
                                        string="Carpoolings",
                                        default=0)
    # contact_address_complete = fields.Char(compute='_compute_complete_address', store=True)

    # @api.model
    # def update_latitude_longitude(self, partners):
    #     partners_data = defaultdict(list)

    #     for partner in partners:
    #         if 'id' in partner and 'partner_latitude' in partner and 'partner_longitude' in partner:
    #             partners_data[(partner['partner_latitude'], partner['partner_longitude'])].append(partner['id'])

    #     for values, partner_ids in partners_data.items():
    #         # NOTE this should be done in sudo to avoid crashing as soon as the view is used
    #         self.browse(partner_ids).sudo().write({
    #             'partner_latitude': values[0],
    #             'partner_longitude': values[1],
    #         })

    #     return {}

    @api.onchange('street', 'zip', 'city', 'state_id', 'country_id')
    def _delete_coordinates(self):
        self.partner_latitude = False
        self.partner_longitude = False

    @api.depends('street', 'zip', 'city', 'country_id')
    def _compute_complete_address(self):
        for record in self:
            record.contact_address_complete = ''
            if record.street:
                record.contact_address_complete += record.street+','
            if record.zip:
                record.contact_address_complete += record.zip+ ' '
            if record.city:
                record.contact_address_complete += record.city+','
            if record.country_id:
                record.contact_address_complete += record.country_id.name





class Days(models.Model):
    _name           = 'carpooling.days'
    _description    = 'Represents days of the week'

    journey_id      = fields.Many2one('carpooling.journey', ondelete='cascade')
    times           = fields.Float(string="Hour")
    day             = fields.Selection([('monday', 'Monday'),
                                        ('tuesday', 'Tuesday'),
                                        ('wednesday', 'Wednesday'),
                                        ('thursday', 'Thursday'),
                                        ('friday', 'Friday')])