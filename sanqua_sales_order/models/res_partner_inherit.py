from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    x_division_ids = fields.Many2many('sanqua.sales.division', string='Sales Divisions')
    x_remaining_credit_limit = fields.Monetary(string="Remaining Credit Limit", currency_field="x_company_currency_id", compute='_compute_remaining_credit_limit', store=True)
    x_company_currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    # Status
    x_credit_limit_status = fields.Boolean('Credit Limit Status', compute='_compute_credit_limit_status')
    x_overdue_status = fields.Boolean(compute='_compute_x_overdue_status')

    x_sales_person_ids = fields.One2many('res.partner.sales.person', 'x_partner_id', string='Sales Persons')

    @api.onchange('x_division_ids')
    def _onchange_x_division_ids(self):
        existing_division_ids = self.x_sales_person_ids.mapped('x_division_id.id')
        new_sales_person_lines = []
        for division in self.x_division_ids:
            if division.id not in existing_division_ids:
                new_sales_person_lines.append((0, 0, {'x_division_id': division.id}))
        self.x_sales_person_ids = [(5, 0, 0)] + new_sales_person_lines

    @api.depends('invoice_ids')
    def _compute_x_overdue_status(self):
        for partner in self:
            overdue_invoices = self.env['account.move'].search([
                ('partner_id', '=', partner.id),
                ('state', '=', 'posted'),
                ('invoice_date_due', '<', fields.Date.today()),
                ('amount_residual', '>', 0)
            ])
            partner.x_overdue_status = bool(overdue_invoices)

    @api.depends('credit_limit', 'credit')
    def _compute_remaining_credit_limit(self):
        for partner in self:
            partner.x_remaining_credit_limit = partner.credit_limit - partner.credit

    @api.depends('x_remaining_credit_limit', 'credit_limit')
    def _compute_credit_limit_status(self):
        for partner in self:
            if partner.credit_limit == 0:
                partner.x_credit_limit_status = False
            else:
                partner.x_credit_limit_status = partner.x_remaining_credit_limit < 0

class PartnerSalesPerson(models.Model):
    _name = 'res.partner.sales.person'
    _description = 'Sales Person per Division'

    x_partner_id = fields.Many2one('res.partner', string='Customer')
    x_division_id = fields.Many2one('sanqua.sales.division', string='Division')
    x_sales_person_id = fields.Many2one('res.users', string='Sales Person')