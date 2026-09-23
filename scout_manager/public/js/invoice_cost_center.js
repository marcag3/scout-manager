function scout_manager_apply_party_cost_center(frm, party_type, party_field) {
	const party = frm.doc[party_field];
	if (!party) {
		return;
	}

	frappe.call({
		method: "scout_manager.scout_manager.accounting.cost_center.resolve_cost_center",
		args: { party_type, party },
		callback(r) {
			const cost_center = r.message;
			if (cost_center && frm.doc.cost_center !== cost_center) {
				frm.set_value("cost_center", cost_center);
			}
		},
	});
}

frappe.ui.form.on("Sales Invoice", {
	customer(frm) {
		scout_manager_apply_party_cost_center(frm, "Customer", "customer");
	},
});

frappe.ui.form.on("Purchase Invoice", {
	supplier(frm) {
		scout_manager_apply_party_cost_center(frm, "Supplier", "supplier");
	},
});
