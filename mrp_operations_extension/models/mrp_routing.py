# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _
from openerp.addons import decimal_precision as dp


class MrpRouting(models.Model):
    _inherit = 'mrp.routing'
    @api.constrains('operation_ids')
    def _check_produce_operation(self):
        if not self.operation_ids:
            return
        num_produce = sum([x.do_production for x in self.operation_ids])
        if num_produce != 1:
            raise Warning(_("There must be one and only one operation with "
                            "'Produce here' check marked."))

    previous_operations_finished = fields.Boolean(
        string='Previous operations finished')


class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    def get_routing_previous_operations(self):
        self.previous_operations_finished = \
            self.routing_id.previous_operations_finished

    operation = fields.Many2one('mrp.routing.operation', string='Operation')
    op_wc_lines = fields.One2many(
        'mrp.operation.workcenter', 'routing_workcenter',
        string='Possible work centers for this operation')
    do_production = fields.Boolean(
        string='Produce here',
        help="If enabled, the production and movement to stock of the final "
             "products will be done in this operation. There can be only one "
             "operation per route with this check marked.")
    previous_operations_finished = fields.Boolean(
        string='Previous operations finished',
        default="get_routing_previous_operations")
    picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type',
                                      domain=[('code', '=', 'outgoing')])
    @api.constrains('op_wc_lines')
    def _check_default_op_wc_lines(self):
        if not self.op_wc_lines:
            return
        num_default = len([x for x in self.op_wc_lines if x.default])
        if num_default != 1:
            raise Warning(
                _('There must be one and only one line set as default.'))

    @api.onchange('operation')
    def onchange_operation(self):
        if self.operation:
            self.name = self.operation.name
            self.note = self.operation.description
            op_wc_lst = []
            is_default = True
            for operation_wc in self.operation.workcenters:
                print operation_wc.name
                data = {
                    'default': is_default,
                    'workcenter': operation_wc.id,
                    'capacity_per_cycle': operation_wc.capacity,
                    'time_efficiency': operation_wc.time_efficiency,
                    'time_start': operation_wc.time_start,
                    'time_stop': operation_wc.time_stop,
                    'op_number': self.operation.op_number,
                }
                op_wc_lst.append(data)
                is_default = False
            self.op_wc_lines = op_wc_lst

    @api.onchange('op_wc_lines')
    def onchange_lines_default(self):
        for line in self.op_wc_lines:
            if line.default:
                self.workcenter_id = line.workcenter
                break


class MrpOperationWorkcenter(models.Model):
    _name = 'mrp.operation.workcenter'
    _description = 'MRP Operation Workcenter'

    workcenter = fields.Many2one(
        'mrp.workcenter', string='Workcenter', required=True)
    routing_workcenter = fields.Many2one(
        'mrp.routing.workcenter', 'Routing workcenter', required=True)
    time_efficiency = fields.Float('Efficiency factor')
    capacity_per_cycle = fields.Float('Capacity per cycle')
    time_cycle = fields.Float('Time for 1 cycle (hours)',
                              help="Time in hours for doing one cycle.")
    time_start = fields.Float('Time before prod.',
                              help="Time in hours for the setup.")
    time_stop = fields.Float('Time after prod.',
                             help="Time in hours for the cleaning.")
    op_number = fields.Integer('# operators', default='0')
    op_avg_cost = fields.Float(
        string='Operator avg. hour cost',
        digits=dp.get_precision('Product Price'))
    default = fields.Boolean('Default')

    @api.onchange('workcenter')
    def onchange_workcenter(self):
        if self.workcenter:
            self.capacity_per_cycle = self.workcenter.capacity
            self.time_efficiency = self.workcenter.time_efficiency
            self.time_start = self.workcenter.time_start
            self.time_stop = self.workcenter.time_stop
            self.op_number = self.workcenter.op_number
            self.op_avg_cost = self.workcenter.op_avg_cost
