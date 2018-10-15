# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class StockMove(models.Model):
    _inherit = "stock.move"

    work_order = fields.Many2one('mrp.workorder',
                                 string='Work Order')
