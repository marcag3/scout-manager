import json

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate

from scout_manager.scout_manager.bank_reconciliation.bank_account_matcher import match_bank_account
from scout_manager.scout_manager.bank_reconciliation.csv_importer import parse_csv
from scout_manager.scout_manager.bank_reconciliation.file_reader import read_import_file_bytes
from scout_manager.scout_manager.bank_reconciliation.duplicate_detector import deduplicate_transactions
from scout_manager.scout_manager.bank_reconciliation.import_config import ImportConfig, get_default_config_path


class ScoutBankImport(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		bank_account: DF.Link
		closing_balance: DF.Currency
		detected_account_number: DF.Data | None
		import_config: DF.Literal["ca/desjardins/account.json"]
		import_file: DF.Attach
		import_log: DF.LongText | None
		opening_balance: DF.Currency
		preview_html: DF.HTMLEditor | None
		statement_from_date: DF.Date | None
		statement_to_date: DF.Date | None
		status: DF.Literal["Draft", "Imported", "Partial", "Failed"]
	# end: auto-generated types

	def validate(self):
		self._validate_permissions()

	def _validate_permissions(self):
		required = {
			"read": _("read"),
			"create": _("create"),
			"write": _("write"),
			"submit": _("submit"),
		}
		for perm, label in required.items():
			if not frappe.has_permission("Bank Transaction", perm):
				frappe.throw(
					_("You do not have permission to {0} bank transactions").format(label),
					title=_("Permission Denied"),
				)

	@frappe.whitelist()
	def preview_import(self):
		parsed = self._parse_file()
		suggested_bank_account = match_bank_account(parsed.account_number, self.bank_account)

		return {
			"transactions": parsed.transactions[:100],
			"total_transactions": len(parsed.transactions),
			"account_number": parsed.account_number,
			"account_name": parsed.account_name,
			"statement_from_date": parsed.statement_from_date,
			"statement_to_date": parsed.statement_to_date,
			"opening_balance": parsed.opening_balance,
			"closing_balance": parsed.closing_balance,
			"suggested_bank_account": suggested_bank_account,
		}

	@frappe.whitelist()
	def import_transactions(self):
		if self.status not in ("Draft", "Partial"):
			frappe.throw(_("Only draft imports can be processed"))

		parsed = self._parse_file()
		bank_account = self.bank_account or match_bank_account(parsed.account_number)
		if not bank_account:
			frappe.throw(_("Select a bank account or include a recognizable account number in the file"))

		config = self._get_config()
		to_create, skipped, flagged = deduplicate_transactions(
			parsed.transactions,
			bank_account,
			ignore_duplicate_lines=config.ignore_duplicate_lines,
		)

		company, currency = frappe.db.get_value(
			"Bank Account",
			bank_account,
			["company", "account"],
		)
		currency = frappe.get_cached_value("Account", currency, "account_currency")

		created = []
		failed = []

		for row in to_create:
			try:
				bank_tx = frappe.get_doc(
					{
						"doctype": "Bank Transaction",
						"date": row.get("date"),
						"status": "Unreconciled",
						"bank_account": bank_account,
						"withdrawal": row.get("withdrawal") or 0,
						"deposit": row.get("deposit") or 0,
						"description": row.get("description"),
						"reference_number": row.get("reference_number"),
						"transaction_id": row.get("transaction_id"),
						"currency": currency,
						"company": company,
					}
				)
				bank_tx.insert()
				bank_tx.submit()
				created.append(bank_tx.name)
			except Exception:
				frappe.log_error(title="Scout Bank Import")
				failed.append(row)

		if parsed.statement_to_date and parsed.closing_balance is not None:
			from erpnext.accounts.doctype.bank_account.bank_account import set_closing_balance_as_per_statement

			set_closing_balance_as_per_statement(
				bank_account,
				getdate(parsed.statement_to_date),
				parsed.closing_balance,
			)

		if created:
			from erpnext.accounts.doctype.bank_transaction_rule.bank_transaction_rule import run_rule_evaluation

			run_rule_evaluation()

		self.bank_account = bank_account
		self.detected_account_number = parsed.account_number
		self.statement_from_date = parsed.statement_from_date
		self.statement_to_date = parsed.statement_to_date
		self.opening_balance = parsed.opening_balance
		self.closing_balance = parsed.closing_balance
		self.import_log = json.dumps(
			{
				"created": len(created),
				"skipped": len(skipped),
				"flagged": len(flagged),
				"failed": len(failed),
				"created_names": created,
				"skipped_rows": skipped[:50],
				"flagged_rows": flagged[:50],
			},
			indent=2,
		)
		self.status = "Imported" if created and not failed else "Partial" if created else "Failed"
		self.save()

		return {
			"created": len(created),
			"skipped": len(skipped),
			"flagged": len(flagged),
			"failed": len(failed),
			"status": self.status,
		}

	def _parse_file(self):
		if not self.import_file:
			frappe.throw(_("Attach a CSV file before importing"))

		config = self._get_config()
		content = read_import_file_bytes(self.import_file)
		return parse_csv(content, config)

	def _get_config(self) -> ImportConfig:
		config_path = self.import_config or get_default_config_path()
		return ImportConfig.from_path(config_path)


@frappe.whitelist()
def preview_bank_import(import_file, import_config=None, bank_account=None):
	"""Parse an uploaded file without saving the Scout Bank Import document."""
	doc = frappe.get_doc(
		{
			"doctype": "Scout Bank Import",
			"import_file": import_file,
			"import_config": import_config or get_default_config_path(),
			"bank_account": bank_account,
		}
	)
	return doc.preview_import()


@frappe.whitelist()
def get_import_config_options():
	from scout_manager.scout_manager.bank_reconciliation.import_config import list_bundled_configs

	return list_bundled_configs()
