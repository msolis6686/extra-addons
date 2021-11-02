# Author: Damien Crier
# Author: Julien Coux
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models


class GeneralLedgerXslx(models.AbstractModel):
    _inherit = "report.a_f_r.report_general_ledger_xlsx"
    
    def _get_report_columns(self, report):
        res = [
            {"header": _("Date"), "field": "date", "width": 11},
            {"header": _("Entry"), "field": "entry", "width": 18},
            #{"header": _("Journal"), "field": "journal", "width": 8,"hidden": True},
            #{"header": _("Account"), "field": "account", "width": 9,"hidden": True},
            #{"header": _("Taxes"), "field": "taxes_description", "width": 15,"hidden": True},
            {"header": _("Partner"), "field": "partner_name", "width": 25},
            {"header": _("Ref - Label"), "field": "ref_label", "width": 40},
        ]
        """  if report.show_cost_center:
            res += [
                {
                    "header": _("Analytic Account"),
                    "field": "analytic_account",
                    "width": 20,
                },
            ]"""
        """ if report.show_analytic_tags:
            res += [
                {"header": _("Tags"), "field": "tags", "width": 10},
            ]  """
        res += [
            #{"header": _("Rec."), "field": "rec_name", "width": 15},
            {
                "header": _("Debit"),
                "field": "debit",
                "field_initial_balance": "initial_debit",
                "field_final_balance": "final_debit",
                "type": "amount",
                "width": 14,
            },
            {
                "header": _("Credit"),
                "field": "credit",
                "field_initial_balance": "initial_credit",
                "field_final_balance": "final_credit",
                "type": "amount",
                "width": 14,
            },
            {
                "header": _("Cumul. Bal."),
                "field": "balance",
                "field_initial_balance": "initial_balance",
                "field_final_balance": "final_balance",
                "type": "amount",
                "width": 14,
            },
        ]
        if report.foreign_currency:
            res += [
                {
                    "header": _("Cur."),
                    "field": "currency_name",
                    "field_currency_balance": "currency_name",
                    "type": "currency_name",
                    "width": 7,
                },
                {
                    "header": _("Amount cur."),
                    "field": "bal_curr",
                    "field_initial_balance": "initial_bal_curr",
                    "field_final_balance": "final_bal_curr",
                    "type": "amount_currency",
                    "width": 14,
                },
            ]
        res_as_dict = {}
        for i, column in enumerate(res):
            res_as_dict[i] = column
        return res_as_dict

    def _get_col_count_filter_name(self):
        return 2

    def _get_col_count_filter_value(self):
        return 0

    def _get_col_pos_initial_balance_label(self):
        return 3

    def _get_col_count_final_balance_name(self):
        return 3

    def _get_col_pos_final_balance_label(self):
        return 3



