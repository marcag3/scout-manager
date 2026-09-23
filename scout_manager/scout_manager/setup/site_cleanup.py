"""Remove site-only copies of Scout Manager assets before app sync."""

import frappe

from scout_manager.scout_manager.config.names import (
	APP_DASHBOARD_CHARTS,
	APP_DASHBOARD_CHART_SOURCES,
	APP_MODULE,
	APP_NAME,
	APP_NUMBER_CARDS,
	APP_REPORTS,
	APP_WORKSPACES,
	ARGENT_DISPONIBLE_BLOCK,
	ARGENT_DISPONIBLE_JS,
)


def remove_site_owned_duplicates():
	"""Drop site-built copies so scout_manager JSON and fixtures can own them.

	Runs before customization tagging so troop Custom Fields and related records
	can be exported and re-imported from fixtures without duplicate names.
	"""
	removed = []

	for report_name in APP_REPORTS:
		if _remove_module_owned_doc("Report", report_name):
			removed.append(f"Report/{report_name}")

	for asset_name in APP_WORKSPACES:
		for doctype in ("Workspace", "Workspace Sidebar", "Dashboard", "Desktop Icon"):
			if _remove_app_asset(doctype, asset_name):
				removed.append(f"{doctype}/{asset_name}")

	for chart_name in APP_DASHBOARD_CHARTS:
		if _remove_module_owned_doc("Dashboard Chart", chart_name):
			removed.append(f"Dashboard Chart/{chart_name}")

	for source_name in APP_DASHBOARD_CHART_SOURCES:
		if _remove_module_owned_doc("Dashboard Chart Source", source_name):
			removed.append(f"Dashboard Chart Source/{source_name}")

	for card_name in APP_NUMBER_CARDS:
		if _remove_module_owned_doc("Number Card", card_name):
			removed.append(f"Number Card/{card_name}")

	if _remove_custom_html_block():
		removed.append(f"Custom HTML Block/{ARGENT_DISPONIBLE_BLOCK}")

	if removed:
		frappe.db.commit()
		frappe.logger("scout_manager").info(
			"Removed site-owned Scout Manager duplicates: %s", ", ".join(removed)
		)

	return removed


def _remove_module_owned_doc(doctype, name):
	if not frappe.db.exists(doctype, name):
		return False

	if frappe.db.get_value(doctype, name, "module") == APP_MODULE:
		return False

	frappe.delete_doc(doctype, name, force=True, ignore_permissions=True)
	return True


def _remove_app_asset(doctype, name):
	if not frappe.db.exists(doctype, name):
		return False

	if doctype == "Desktop Icon":
		if frappe.db.get_value(doctype, name, "app") == APP_NAME:
			return False
	elif frappe.db.get_value(doctype, name, "module") == APP_MODULE:
		return False

	frappe.delete_doc(doctype, name, force=True, ignore_permissions=True)
	return True


def _remove_custom_html_block():
	"""Remove site-built widget shell so the app fixture can replace inline script/style."""
	if not frappe.db.exists("Custom HTML Block", ARGENT_DISPONIBLE_BLOCK):
		return False

	script = frappe.db.get_value("Custom HTML Block", ARGENT_DISPONIBLE_BLOCK, "script") or ""
	widget_script = f"/assets/{APP_NAME}/js/{ARGENT_DISPONIBLE_JS}"
	if widget_script in script:
		return False

	frappe.delete_doc("Custom HTML Block", ARGENT_DISPONIBLE_BLOCK, force=True, ignore_permissions=True)
	return True
