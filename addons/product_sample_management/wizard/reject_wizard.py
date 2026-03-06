# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductSampleRejectWizard(models.TransientModel):
    _name = 'product.sample.reject.wizard'
    _description = 'Wizard de rechazo de muestra'

    sample_request_id = fields.Many2one(
        'product.sample.request',
        string='Solicitud de muestra',
        required=True,
    )
    reject_reason = fields.Text(
        string='Motivo del rechazo',
        required=True,
    )

    def action_reject(self):
        """Confirmar rechazo: guarda motivo en notas y cambia estado."""
        self.ensure_one()
        self.sample_request_id.write({
            'notes': self.reject_reason,
            'state': 'rejected',
        })
        return {'type': 'ir.actions.act_window_close'}
