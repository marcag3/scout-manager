import csv
import io
import re
from dataclasses import dataclass, field
from datetime import datetime

from scout_manager.scout_manager.bank_reconciliation.import_config import ImportConfig

TRANSACTION_ROLES = {
	"date_transaction",
	"description",
	"amount_debit",
	"amount_credit",
	"account-number",
	"account-name",
	"reference",
}


@dataclass
class ParsedImport:
	transactions: list[dict] = field(default_factory=list)
	account_number: str | None = None
	account_name: str | None = None
	statement_from_date: str | None = None
	statement_to_date: str | None = None
	opening_balance: float | None = None
	closing_balance: float | None = None


def decode_csv_content(content: bytes | str, encoding: str | None = None) -> str:
	if isinstance(content, str):
		return content

	if encoding:
		return content.decode(encoding)

	for candidate in ("utf-8-sig", "utf-8", "iso-8859-1", "windows-1252", "latin-1"):
		try:
			return content.decode(candidate)
		except UnicodeDecodeError:
			continue
	return content.decode("iso-8859-1", errors="replace")


def parse_csv(content: bytes | str, config: ImportConfig) -> ParsedImport:
	text = decode_csv_content(content, config.encoding)
	reader = csv.reader(io.StringIO(text), delimiter=config.delimiter)
	rows = list(reader)

	if config.has_headers and rows:
		rows = rows[1:]

	result = ParsedImport()
	dates: list[str] = []

	for row in rows:
		if not _is_transaction_row(row, config):
			continue

		parsed = _parse_row(row, config)
		if not parsed:
			continue

		if parsed.get("account_number") and not result.account_number:
			result.account_number = parsed["account_number"]
		if parsed.get("account_name") and not result.account_name:
			result.account_name = parsed["account_name"]

		result.transactions.append(parsed)
		if parsed.get("date"):
			dates.append(parsed["date"])
		if parsed.get("balance") is not None:
			result.closing_balance = parsed["balance"]

	if dates:
		result.statement_from_date = min(dates)
		result.statement_to_date = max(dates)

	return result


def _is_transaction_row(row: list[str], config: ImportConfig) -> bool:
	date_idx = config.get_column("date_transaction")
	if date_idx is None or date_idx >= len(row):
		return False

	date_value = (row[date_idx] or "").strip()
	if not date_value:
		return False

	try:
		datetime.strptime(date_value, config.date_format)
	except ValueError:
		return False

	debit_idx = config.get_column("amount_debit")
	credit_idx = config.get_column("amount_credit")
	debit = parse_amount(row[debit_idx] if debit_idx is not None and debit_idx < len(row) else "", config)
	credit = parse_amount(row[credit_idx] if credit_idx is not None and credit_idx < len(row) else "", config)
	return bool(debit or credit)


def _parse_row(row: list[str], config: ImportConfig) -> dict | None:
	date_idx = config.get_column("date_transaction")
	description_idx = config.get_column("description")
	debit_idx = config.get_column("amount_debit")
	credit_idx = config.get_column("amount_credit")
	account_number_idx = config.get_column("account-number")
	account_name_idx = config.get_column("account-name")
	reference_idx = config.get_column("reference")
	balance_idx = config.get_column("balance")

	date_value = _cell(row, date_idx)
	try:
		parsed_date = datetime.strptime(date_value, config.date_format).strftime("%Y-%m-%d")
	except ValueError:
		return None

	description = _cell(row, description_idx)
	withdrawal = parse_amount(_cell(row, debit_idx), config)
	deposit = parse_amount(_cell(row, credit_idx), config)
	reference = _cell(row, reference_idx) or description

	if not withdrawal and not deposit:
		return None

	balance_value = _cell(row, balance_idx)
	balance = parse_amount(balance_value, config) if balance_value else None

	return {
		"date": parsed_date,
		"description": description,
		"withdrawal": withdrawal,
		"deposit": deposit,
		"reference_number": reference,
		"account_number": _cell(row, account_number_idx) or None,
		"account_name": _cell(row, account_name_idx) or None,
		"balance": balance,
	}


def parse_amount(value: str | None, config: ImportConfig) -> float:
	text = (value or "").strip()
	if not text:
		return 0.0

	if config.conversion:
		text = text.replace("\u00a0", " ").replace(" ", "")
		text = text.replace(",", ".")

	text = re.sub(r"[^\d.\-]", "", text)
	if not text or text in {"-", "."}:
		return 0.0

	return abs(float(text))


def _cell(row: list[str], index: int | None) -> str:
	if index is None or index >= len(row):
		return ""
	return (row[index] or "").strip()
