import erpnext
import frappe
from frappe.utils import flt, today

CASH_ACCOUNT_TYPES = ("Bank", "Cash")


def get_cash_accounts(company):
	return frappe.get_all(
		"Account",
		filters={"company": company, "account_type": ["in", CASH_ACCOUNT_TYPES], "is_group": 0},
		pluck="name",
	)


@frappe.whitelist()
def get_cash_balance(filters=None):
	"""Number card: current balance of all bank and cash accounts."""
	filters = frappe.parse_json(filters) or {}
	if isinstance(filters, list):
		filters = {f[1]: f[3] for f in filters if len(f) > 3}
	company = filters.get("company") or erpnext.get_default_company()

	accounts = get_cash_accounts(company)
	balance = 0
	if accounts:
		balance = frappe.db.sql(
			"""
			SELECT SUM(debit - credit)
			FROM `tabGL Entry`
			WHERE company = %(company)s
				AND account IN %(accounts)s
				AND is_cancelled = 0
				AND posting_date <= %(today)s
			""",
			{"company": company, "accounts": accounts, "today": today()},
		)[0][0]

	return {
		"value": flt(balance, 2),
		"fieldtype": "Currency",
		"route": ["query-report", "General Ledger"],
		"route_options": {"company": company, "account": accounts},
	}
