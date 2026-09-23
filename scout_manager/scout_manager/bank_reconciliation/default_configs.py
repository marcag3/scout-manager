import frappe

from scout_manager.scout_manager.bank_reconciliation.import_config import (
	get_default_config_path,
	resolve_config_path,
)

DEFAULT_CONFIG_NAME = "Desjardins — CSV Accentué"
LEGACY_CONFIG_PATH = "ca/desjardins/account.json"


def get_default_import_config() -> str | None:
	return frappe.db.get_value(
		"Bank Import Config",
		{"is_default": 1, "disabled": 0},
		"name",
		order_by="modified desc",
	)


def is_legacy_import_config(value: str | None) -> bool:
	if not value:
		return False
	return value == LEGACY_CONFIG_PATH or value.endswith(".json") or "/" in value


def resolve_import_config_name(import_config: str | None) -> str | None:
	"""Map legacy bundled paths and missing links to the default Bank Import Config."""
	if not import_config or is_legacy_import_config(import_config):
		return get_default_import_config()

	if frappe.db.exists("Bank Import Config", import_config):
		return import_config

	return get_default_import_config()


def load_bundled_config_json(config_path: str | None = None) -> str:
	path = resolve_config_path(config_path or get_default_config_path())
	return path.read_text(encoding="utf-8")


def sync_desjardins_default_config() -> str:
	"""Create or re-sync the default Desjardins config from the bundled JSON file."""
	config_json = load_bundled_config_json()

	if frappe.db.exists("Bank Import Config", DEFAULT_CONFIG_NAME):
		doc = frappe.get_doc("Bank Import Config", DEFAULT_CONFIG_NAME)
		doc.config_json = config_json
		doc.is_default = 1
		doc.disabled = 0
		doc.save(ignore_permissions=True)
		return doc.name

	doc = frappe.get_doc(
		{
			"doctype": "Bank Import Config",
			"config_name": DEFAULT_CONFIG_NAME,
			"config_json": config_json,
			"is_default": 1,
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name


def migrate_scout_bank_import_configs(config_name: str):
	frappe.db.sql(
		"""
		UPDATE `tabScout Bank Import`
		SET import_config = %s
		WHERE import_config = %s OR import_config IS NULL OR import_config = ''
		""",
		(config_name, LEGACY_CONFIG_PATH),
	)
