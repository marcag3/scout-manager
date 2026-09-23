import frappe
from frappe import _

DIMENSIONS = ("cost_center", "project")
BANK_ENTRY_VOUCHER_TYPES = frozenset({"Bank Entry", "Credit Card Entry"})


def sync_bank_entry_dimensions(doc, method=None):
	"""Copy cost_center and project from offset rows onto the bank GL row."""
	if doc.voucher_type not in BANK_ENTRY_VOUCHER_TYPES:
		return

	accounts = doc.get("accounts") or []
	if not accounts:
		return

	values = {dim: set() for dim in DIMENSIONS}
	for row in accounts:
		for dim in DIMENSIONS:
			if row.get(dim):
				values[dim].add(row.get(dim))

	for dim in DIMENSIONS:
		unique = values[dim]
		if len(unique) > 1:
			display = ", ".join(
				v or _("(empty)") for v in sorted(unique, key=lambda x: x or "")
			)
			frappe.throw(
				_("Bank entry account rows have different {0}: {1}.").format(
					_(frappe.unscrub(dim)), display
				)
			)

	for dim in DIMENSIONS:
		if not values[dim]:
			continue
		value = next(iter(values[dim]))
		for row in accounts:
			if not row.get(dim):
				row.set(dim, value)
