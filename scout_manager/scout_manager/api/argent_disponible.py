import frappe
from frappe.desk.query_report import run
from frappe.utils import getdate, today

from scout_manager.scout_manager.config.troop import DEFAULT_COMPANY, UNIT_ORDER

REPORT_NAME = "Argent disponible par unité"


@frappe.whitelist()
def get_argent_disponible_by_unit(company=None, to_date=None):
	"""Return disponible par unité rows for the workspace widget."""
	company = company or DEFAULT_COMPANY
	to_date = getdate(to_date or today())

	data = run(REPORT_NAME, filters={"company": company, "to_date": to_date})
	rows = [row for row in (data.get("result") or []) if isinstance(row, dict)]

	return {
		"company": company,
		"to_date": str(to_date),
		"units": [_normalize_row(row) for row in _sort_units(rows)],
		"totals": _calc_totals(rows),
	}


def _normalize_row(row):
	cost_center_name = row.get("cost_center_name") or row.get("cost_center")
	return {
		"name": cost_center_name,
		"cost_center": row.get("cost_center"),
		"banque": row.get("banque") or 0,
		"caisse": row.get("caisse") or 0,
		"ar": row.get("ar") or 0,
		"passif": row.get("passif") or 0,
		"disponible": row.get("disponible") or 0,
		"disponible_ar": row.get("disponible_ar") or 0,
	}


def _sort_units(rows):
	order = {name: index for index, name in enumerate(UNIT_ORDER)}

	def sort_key(row):
		label = row.get("cost_center_name") or row.get("cost_center") or ""
		return (order.get(label, len(UNIT_ORDER)), label)

	return sorted(rows, key=sort_key)


def _calc_totals(rows):
	disponible = sum(row.get("disponible") or 0 for row in rows)
	disponible_ar = sum(row.get("disponible_ar") or 0 for row in rows)
	return {"disponible": disponible, "disponible_ar": disponible_ar}
