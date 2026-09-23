import frappe
from frappe import _

from scout_manager.scout_manager.config.names import ROLE_SCOUT_TREASURER

COTISATION_ROLES = frozenset(
	{
		ROLE_SCOUT_TREASURER,
		"Accounts Manager",
		"System Manager",
	}
)


def require_gl_entry_read():
	frappe.has_permission("GL Entry", "read", throw=True)


def require_cotisation_role():
	if set(frappe.get_roles()) & COTISATION_ROLES:
		return

	frappe.throw(_("You are not permitted to create cotisation invoices."), frappe.PermissionError)
