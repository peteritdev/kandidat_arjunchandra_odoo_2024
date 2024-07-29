from datetime import datetime, timedelta
from odoo import models, fields, api

class StockQuantExtension(models.Model):
    _inherit = 'stock.quant'

    x_saldo_awal = fields.Float(string='Saldo Awal', compute='_compute_x_saldo_awal')
    x_total_masuk = fields.Float(string='Total Masuk', compute='_compute_x_total_masuk')
    x_total_keluar = fields.Float(string='Total Keluar', compute='_compute_x_total_keluar')
    x_saldo_akhir = fields.Float(string='Saldo Akhir', compute='_compute_x_saldo_akhir')

    @api.depends('product_id', 'location_id', 'lot_id')
    def _compute_x_saldo_awal(self):
        for quant in self:
            lot_id = quant.lot_id.id if quant.lot_id else None
            self.env.cr.execute("""
                SELECT COALESCE(SUM(quantity), 0) FROM stock_quant 
                WHERE product_id = %s AND location_id = %s AND (%s IS NULL OR lot_id = %s)
            """, (quant.product_id.id, quant.location_id.id, lot_id, lot_id))
            result = self.env.cr.fetchone()
            quant.x_saldo_awal = result[0] if result else 0

    @api.depends('product_id', 'location_id', 'lot_id')
    def _compute_x_total_masuk(self):
        for quant in self:
            lot_id = quant.lot_id.id if quant.lot_id else None
            self.env.cr.execute("""
                SELECT COALESCE(SUM(sml.qty_done), 0) FROM stock_move_line sml
                JOIN stock_location sl ON sml.location_dest_id = sl.id
                WHERE sml.product_id = %s AND sl.complete_name LIKE %s 
                AND (%s IS NULL OR sml.lot_id = %s) AND sml.state = 'done'
            """, (quant.product_id.id, 'WH/Stock%', lot_id, lot_id))
            result = self.env.cr.fetchone()
            quant.x_total_masuk = result[0] if result else 0

    @api.depends('product_id', 'location_id', 'lot_id')
    def _compute_x_total_keluar(self):
        for quant in self:
            lot_id = quant.lot_id.id if quant.lot_id else None
            self.env.cr.execute("""
                SELECT COALESCE(SUM(sml.qty_done), 0) FROM stock_move_line sml
                JOIN stock_location sl_src ON sml.location_id = sl_src.id
                JOIN stock_location sl_dest ON sml.location_dest_id = sl_dest.id
                WHERE sml.product_id = %s AND sl_src.complete_name LIKE %s 
                AND sl_dest.complete_name NOT LIKE %s AND (%s IS NULL OR sml.lot_id = %s)
                AND sml.state = 'done'
            """, (quant.product_id.id, 'WH/Stock%', 'WH/Stock%', lot_id, lot_id))
            result = self.env.cr.fetchone()
            quant.x_total_keluar = result[0] if result else 0

    @api.depends('x_total_masuk', 'x_total_keluar')
    def _compute_x_saldo_akhir(self):
        for quant in self:
            quant.x_saldo_akhir = quant.x_total_masuk - quant.x_total_keluar