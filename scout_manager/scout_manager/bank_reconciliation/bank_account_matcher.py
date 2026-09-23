import frappe


def suggest_bank_account(
	account_number: str | None,
	import_config: str | None = None,
	account_name: str | None = None,
	fallback: str | None = None,
) -> str | None:
	if fallback:
		return fallback

	matched = match_bank_account(account_number)
	if matched:
		return matched

	matched = match_bank_account_by_name(account_name)
	if matched:
		return matched

	if import_config:
		bank = frappe.db.get_value("Bank Import Config", import_config, "bank")
		if bank:
			accounts = _company_bank_accounts(bank=bank)
			if len(accounts) == 1:
				return accounts[0]

	company_accounts = _company_bank_accounts()
	if len(company_accounts) == 1:
		return company_accounts[0]

	return None


def match_bank_account(account_number: str | None, fallback: str | None = None) -> str | None:
	if not account_number:
		return fallback

	normalized = _normalize_account_number(account_number)
	if not normalized:
		return fallback

	accounts = _company_bank_accounts(fields=["name", "bank_account_no"])

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


def match_bank_account_by_name(account_name: str | None, fallback: str | None = None) -> str | None:
	if not account_name:
		return fallback

	normalized = account_name.strip().casefold()
	if not normalized:
		return fallback

	accounts = _company_bank_accounts(fields=["name", "account_name"])
	exact = [
		row.name
		for row in accounts
		if row.account_name and row.account_name.strip().casefold() == normalized
	]
	if len(exact) == 1:
		return exact[0]
	if len(exact) > 1:
		frappe.throw(
			frappe._("Multiple bank accounts match account name {0}. Select one manually.").format(
				account_name
			)
		)

	partial = [
		row.name
		for row in accounts
		if row.account_name
		and (
			normalized in row.account_name.strip().casefold()
			or row.account_name.strip().casefold() in normalized
		)
	]
	if len(partial) == 1:
		return partial[0]

	return fallback


def _company_bank_accounts(bank: str | None = None, fields: list[str] | None = None):
	filters = {"is_company_account": 1, "disabled": 0}
	if bank:
		filters["bank"] = bank

	if fields:
		return frappe.get_all("Bank Account", filters=filters, fields=fields)

	return frappe.get_all("Bank Account", filters=filters, pluck="name")


def _normalize_account_number(value: str | None) -> str:
	if not value:
		return ""
	return "".join(ch for ch in str(value).strip() if ch.isdigit())
