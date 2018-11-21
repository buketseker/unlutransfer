##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api


class ProductTemplate(models.Model):

    _inherit = "product.template"

    force_currency_id = fields.Many2one(
        'res.currency',
        'Force Currency',
        help='Use this currency instead of the product company currency'
    )
    company_currency_id = fields.Many2one(
        related='company_id.currency_id')

    @api.depends(
        'force_currency_id',
        'company_id',
        'company_id.currency_id')
    def _compute_currency_id(self):
        super(ProductTemplate, self)._compute_currency_id()
        for rec in self.filtered('force_currency_id'):
            rec.currency_id = rec.force_currency_id

    @api.depends('force_currency_id',
                 'standard_price')
    def _compute_standard_price(self):
        super(ProductTemplate, self)._compute_standard_price()

        for rec in self:
            force_currency_id = rec.force_currency_id
            standard_price = rec.standard_price

            if rec.categ_id.property_cost_method in ['fifo', 'average']:
                if force_currency_id:
                    currency_def = self.env['res.currency'].search([('name', '=', force_currency_id.name)])
                    if currency_def:
                        rec.standard_price = standard_price * currency_def.rate

