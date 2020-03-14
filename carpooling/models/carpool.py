# -*- coding: utf-8 -*-

from odoo import fields,api,models

class Carpool(models.Model):
    _name   =   'carpooling.carpool'
    from_id         =   fields.Many2one('carpooling.address', string="From")
    to_id           =   fields.Many2one('carpooling.address', string="To")
    step_ids        =   fields.Many2many('carpooling.address', 'carpooling_schedule_carpooling_address_steps', string="Steps")
    schedule_ids    =   fields.Many2many('carpooling.schedule', string="Cummuting days/times")
    carpooler_ids   =   fields.Many2many('carpooling.carpooler', string="Carpoolers")
    status          =   fields.Selection([('open', 'Open poolationship'), ('close', 'Closed poolationship')], default="open")

class CarpoolSchedule(models.Model):
    _name   =   'carpooling.schedule'
    _rec_name   =   'formatted_datetime'

    name        =   fields.Char()
    formatted_datetime  =   fields.Char(compute='_on_date_time', string="Days / Times", store=True)
    days        =   fields.Selection([('mon',   'Monday'),
                                    ('tue',     'Tuesday'),
                                    ('wed',     'Wednesday'),
                                    ('thu',     'Thursday'),
                                    ('fri',     'Friday')])

    time_go     =   fields.Selection([('early',     '7:30 - 8:30'),
                                    ('midearly',    '8:00 - 9:00'),
                                    ('normal',      '8:30 - 9:30'),
                                    ('midlate',     '9:00 - 10:00'),
                                    ('late',        '9:30 - 10:30'),
                                    ('amearly',     '15:30 - 16:30'),
                                    ('ammidearly',    '16:00 - 17:00'),
                                    ('amnormal',      '16:30 - 17:30'),
                                    ('ammidlate',     '17:00 - 18:00'),
                                    ('amlate',        '17:30 - 18:30')], default=False)
    time_back     =   fields.Selection([('early',     '7:30 - 8:30'),
                                    ('midearly',    '8:00 - 9:00'),
                                    ('normal',      '8:30 - 9:30'),
                                    ('midlate',     '9:00 - 10:00'),
                                    ('late',        '9:30 - 10:30'),
                                    ('amearly',     '15:30 - 16:30'),
                                    ('ammidearly',    '16:00 - 17:00'),
                                    ('amnormal',      '16:30 - 17:30'),
                                    ('ammidlate',     '17:00 - 18:00'),
                                    ('amlate',        '17:30 - 18:30')], default=False)

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
        'late'      : '9:30 - 10:30',
        'amearly'     : '15:30 - 16:30',
        'ammidearly'  : '16:00 - 17:00',
        'amnormal'    : '16:30 - 17:30',
        'ammidlate'   : '17:00 - 18:00',
        'amlate'      : '17:30 - 18:30'
    }

    @api.depends('days', 'time_go', 'time_back')
    def _on_date_time(self):
        for rec in self:
            if rec.days and rec.time_go and rec.time_back:
                rec.formatted_datetime = rec.relations[rec.days] + ' ' + rec.relations[rec.time_go] + ' : ' + rec.relations[rec.time_back]