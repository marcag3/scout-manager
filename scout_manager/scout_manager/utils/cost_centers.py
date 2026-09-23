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


def sort_by_unit_order(rows, units, cost_center_key="cost_center", name_key="cost_center_name"):
	"""Sort report or API rows in the same order as get_unit_cost_centers."""
	order = {unit["name"]: index for index, unit in enumerate(units)}
	fallback = len(order)

	def sort_key(row):
		if isinstance(row, dict):
			cost_center = row.get(cost_center_key) or ""
			label = row.get(name_key) or cost_center
		else:
			cost_center = getattr(row, cost_center_key, "") or ""
			label = getattr(row, name_key, None) or cost_center
		return (order.get(cost_center, fallback), label)

	return sorted(rows, key=sort_key)
