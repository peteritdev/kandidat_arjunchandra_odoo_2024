from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class SanquaSalesDivision(models.Model):
    _name = 'sanqua.sales.division'
    _description = 'Sanqua Sales Division'

    name = fields.Char(string='Division Name', required=True)
    x_product_pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')
    x_note = fields.Text(string='Note')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The division name must be unique!')
    ]

    @api.constrains('name')
    def _check_name_unique(self):
        for record in self:
            if self.search([('name', '=', record.name), ('id', '!=', record.id)]):
                raise ValidationError("The division name must be unique!")

