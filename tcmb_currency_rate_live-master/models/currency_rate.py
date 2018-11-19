# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp

from datetime import datetime


class CurrencyRateType(models.Model):
    _name = 'res.currency.rate.type'
    _description = 'Para Birimi Kur Tipi'

    name = fields.Char(string='Kur Tipi')


class CurrencyRate(models.Model):
    _inherit = 'res.currency.rate'

    banknot_buying_rate = fields.Float(digits=(12, 6), string="Efektif Alış")
    forex_selling_rate = fields.Float(digits=(12, 6), string="Döviz Satış")
    forex_buying_rate = fields.Float(digits=(12, 6), string="Döviz Alış")
    special_rate = fields.Float(digits=(12, 6), string="Özel Kur")


class Currency(models.Model):
    _inherit = 'res.currency'

    rate = fields.Float(compute='_compute_current_rate', string='Efektif Satış', digits=(12, 6),
                        help='The rate of the currency to the currency of rate 1.')
    banknot_buying_rate = fields.Float(digits=(12, 6), string="Efektif Alış", compute='compute_banknot_buying_rate')
    forex_selling_rate = fields.Float(digits=(12, 6), string="Döviz Satış", compute='compute_forex_selling_rate')
    forex_buying_rate = fields.Float(digits=(12, 6), string="Döviz Alış", compute='compute_forex_buying_rate')
    special_rate = fields.Float(digits=(12, 6), string="Özel Kur")

    @api.multi
    @api.depends('rate_ids.rate')
    def compute_banknot_buying_rate(self):
        date = self._context.get('date') or fields.Date.today()
        company_id = self._context.get('company_id') or self.env['res.users']._get_company().id
        query = """SELECT c.id, (SELECT r.banknot_buying_rate FROM res_currency_rate r
                                          WHERE r.currency_id = c.id AND r.name <= %s
                                            AND (r.company_id IS NULL OR r.company_id = %s)
                                       ORDER BY r.company_id, r.name DESC
                                          LIMIT 1) AS banknot_buying_rate
                           FROM res_currency c
                           WHERE c.id IN %s"""
        self._cr.execute(query, (date, company_id, tuple(self.ids)))
        currency_rates = dict(self._cr.fetchall())
        for currency in self:
            currency.banknot_buying_rate = currency_rates.get(currency.id) or 1.0

    @api.multi
    @api.depends('rate_ids.rate')
    def compute_forex_selling_rate(self):
        date = self._context.get('date') or fields.Date.today()
        company_id = self._context.get('company_id') or self.env['res.users']._get_company().id
        query = """SELECT c.id, (SELECT r.forex_selling_rate FROM res_currency_rate r
                                          WHERE r.currency_id = c.id AND r.name <= %s
                                            AND (r.company_id IS NULL OR r.company_id = %s)
                                       ORDER BY r.company_id, r.name DESC
                                          LIMIT 1) AS forex_selling_rate
                           FROM res_currency c
                           WHERE c.id IN %s"""
        self._cr.execute(query, (date, company_id, tuple(self.ids)))
        currency_rates = dict(self._cr.fetchall())
        for currency in self:
            currency.forex_selling_rate = currency_rates.get(currency.id) or 1.0

    @api.multi
    @api.depends('rate_ids.rate')
    def compute_forex_buying_rate(self):
        date = self._context.get('date') or fields.Date.today()
        company_id = self._context.get('company_id') or self.env['res.users']._get_company().id
        query = """SELECT c.id, (SELECT r.forex_buying_rate FROM res_currency_rate r
                                          WHERE r.currency_id = c.id AND r.name <= %s
                                            AND (r.company_id IS NULL OR r.company_id = %s)
                                       ORDER BY r.company_id, r.name DESC
                                          LIMIT 1) AS forex_buying_rate
                           FROM res_currency c
                           WHERE c.id IN %s"""
        self._cr.execute(query, (date, company_id, tuple(self.ids)))
        currency_rates = dict(self._cr.fetchall())
        for currency in self:
            currency.forex_buying_rate = currency_rates.get(currency.id) or 1.0


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    currency_rate_type_id = fields.Many2one('res.currency.rate.type', string='Para Birimi Kur Tipi')

    currency_rate = fields.Float(string="Para Birimi Kuru", digits=dp.get_precision('Payroll Rate'), default=1.0,
                                 compute='update_currency_rate', store=True,
                                 states={'draft': [('readonly', False)]})

    custom_rate = fields.Boolean(string="Özel Kur")

    default_currency = fields.Char(string="Default Currency", default=lambda self: self.env.user.company_id.currency_id.name)

    @api.model
    def create(self, vals):
        res = super(AccountInvoice, self).create(vals)
        if vals.get('custom_rate') and vals.get('currency_rate'):
            self.setup_custom_currency(vals)
            res.update({
                'currency_rate': vals['currency_rate']
            })
        return res

    @api.multi
    def write(self, vals):
        res = super(AccountInvoice, self).write(vals)
        if vals.get('currency_rate'):
            for record in self:
                if record.custom_rate and vals.get('currency_rate'):
                    record.setup_custom_currency(vals)
        return res

    def setup_custom_currency(self, vals):
        currency_id = self.currency_id.id
        currency_object = self.env['res.currency'].search([('id', '=', currency_id)])
        if currency_object:
            currency_object.write({
                'special_rate': vals['currency_rate']
            })
        
    @api.one
    @api.depends('currency_id',
                 'currency_rate_type_id',
                 'date_invoice')
    def update_currency_rate(self):
        for record in self:
            if record.currency_rate_type_id:
                currency = record.currency_id
                rate_type = record.currency_rate_type_id
                currency_rate_obj = self.env['res.currency.rate']
                expected_currency = record.env['res.currency'].search([('name', '=', currency.name)])
                currencyRateIds = currency_rate_obj.search([('currency_id', '=', expected_currency.id)])
                if currencyRateIds:
                    # last_id = currencyRateIds and max(currencyRateIds)
                    last_id = currencyRateIds and currencyRateIds[1]  # exchange rate a day before
                    if record.date_invoice:
                        today = datetime.now().strftime("%Y-%m-%d")
                        if record.date_invoice != today:
                            rate_by_date = currency_rate_obj.search([('currency_id', '=', expected_currency.id),
                                                                     ('name', '=', record.date_invoice)], limit=1)
                            last_id = currency_rate_obj.search([('currency_id', '=', expected_currency.id),
                                                                ('id', '<', rate_by_date.id)], order="id desc", limit=1)

                    if rate_type.name == 'Efektif Satış':
                        if last_id.rate > 0.0:
                            record.currency_rate = 1 / last_id.rate
                    elif rate_type.name == 'Efektif Alış':
                        if last_id.banknot_buying_rate > 0.0:
                            record.currency_rate = 1 / last_id.banknot_buying_rate
                    elif rate_type.name == 'Döviz Satış':
                        if last_id.forex_selling_rate > 0.0:
                            record.currency_rate = 1 / last_id.forex_selling_rate
                    elif rate_type.name == 'Döviz Alış':
                        if last_id.forex_buying_rate > 0.0:
                            record.currency_rate = 1 / last_id.forex_buying_rate

















