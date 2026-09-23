import frappe
from frappe import _

from scout_manager.scout_manager.config.troop import DEFAULT_COMPANY
from scout_manager.scout_manager.utils.cost_centers import get_unit_cost_centers
from scout_manager.scout_manager.utils.report_columns import build_pivot_columns, build_pivot_selects

BALANCE_SHEET_ROOT_TYPES = ("Asset", "Liability", "Equity")
VALUE_EXPR = "gle.debit - gle.credit"


def execute(filters=None):
	filters = filters or {}
	company = filters.get("company") or DEFAULT_COMPANY
	to_date = filters.get("to_date")

	units = get_unit_cost_centers(company)
	columns = get_columns(units)
	data = get_data(company, to_date, units)
	return columns, data


def get_columns(units):
	return [
		{
			"label": _("Account"),
			"fieldname": "account",
			"fieldtype": "Link",
			"options": "Account",
			"width": 220,
		},
		*build_pivot_columns(units),
	]


def get_data(company, to_date, units):
	if not units:
		return []

	selects, params = build_pivot_selects(units, VALUE_EXPR)
	params.update(
		{
			"company": company,
			"to_date": to_date,
			"root_types": BALANCE_SHEET_ROOT_TYPES,
		}
	)

	return frappe.db.sql(
		f"""
		SELECT
			gle.account AS account,
			{", ".join(selects)}
		FROM `tabGL Entry` gle
		INNER JOIN `tabAccount` acc ON acc.name = gle.account
		WHERE gle.company = %(company)s
			AND gle.is_cancelled = 0
			AND gle.posting_date <= %(to_date)s
			AND acc.root_type IN %(root_types)s
			AND acc.is_group = 0
		GROUP BY gle.account
		HAVING ABS(SUM({VALUE_EXPR})) > 0.005
		ORDER BY acc.root_type, gle.account
		""",
		params,
		as_dict=True,
	)
