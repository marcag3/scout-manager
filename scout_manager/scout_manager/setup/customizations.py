"""Tag troop-specific Custom Fields, Property Setters, and related records for fixture export."""

import frappe

from scout_manager.scout_manager.config.names import (
	APP_MODULE,
	RETIRED_CUSTOM_FIELDS,
	TROOP_CUSTOM_FIELDS,
	TROOP_PRINT_FORMATS,
	TROOP_PROPERTY_SETTER_DOCTYPES,
	TROOP_SERVER_SCRIPTS,
)


def tag_troop_customizations():
	"""Assign Scout Manager module to site-built troop customizations."""
	updated = []

	for doctype, fieldnames in TROOP_CUSTOM_FIELDS.items():
		for fieldname in fieldnames:
			name = f"{doctype}-{fieldname}"
			if not frappe.db.exists("Custom Field", name):
				continue
			if _set_module("Custom Field", name):
				updated.append(name)

	for doctype in TROOP_PROPERTY_SETTER_DOCTYPES:
		for row in frappe.get_all(
			"Property Setter",
			filters={"doc_type": doctype},
			pluck="name",
		):
			if _set_module("Property Setter", row):
				updated.append(row)

	for name in TROOP_SERVER_SCRIPTS:
		if frappe.db.exists("Server Script", name) and _set_module("Server Script", name):
			updated.append(name)

	for name in TROOP_PRINT_FORMATS:
		if frappe.db.exists("Print Format", name) and _set_module("Print Format", name):
			updated.append(name)

	if updated:
		frappe.db.commit()
		frappe.logger("scout_manager").info(
			"Tagged troop customizations with %s: %s",
			APP_MODULE,
			", ".join(updated),
		)

	return updated


def cleanup_retired_custom_fields():
	"""Remove custom fields dropped from fixtures."""
	removed = []

	for name in RETIRED_CUSTOM_FIELDS:
		if not frappe.db.exists("Custom Field", name):
			continue
		frappe.delete_doc("Custom Field", name, force=True, ignore_permissions=True)
		removed.append(name)

	if removed:
		frappe.db.commit()
		for doctype in ("Customer", "Customer Group", "Contact", "Supplier Group"):
			frappe.clear_cache(doctype=doctype)
		frappe.logger("scout_manager").info("Removed retired custom fields: %s", ", ".join(removed))

	return removed


def _set_module(doctype, name):
	current = frappe.db.get_value(doctype, name, "module")
	if current == APP_MODULE:
		return False

	frappe.db.set_value(doctype, name, "module", APP_MODULE, update_modified=False)
	return True
