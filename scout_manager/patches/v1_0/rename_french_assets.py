"""Rename French-named Scout Manager assets to English source names."""

import frappe

from scout_manager.scout_manager.config.names import FRENCH_ASSET_RENAMES


def execute():
	for doctype, old_name, new_name in FRENCH_ASSET_RENAMES:
		if not frappe.db.exists(doctype, old_name):
			continue

		if frappe.db.exists(doctype, new_name):
			frappe.delete_doc(doctype, old_name, force=True, ignore_permissions=True)
			continue

		frappe.rename_doc(doctype, old_name, new_name, force=True, merge=False)
