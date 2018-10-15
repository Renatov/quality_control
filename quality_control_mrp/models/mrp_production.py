# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, exceptions, _
from openerp.addons.quality_control.models.qc_trigger_line import\
    _filter_trigger_lines


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.one
    @api.depends('qc_inspections')
    def _count_inspections(self):
        self.created_inspections = len(self.qc_inspections)

    qc_inspections = fields.One2many(
        comodel_name='qc.inspection', inverse_name='production', copy=False,
        string='Inspections', help="Inspections related to this production.")
    created_inspections = fields.Integer(
        compute="_count_inspections", string="Created inspections")

    @api.v7
    def action_produce(self, cr, uid, production_id, production_qty,
                       production_mode, wiz=False, context=None):
        production = self.browse(cr, uid, production_id, context=context)
        production.action_produce(
            production_id, production_qty, production_mode, wiz=wiz)

#    @api.model
#    def create(self, values):
#        if not values.get('name', False) or values['name'] == _('New'):
#            values['name'] = self.env['ir.sequence'].next_by_code('mrp.production') or _('New')
#        if not values.get('procurement_group_id'):
#            values['procurement_group_id'] = self.env["procurement.group"].create({'name': values['name']}).id
#        production = super(MrpProduction, self).create(values)
#        if production.move_finished_ids:
#            inspection_model = self.env['qc.inspection']
#            for move in production.move_finished_ids:
#                qc_trigger = self.env.ref('quality_control_mrp.qc_trigger_mrp')
#                trigger_lines = set()
#                for model in ['qc.trigger.product_category_line',
#                              'qc.trigger.product_template_line',
#                              'qc.trigger.product_line']:
#                    trigger_lines = trigger_lines.union(
#                        self.env[model].get_trigger_line_for_product(
#                            qc_trigger, move.product_id))
#                for trigger_line in _filter_trigger_lines(trigger_lines):
#                    inspection_model._make_inspection(move, trigger_line)
#        return production
    @api.multi
    def button_mark_done(self):
        if self.move_finished_ids:
            inspection_model = self.env['qc.inspection']
            for move in self.move_finished_ids:
                qc_trigger = self.env.ref('quality_control_mrp.qc_trigger_mrp')
                trigger_lines = set()
                for model in ['qc.trigger.product_category_line',
                              'qc.trigger.product_template_line',
                              'qc.trigger.product_line']:
                    trigger_lines = trigger_lines.union(
                        self.env[model].get_trigger_line_for_product(
                            qc_trigger, move.product_id))
                for trigger_line in _filter_trigger_lines(trigger_lines):
                    inspection_model._make_inspection(move, trigger_line)
        self.ensure_one()
        for wo in self.workorder_ids:
            if wo.time_ids.filtered(lambda x: (not x.date_end) and (x.loss_type in ('productive', 'performance'))):
                raise UserError(_('Work order %s is still running') % wo.name)
        self.post_inventory()
        moves_to_cancel = (self.move_raw_ids | self.move_finished_ids).filtered(lambda x: x.state not in ('done', 'cancel'))
        moves_to_cancel.action_cancel()
        self.write({'state': 'done', 'date_finished': fields.Datetime.now()})
        self.env["procurement.order"].search([('production_id', 'in', self.ids)]).check()
        self.write({'state': 'done'})
