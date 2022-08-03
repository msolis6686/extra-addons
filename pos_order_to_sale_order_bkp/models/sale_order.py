# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from datetime import datetime

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _prepare_from_pos(self, order_data):
        PosSession = self.env["pos.session"]
        session = PosSession.browse(order_data["pos_session_id"])
        return {
            "partner_id": order_data["partner_id"],
            "origin": _("Point of Sale %s") % (session.name),
            "client_order_ref": order_data["name"],
            "user_id": order_data["user_id"],
            "pricelist_id": order_data["pricelist_id"],
            "fiscal_position_id": order_data["fiscal_position_id"],
        }

    @api.model
    def create_order_from_pos(self, order_data, action):
        SaleOrderLine = self.env["sale.order.line"]

        # Create Draft Sale order
        order_vals = self._prepare_from_pos(order_data)
        sale_order = self.create(order_vals.copy())
        sale_order.onchange_partner_id()
        # we rewrite data, because onchange could alter some
        # custom data (like pricelist)
        sale_order.write(order_vals)

        # create Sale order lines
        for order_line_data in order_data["lines"]:
            # Create Sale order lines
            order_line_vals = SaleOrderLine._prepare_from_pos(
                sale_order, order_line_data[2]
            )
            sale_order_line = SaleOrderLine.create(order_line_vals.copy())
            sale_order_line.product_id_change()
            # we rewrite data, because onchange could alter some
            # data (like quantity, or price)
            sale_order_line.write(order_line_vals)

        # Confirm Sale Order
        if action in ["confirmed", "delivered"]:
            sale_order.action_confirm()

        # mark picking as delivered
        if action == "delivered":
            # Mark all moves are delivered
            for move in sale_order.mapped("picking_ids.move_ids_without_package"):
                move.quantity_done = move.product_uom_qty
            sale_order.mapped("picking_ids").button_validate()

        return {
            "sale_order_id": sale_order.id,
        }

class SalesReport(models.TransientModel):
    _name = 'sale.wizard'
    _description = "Sale Wizard Model" 

    def get_lines(self, order_id):
        sale = self.env['sale.order'].search([('client_order_ref','=',int(order_id))])
        return sale.order_line
    
    def get_folio_numbers(self, folio):
        folio_filtrado = filter(str.isdigit, folio)
        return "".join(folio_filtrado)
    
    def generate_final_barcode(self, price_total, company_mx_id):
        bar_code = ''
        sign = '$'
        comp_last_3 = company_mx_id[4:7]
        #RELLENO CON CEROS A LA IZQ EL TOTAL ENTERO
        price_total = str(int(price_total)).zfill(5)
        print("RELLENO CON CEROS A LA IZQ EL TOTAL ENTERO")
        print(price_total)
        #RECUPERO ULTIMOS 3 DIGITOS DEL TOTAL
        price_total_1 = price_total[-3:]
        print("RECUPERO ULTIMOS 3 DIGITOS DEL TOTAL")
        print(price_total_1)
        #RECUPERO PRIMEROS DOS DIGITOS DEL TOTAL
        price_first_two = price_total[0:2]
        print("RECUPERO PRIMEROS DOS DIGITOS DEL TOTAL")
        print(price_first_two)
        comission = '35'        
        comp_first_4 = company_mx_id[:4]
        bar_code = f"{sign}{comp_last_3}{price_total_1}{comission}{price_first_two}{comp_first_4}"
        return bar_code


    def print_report(self):
        sale = self.env['sale.order'].search([('client_order_ref','=',self.id['name'])])
        company = sale.company_id
        current_time = datetime.now().strftime("%H:%M")
        pos_session = self.env['pos.session'].search([('id','=',self.id['pos_session_id'])])
        date_unconverted = sale.date_order
        date_converted = date_unconverted.strftime('%d/%b/%Y %H:%M:%S')
        company_registry = company.company_registry
        """ data = self.parse """
        recibo = {
            'company_name': company.name,
            'comp_street': company.street,
            'comp_street_2': company.street2,
            'comp_rfc': company.vat,
            'comp_state': company.state_id.name,
            'comp_zip': company.zip,
            'comp_country': company.country_id,
            'comp_city': company.city,
            'comp_phone': company.phone,
            'system_time': current_time,
            'comp_street': company.street,
            'folio': sale.name,
            'amount': sale.amount_total,
            'lines': sale.order_line,
            'client_name': sale.partner_id.name,
            'pos_name': pos_session.config_id.name,
            'pos_session': pos_session.name,
            'pos_session_user': pos_session.user_id.name,
            'date': date_converted[:len(date_converted)-3],#datetime.strptime(str(sale.date_order),'%d-%b-%Y'),
            'folio_numbers': self.get_folio_numbers(sale.name),
            'sale_id': sale.id,
            'bar_code_final': self.generate_final_barcode(sale.amount_total,company_registry)
        }
        print(sale.date_order)
        return self.env.ref('pos_order_to_sale_order.pos_ord_session_reprt').report_action(self, recibo)