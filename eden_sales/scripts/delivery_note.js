frappe.provide('eden_sales.dn');

frappe.ui.form.on("Delivery Note", {
    refresh: function (frm) {
        if (frm.doc.docstatus === 1 && frm.doc.po_no) {
            frm.add_custom_button(__('Mark delivery to Company'), function () {
                frappe.call({
                    type: "GET",
                    method: "eden_sales.purchase_order.lookup_company",
                    args: {
                        name: frm.doc.po_no
                    },
                    freeze: true,
                    callback: function (r) {
                        if (!r.exc) {
                            if (r.message) {
                                eden_sales.dn.sendToCompany(frm, r.message);
                            } else {
                                frappe.msgprint(__("No linked company found on customer {0}", [frm.doc.customer]))
                            }
                        }
                    }
                })
            });
        }
    }
});

eden_sales.dn = {
    sendToCompany: function (frm, company) {
        var dialog = new frappe.ui.Dialog({
            title: __('Mark delivery'),
            fields: [
                {
                    fieldname: 'company', label: __('Company'), 'default': company,
                    fieldtype: 'Link', options: 'Company', read_only: 1
                },
                {
                    fieldname: 'po_no', label: __('Purchase Order'), 'default': frm.doc.po_no,
                    fieldtype: 'Link', options: 'Purchase Order', read_only: 1
                },
                {
                    fieldtype: "Button", label: __("Send"), fieldname: "send"
                }
            ]
        });

        dialog.fields_dict.send.$input.removeClass('btn-default btn-xs');
        dialog.fields_dict.send.$input.addClass('btn-primary btn-sm');
        dialog.fields_dict.send.$input.click(function () {
            var args = dialog.get_values();
            if (!args) return;
            dialog.hide();

            return frappe.call({
                type: "GET",
                method: "eden_sales.delivery_note.send_to_company",
                args: {
                    name: frm.doc.name
                },
                freeze: true,
                callback: function (r) {
                    if (!r.exc) {
                        var po = r.message;
                        frappe.show_alert(__('Purchase Order {0} was updated in company {1}',
					['<a href="#Form/Purchase Order/'+ po.name + '">' + po.name+ '</a>',
                    '<a href="#Form/Company/' + company + '">' + company + '</a>']
                        ));
                    }
                }
            })
        });

        dialog.show();
    }
};
