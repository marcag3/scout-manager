import frappe
from frappe import _

INVOICE_DOCTYPES = ("Sales Invoice", "Purchase Invoice")
DIMENSIONS = ("cost_center", "project")


def inherit_dimensions_from_references(doc, method=None):
	"""Set Payment Entry dimensions from referenced invoices; block mixed values."""
	refs = [
		r
		for r in doc.get("references") or []
		if r.reference_doctype in INVOICE_DOCTYPES and r.reference_name
	]
	if not refs:
		return

	values = {dim: set() for dim in DIMENSIONS}
	for ref in refs:
		row = (
			frappe.db.get_value(
				ref.reference_doctype,
				ref.reference_name,
				DIMENSIONS,
				as_dict=True,
			)
			or {}
		)
		for dim in DIMENSIONS:
			values[dim].add(row.get(dim) or None)

	for dim in DIMENSIONS:
		unique = values[dim]
		if len(unique) > 1:
			display = ", ".join(
				v or _("(empty)") for v in sorted(unique, key=lambda x: x or "")
			)
			frappe.throw(
				_("Selected invoices have different {0}: {1}. Record one payment per {0}.").format(
					_(frappe.unscrub(dim)), display
				)
			)
		if not doc.get(dim):
			doc.set(dim, next(iter(unique)))
