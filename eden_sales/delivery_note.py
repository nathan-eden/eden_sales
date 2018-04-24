# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import frappe
from frappe.utils.data import flt

@frappe.whitelist()
def send_to_company(name):
	doc = frappe.get_doc("Delivery Note", name)
	if not doc.po_no:
		frappe.throw("Delivery Note must be dropship type")

	from_so = next(d.against_sales_order for d in doc.items if d.against_sales_order)

	if not from_so:
		frappe.throw("No linked Sales Order found")

	so = frappe.get_doc("Sales Order", from_so)
	if not so.dropship_order or not so.po_no:
		frappe.throw("Linked Sales Order {0} must be dropship type to use this feature".format(so.name))

	po = frappe.get_doc("Purchase Order", doc.po_no)

	if po.per_received == so.per_delivered:
		frappe.throw("Purchase Order {0} was already set to latest status".format(po.name))

	# update % Received
	po.per_received = so.per_delivered
	if flt(so.per_delivered, 2) > 99.99:
		po.update_status("Delivered")
		po.update_delivered_qty_in_sales_order()

	po.flags.ignore_validate_update_after_submit = True
	po.save()
	frappe.db.commit()

	return po
