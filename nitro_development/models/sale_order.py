# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SalesOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_id', 'purchase_price', 'product_uom_qty', 'price_unit', 'price_subtotal')
    def _product_margin(self):
        for line in self:
            currency = line.order_id.pricelist_id.currency_id
            price = line.purchase_price
            if not price:
                from_cur = line.env.user.company_id.currency_id.with_context(date=line.order_id.date_order)
                price = from_cur.compute(line.product_id.standard_price, currency, round=False)

            line.margin = currency.round(line.price_subtotal - (price * line.product_uom_qty))

            # extra opt.
            if currency != line.product_id.currency_id:
                from_cur = line.product_id.currency_id.with_context(date=line.order_id.date_order)
                # price = from_cur.compute(price, line.product_id.currency_id, round=False)
                price = price / from_cur.rate
                line.margin = currency.round(line.price_subtotal - (price * line.product_uom_qty))


