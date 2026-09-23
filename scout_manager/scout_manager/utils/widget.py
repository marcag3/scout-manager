import os

import frappe

RETIRED_CLIENT_SCRIPTS = ("set cost center payment", "set unit")


def cleanup_retired_client_scripts():
	for script_name in RETIRED_CLIENT_SCRIPTS:
		if frappe.db.exists("Client Script", script_name):
			frappe.db.delete("Client Script", script_name)


def sync_argent_disponible_block():
	"""Keep Custom HTML Block styles in sync with the public CSS file."""
	block_name = "Argent disponible"
	if not frappe.db.exists("Custom HTML Block", block_name):
		return

	css_path = frappe.get_app_path("scout_manager", "public", "css", "argent_disponible_widget.css")
	if not os.path.exists(css_path):
		return

	with open(css_path, encoding="utf-8") as css_file:
		css = css_file.read()

	block = frappe.get_doc("Custom HTML Block", block_name)
	if block.style == css:
		return

	block.style = css
	block.save(ignore_permissions=True)
	frappe.db.commit()
