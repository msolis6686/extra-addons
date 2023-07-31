# Copyright 2022 Tecnativa - Carlos Roca
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import Form

from odoo.addons.stock_picking_invoice_link.tests.test_stock_picking_invoice_link import (
    TestStockPickingInvoiceLink,
)


class TestAccountSaleStrockReportNonBilled(TestStockPickingInvoiceLink):
    def setUp(self):
        super().setUp()
        self.prod_order.invoice_policy = "delivery"

    def get_picking_done_so(self):
        picking = self.so.picking_ids.filtered(
            lambda x: x.picking_type_code == "outgoing"
            and x.state in ("confirmed", "assigned", "partially_available")
        )
        picking.move_line_ids.write({"qty_done": 2})
        picking.action_done()
        return picking

    def test_01_report_move_not_invoiced(self):
        pick_1 = self.get_picking_done_so()
        wiz = self.env["account.sale.stock.report.non.billed.wiz"].create(
            {"date_check": fields.Date.today()}
        )
        action = wiz.open_at_date()
        domain_ids = action["domain"][0][2]
        for move in pick_1.move_lines:
            self.assertIn(move.id, domain_ids)

    def test_02_report_move_full_invoiced(self):
        pick_1 = self.get_picking_done_so()
        inv = self.so._create_invoices()
        inv.action_post()
        wiz = self.env["account.sale.stock.report.non.billed.wiz"].create(
            {"date_check": fields.Date.today()}
        )
        action = wiz.open_at_date()
        domain_ids = action["domain"][0][2]
        for move in pick_1.move_lines:
            self.assertNotIn(move.id, domain_ids)

    def test_03_report_move_partially_invoiced(self):
        # First done just one move + invoice
        picking = self.so.picking_ids.filtered(
            lambda x: x.picking_type_code == "outgoing"
            and x.state in ("confirmed", "assigned", "partially_available")
        )
        move_done = picking.move_lines[0]
        moves_not_done = picking.move_lines[1:]
        move_done.move_line_ids.write({"qty_done": 2})
        picking.action_done()
        inv = self.so._create_invoices()
        inv.action_post()
        # Done other moves to appear at report
        self.get_picking_done_so()
        wiz = self.env["account.sale.stock.report.non.billed.wiz"].create(
            {"date_check": fields.Date.today()}
        )
        action = wiz.open_at_date()
        domain_ids = action["domain"][0][2]
        self.assertNotIn(move_done.id, domain_ids)
        for move in moves_not_done:
            self.assertIn(move.id, domain_ids)

    def test_04_report_move_full_invoice_refund(self):
        pick_1 = self.get_picking_done_so()
        inv = self.so._create_invoices()
        inv.action_post()
        # Refund invoice
        wiz_invoice_refund = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=inv.ids)
            .create({"refund_method": "cancel", "reason": "test"})
        )
        wiz_invoice_refund.reverse_moves()
        wiz = self.env["account.sale.stock.report.non.billed.wiz"].create(
            {"date_check": fields.Date.today()}
        )
        action = wiz.open_at_date()
        domain_ids = action["domain"][0][2]
        for move in pick_1.move_lines:
            self.assertIn(move.id, domain_ids)

    def test_05_report_move_full_return_no_invoiced(self):
        picking = self.get_picking_done_so()
        wiz_return_form = Form(
            self.env["stock.return.picking"].with_context(
                active_model="stock.picking", active_id=picking.id
            )
        )
        wiz_return = wiz_return_form.save()
        return_id = wiz_return.create_returns()["res_id"]
        picking_return = self.env["stock.picking"].browse(return_id)
        picking_return.move_line_ids.write({"qty_done": 2})
        picking_return.action_done()
        wiz = self.env["account.sale.stock.report.non.billed.wiz"].create(
            {"date_check": fields.Date.today()}
        )
        action = wiz.open_at_date()
        domain_ids = action["domain"][0][2]
        for move in picking.move_lines:
            self.assertNotIn(move.id, domain_ids)
        for move in picking_return.move_lines:
            self.assertNotIn(move.id, domain_ids)

    def test_06_report_move_full_return_invoiced(self):
        picking = self.get_picking_done_so()
        inv = self.so._create_invoices()
        inv.action_post()
        wiz_return_form = Form(
            self.env["stock.return.picking"].with_context(
                active_model="stock.picking", active_id=picking.id
            )
        )
        wiz_return = wiz_return_form.save()
        return_id = wiz_return.create_returns()["res_id"]
        picking_return = self.env["stock.picking"].browse(return_id)
        picking_return.move_line_ids.write({"qty_done": 2})
        picking_return.action_done()
        wiz = self.env["account.sale.stock.report.non.billed.wiz"].create(
            {"date_check": fields.Date.today()}
        )
        action = wiz.open_at_date()
        domain_ids = action["domain"][0][2]
        for move in picking.move_lines:
            self.assertNotIn(move.id, domain_ids)
        for move in picking_return.move_lines:
            self.assertIn(move.id, domain_ids)
        inv = self.so._create_invoices(final=True)
        inv.post()
        action = wiz.open_at_date()
        domain_ids = action["domain"][0][2]
        for move in picking_return.move_lines:
            self.assertNotIn(move.id, domain_ids)

    def test_07_move_return_return_full_invoiced(self):
        picking = self.get_picking_done_so()
        wiz_return_form = Form(
            self.env["stock.return.picking"].with_context(
                active_model="stock.picking", active_id=picking.id
            )
        )
        wiz_return = wiz_return_form.save()
        return_id = wiz_return.create_returns()["res_id"]
        picking_return = self.env["stock.picking"].browse(return_id)
        picking_return.move_line_ids.write({"qty_done": 2})
        picking_return.action_done()
        wiz_return_return_form = Form(
            self.env["stock.return.picking"].with_context(
                active_model="stock.picking", active_id=picking_return.id
            )
        )
        wiz_return_return = wiz_return_return_form.save()
        return_return_id = wiz_return_return.create_returns()["res_id"]
        picking_return_return = self.env["stock.picking"].browse(return_return_id)
        picking_return_return.move_line_ids.write({"qty_done": 2})
        picking_return_return.action_done()
        self.so._create_invoices(final=True)
        wiz = self.env["account.sale.stock.report.non.billed.wiz"].create(
            {"date_check": fields.Date.today()}
        )
        action = wiz.open_at_date()
        domain_ids = action["domain"][0][2]
        for move in picking.move_lines:
            self.assertNotIn(move.id, domain_ids)
        for move in picking_return.move_lines:
            self.assertNotIn(move.id, domain_ids)
        for move in picking_return_return.move_lines:
            self.assertNotIn(move.id, domain_ids)

    def test_08_move_return_return_non_invoiced(self):
        picking = self.get_picking_done_so()
        wiz_return_form = Form(
            self.env["stock.return.picking"].with_context(
                active_model="stock.picking", active_id=picking.id
            )
        )
        wiz_return = wiz_return_form.save()
        return_id = wiz_return.create_returns()["res_id"]
        picking_return = self.env["stock.picking"].browse(return_id)
        picking_return.move_line_ids.write({"qty_done": 2})
        picking_return.action_done()
        wiz_return_return_form = Form(
            self.env["stock.return.picking"].with_context(
                active_model="stock.picking", active_id=picking_return.id
            )
        )
        wiz_return_return = wiz_return_return_form.save()
        return_return_id = wiz_return_return.create_returns()["res_id"]
        picking_return_return = self.env["stock.picking"].browse(return_return_id)
        picking_return_return.move_line_ids.write({"qty_done": 2})
        picking_return_return.action_done()
        wiz = self.env["account.sale.stock.report.non.billed.wiz"].create(
            {"date_check": fields.Date.today()}
        )
        action = wiz.open_at_date()
        domain_ids = action["domain"][0][2]
        for move in picking.move_lines:
            self.assertNotIn(move.id, domain_ids)
        for move in picking_return.move_lines:
            self.assertNotIn(move.id, domain_ids)
        for move in picking_return_return.move_lines:
            self.assertIn(move.id, domain_ids)

    def test_09_move_invoice_return_without_update_qty(self):
        picking = self.get_picking_done_so()
        self.so._create_invoices(final=True)
        wiz_return_form = Form(
            self.env["stock.return.picking"].with_context(
                active_model="stock.picking",
                active_id=picking.id,
                default_to_refund=False,
            )
        )
        wiz_return = wiz_return_form.save()
        return_id = wiz_return.create_returns()["res_id"]
        picking_return = self.env["stock.picking"].browse(return_id)
        picking_return.move_line_ids.write({"qty_done": 2})
        picking_return.action_done()
        wiz_return_return_form = Form(
            self.env["stock.return.picking"].with_context(
                active_model="stock.picking",
                active_id=picking_return.id,
                default_to_refund=False,
            )
        )
        wiz_return_return = wiz_return_return_form.save()
        return_return_id = wiz_return_return.create_returns()["res_id"]
        picking_return_return = self.env["stock.picking"].browse(return_return_id)
        picking_return_return.move_line_ids.write({"qty_done": 2})
        picking_return_return.action_done()
        wiz = self.env["account.sale.stock.report.non.billed.wiz"].create(
            {"date_check": fields.Date.today()}
        )
        action = wiz.open_at_date()
        domain_ids = action["domain"][0][2]
        for move in picking.move_lines:
            self.assertNotIn(move.id, domain_ids)
        for move in picking_return.move_lines:
            self.assertNotIn(move.id, domain_ids)
        for move in picking_return_return.move_lines:
            self.assertNotIn(move.id, domain_ids)

    def test_10_report_move_full_invoiced_out_of_date(self):
        picking = self.so.picking_ids.filtered(
            lambda x: x.picking_type_code == "outgoing"
            and x.state in ("confirmed", "assigned", "partially_available")
        )
        picking.move_line_ids.write({"qty_done": 2})
        picking.action_done()
        # Emulate prepaying invoice
        inv = self.so._create_invoices()
        inv.date = fields.Date.today() - relativedelta(days=5)
        wiz = self.env["account.sale.stock.report.non.billed.wiz"].create(
            {"date_check": fields.Date.today(), "interval_restrict_invoices": True}
        )
        action = wiz.open_at_date()
        domain_ids = action["domain"][0][2]
        for move in picking.move_lines:
            self.assertIn(move.id, domain_ids)
