# Copyright 2022 Tecnativa - Carlos Roca
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import Form, common


class TestAccountPurchaseStockReportNonBilled(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supplier = cls.env["res.partner"].create({"name": "Supplier for Test"})
        cls.product = cls.env["product.product"].create({"name": "Product for Test"})
        po_form = Form(cls.env["purchase.order"])
        po_form.partner_id = cls.supplier
        with po_form.order_line.new() as po_line_form:
            po_line_form.product_id = cls.product
            po_line_form.price_unit = 15.0
        cls.po = po_form.save()

    def get_picking_done_po(self):
        self.po.button_confirm()
        picking = self.po.picking_ids[0]
        picking.action_confirm()
        picking.move_lines.quantity_done = 1.0
        picking.button_validate()
        return picking

    def test_01_report_move_not_invoiced(self):
        picking = self.get_picking_done_po()
        wiz = self.env["account.sale.stock.report.non.billed.wiz"].create(
            {"date_check": fields.Date.today()}
        )
        action = wiz.open_at_date()
        domain_ids = action["domain"][0][2]
        for move in picking.move_lines:
            self.assertIn(move.id, domain_ids)

    def test_02_report_move_full_invoiced(self):
        picking = self.get_picking_done_po()
        inv_action = self.po.action_view_invoice()
        inv_form = Form(self.env["account.move"].with_context(**inv_action["context"]))
        invoice = inv_form.save()
        invoice.action_post()
        wiz = self.env["account.sale.stock.report.non.billed.wiz"].create(
            {"date_check": fields.Date.today()}
        )
        action = wiz.open_at_date()
        domain_ids = action["domain"][0][2]
        for move in picking.move_lines:
            self.assertNotIn(move.id, domain_ids)

    def test_03_report_move_partially_invoiced(self):
        # First done just one move + invoice
        self.po.button_confirm()
        picking = self.po.picking_ids[0]
        picking.action_confirm()
        move_done = picking.move_lines[0]
        move_done.quantity_done = 1.0
        picking.action_done()
        inv_action = self.po.action_view_invoice()
        inv_form = Form(self.env["account.move"].with_context(**inv_action["context"]))
        inv = inv_form.save()
        inv.action_post()
        # Done other moves to appear at report
        picking_ret = self.po.picking_ids.filtered(lambda p: p.state == "assigned")
        picking_ret.action_confirm()
        picking_ret.move_lines.quantity_done = 1.0
        picking_ret.action_done()
        moves_not_done = picking_ret.move_lines
        wiz = self.env["account.sale.stock.report.non.billed.wiz"].create(
            {"date_check": fields.Date.today()}
        )
        action = wiz.open_at_date()
        domain_ids = action["domain"][0][2]
        self.assertNotIn(move_done.id, domain_ids)
        for move in moves_not_done:
            self.assertIn(move.id, domain_ids)

    def test_04_report_move_full_invoice_refund(self):
        self.po.button_confirm()
        # Validate shipment
        picking = self.po.picking_ids[0]
        # Process pickings
        picking.action_confirm()
        picking.move_lines.quantity_done = 1.0
        picking.button_validate()
        # Create invoice
        inv_action = self.po.action_view_invoice()
        inv_form = Form(self.env["account.move"].with_context(**inv_action["context"]))
        invoice = inv_form.save()
        invoice.action_post()
        wiz = self.env["account.sale.stock.report.non.billed.wiz"].create(
            {"date_check": fields.Date.today()}
        )
        action = wiz.open_at_date()
        domain_ids = action["domain"][0][2]
        for move in picking.move_lines:
            self.assertNotIn(move.id, domain_ids)
        # Refund invoice
        wiz_invoice_refund = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=invoice.ids)
            .create({"refund_method": "cancel", "reason": "test"})
        )
        wiz_invoice_refund.reverse_moves()
        action = wiz.open_at_date()
        domain_ids = action["domain"][0][2]
        for move in picking.move_lines:
            self.assertIn(move.id, domain_ids)
        # Create invoice again
        inv_action = self.po.action_view_invoice()
        inv_form = Form(self.env["account.move"].with_context(**inv_action["context"]))
        new_inv = inv_form.save()
        new_inv.action_post()
        action = wiz.open_at_date()
        domain_ids = action["domain"][0][2]
        for move in picking.move_lines:
            self.assertNotIn(move.id, domain_ids)

    def test_05_report_move_partial_pickings_full_invoice(self):
        self.po.order_line.product_qty = 5
        self.po.button_confirm()
        picking = self.po.picking_ids[0]
        picking.action_confirm()
        picking.move_lines.quantity_done = 3.0
        picking.button_validate()
        move_lines = picking.move_lines
        wiz = self.env["stock.backorder.confirmation"].create(
            {"pick_ids": [(4, picking.id)]}
        )
        wiz.process()
        picking = self.po.picking_ids.filtered(lambda p: p.state != "done")
        picking.action_confirm()
        picking.move_lines.quantity_done = 2.0
        picking.button_validate()
        move_lines += picking.move_lines
        wiz = self.env["account.sale.stock.report.non.billed.wiz"].create(
            {"date_check": fields.Date.today()}
        )
        action = wiz.open_at_date()
        domain_ids = action["domain"][0][2]
        for move in move_lines:
            self.assertIn(move.id, domain_ids)
        inv_action = self.po.action_view_invoice()
        inv_form = Form(self.env["account.move"].with_context(**inv_action["context"]))
        invoice = inv_form.save()
        invoice.action_post()
        action = wiz.open_at_date()
        domain_ids = action["domain"][0][2]
        for move in move_lines:
            self.assertNotIn(move.id, domain_ids)

    def test_06_report_move_partial_pickings_each_invoice(self):
        self.po.order_line.product_qty = 5
        self.po.button_confirm()
        picking = self.po.picking_ids[0]
        picking.action_confirm()
        picking.move_lines.quantity_done = 3.0
        picking.button_validate()
        wiz = self.env["stock.backorder.confirmation"].create(
            {"pick_ids": [(4, picking.id)]}
        )
        wiz.process()
        move_lines = picking.move_lines
        inv_action = self.po.action_view_invoice()
        inv_form = Form(self.env["account.move"].with_context(**inv_action["context"]))
        invoice = inv_form.save()
        invoice.action_post()
        picking = self.po.picking_ids.filtered(lambda p: p.state != "done")
        picking.action_confirm()
        picking.move_lines.quantity_done = 2.0
        picking.button_validate()
        wiz = self.env["account.sale.stock.report.non.billed.wiz"].create(
            {"date_check": fields.Date.today()}
        )
        action = wiz.open_at_date()
        domain_ids = action["domain"][0][2]
        for move in move_lines:
            self.assertNotIn(move.id, domain_ids)
        for move in picking.move_lines:
            self.assertIn(move.id, domain_ids)
        inv_action = self.po.action_view_invoice()
        inv_form = Form(self.env["account.move"].with_context(**inv_action["context"]))
        invoice = inv_form.save()
        invoice.action_post()
        action = wiz.open_at_date()
        domain_ids = action["domain"][0][2]
        for move in move_lines + picking.move_lines:
            self.assertNotIn(move.id, domain_ids)

    def test_07_report_move_full_invoice_return_without_update(self):
        self.po.button_confirm()
        # Validate shipment
        picking = self.po.picking_ids[0]
        # Process pickings
        picking.action_confirm()
        picking.move_lines.quantity_done = 1.0
        picking.button_validate()
        # Create invoice
        inv_action = self.po.action_view_invoice()
        inv_form = Form(self.env["account.move"].with_context(**inv_action["context"]))
        invoice = inv_form.save()
        invoice.action_post()
        wiz = self.env["account.sale.stock.report.non.billed.wiz"].create(
            {"date_check": fields.Date.today()}
        )
        action = wiz.open_at_date()
        domain_ids = action["domain"][0][2]
        for move in picking.move_lines:
            self.assertNotIn(move.id, domain_ids)
        # Return move
        wiz_return_form = Form(
            self.env["stock.return.picking"].with_context(
                active_model="stock.picking", active_id=picking.id
            )
        )
        wiz_return = wiz_return_form.save()
        wiz_return.product_return_moves.to_refund = False
        return_id = wiz_return.create_returns()["res_id"]
        picking_return = self.env["stock.picking"].browse(return_id)
        picking_return.move_line_ids.write({"qty_done": 1})
        picking_return.action_done()
        for move in picking_return.move_lines:
            self.assertNotIn(move.id, domain_ids)

    def test_08_move_return_return_full_invoiced(self):
        self.po.button_confirm()
        # Validate shipment
        picking = self.po.picking_ids[0]
        # Process pickings
        picking.action_confirm()
        picking.move_lines.quantity_done = 1.0
        picking.button_validate()
        wiz_return_form = Form(
            self.env["stock.return.picking"].with_context(
                active_model="stock.picking", active_id=picking.id
            )
        )
        wiz_return = wiz_return_form.save()
        return_id = wiz_return.create_returns()["res_id"]
        picking_return = self.env["stock.picking"].browse(return_id)
        picking_return.move_line_ids.write({"qty_done": 1})
        picking_return.action_done()
        wiz_return_return_form = Form(
            self.env["stock.return.picking"].with_context(
                active_model="stock.picking", active_id=picking_return.id
            )
        )
        wiz_return_return = wiz_return_return_form.save()
        return_return_id = wiz_return_return.create_returns()["res_id"]
        picking_return_return = self.env["stock.picking"].browse(return_return_id)
        picking_return_return.move_line_ids.write({"qty_done": 1})
        picking_return_return.action_done()
        inv_action = self.po.action_view_invoice()
        inv_form = Form(self.env["account.move"].with_context(**inv_action["context"]))
        inv_form.save()
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

    def test_09_move_return_return_non_invoiced(self):
        self.po.button_confirm()
        # Validate shipment
        picking = self.po.picking_ids[0]
        # Process pickings
        picking.action_confirm()
        picking.move_lines.quantity_done = 1.0
        picking.button_validate()
        wiz_return_form = Form(
            self.env["stock.return.picking"].with_context(
                active_model="stock.picking", active_id=picking.id
            )
        )
        wiz_return = wiz_return_form.save()
        return_id = wiz_return.create_returns()["res_id"]
        picking_return = self.env["stock.picking"].browse(return_id)
        picking_return.move_line_ids.write({"qty_done": 1})
        picking_return.action_done()
        wiz_return_return_form = Form(
            self.env["stock.return.picking"].with_context(
                active_model="stock.picking", active_id=picking_return.id
            )
        )
        wiz_return_return = wiz_return_return_form.save()
        return_return_id = wiz_return_return.create_returns()["res_id"]
        picking_return_return = self.env["stock.picking"].browse(return_return_id)
        picking_return_return.move_line_ids.write({"qty_done": 1})
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

    def test_10_move_invoice_return_without_update_qty(self):
        self.po.button_confirm()
        # Validate shipment
        picking = self.po.picking_ids[0]
        # Process pickings
        picking.action_confirm()
        picking.move_lines.quantity_done = 1.0
        picking.button_validate()
        inv_action = self.po.action_view_invoice()
        inv_form = Form(self.env["account.move"].with_context(**inv_action["context"]))
        inv_form.save()
        wiz_return_form = Form(
            self.env["stock.return.picking"].with_context(
                active_model="stock.picking", active_id=picking.id, to_refund=False
            )
        )
        wiz_return = wiz_return_form.save()
        return_id = wiz_return.create_returns()["res_id"]
        picking_return = self.env["stock.picking"].browse(return_id)
        picking_return.move_line_ids.write({"qty_done": 1})
        picking_return.action_done()
        wiz_return_return_form = Form(
            self.env["stock.return.picking"].with_context(
                active_model="stock.picking",
                active_id=picking_return.id,
                to_refund=False,
            )
        )
        wiz_return_return = wiz_return_return_form.save()
        return_return_id = wiz_return_return.create_returns()["res_id"]
        picking_return_return = self.env["stock.picking"].browse(return_return_id)
        picking_return_return.move_line_ids.write({"qty_done": 1})
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

    def test_11_report_move_full_invoiced_out_of_date(self):
        self.po.button_confirm()
        # Validate shipment
        picking = self.po.picking_ids[0]
        # Process pickings
        picking.action_confirm()
        picking.move_lines.quantity_done = 1.0
        picking.button_validate()
        # Emulate prepaying invoice
        inv_action = self.po.action_view_invoice()
        inv_form = Form(self.env["account.move"].with_context(**inv_action["context"]))
        inv_form.date = fields.Date.today() - relativedelta(days=5)
        inv_form.save()
        wiz = self.env["account.sale.stock.report.non.billed.wiz"].create(
            {"date_check": fields.Date.today(), "interval_restrict_invoices": True}
        )
        action = wiz.open_at_date()
        domain_ids = action["domain"][0][2]
        for move in picking.move_lines:
            self.assertIn(move.id, domain_ids)
