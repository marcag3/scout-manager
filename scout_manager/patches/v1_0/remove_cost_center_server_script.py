import frappe

RETIRED_SERVER_SCRIPT = "modifier les cost center"


def execute():
	if not frappe.db.exists("Server Script", RETIRED_SERVER_SCRIPT):
		return

	frappe.delete_doc("Server Script", RETIRED_SERVER_SCRIPT, force=True, ignore_permissions=True)
	frappe.db.commit()
