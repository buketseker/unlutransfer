# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ContactRegion(models.Model):
    _name = 'res.contact.region'

    name = fields.Char(string="Bölge", required=True)
    country_id = fields.Many2one('res.country', string="Ülke", required=True)
    code = fields.Char(string="Kod", required=True)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_invoice_name = fields.Char(string='Ürün Fatura İsmi', translate=True,
                                       help='Ürüne ait faturada görünecek ismi yazılacağı alan')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    region_id = fields.Many2one('res.contact.region', string='Bölge')

    _sql_constraints = [
        ('mobil_unique', 'unique(mobile)', 'Mobil numara daha önce sisteme kaydedilmiş !')
    ]

    @api.model
    def create(self, vals):
        if vals.get('company_type'):
            company_type = vals['company_type']
            if company_type == 'person':
                if not vals.get('mobile'):
                    raise ValidationError(
                        'Eğer müşteri bireysel ise Mobil alanı girilmek zorundadır.'
                    )
            elif company_type == 'company':
                if not vals.get('vat'):
                    raise ValidationError(
                        'Eğer müşteri şirket ise Vergi No alanı girilmek zorundadır.'
                    )

        if vals.get('lang') and vals['lang'] != 'tr_TR':
            vals['lang'] = 'tr_TR'
        elif 'lang' not in vals:
            vals['lang'] = 'tr_TR'

        return super(ResPartner, self).create(vals)




