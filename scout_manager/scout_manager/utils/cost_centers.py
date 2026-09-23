import frappe

from scout_manager.scout_manager.config.names import COST_CENTER_DISPLAY_ORDER_FIELD


def get_unit_cost_centers(company):
	"""Return active leaf cost centers for a company, ordered for display."""
	rows = frappe.get_all(
		"Cost Center",
		filters={"company": company, "is_group": 0, "disabled": 0},
		fields=["name", "cost_center_name", COST_CENTER_DISPLAY_ORDER_FIELD],
		order_by=f"{COST_CENTER_DISPLAY_ORDER_FIELD} asc, cost_center_name asc",
	)
	return [
		{
			"name": row.name,
			"cost_center_name": row.cost_center_name,
			"fieldname": frappe.scrub(row.cost_center_name),
		}
		for row in rows
	]


def get_unit_cost_center_names(company):
	return [unit["name"] for unit in get_unit_cost_centers(company)]
