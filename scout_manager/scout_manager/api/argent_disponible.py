import frappe
from frappe.desk.query_report import run
from frappe.utils import getdate, today

from scout_manager.scout_manager.config.names import REPORT_ARGENT_DISPONIBLE
from scout_manager.scout_manager.config.troop import DEFAULT_COMPANY
from scout_manager.scout_manager.report.argent_disponible_par_unité.argent_disponible_par_unité import (
	AMOUNT_FIELDS,
)
from scout_manager.scout_manager.utils.cost_centers import get_unit_cost_centers


@frappe.whitelist()
def get_argent_disponible_by_unit(company=None, to_date=None):
	"""Return disponible par unité rows for the workspace widget."""
	company = company or DEFAULT_COMPANY
	to_date = getdate(to_date or today())

	data = run(REPORT_ARGENT_DISPONIBLE, filters={"company": company, "to_date": to_date})
	rows = [row for row in (data.get("result") or []) if isinstance(row, dict)]

	return {
		"company": company,
		"to_date": str(to_date),
		"currency": frappe.db.get_value("Company", company, "default_currency"),
		"units": [_normalize_row(row) for row in _sort_units(rows, company)],
		"totals": _calc_totals(rows),
	}


def _normalize_row(row):
	cost_center_name = row.get("cost_center_name") or row.get("cost_center")
	return {
		"name": cost_center_name,
		"cost_center": row.get("cost_center"),
		**{field: row.get(field) or 0 for field in AMOUNT_FIELDS},
	}


def _sort_units(rows, company):
	order = {unit["name"]: index for index, unit in enumerate(get_unit_cost_centers(company))}

	def sort_key(row):
		cost_center = row.get("cost_center") or ""
		label = row.get("cost_center_name") or cost_center
		return (order.get(cost_center, len(order)), label)

	return sorted(rows, key=sort_key)


def _calc_totals(rows):
	disponible = sum(row.get("disponible") or 0 for row in rows)
	disponible_ar = sum(row.get("disponible_ar") or 0 for row in rows)
	return {"disponible": disponible, "disponible_ar": disponible_ar}
