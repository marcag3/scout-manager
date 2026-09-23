import frappe
from frappe.utils.dashboard import cache_source

from scout_manager.scout_manager.api.argent_disponible import get_argent_disponible_by_unit


@frappe.whitelist()
@cache_source
def get(
	chart_name=None,
	chart=None,
	no_cache=None,
	filters=None,
	from_date=None,
	to_date=None,
	timespan=None,
	time_interval=None,
	heatmap_year=None,
):
	filters = frappe.parse_json(filters) or {}
	data = get_argent_disponible_by_unit(company=filters.get("company"), to_date=filters.get("to_date"))
	units = data["units"]

	return {
		"labels": [unit["name"] for unit in units],
		"datasets": [
			{"name": "Disponible", "values": [unit["disponible"] for unit in units]},
			{
				"name": "Disponible incluant les comptes à recevoir",
				"values": [unit["disponible_ar"] for unit in units],
			},
		],
	}
