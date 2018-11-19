# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
                 'currency_id', 'company_id', 'date_invoice', 'type')
    def _compute_amount(self):
        round_curr = self.currency_id.round
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(round_curr(line.amount_total) for line in self.tax_line_ids)
        self.amount_total = self.amount_untaxed + self.amount_tax
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)

            # TODO: company currency => will send to compute method with the new parameter called rate_type_id -> comp.
            if self.currency_rate_type_id:
                amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id,
                                                                  rate_type=self.currency_rate_type_id, date=self.date_invoice)

            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign


class ResCurrency(models.Model):
    _inherit = "res.currency"

    @api.model
    def _get_conversion_rate(self, from_currency, to_currency, rate_type=False, date=False):
        from_currency = from_currency.with_env(self.env)
        to_currency = to_currency.with_env(self.env)

        # TODO : the calculation to be done by date_invoice again
        if date:
            rate_by_date = self.env['res.currency.rate'].search([('currency_id', '=', from_currency.id), ('name', '<=', date)])
            from_currency.rate_ids = rate_by_date
        # TODO: calculation by rate type -> completed
        if rate_type:
            if rate_type.name == "Döviz Alış":
                return to_currency.forex_buying_rate / from_currency.rate_ids[1].forex_buying_rate
            elif rate_type.name == "Döviz Satış":
                return to_currency.forex_selling_rate / from_currency.rate_ids[1].forex_selling_rate
            elif rate_type.name == "Efektif Alış":
                return to_currency.banknot_buying_rate / from_currency.rate_ids[1].banknot_buying_rate
            else:
                return to_currency.rate / from_currency.rate_ids[1].rate

        return to_currency.rate / from_currency.rate_ids[1].rate

    # TODO: company_currency => method parameter count to be increased -> completed
    @api.multi
    def compute(self, from_amount, to_currency, round=True, rate_type=False, date=False):
        """ Convert `from_amount` from currency `self` to `to_currency`. """
        self, to_currency = self or to_currency, to_currency or self
        assert self, "compute from unknown currency"
        assert to_currency, "compute to unknown currency"
        # apply conversion rate
        if self == to_currency:
            to_amount = from_amount
        else:
            to_amount = from_amount * self._get_conversion_rate(self, to_currency, rate_type=rate_type, date=date) # method called with extra parameter
        # apply rounding
        return to_currency.round(to_amount) if round else to_amount
