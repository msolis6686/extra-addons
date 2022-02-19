from odoo import models, fields, api
from odoo import _
from odoo.exceptions import UserError, ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    cnic_no = fields.Char('CNIC no', copy=False, company_dependent=True)
    contract_id = fields.One2many('real.estate.contract', 'contract_partner_id')

    def name_get(self):
        res = []
        for partner in self:
            if partner.cnic_no:
                name = partner.name + ' (' + partner.cnic_no + ')'
            else:
                name = partner._get_name()
            res.append((partner.id, name))
        return res

    #for buttons only
    transactions = fields.Char(default="Transaction")
    contract = fields.Char(default="Contract")



    # def transaction_button_click(self):
    #     return {
    #         'name': _('Transaction'),
    #         'domain': [('partner_id', '=', self.id)],
    #         # 'view_type': 'tree,pivot,graph',
    #         'res_model': 'account.move.line',
    #         'view_id': self.env.ref("Property management.view_move_line_tree_grouped_sales_purchases").id,
    #         'view_mode': 'list',
    #         'type': 'ir.actions.act_window',
    #         'target': 'current',
    #         'context': {'default_partner_id': self.id},
    #     }


    @api.onchange('cnic_no')
    def add_validation(self):
        if self.cnic_no:
            if len(self.cnic_no) < 13:
                raise ValidationError('Invalid CNIC \n Enter 13 digit CNIC number')

    def action_partner_contract(self):
        # context = self._context.copy()
        # context['default_member_partner_id'] = self.id
        # print('partner', self.env.ref("Property management.member_form_view").id)
        return {
            'name': _('Contract'),
            'domain': [('contract_partner_id','=', self.id)],
            'view_type': 'form',
            'res_model': 'real.estate.contract',
            'view_id': self.env.ref("Property management.view_contract_form").id,
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {'default_contract_partner_id': self.id, 'contract_partner_name': self.name,},
        }

    def action_transactions(self):
        # action = self.env.ref('account.action_move_out_invoice_type')
        # result = action.read()[0]
        # context = self._context.copy()
        # context['default_partner_id'] = self.id
        # print('partner id', self.id)
        return {
            'name': _('Account'),
            'domain': [('partner_id', '=', self.id), ('state', '=', 'posted')],
            'view_type': 'tree',
            'res_model': 'account.move',
            # 'view_id': self.env.ref("account.action_move_out_invoice_type").id,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            # 'target': 'new',
            # 'context': context,
        }




