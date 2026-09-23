import frappe

from scout_manager.scout_manager.config.names import GROUP_COST_CENTER_FIELD

PARTY_GROUP_MAP = {
	"Customer": ("Customer Group", "customer_group"),
	"Supplier": ("Supplier Group", "supplier_group"),
}


def get_cost_center_for_group(group_doctype, group_name):
	if not group_name:
		return None
	return frappe.db.get_value(group_doctype, group_name, GROUP_COST_CENTER_FIELD)


def get_cost_center_for_party(party_type, party):
	if not party_type or not party:
		return None

	mapping = PARTY_GROUP_MAP.get(party_type)
	if not mapping:
		return None

	group_doctype, group_field = mapping
	group_name = frappe.db.get_value(party_type, party, group_field)
	return get_cost_center_for_group(group_doctype, group_name)


@frappe.whitelist()
def resolve_cost_center(party_type, party):
	return get_cost_center_for_party(party_type, party)
