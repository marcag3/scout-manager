import frappe
from frappe import _

from scout_manager.scout_manager.config.troop import DEFAULT_COMPANY
from scout_manager.scout_manager.utils.cost_centers import get_unit_cost_centers
from scout_manager.scout_manager.utils.report_columns import build_pivot_columns, build_pivot_selects

PROFIT_ROOT_TYPES = ("Income", "Expense")
VALUE_EXPR = (
	"CASE WHEN acc.root_type IN %(root_types)s THEN gle.credit - gle.debit ELSE 0 END"
)


def execute(filters=None):
	filters = filters or {}
	company = filters.get("company") or DEFAULT_COMPANY
	fiscal_year = filters.get("fiscal_year")

	units = get_unit_cost_centers(company)
	columns = get_columns(units)
	data = get_data(company, fiscal_year, units)
	return columns, data


def get_columns(units):
	return [
		{
			"label": _("Project"),
			"fieldname": "project",
			"fieldtype": "Link",
			"options": "Project",
			"width": 180,
		},
		{
			"label": _("Project Name"),
			"fieldname": "project_name",
			"fieldtype": "Data",
			"width": 200,
		},
		*build_pivot_columns(units),
	]


def get_data(company, fiscal_year, units):
	if not units or not fiscal_year:
		return []

	selects, params = build_pivot_selects(units, VALUE_EXPR, round_result=True)
	params.update(
		{
			"company": company,
			"fiscal_year": fiscal_year,
			"root_types": PROFIT_ROOT_TYPES,
		}
	)

	return frappe.db.sql(
		f"""
		SELECT
			gle.project AS project,
			IFNULL(proj.project_name, gle.project) AS project_name,
			{", ".join(selects)}
		FROM `tabGL Entry` gle
		INNER JOIN `tabAccount` acc ON acc.name = gle.account
		INNER JOIN `tabFiscal Year` fy ON fy.name = %(fiscal_year)s
		LEFT JOIN `tabProject` proj ON proj.name = gle.project
		WHERE gle.company = %(company)s
			AND gle.is_cancelled = 0
			AND gle.posting_date BETWEEN fy.year_start_date AND fy.year_end_date
			AND IFNULL(gle.project, '') != ''
		GROUP BY gle.project, proj.project_name
		HAVING ABS(ROUND(SUM({VALUE_EXPR}), 2)) > 0.005
		ORDER BY proj.project_name
		""",
		params,
		as_dict=True,
	)
