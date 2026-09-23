import os

import frappe

from scout_manager.scout_manager.config.names import (
	ARGENT_DISPONIBLE_BLOCK,
	ARGENT_DISPONIBLE_CSS,
	RETIRED_CLIENT_SCRIPTS,
)


def cleanup_retired_client_scripts():
	for script_name in RETIRED_CLIENT_SCRIPTS:
		if frappe.db.exists("Client Script", script_name):
			frappe.db.delete("Client Script", script_name)


def sync_argent_disponible_block():
	"""Keep Custom HTML Block styles in sync with the public CSS file."""
	if not frappe.db.exists("Custom HTML Block", ARGENT_DISPONIBLE_BLOCK):
		return

	css_path = frappe.get_app_path("scout_manager", "public", "css", ARGENT_DISPONIBLE_CSS)
	if not os.path.exists(css_path):
		return

	with open(css_path, encoding="utf-8") as css_file:
		css = css_file.read()

	block = frappe.get_doc("Custom HTML Block", ARGENT_DISPONIBLE_BLOCK)
	if block.style == css:
		return

	block.style = css
	block.save(ignore_permissions=True)
	frappe.db.commit()
