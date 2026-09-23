function scout_manager_set_customer_age(frm) {
	if (!frm.doc.custom_date_de_naissance) {
		frm.set_value("custom_age", null, false, true);
		return;
	}

	const age = moment().diff(frm.doc.custom_date_de_naissance, "years");
	frm.set_value("custom_age", age, false, true);
}

frappe.ui.form.on("Customer", {
	refresh(frm) {
		scout_manager_set_customer_age(frm);
	},
	custom_date_de_naissance(frm) {
		scout_manager_set_customer_age(frm);
	},
});
