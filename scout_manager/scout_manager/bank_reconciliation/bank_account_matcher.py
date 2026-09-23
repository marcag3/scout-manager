import frappe


def match_bank_account(account_number: str | None, fallback: str | None = None) -> str | None:
	if not account_number:
		return fallback

	normalized = _normalize_account_number(account_number)
	if not normalized:
		return fallback

	accounts = frappe.get_all(
		"Bank Account",
		filters={"is_company_account": 1, "disabled": 0},
		fields=["name", "bank_account_no"],
	)

	exact = [row.name for row in accounts if _normalize_account_number(row.bank_account_no) == normalized]
	if len(exact) == 1:
		return exact[0]
	if len(exact) > 1:
		frappe.throw(
			frappe._("Multiple bank accounts match account number {0}. Select one manually.").format(
				account_number
			)
		)

	suffix_matches = [
		row.name
		for row in accounts
		if row.bank_account_no
		and (
			normalized.endswith(_normalize_account_number(row.bank_account_no))
			or _normalize_account_number(row.bank_account_no).endswith(normalized)
		)
	]
	if len(suffix_matches) == 1:
		return suffix_matches[0]
	if len(suffix_matches) > 1:
		frappe.throw(
			frappe._("Multiple bank accounts match account number {0}. Select one manually.").format(
				account_number
			)
		)

	return fallback


def _normalize_account_number(value: str | None) -> str:
	if not value:
		return ""
	return "".join(ch for ch in str(value).strip() if ch.isdigit())
