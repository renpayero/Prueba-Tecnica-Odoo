# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sample_request_ids = fields.One2many(
        'product.sample.request',
        'partner_id',
        string='Solicitudes de muestra',
    )
    sample_count = fields.Integer(
        string='Nº de muestras',
        compute='_compute_sample_count',
    )

    def _compute_sample_count(self):
        sample_data = self.env['product.sample.request'].read_group(
            domain=[('partner_id', 'in', self.ids)],
            fields=['partner_id'],
            groupby=['partner_id'],
        )
        mapped_data = {
            item['partner_id'][0]: item['partner_id_count']
            for item in sample_data
        }
        for partner in self:
            partner.sample_count = mapped_data.get(partner.id, 0)

    def action_view_sample_requests(self):
        """Abrir las solicitudes de muestra del cliente."""
        self.ensure_one()
        return {
            'name': 'Solicitudes de muestra',
            'type': 'ir.actions.act_window',
            'res_model': 'product.sample.request',
            'view_mode': 'tree,form,kanban',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }
