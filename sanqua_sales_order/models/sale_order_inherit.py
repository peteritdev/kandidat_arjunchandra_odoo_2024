# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'


    x_division_id = fields.Many2one('sanqua.sales.division', string='Division', required=True)
    x_pickup_method = fields.Selection([
            ('delivery', 'Delivery'),
            ('take_in_plant', 'Take in Plant'),
        ], string='Pickup Method')
    partner_id = fields.Many2one(
            'res.partner', string='Customer', readonly=True,
            states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
            required=True, change_default=True, index=True, tracking=1,
            domain="['|', ('company_id', '=', False), ('company_id', '=', company_id), ('x_division_ids', 'in', x_division_id)]"
        )
    overlimit_status = fields.Boolean(string='Overlimit Status', compute='_compute_credit_limit_status')
    overdue_status = fields.Boolean(string='Overdue Status', compute='_compute_credit_limit_status')
    overlimit_and_overdue_status = fields.Boolean(string='Overlimit and Overdue Status', compute='_compute_credit_limit_status')


    @api.onchange('x_pickup_method', 'order_line.product_id','pricelist_id')
    def _onchange_pickup_method_or_product(self):
        for line in self.order_line:
            if not line.product_id:
                line.discount = 0
                continue

            line.price_unit = self.pricelist_id.get_product_price(line.product_id, line.product_uom_qty or 1, self.partner_id)
            if self.x_pickup_method == 'take_in_plant':
                discount_amount = line.product_id.product_tmpl_id.take_in_plant_discount
                if line.product_id.list_price > 0:
                    discount_percentage = (discount_amount / line.product_id.list_price) * 100
                    line.discount = min(discount_percentage, 100)
                else:
                    line.discount = 0
            else:
                line.discount = 0

    @api.onchange('x_division_id')
    def _onchange_x_division_id(self):
        if self.x_division_id:
            self.pricelist_id = self.x_division_id.x_product_pricelist_id
            self.partner_id = False
            self.x_pickup_method = False
            self.payment_term_id = False


    @api.depends('partner_id')
    def _compute_credit_limit_status(self):
        for order in self:
            partner = order.partner_id
            order.overlimit_status = partner.x_credit_limit_status and not partner.x_overdue_status
            order.overdue_status = partner.x_overdue_status and not partner.x_credit_limit_status
            order.overlimit_and_overdue_status = partner.x_credit_limit_status and partner.x_overdue_status


    def _check_credit_limit(self):
        for order in self:
            partner = order.partner_id
            messages = []

            if partner.x_credit_limit_status and partner.x_overdue_status:
                messages.append("This customer has exceeded their credit limit and has overdue invoices. Do you want to continue?")

            else:
                if partner.x_credit_limit_status:
                    messages.append("This customer has exceeded their credit limit. Do you want to continue?")

                if partner.x_overdue_status:
                    messages.append("This customer has overdue invoices. Do you want to continue?")

            if messages:
                return "\n".join(messages)
        return False


    def show_sale_order_confirmation(self, warning):
        title = 'Warning'
        view = self.env.ref('sanqua_sales_order.view_sale_order_warning_wizard_form') 
        
        return {
            'name': title,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sale.order.warning.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': {
                'default_message': warning,
                'active_id': self.id,
            },
        }
    
    def action_confirm(self):
        if not self.env.context.get('skip_check'):
            warning = self._check_credit_limit()
            if warning:
                return self.show_sale_order_confirmation(warning)
        return super(SaleOrderInherit, self).action_confirm()
    


class SaleOrderWarningWizard(models.TransientModel):
    _name = 'sale.order.warning.wizard'
    _description = 'Sale Order Warning Wizard'

    message = fields.Text(string='Warning Message')

    def action_confirm(self):
        sale_order = self.env['sale.order'].browse(self.env.context.get('active_id'))
        return sale_order.with_context(skip_check=True).action_confirm()
    



class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    x_division_id = fields.Many2one('sanqua.sales.division', string='Division', related='order_id.x_division_id', store=True)

    product_id = fields.Many2one(
        'product.product', string='Product',
        domain="[('sale_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id), ('x_division_id', '=', x_division_id)]",
        change_default=True, ondelete='restrict', check_company=True
    )



class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    x_sales_person_id = fields.Many2one('res.users', string='Sales Person')
    x_division_id = fields.Many2one('sanqua.sales.division', string='Division')
    take_in_plant_discount = fields.Float(string='Take in Plant Discount')


class ProductProductInherit(models.Model):
    _inherit = 'product.product'

    x_division_id = fields.Many2one('sanqua.sales.division', string='Division', related='product_tmpl_id.x_division_id', store=True)
    