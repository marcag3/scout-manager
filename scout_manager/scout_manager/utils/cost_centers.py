import frappe

from scout_manager.scout_manager.config.names import COST_CENTER_DISPLAY_ORDER_FIELD

# Used only once on migrate to seed display order when the custom field is unset.
_SEED_DISPLAY_ORDER_BY_NAME = {
	"Groupe": 1,
	"Colonie": 2,
	"Louvette": 3,
	"Meute": 4,
	"Troupe": 5,
	"Clan": 6,
}


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


def seed_cost_center_display_order(company=None):
	"""Set custom_ordre_affichage on unit cost centers when still unset."""
	from scout_manager.scout_manager.config.troop import DEFAULT_COMPANY

	company = company or DEFAULT_COMPANY
	for cost_center_name, order in _SEED_DISPLAY_ORDER_BY_NAME.items():
		name = frappe.db.get_value(
			"Cost Center",
			{"company": company, "cost_center_name": cost_center_name, "is_group": 0},
			"name",
		)
		if not name:
			continue

		current = frappe.db.get_value("Cost Center", name, COST_CENTER_DISPLAY_ORDER_FIELD)
		if current:
			continue

		frappe.db.set_value("Cost Center", name, COST_CENTER_DISPLAY_ORDER_FIELD, order, update_modified=False)

	frappe.db.commit()
