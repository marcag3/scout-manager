from scout_manager.scout_manager.accounting.cost_center import get_cost_center_for_party

HEADER_DIMENSIONS = ("cost_center", "project")

INVOICE_PARTY_MAP = {
	"Sales Invoice": ("Customer", "customer"),
	"Purchase Invoice": ("Supplier", "supplier"),
}


def sync_header_dimensions_to_items(doc, method=None):
	"""Copy header cost_center and project to every invoice line."""
	for item in doc.get("items") or []:
		for dim in HEADER_DIMENSIONS:
			item.set(dim, doc.get(dim))


def apply_party_cost_center(doc, method=None):
	"""Fill header cost_center from party group mapping when not set."""
	if doc.get("cost_center"):
		return

	party_mapping = INVOICE_PARTY_MAP.get(doc.doctype)
	if not party_mapping:
		return

	party_type, party_field = party_mapping
	cost_center = get_cost_center_for_party(party_type, doc.get(party_field))
	if cost_center:
		doc.cost_center = cost_center
