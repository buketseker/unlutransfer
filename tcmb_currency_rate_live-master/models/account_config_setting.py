# -*- coding: utf-8 -*-

import datetime
from lxml import etree
import json
from dateutil.relativedelta import relativedelta
import requests
import urllib

from odoo import api, fields, models
from odoo.addons.web.controllers.main import xml2json_from_elementtree
from odoo.exceptions import UserError
from odoo.tools.translate import _

class ResCompany(models.Model):
    _inherit = 'res.company'
    currency_provider = fields.Selection(selection_add = [('tcmb', 'TCMB')], default='tcmb', string='Service Provider')

    @api.multi
    def update_currency_rates(self):
        ''' This method is used to update all currencies given by the provider. Depending on the selection call _update_currency_ecb _update_currency_yahoo. '''
        res = True
        for company in self:
            if company.currency_provider == 'yahoo':
                res = company._update_currency_yahoo()
            elif company.currency_provider == 'ecb':
                res = company._update_currency_ecb()
            elif company.currency_provider == 'tcmb':
                res = company._update_currency_tcmb()
            if not res:
                raise UserError(_('Unable to connect to the online exchange rate platform. The web service may be temporary down. Please try again in a moment.'))

    @api.multi
    def _update_currency_tcmb(self):

        Currency = self.env['res.currency']
        CurrencyRate = self.env['res.currency.rate']

        currencies = Currency.search([])
        currencies = [x.name for x in currencies]
        request_url = "http://www.tcmb.gov.tr/kurlar/today.xml"
        try:
            parse_url = requests.request('GET', request_url)
        except:
            #connection error, the request wasn't successful
            return False

        xmlstr = etree.fromstring(parse_url.content)
        data = xml2json_from_elementtree(xmlstr)

        node = data
        currency_node = [(x['attrs']['CurrencyCode'], x['children'][6]['children'][0],
                                                      x['children'][5]['children'][0],
                                                      x['children'][4]['children'][0],
                                                      x['children'][3]['children'][0]) for x in node['children'] if x['attrs']['CurrencyCode'] in currencies]

        for company in self:
            base_currency_rate = 1
            if company.currency_id.name != 'TRY':
                #find today's rate for the base currency
                base_currency = company.currency_id.name
                base_currency_rates = [(x['attrs']['CurrencyCode'], x['children'][6]['children'][0],
                                                                    x['children'][5]['children'][0],
                                                                    x['children'][4]['children'][0],
                                                                    x['children'][3]['children'][0]) for x in node['children'] if x['attrs']['CurrencyCode'] == base_currency]

                base_currency_rate = len(base_currency_rates) and base_currency_rates[0][1] or 1

                banknot_buying = len(base_currency_rates) and base_currency_rates[0][2] or 1
                forex_selling = len(base_currency_rates) and base_currency_rates[0][3] or 1
                forex_buying = len(base_currency_rates) and base_currency_rates[0][4] or 1

                currency_node += [('TRY', '1.0000')]

            for currency_code, rate, banknot_buying, forex_selling, forex_buying in currency_node:
                rate = float(base_currency_rate)/float(rate)

                banknot_buying_rate = float(base_currency_rate)/float(banknot_buying)
                forex_selling_rate = float(base_currency_rate)/float(forex_selling)
                forex_buying_rate = float(base_currency_rate)/float(forex_buying)

                currency = Currency.search([('name', '=', currency_code)], limit=1)
                if currency:
                    CurrencyRate.create({'currency_id': currency.id,
                                         'rate': rate,
                                         'banknot_buying_rate': banknot_buying_rate,
                                         'forex_selling_rate': forex_selling_rate,
                                         'forex_buying_rate': forex_buying_rate,
                                         'name': fields.Datetime.now(),
                                         'company_id': company.id})

            if company.currency_id.rate != 1.0:
                CurrencyRate.create({'currency_id': company.currency_id.id,
                                     'rate': 1.0,
                                     'banknot_buying_rate': 1.0,
                                     'forex_selling_rate': 1.0,
                                     'forex_buying_rate': 1.0,
                                     'name': fields.Datetime.now(),
                                     'company_id': company.id})

        return True