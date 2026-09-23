import erpnext
import frappe
from frappe.utils import add_months, formatdate, get_first_day, get_last_day, getdate, today
from frappe.utils.dashboard import cache_source

from scout_manager.scout_manager.api.dashboard import get_cash_accounts

MONTHS = 12


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
	"""Monthly money in and out of bank and cash accounts over the last 12 months.

	Amounts are netted per voucher so transfers between bank and petty cash cancel out.
	"""
	filters = frappe.parse_json(filters) or {}
	company = filters.get("company") or erpnext.get_default_company()

	end = get_last_day(today())
	start = get_first_day(add_months(end, -(MONTHS - 1)))
	months = [getdate(add_months(start, i)) for i in range(MONTHS)]
	inflows = {month: 0.0 for month in months}
	outflows = {month: 0.0 for month in months}

	accounts = get_cash_accounts(company)
	rows = []
	if accounts:
		rows = frappe.db.sql(
			"""
			SELECT
				DATE_FORMAT(posting_date, '%%Y-%%m-01') AS month,
				SUM(debit - credit) AS net
			FROM `tabGL Entry`
			WHERE company = %(company)s
				AND account IN %(accounts)s
				AND is_cancelled = 0
				AND is_opening = 'No'
				AND posting_date BETWEEN %(start)s AND %(end)s
			GROUP BY month, voucher_type, voucher_no
			""",
			{"company": company, "accounts": accounts, "start": start, "end": end},
			as_dict=True,
		)

	for row in rows:
		month = getdate(row.month)
		if row.net > 0:
			inflows[month] += row.net
		else:
			outflows[month] -= row.net

	return {
		"labels": [formatdate(month, "MMM yy") for month in months],
		"datasets": [
			{"name": "Encaissements", "values": [round(inflows[m], 2) for m in months]},
			{"name": "Décaissements", "values": [round(outflows[m], 2) for m in months]},
		],
	}
