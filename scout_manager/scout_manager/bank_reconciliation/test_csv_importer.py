import frappe
from frappe.tests import IntegrationTestCase

from scout_manager.scout_manager.bank_reconciliation.csv_importer import (
	decode_csv_content,
	parse_amount,
	parse_csv,
)
from scout_manager.scout_manager.bank_reconciliation.duplicate_detector import (
	deduplicate_transactions,
	transaction_fingerprint,
)
from scout_manager.scout_manager.bank_reconciliation.default_configs import sync_desjardins_default_config
from scout_manager.scout_manager.bank_reconciliation.import_config import (
	ImportConfig,
	get_default_config_path,
)

DESJARDINS_CONFIG = ImportConfig.from_path(get_default_config_path())


def make_sample_csv(**overrides):
	rows = [
		'Test Chequing,1234567890,,2025/09/15,,Virement Interac de: TEST USER,,,"150,00",,,,,"1 650,00"',
		'Test Chequing,1234567890,,2025/09/16,,Frais bancaires,,"12,34",,,,,,"1 637,66"',
	]
	if overrides.get("include_duplicate"):
		rows.append(
			'Test Chequing,1234567890,,2025/09/15,,Virement Interac de: TEST USER,,,"150,00",,,,,"1 650,00"'
		)
	return "\n".join(rows) + "\n"


def make_sample_csv_bytes(**overrides):
	return make_sample_csv(**overrides).encode("iso-8859-1")


class TestCSVImporter(IntegrationTestCase):
	def test_import_config_from_doc_matches_bundled_path(self):
		config_name = sync_desjardins_default_config()
		from_doc = ImportConfig.from_doc(config_name)
		from_path = ImportConfig.from_path(get_default_config_path())

		self.assertEqual(from_doc.roles, from_path.roles)
		self.assertEqual(from_doc.encoding, from_path.encoding)
		self.assertEqual(from_doc.conversion, from_path.conversion)

	def test_parse_desjardins_rows(self):
		parsed = parse_csv(make_sample_csv(), DESJARDINS_CONFIG)

		self.assertEqual(parsed.account_number, "1234567890")
		self.assertEqual(parsed.statement_from_date, "2025-09-15")
		self.assertEqual(parsed.statement_to_date, "2025-09-16")
		self.assertEqual(len(parsed.transactions), 2)

		deposit = parsed.transactions[0]
		self.assertEqual(deposit["date"], "2025-09-15")
		self.assertEqual(deposit["deposit"], 150.0)
		self.assertEqual(deposit["withdrawal"], 0.0)
		self.assertIn("TEST USER", deposit["description"])

		withdrawal = parsed.transactions[1]
		self.assertEqual(withdrawal["withdrawal"], 12.34)
		self.assertEqual(withdrawal["deposit"], 0.0)
		self.assertEqual(parsed.opening_balance, 1500.0)
		self.assertEqual(parsed.closing_balance, 1637.66)

	def test_iso_8859_1_encoding(self):
		row = "Test,1234567890,,2025/09/15,,Virement Interac à /SMGM /,,,\"150,00\",,,,,\"1 650,00\"\n"
		parsed = parse_csv(row.encode("iso-8859-1"), DESJARDINS_CONFIG)
		self.assertIn("à", parsed.transactions[0]["description"])
		self.assertNotIn("ŕ", parsed.transactions[0]["description"])

	def test_decode_respects_config_encoding(self):
		text = decode_csv_content("Virement Interac à".encode("iso-8859-1"), "iso-8859-1")
		self.assertIn("à", text)

	def test_french_amount_conversion(self):
		self.assertEqual(parse_amount("1 234,56", DESJARDINS_CONFIG), 1234.56)

	def test_ignore_duplicate_lines_within_file(self):
		parsed = parse_csv(make_sample_csv(include_duplicate=True), DESJARDINS_CONFIG)
		self.assertEqual(len(parsed.transactions), 3)

		to_create, skipped, _flagged = deduplicate_transactions(
			parsed.transactions,
			"Test Bank - _TC",
			ignore_duplicate_lines=DESJARDINS_CONFIG.ignore_duplicate_lines,
		)
		self.assertEqual(len(to_create), 2)
		self.assertEqual(len(skipped), 1)
		self.assertEqual(skipped[0]["reason"], "duplicate_in_file")

	def test_fingerprint_dedup_against_existing_bank_transaction(self):
		if not frappe.db.exists("Bank Account", "Checking Account - Citi Bank"):
			self.skipTest("Standard ERPNext bank account fixture not available")

		parsed = parse_csv(make_sample_csv(), DESJARDINS_CONFIG)
		txn = parsed.transactions[0]
		bank_account = "Checking Account - Citi Bank"
		fingerprint = transaction_fingerprint(
			bank_account,
			txn["date"],
			txn["withdrawal"],
			txn["deposit"],
			txn["description"],
		)

		existing = frappe.get_all(
			"Bank Transaction",
			filters={"transaction_id": fingerprint, "bank_account": bank_account},
			pluck="name",
		)
		for name in existing:
			frappe.delete_doc("Bank Transaction", name, force=True)

		doc = frappe.get_doc(
			{
				"doctype": "Bank Transaction",
				"date": txn["date"],
				"status": "Unreconciled",
				"bank_account": bank_account,
				"withdrawal": txn["withdrawal"],
				"deposit": txn["deposit"],
				"description": txn["description"],
				"transaction_id": fingerprint,
				"currency": "CAD",
				"company": frappe.defaults.get_global_default("company"),
			}
		)
		doc.insert()
		doc.submit()

		to_create, skipped, _flagged = deduplicate_transactions(
			parsed.transactions,
			bank_account,
			ignore_duplicate_lines=True,
		)
		self.assertEqual(len(skipped), 1)
		self.assertEqual(skipped[0]["reason"], "already_imported")
		self.assertEqual(len(to_create), 1)
