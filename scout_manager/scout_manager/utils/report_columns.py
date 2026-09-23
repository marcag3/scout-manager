from frappe import _

AUTRES_FIELDNAME = "autres"
TOTAL_FIELDNAME = "total"


def build_pivot_selects(units, value_expr, round_result=False):
	"""Build SQL SELECT fragments and params for one column per cost center."""
	selects = []
	params = {}
	wrap = (lambda expr: f"ROUND({expr}, 2)") if round_result else (lambda expr: expr)

	for index, unit in enumerate(units):
		param_key = f"cc_{index}"
		params[param_key] = unit["name"]
		case_expr = f"SUM(CASE WHEN gle.cost_center = %({param_key})s THEN {value_expr} ELSE 0 END)"
		selects.append(f"{wrap(case_expr)} AS `{unit['fieldname']}`")

	params["unit_ccs"] = [unit["name"] for unit in units] or [""]
	autres_expr = (
		"SUM(CASE WHEN IFNULL(gle.cost_center, '') = '' "
		"OR gle.cost_center NOT IN %(unit_ccs)s THEN {value} ELSE 0 END)"
	).format(value=value_expr)
	selects.append(f"{wrap(autres_expr)} AS {AUTRES_FIELDNAME}")
	selects.append(f"{wrap(f'SUM({value_expr})')} AS {TOTAL_FIELDNAME}")

	return selects, params


def build_pivot_columns(units, currency_options="company:company:default_currency"):
	columns = []
	for unit in units:
		columns.append(
			{
				"label": unit["cost_center_name"],
				"fieldname": unit["fieldname"],
				"fieldtype": "Currency",
				"options": currency_options,
				"cost_center": unit["name"],
				"width": 120,
			}
		)

	columns.extend(
		[
			{
				"label": _("Autres"),
				"fieldname": AUTRES_FIELDNAME,
				"fieldtype": "Currency",
				"options": currency_options,
				"width": 120,
			},
			{
				"label": _("Total"),
				"fieldname": TOTAL_FIELDNAME,
				"fieldtype": "Currency",
				"options": currency_options,
				"width": 120,
			},
		]
	)
	return columns
