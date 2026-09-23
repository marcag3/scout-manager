import json

import frappe
from frappe import _
from frappe.model.document import Document


class BankImportConfig(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		bank: DF.Link | None
		config_json: DF.Code | None
		config_name: DF.Data
		disabled: DF.Check
		is_default: DF.Check
	# end: auto-generated types

	def validate(self):
		self._validate_config_json()
		if self.is_default:
			self._ensure_single_default()

	def _validate_config_json(self):
		if not self.config_json:
			frappe.throw(_("Config JSON is required"))

		try:
			json.loads(self.config_json)
		except (TypeError, json.JSONDecodeError):
			frappe.throw(_("Config JSON must be valid JSON"))

	def _ensure_single_default(self):
		for name in frappe.get_all(
			"Bank Import Config",
			filters={"is_default": 1, "name": ["!=", self.name]},
			pluck="name",
		):
			frappe.db.set_value("Bank Import Config", name, "is_default", 0)
