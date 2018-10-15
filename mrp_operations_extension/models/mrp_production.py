# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from odoo import models, fields, api, exceptions, _
import math


class MrpProduction(models.Model):
    _inherit = 'mrp.production'


class MrpProductionWorkcenterLine(models.Model):
    _inherit = 'mrp.workorder'


