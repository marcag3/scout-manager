"""Rename French-named Scout Manager assets to English source names."""

import frappe


RENAMES = (
	("Report", "Argent disponible par unité", "Available Funds per Unit"),
	("Report", "Rentabilité par projet par centre de coût", "Project Profitability by Cost Center"),
	("Custom HTML Block", "Argent disponible", "Available Funds"),
	("Dashboard Chart", "Argent disponible par unité", "Available Funds per Unit"),
)


def execute():
	for doctype, old_name, new_name in RENAMES:
		if not frappe.db.exists(doctype, old_name):
			continue

		if frappe.db.exists(doctype, new_name):
			frappe.delete_doc(doctype, old_name, force=True, ignore_permissions=True)
			continue

		frappe.rename_doc(doctype, old_name, new_name, force=True, merge=False)
