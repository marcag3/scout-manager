import frappe
from frappe.tests.utils import FrappeTestCase

from scout_manager.scout_manager.bank_reconciliation.default_configs import (
	DEFAULT_CONFIG_NAME,
	sync_desjardins_default_config,
)
from scout_manager.scout_manager.bank_reconciliation.test_csv_importer import make_sample_csv


class TestScoutBankImport(FrappeTestCase):
	def setUp(self):
		sync_desjardins_default_config()
		self.company = frappe.defaults.get_global_default("company") or "_Test Company"
		self.bank_account = self._ensure_bank_account()

	def _ensure_bank_account(self):
		existing = frappe.db.get_value(
			"Bank Account",
			{"bank_account_no": "1234567890", "company": self.company, "is_company_account": 1},
			"name",
		)
		if existing:
			return existing

		bank_account = frappe.db.get_value(
			"Bank Account",
			{"company": self.company, "is_company_account": 1, "disabled": 0},
			"name",
		)
		if not bank_account:
			self.skipTest("No company bank account available for test company")

		frappe.db.set_value("Bank Account", bank_account, "bank_account_no", "1234567890")
		return bank_account

	def _create_import_file(self):
		file_doc = frappe.get_doc(
			{
				"doctype": "File",
				"file_name": "scout_bank_import_test.csv",
				"is_private": 1,
				"content": make_sample_csv(),
			}
		)
		file_doc.save(ignore_permissions=True)
		return file_doc.file_url

	def _create_import_doc(self, import_file):
		return frappe.get_doc(
			{
				"doctype": "Scout Bank Import",
				"import_file": import_file,
				"import_config": DEFAULT_CONFIG_NAME,
				"bank_account": self.bank_account,
			}
		).insert(ignore_permissions=True)

	def _cleanup_test_transactions(self):
		for name in frappe.get_all(
			"Bank Transaction",
			filters={
				"bank_account": self.bank_account,
				"description": ["like", "%TEST USER%"],
			},
			pluck="name",
		) + frappe.get_all(
			"Bank Transaction",
			filters={
				"bank_account": self.bank_account,
				"description": ["like", "%Frais bancaires%"],
			},
			pluck="name",
		):
			doc = frappe.get_doc("Bank Transaction", name)
			if doc.docstatus == 1:
				doc.cancel()
			doc.delete()

	def test_preview_without_bank_account(self):
		import_file = self._create_import_file()
		doc = frappe.get_doc(
			{
				"doctype": "Scout Bank Import",
				"import_file": import_file,
				"import_config": DEFAULT_CONFIG_NAME,
			}
		)

		preview = doc.preview_import()
		self.assertEqual(preview["account_number"], "1234567890")
		self.assertEqual(preview["suggested_bank_account"], self.bank_account)
		self.assertEqual(preview["total_transactions"], 2)

	def test_preview_and_import(self):
		self._cleanup_test_transactions()
		import_file = self._create_import_file()
		doc = self._create_import_doc(import_file)

		preview = doc.preview_import()
		self.assertEqual(preview["account_number"], "1234567890")
		self.assertEqual(preview["total_transactions"], 2)
		self.assertEqual(len(preview["transactions"]), 2)

		result = doc.import_transactions()
		self.assertEqual(result["created"], 2)
		self.assertEqual(result["skipped"], 0)
		self.assertEqual(doc.status, "Imported")

		created = frappe.get_all(
			"Bank Transaction",
			filters={"bank_account": self.bank_account, "description": ["like", "%TEST USER%"]},
			pluck="transaction_id",
		)
		self.assertTrue(created)
		self.assertTrue(all(created))

		replay_doc = self._create_import_doc(import_file)
		replay = replay_doc.import_transactions()
		self.assertEqual(replay["skipped"], 2)
		self.assertEqual(replay["created"], 0)
