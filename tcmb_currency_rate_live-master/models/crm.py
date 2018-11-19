# -*- coding: utf-8 -*-

from odoo import models, fields, api



class MechSoftLead(models.Model):
    _inherit = "crm.lead"

    planned_revenue = fields.Float(compute='_compute_planned_revenue', store=True)
    beklenen_ciro_kuru = fields.Many2one('res.currency', string="Kur")
    beklenen_ciro = fields.Integer(string="Beklenen Ciro")

    @api.one
    @api.depends('planned_revenue', 'beklenen_ciro', 'beklenen_ciro_kuru')
    def _compute_planned_revenue(self):
        beklenenCiroKuru = self.beklenen_ciro_kuru
        beklenenCiro = self.beklenen_ciro or 0

        if beklenenCiroKuru:
            currencyDef = self.env['res.currency'].search([('name', '=', beklenenCiroKuru.name)])
            if currencyDef:
                currencyRateIds = self.env['res.currency.rate'].search([('currency_id', '=', currencyDef.id)])
                if currencyRateIds:
                    last_id = currencyRateIds and max(currencyRateIds)
                    self.planned_revenue = int(self.beklenen_ciro) * 1 / last_id.rate
