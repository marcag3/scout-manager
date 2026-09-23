import hashlib
import re

import frappe


def normalize_description(description: str | None) -> str:
	text = (description or "").strip().lower()
	text = re.sub(r"\s+", " ", text)
	return text


def transaction_fingerprint(
	bank_account: str,
	date: str,
	withdrawal: float,
	deposit: float,
	description: str | None,
) -> str:
	payload = "|".join(
		[
			bank_account or "",
			date or "",
			f"{withdrawal:.2f}",
			f"{deposit:.2f}",
			normalize_description(description),
		]
	)
	return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def deduplicate_transactions(
	transactions: list[dict],
	bank_account: str,
	ignore_duplicate_lines: bool = True,
) -> tuple[list[dict], list[dict], list[dict]]:
	existing_ids = _existing_transaction_ids(bank_account)
	seen_in_file: set[str] = set()

	to_create: list[dict] = []
	skipped: list[dict] = []
	flagged: list[dict] = []

	for row in transactions:
		fingerprint = transaction_fingerprint(
			bank_account,
			row.get("date"),
			row.get("withdrawal") or 0,
			row.get("deposit") or 0,
			row.get("description"),
		)
		row["transaction_id"] = fingerprint

		if ignore_duplicate_lines and fingerprint in seen_in_file:
			skipped.append({**row, "reason": "duplicate_in_file"})
			continue

		if fingerprint in existing_ids:
			skipped.append({**row, "reason": "already_imported"})
			seen_in_file.add(fingerprint)
			continue

		seen_in_file.add(fingerprint)
		to_create.append(row)

	return to_create, skipped, flagged


def _existing_transaction_ids(bank_account: str) -> set[str]:
	rows = frappe.get_all(
		"Bank Transaction",
		filters={"bank_account": bank_account, "docstatus": 1},
		pluck="transaction_id",
	)
	return {row for row in rows if row}
