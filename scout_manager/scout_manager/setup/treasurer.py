import json
import os

import frappe
from frappe.modules.export_file import strip_default_fields
from frappe.modules.utils import create_directory_on_app_path

from scout_manager.scout_manager.config.names import (
	REPORT_ARGENT_DISPONIBLE,
	REPORT_BALANCE_SHEET_CC,
	REPORT_RENTABILITE_CC,
)

ROLE = "Scout Treasurer"
WORKSPACE = "Scout Treasurer"
SIDEBAR = "Scout Treasurer"
DASHBOARD = "Scout Treasurer"

DOCTYPE_ICONS = {
	"Customer": "customer",
	"Contact": "contact",
	"Address": "address",
	"Supplier": "supplier",
	"Sales Invoice": "receipt",
	"Item": "stock",
	"Dunning": "mail",
	"Process Statement Of Accounts": "mail",
	"Purchase Invoice": "purchase-invoice",
	"Payment Entry": "payment",
	"Payment Reconciliation": "tool",
	"Unreconcile Payment": "split",
	"Bank Statement Import": "upload",
	"Bank Reconciliation Tool": "tool",
	"Bank Clearance": "check",
	"Process Payment Reconciliation": "tool",
	"Bank Transaction Rule": "filter",
	"Bank Transaction": "bank",
	"Journal Entry": "book",
	"Period Closing Voucher": "lock",
	"Cost Center": "organization",
	"Project": "project",
	"Budget": "wallet",
	"Account": "tree",
	"Bank": "bank",
	"Bank Account": "bank",
	"Fiscal Year": "calendar",
	"Accounts Settings": "settings",
	"GL Entry": "list",
}

# DocType -> permission level for the Scout Treasurer role.
# Transactional docs need submit; setup masters need write; audit views are read-only.
DOCTYPE_PERMISSIONS = {
	"Customer": {"read": 1, "write": 1, "create": 1, "export": 1, "print": 1, "email": 1, "report": 1},
	"Contact": {"read": 1, "write": 1, "create": 1, "export": 1, "print": 1, "email": 1, "report": 1},
	"Address": {"read": 1, "write": 1, "create": 1, "export": 1, "print": 1, "email": 1, "report": 1},
	"Supplier": {"read": 1, "write": 1, "create": 1, "export": 1, "print": 1, "email": 1, "report": 1},
	"Sales Invoice": {
		"read": 1,
		"write": 1,
		"create": 1,
		"submit": 1,
		"cancel": 1,
		"export": 1,
		"print": 1,
		"email": 1,
		"report": 1,
	},
	"Item": {"read": 1, "write": 1, "create": 1, "export": 1, "print": 1, "email": 1, "report": 1},
	"Dunning": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "export": 1, "print": 1, "email": 1},
	"Process Statement Of Accounts": {
		"read": 1,
		"write": 1,
		"create": 1,
		"submit": 1,
		"cancel": 1,
		"export": 1,
		"print": 1,
		"email": 1,
	},
	"Purchase Invoice": {
		"read": 1,
		"write": 1,
		"create": 1,
		"submit": 1,
		"cancel": 1,
		"export": 1,
		"print": 1,
		"email": 1,
		"report": 1,
	},
	"Payment Entry": {
		"read": 1,
		"write": 1,
		"create": 1,
		"submit": 1,
		"cancel": 1,
		"export": 1,
		"print": 1,
		"email": 1,
		"report": 1,
	},
	"Payment Reconciliation": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1},
	"Unreconcile Payment": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1},
	"Bank Statement Import": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1},
	"Bank Reconciliation Tool": {"read": 1, "write": 1},
	"Bank Clearance": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1},
	"Process Payment Reconciliation": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1},
	"Bank Transaction Rule": {"read": 1, "write": 1, "create": 1, "delete": 1},
	"Bank Transaction": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "export": 1, "report": 1},
	"Journal Entry": {
		"read": 1,
		"write": 1,
		"create": 1,
		"submit": 1,
		"cancel": 1,
		"export": 1,
		"print": 1,
		"email": 1,
		"report": 1,
	},
	"Period Closing Voucher": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1},
	"Cost Center": {"read": 1, "write": 1, "create": 1, "export": 1, "report": 1},
	"Project": {"read": 1, "write": 1, "create": 1, "export": 1, "report": 1},
	"Budget": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "export": 1, "report": 1},
	"Account": {"read": 1, "write": 1, "create": 1, "export": 1, "report": 1},
	"Bank": {"read": 1, "write": 1, "create": 1},
	"Bank Account": {"read": 1, "write": 1, "create": 1, "export": 1, "report": 1},
	"Fiscal Year": {"read": 1, "write": 1, "create": 1},
	"Accounts Settings": {"read": 1, "write": 1},
	"GL Entry": {"read": 1, "export": 1, "report": 1},
	"Dashboard": {"read": 1},
	"Dashboard Chart": {"read": 1},
	"Number Card": {"read": 1},
	"Workspace": {"read": 1},
}

REPORTS = [
	"Accounts Receivable",
	"Customer Credit Balance",
	"Customer Ledger Summary",
	"Accounts Payable",
	"Supplier Ledger Summary",
	"Budget Variance Report",
	"Trial Balance",
	"Profit and Loss Statement",
	"Balance Sheet",
	REPORT_BALANCE_SHEET_CC,
	"Cash Flow",
	"General Ledger",
	REPORT_RENTABILITE_CC,
	REPORT_ARGENT_DISPONIBLE,
	"Bank Reconciliation Statement",
]

BANKING_LINKS = [
	{
		"label": "Bank Reconciliation Tool",
		"link_to": "Bank Reconciliation Tool",
		"link_type": "DocType",
		"type": "Link",
		"hidden": 0,
		"is_query_report": 0,
		"link_count": 0,
		"onboard": 0,
	},
	{
		"label": "Bank Clearance",
		"link_to": "Bank Clearance",
		"link_type": "DocType",
		"type": "Link",
		"hidden": 0,
		"is_query_report": 0,
		"link_count": 0,
		"onboard": 0,
	},
	{
		"label": "Process Payment Reconciliation",
		"link_to": "Process Payment Reconciliation",
		"link_type": "DocType",
		"type": "Link",
		"hidden": 0,
		"is_query_report": 0,
		"link_count": 0,
		"onboard": 0,
	},
	{
		"label": "Bank Reconciliation Statement",
		"link_to": "Bank Reconciliation Statement",
		"link_type": "Report",
		"type": "Link",
		"hidden": 0,
		"is_query_report": 1,
		"link_count": 0,
		"onboard": 0,
		"dependencies": "Bank Transaction",
	},
]

BANKING_SHORTCUTS = [
	{"label": "Banking", "type": "URL", "url": "/banking", "color": "Green"},
	{"label": "Bank Statement Importer", "type": "URL", "url": "/banking/statement-importer", "color": "Grey"},
]


def setup_scout_treasurer():
	ensure_role()
	ensure_doctype_permissions()
	ensure_report_permissions()
	ensure_banking_workspace_links()
	sync_scout_treasurer_sidebar()
	set_default_workspace_for_role()


def ensure_role():
	if frappe.db.exists("Role", ROLE):
		return

	frappe.get_doc(
		{
			"doctype": "Role",
			"role_name": ROLE,
			"desk_access": 1,
			"is_custom": 1,
		}
	).insert(ignore_permissions=True)


def ensure_doctype_permissions():
	from frappe.permissions import add_permission, update_permission_property

	for doctype, permissions in DOCTYPE_PERMISSIONS.items():
		if not frappe.db.exists("DocType", doctype):
			continue

		if not frappe.db.exists("Custom DocPerm", {"parent": doctype, "role": ROLE}):
			add_permission(doctype, ROLE, 0)

		for perm_type, value in permissions.items():
			if value:
				update_permission_property(doctype, ROLE, 0, perm_type, 1)


def ensure_report_permissions():
	for report in REPORTS:
		if not frappe.db.exists("Report", report):
			continue

		if frappe.db.exists(
			"Has Role",
			{"parent": report, "parenttype": "Report", "role": ROLE},
		):
			continue

		frappe.get_doc(
			{
				"doctype": "Has Role",
				"parent": report,
				"parenttype": "Report",
				"parentfield": "roles",
				"role": ROLE,
			}
		).insert(ignore_permissions=True)


def ensure_banking_workspace_links():
	"""Add ERPNext v16 banking links and shortcuts to the Scout Treasurer workspace."""
	if not frappe.db.exists("Workspace", WORKSPACE):
		return

	workspace = frappe.get_doc("Workspace", WORKSPACE)
	banking_idx = next(
		(i for i, link in enumerate(workspace.links) if link.label == "Banking" and link.type == "Card Break"),
		None,
	)
	if banking_idx is None:
		return

	next_break = next(
		(i for i, link in enumerate(workspace.links) if i > banking_idx and link.type == "Card Break"),
		len(workspace.links),
	)
	existing_banking = {link.label: link.as_dict() for link in workspace.links[banking_idx + 1 : next_break]}
	ordered_specs = BANKING_LINKS + [
		{
			"label": "Bank Statement Import",
			"link_to": "Bank Statement Import",
			"link_type": "DocType",
			"type": "Link",
			"hidden": 0,
			"is_query_report": 0,
			"link_count": 0,
			"onboard": 0,
		},
		{
			"label": "Bank Transaction",
			"link_to": "Bank Transaction",
			"link_type": "DocType",
			"type": "Link",
			"hidden": 0,
			"is_query_report": 0,
			"link_count": 0,
			"onboard": 0,
		},
	]
	ordered_banking = [existing_banking.get(spec["label"], spec) for spec in ordered_specs]

	prefix = [link.as_dict() for link in workspace.links[:banking_idx]]
	suffix = [link.as_dict() for link in workspace.links[next_break:]]
	card_break = workspace.links[banking_idx].as_dict()
	card_break["link_count"] = len(ordered_banking)

	workspace.links = []
	for row in prefix + [card_break] + ordered_banking + suffix:
		workspace.append("links", row)

	existing_shortcuts = {shortcut.label for shortcut in workspace.shortcuts}
	for shortcut in BANKING_SHORTCUTS:
		if shortcut["label"] not in existing_shortcuts:
			workspace.append("shortcuts", shortcut)

	content = json.loads(workspace.content or "[]")
	shortcut_names = {
		block["data"].get("shortcut_name")
		for block in content
		if block.get("type") == "shortcut"
	}
	dashboard_idx = next(
		(
			i
			for i, block in enumerate(content)
			if block.get("type") == "shortcut" and block["data"].get("shortcut_name") == "Accounts Dashboard"
		),
		None,
	)
	if dashboard_idx is not None and "Banking" not in shortcut_names:
		content.insert(
			dashboard_idx + 1,
			{"id": "banking-sc", "type": "shortcut", "data": {"shortcut_name": "Banking", "col": 4}},
		)
	if "Bank Statement Importer" not in shortcut_names:
		banking_block_idx = next(
			(
				i
				for i, block in enumerate(content)
				if block.get("type") == "shortcut" and block["data"].get("shortcut_name") == "Banking"
			),
			None,
		)
		if banking_block_idx is not None:
			content.insert(
				banking_block_idx + 1,
				{
					"id": "bsi-sc",
					"type": "shortcut",
					"data": {"shortcut_name": "Bank Statement Importer", "col": 4},
				},
			)

	workspace.content = json.dumps(content)
	workspace.flags.ignore_links = True
	workspace.save(ignore_permissions=True)


def sync_scout_treasurer_sidebar():
	if not frappe.db.exists("Workspace", WORKSPACE):
		return

	workspace = frappe.get_doc("Workspace", WORKSPACE)
	items = _build_sidebar_items(workspace)

	if not frappe.db.exists("Workspace Sidebar", SIDEBAR):
		return

	sidebar = frappe.get_doc("Workspace Sidebar", SIDEBAR)
	sidebar.items = []
	for item in items:
		sidebar.append("items", item)
	sidebar.save(ignore_permissions=True)
	_export_sidebar(sidebar)


def _build_sidebar_items(workspace):
	items = [
		{
			"type": "Link",
			"label": "Home",
			"icon": "home",
			"link_type": "Workspace",
			"link_to": WORKSPACE,
			"child": 0,
			"collapsible": 1,
			"indent": 0,
			"keep_closed": 0,
			"show_arrow": 0,
		}
	]

	for shortcut in workspace.shortcuts:
		items.append(_sidebar_item_for_shortcut(shortcut))

	for link in workspace.links:
		if link.type == "Card Break":
			items.append(
				{
					"type": "Section Break",
					"label": link.label,
					"link_type": link.link_type or "DocType",
					"child": 0,
					"collapsible": 1,
					"indent": 1,
					"keep_closed": 1 if link.label == "Setup" else 0,
					"show_arrow": 0,
				}
			)
			continue

		if link.type != "Link":
			continue

		icon = "table" if link.link_type == "Report" else DOCTYPE_ICONS.get(link.link_to, "")
		items.append(
			{
				"type": "Link",
				"label": link.label,
				"icon": icon,
				"link_type": link.link_type,
				"link_to": link.link_to,
				"child": 1,
				"collapsible": 1,
				"indent": 0,
				"keep_closed": 0,
				"show_arrow": 0,
			}
		)

	return items


def _sidebar_item_for_shortcut(shortcut):
	item = {
		"type": "Link",
		"label": shortcut.label,
		"icon": "chart",
		"child": 0,
		"collapsible": 1,
		"indent": 0,
		"keep_closed": 0,
		"show_arrow": 0,
	}

	if shortcut.type == "URL":
		item["link_type"] = "URL"
		item["url"] = shortcut.url
	else:
		item["link_type"] = shortcut.type
		item["link_to"] = shortcut.link_to

	return item


def _export_sidebar(sidebar):
	if not frappe.conf.developer_mode:
		return

	folder_path = create_directory_on_app_path("workspace_sidebar", sidebar.app or "scout_manager")
	file_path = os.path.join(folder_path, f"{frappe.scrub(sidebar.title)}.json")
	doc_export = strip_default_fields(sidebar, sidebar.as_dict(no_nulls=True, no_private_properties=True))
	with open(file_path, "w+", encoding="utf-8") as doc_file:
		doc_file.write(frappe.as_json(doc_export) + "\n")


def set_default_workspace_for_role():
	"""Set Scout Treasurer as the default workspace for users who only have treasurer-facing roles."""
	if not frappe.db.exists("Workspace", WORKSPACE):
		return

	treasurer_users = frappe.get_all(
		"Has Role",
		filters={"role": ROLE, "parenttype": "User"},
		pluck="parent",
	)
	admin_roles = {"Administrator", "System Manager", "Accounts Manager", "Accounts User"}

	for user in treasurer_users:
		if user in ("Administrator", "Guest"):
			continue

		user_roles = set(frappe.get_roles(user)) - {"All", "Guest"}
		if user_roles & admin_roles:
			continue

		frappe.db.set_value("User", user, "default_workspace", WORKSPACE, update_modified=False)
