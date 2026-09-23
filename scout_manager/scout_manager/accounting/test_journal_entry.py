import frappe
from frappe.tests import IntegrationTestCase

from scout_manager.scout_manager.accounting.journal_entry import sync_bank_entry_dimensions


class TestJournalEntryDimensions(IntegrationTestCase):
	def test_sync_bank_entry_dimensions_copies_to_bank_row(self):
		doc = frappe.get_doc(
			{
				"doctype": "Journal Entry",
				"voucher_type": "Bank Entry",
				"accounts": [
					{"account": "Bank - TEST", "cost_center": "", "project": ""},
					{
						"account": "Expenses - TEST",
						"cost_center": "Main - TEST",
						"project": "Camp - TEST",
					},
				],
			}
		)

		sync_bank_entry_dimensions(doc)

		self.assertEqual(doc.accounts[0].cost_center, "Main - TEST")
		self.assertEqual(doc.accounts[0].project, "Camp - TEST")

	def test_sync_bank_entry_dimensions_ignores_other_voucher_types(self):
		doc = frappe.get_doc(
			{
				"doctype": "Journal Entry",
				"voucher_type": "Journal Entry",
				"accounts": [
					{"account": "Bank - TEST", "cost_center": "", "project": ""},
					{
						"account": "Expenses - TEST",
						"cost_center": "Main - TEST",
						"project": "Camp - TEST",
					},
				],
			}
		)

		sync_bank_entry_dimensions(doc)

		self.assertEqual(doc.accounts[0].cost_center, "")
		self.assertEqual(doc.accounts[0].project, "")
