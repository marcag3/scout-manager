import frappe
from frappe import _
from frappe.utils import get_first_day, get_last_day, getdate, nowdate, now_datetime

from scout_manager.scout_manager.accounting.cost_center import get_cost_center_for_group
from scout_manager.scout_manager.accounting.invoice_dimensions import sync_header_dimensions_to_items


def create_cotisation_invoices(customer_group_name):
	if not customer_group_name:
		frappe.throw(_("Customer Group Name is required."))

	customers = frappe.get_all(
		"Customer",
		filters={"customer_group": customer_group_name},
		pluck="name",
	)
	if not customers:
		frappe.throw(_("No customers found in the Customer Group: {0}").format(customer_group_name))

	current_year = now_datetime().year
	from_date = getdate(get_first_day(f"{current_year}-10-01"))
	to_date = getdate(get_last_day(f"{current_year + 1}-09-30"))
	cost_center = get_cost_center_for_group("Customer Group", customer_group_name)

	existing_parents = frappe.get_all(
		"Sales Invoice Item",
		filters={"item_code": "Cotisation"},
		pluck="parent",
	)

	added_invoices = []
	for customer in customers:
		filters = {
			"customer": customer,
			"from_date": from_date,
			"to_date": to_date,
			"docstatus": ["!=", 2],
		}
		if existing_parents:
			filters["name"] = ["in", existing_parents]

		existing_invoice = frappe.get_all("Sales Invoice", filters=filters, limit=1)
		if existing_invoice:
			continue

		invoice = frappe.new_doc("Sales Invoice")
		invoice.customer = customer
		invoice.posting_date = nowdate()
		invoice.from_date = from_date
		invoice.to_date = to_date
		invoice.payment_terms_template = "Versements cotisation"
		if cost_center:
			invoice.cost_center = cost_center

		invoice.append("items", {"item_code": "Cotisation", "qty": 1})
		sync_header_dimensions_to_items(invoice)
		invoice.insert()
		added_invoices.append(invoice.name)

	return added_invoices
