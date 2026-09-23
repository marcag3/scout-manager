import erpnext
import frappe
from frappe import _

from scout_manager.scout_manager.config.troop import (
	BANQUE_ACCOUNT_TYPES,
	CAISSE_ACCOUNT_TYPES,
	PASSIF_ROOT_TYPE,
	REALLOC_ACCOUNT_TYPES,
	RECEIVABLE_ACCOUNT_TYPES,
)
from scout_manager.scout_manager.utils.cost_centers import get_unit_cost_centers

AMOUNT_FIELDS = ("banque", "caisse", "ar", "passif", "disponible", "disponible_ar")


def execute(filters=None):
	filters = filters or {}
	company = filters.get("company") or erpnext.get_default_company()
	to_date = filters.get("to_date")

	units = get_unit_cost_centers(company)
	columns = get_columns()
	data = get_data(company, to_date, units)
	return columns, data


def get_columns():
	return [
		{
			"label": _("Cost Center"),
			"fieldname": "cost_center",
			"fieldtype": "Link",
			"options": "Cost Center",
			"width": 180,
		},
		{
			"label": _("Unit"),
			"fieldname": "cost_center_name",
			"fieldtype": "Data",
			"width": 140,
		},
		{
			"label": _("Banque"),
			"fieldname": "banque",
			"fieldtype": "Currency",
			"options": "company:company:default_currency",
			"width": 120,
		},
		{
			"label": _("Caisse"),
			"fieldname": "caisse",
			"fieldtype": "Currency",
			"options": "company:company:default_currency",
			"width": 120,
		},
		{
			"label": _("À recevoir"),
			"fieldname": "ar",
			"fieldtype": "Currency",
			"options": "company:company:default_currency",
			"width": 120,
		},
		{
			"label": _("Passif"),
			"fieldname": "passif",
			"fieldtype": "Currency",
			"options": "company:company:default_currency",
			"width": 120,
		},
		{
			"label": _("Disponible"),
			"fieldname": "disponible",
			"fieldtype": "Currency",
			"options": "company:company:default_currency",
			"width": 120,
		},
		{
			"label": _("Disponible incl. créances"),
			"fieldname": "disponible_ar",
			"fieldtype": "Currency",
			"options": "company:company:default_currency",
			"width": 150,
		},
	]


def get_data(company, to_date, units):
	unit_names = [unit["name"] for unit in units]
	if not unit_names:
		return []

	params = {
		"company": company,
		"to_date": to_date,
		"banque_types": BANQUE_ACCOUNT_TYPES,
		"realloc_types": REALLOC_ACCOUNT_TYPES,
		"caisse_types": CAISSE_ACCOUNT_TYPES,
		"receivable_types": RECEIVABLE_ACCOUNT_TYPES,
		"passif_root_type": PASSIF_ROOT_TYPE,
		"unit_names": unit_names,
	}

	rows = frappe.db.sql(
		"""
		SELECT
			cc.name AS cost_center,
			cc.cost_center_name AS cost_center_name,
			IFNULL(gl.banque, 0) + IFNULL(gl.realloc, 0) AS banque,
			IFNULL(gl.caisse, 0) AS caisse,
			IFNULL(gl.ar, 0) AS ar,
			IFNULL(gl.passif, 0) AS passif,
			IFNULL(gl.banque, 0) + IFNULL(gl.realloc, 0) + IFNULL(gl.caisse, 0) - IFNULL(gl.passif, 0) AS disponible,
			IFNULL(gl.banque, 0) + IFNULL(gl.realloc, 0) + IFNULL(gl.caisse, 0) - IFNULL(gl.passif, 0) + IFNULL(gl.ar, 0) AS disponible_ar
		FROM `tabCost Center` cc
		LEFT JOIN (
			SELECT
				gle.cost_center AS cost_center,
				SUM(
					CASE
						WHEN acc.account_type IN %(banque_types)s
						THEN gle.debit - gle.credit
						ELSE 0
					END
				) AS banque,
				SUM(
					CASE
						WHEN acc.account_type IN %(realloc_types)s
						THEN gle.debit - gle.credit
						ELSE 0
					END
				) AS realloc,
				SUM(
					CASE
						WHEN acc.account_type IN %(caisse_types)s
						THEN gle.debit - gle.credit
						ELSE 0
					END
				) AS caisse,
				SUM(
					CASE
						WHEN acc.account_type IN %(receivable_types)s
						THEN gle.debit - gle.credit
						ELSE 0
					END
				) AS ar,
				SUM(
					CASE
						WHEN acc.root_type = %(passif_root_type)s
						THEN GREATEST(gle.credit - gle.debit, 0)
						ELSE 0
					END
				) AS passif
			FROM `tabGL Entry` gle
			INNER JOIN `tabAccount` acc ON acc.name = gle.account
			WHERE gle.company = %(company)s
				AND gle.posting_date <= %(to_date)s
				AND IFNULL(gle.is_cancelled, 0) = 0
				AND IFNULL(gle.cost_center, '') != ''
				AND acc.is_group = 0
				AND (
					acc.account_type IN %(banque_types)s
					OR acc.account_type IN %(realloc_types)s
					OR acc.account_type IN %(caisse_types)s
					OR acc.account_type IN %(receivable_types)s
					OR acc.root_type = %(passif_root_type)s
				)
			GROUP BY gle.cost_center
		) gl ON gl.cost_center = cc.name
		WHERE cc.company = %(company)s
			AND cc.is_group = 0
			AND cc.disabled = 0
			AND cc.name IN %(unit_names)s
		""",
		params,
		as_dict=True,
	)

	order = {unit["name"]: index for index, unit in enumerate(units)}
	return sorted(rows, key=lambda row: (order.get(row.cost_center, len(units)), row.cost_center_name))
