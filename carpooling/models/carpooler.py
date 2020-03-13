# -*- coding: utf-8 -*-

from odoo import fields,models,api

class Carpooler(models.Model):
    _name       =   'carpooling.carpooler'
    _rec_name   =   'driver_id'

    name            =   fields.Char(string="Name")
    driver_id       =   fields.Many2one('res.partner', default=lambda self: self.env.user.partner_id)
    contact_address =   fields.Char(related='driver_id.contact_address', string="Home address")
    has_car         =   fields.Boolean(default=False, string="Have a car")
    seats           =   fields.Integer(default=1, string="Available seats")
    preference      =   fields.Selection([('quite', 'Quite journey'), ('talk', 'Prefer talking'), ('music', 'Music enthusiast')], string="Preference")
    additional_info =   fields.Text(string="Additional information")

    r_carpool_ids   =   fields.One2many('carpooling.request', 'carpooler_id', string="Carpool request")



class CarpoolRequest(models.Model):
    _name       =   'carpooling.request'

    name            =   fields.Char(string="Name")
    carpooler_id    =   fields.Many2one('carpooling.carpooler', string="Carpooler")
    destination     =   fields.Many2one('carpooling.address', string="Destination")
    step_ids        =   fields.Many2many('carpooling.address', string="Steps")
    datetimes_ids   =   fields.Many2many('carpooling.datetimes', string="Days / Times")



class CarpoolAddress(models.Model):
    _name       =   'carpooling.address'

    name                =   fields.Char()
    street              =   fields.Char(string="Street")
    zipcode             =   fields.Char(stirng="Zip code")
    city                =   fields.Char(string="City")
    country_id          =   fields.Many2one('res.country', string="Country")

    complete_address    =   fields.Char(compute='_on_address_change', store=True)

    @api.depends('street', 'zipcode', 'city', 'country_id')
    def _on_address_change(self):
        for rec in self:
            complete = ''
            if rec.street:
                complete += rec.street
            if rec.zipcode:
                complete += rec.zipcode
            if rec.city:
                complete += rec.city
            if rec.country_id:
                complete += rec.country_id.name
            rec.complete_address = complete


class CarpoolDatetimes(models.Model):
    _name       =   'carpooling.datetimes'
    _rec_name   =   'formatted_datetime'

    name        =   fields.Char()
    formatted_datetime  =   fields.Char(compute='_on_date_time')
    days        =   fields.Selection([('mon',   'Monday'),
                                    ('tue',     'Tuesday'),
                                    ('wed',     'Wednesday'),
                                    ('thu',     'Thursday'),
                                    ('fri',     'Friday')])

    times       =   fields.Selection([('early',     '7:30 - 8:30'),
                                    ('midearly',    '8:00 - 9:00'),
                                    ('normal',      '8:30 - 9:30'),
                                    ('midlate',     '9:00 - 10:00'),
                                    ('late',        '9:30 - 10:30')])
    relations   =   {
        'mon'       : 'Monday',
        'tue'       : 'Tuesday',
        'wed'       : 'Wednesday',
        'thu'       : 'Thursday',
        'fri'       : 'Friday',
        'early'     : '7:30 - 8:30',
        'midearly'  : '8:00 - 9:00',
        'normal'    : '8:30 - 9:30',
        'midlate'   : '9:00 - 10:00',
        'late'      : '9:30 - 10:30'
    }

    @api.depends('days', 'times')
    def _on_date_time(self):
        for rec in self:
            if rec.days and rec.times:
                rec.formatted_datetime = rec.relations[rec.days] + ' ' + rec.relations[rec.times]