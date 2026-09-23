import erpnext
import frappe
from frappe.desk.query_report import run
from frappe.utils import getdate, today

from scout_manager.scout_manager.config.names import REPORT_ARGENT_DISPONIBLE
from scout_manager.scout_manager.report.available_funds_per_unit.available_funds_per_unit import (
	AMOUNT_FIELDS,
)
from scout_manager.scout_manager.utils.cost_centers import get_unit_cost_centers, sort_by_unit_order


@frappe.whitelist()
def get_argent_disponible_by_unit(company=None, to_date=None):
	"""Return disponible par unité rows for the workspace widget."""
	company = company or erpnext.get_default_company()
	to_date = getdate(to_date or today())

	data = run(REPORT_ARGENT_DISPONIBLE, filters={"company": company, "to_date": to_date})
	rows = [row for row in (data.get("result") or []) if isinstance(row, dict)]

	return {
		"company": company,
		"to_date": str(to_date),
		"currency": frappe.db.get_value("Company", company, "default_currency"),
		"units": [
			_normalize_row(row)
			for row in sort_by_unit_order(rows, get_unit_cost_centers(company))
		],
		"totals": _calc_totals(rows),
	}


def _normalize_row(row):
	cost_center_name = row.get("cost_center_name") or row.get("cost_center")
	return {
		"name": cost_center_name,
		"cost_center": row.get("cost_center"),
		**{field: row.get(field) or 0 for field in AMOUNT_FIELDS},
	}


def _calc_totals(rows):
	disponible = sum(row.get("disponible") or 0 for row in rows)
	disponible_ar = sum(row.get("disponible_ar") or 0 for row in rows)
	return {"disponible": disponible, "disponible_ar": disponible_ar}
