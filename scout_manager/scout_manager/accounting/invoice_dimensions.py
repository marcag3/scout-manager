HEADER_DIMENSIONS = ("cost_center", "project")


def sync_header_dimensions_to_items(doc, method=None):
	"""Copy header cost_center and project to every invoice line."""
	for item in doc.get("items") or []:
		for dim in HEADER_DIMENSIONS:
			item.set(dim, doc.get(dim))
