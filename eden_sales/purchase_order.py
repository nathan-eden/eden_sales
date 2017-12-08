# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.utils.data import add_days


@frappe.whitelist()
def make_sales_order(source_name, for_company, target_doc=None):
	def set_missing_values(source, target):
		target.company = for_company
		target.delivery_date = add_days(None, 3)
		target.po_no = source.name
		target.po_date = source.transaction_date

		if any(item.delivered_by_supplier == 1 for item in source.items):
			target.dropship_order = 1
			target.dropship_customer_name = source.customer_name
			target.dropship_contact = source.customer_contact_display
			target.dropship_mobile = source.customer_contact_mobile
			target.dropship_email = source.customer_contact_email

		target.shipping_address = source.shipping_address_display
		target.shipping_address_name = source.shipping_address
                
		target.co_abbr = frappe.get_value("Company", target.company, "abbr")
                target.old_po_no = source.po_no
		
		target.run_method("set_missing_values")
		target.run_method("calculate_taxes_and_totals")

	def update_item(source, target, source_parent):
		target.qty = source.qty

	doclist = get_mapped_doc("Purchase Order", source_name, {
		"Purchase Order": {
			"doctype": "Sales Order",
			"field_no_map": [
				"address_display",
				"contact_display",
				"contact_mobile",
				"contact_email",
				"contact_person",
				"customer",
				"customer_name",
				"currency",
			],
			"validation": {
				"docstatus": ["=", 1]
			}
		},
		"Purchase Order Item": {
			"doctype": "Sales Order Item",
			"field_map": [
				["name", "purchase_order_item"],
				["parent", "purchase_order"],
				["stock_uom", "uom"],
			],
			"field_no_map": [
				"warehouse",
				"rate",
				"price_list_rate",
				"delivered_by_supplier"
			],
			"postprocess": update_item,
		}
	}, target_doc, set_missing_values)

        #sbtang changes start
        if for_company in "Eden Ministry Myanmar":
           doclist.get("items")[0].warehouse = "Finished Goods - MY"
        if for_company in "Tian Yuan KM":
           doclist.get("items")[0].warehouse = "Finished Goods - KM"
        if for_company in "Tian Yuan SH":
           doclist.get("items")[0].warehouse = "Finsihed Goods - SH"
	if for_company in "Eden Ministry Australia":
	   doclist.get("items")[0].warehouse = "Finished Goods - AU"
        #sbtang changes end

	doclist.insert(ignore_permissions=True)
	frappe.db.commit()

	return doclist

@frappe.whitelist()
def lookup_company(name):
	return frappe.get_value("Purchase Order", name, "company")
