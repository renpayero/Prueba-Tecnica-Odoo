# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ProductSampleRequest(models.Model):
    _name = 'product.sample.request'
    _description = 'Solicitud de Muestra de Producto'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    STATES = [
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('sent', 'Enviado'),
        ('received', 'Recibido'),
        ('rejected', 'Rechazado'),
        ('cancelled', 'Cancelado'),
    ]

    name = fields.Char(
        string='Referencia',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('Nuevo'),
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        required=True,
        tracking=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        required=True,
        tracking=True,
    )
    quantity = fields.Float(
        string='Cantidad',
        required=True,
        default=1.0,
    )
    request_date = fields.Date(
        string='Fecha de solicitud',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string='Comercial responsable',
        tracking=True,
    )
    notes = fields.Text(
        string='Observaciones internas',
    )
    state = fields.Selection(
        selection=STATES,
        string='Estado',
        required=True,
        default='draft',
        tracking=True,
        copy=False,
    )
    total_requests = fields.Integer(
        string='Total solicitudes del cliente',
        compute='_compute_total_requests',
    )

    @api.depends('partner_id')
    def _compute_total_requests(self):
        for record in self:
            if record.partner_id:
                record.total_requests = self.search_count([
                    ('partner_id', '=', record.partner_id.id),
                ])
            else:
                record.total_requests = 0

    def action_confirm(self):
        """Confirmar solicitud: draft -> confirmed. Genera secuencia."""
        for record in self:
            if record.quantity <= 0:
                raise UserError(
                    _('No se puede confirmar una solicitud con cantidad '
                      'igual a 0 o negativa.')
                )
            if record.name == _('Nuevo'):
                record.name = self.env['ir.sequence'].next_by_code(
                    'product.sample.request'
                ) or _('Nuevo')
            record.state = 'confirmed'

    def action_send(self):
        """Marcar como enviado: confirmed -> sent."""
        notification = None
        for record in self:
            # Verificar stock disponible (advertencia, no bloqueo)
            if record.product_id.qty_available <= 0:
                notification = {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Advertencia de stock'),
                        'message': _(
                            'El producto "%s" no tiene stock disponible. '
                            'Se continuará con el envío de la muestra.'
                        ) % record.product_id.display_name,
                        'type': 'warning',
                        'sticky': False,
                    },
                }
            record.state = 'sent'
        if notification:
            return notification

    def action_receive(self):
        """Marcar como recibido: sent -> received."""
        for record in self:
            record.state = 'received'

    def action_reject(self):
        """Abrir wizard de rechazo: sent -> rejected."""
        self.ensure_one()
        return {
            'name': _('Motivo de rechazo'),
            'type': 'ir.actions.act_window',
            'res_model': 'product.sample.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sample_request_id': self.id,
            },
        }

    def action_cancel(self):
        """Cancelar solicitud: draft/confirmed -> cancelled."""
        for record in self:
            if record.state not in ('draft', 'confirmed'):
                raise UserError(
                    _('Solo se pueden cancelar solicitudes en estado '
                      'borrador o confirmado.')
                )
            record.state = 'cancelled'

    def action_draft(self):
        """Volver a borrador: confirmed -> draft."""
        for record in self:
            record.state = 'draft'
