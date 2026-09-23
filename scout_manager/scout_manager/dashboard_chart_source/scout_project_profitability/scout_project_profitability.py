import erpnext
import frappe
from erpnext.accounts.utils import get_fiscal_year
from frappe.desk.query_report import run
from frappe.utils import today
from frappe.utils.dashboard import cache_source

from scout_manager.scout_manager.config.names import REPORT_RENTABILITE_CC
# Projects with the largest profit or deficit; more bars make the labels unreadable.
MAX_PROJECTS = 10


@frappe.whitelist()
@cache_source
def get(
	chart_name=None,
	chart=None,
	no_cache=None,
	filters=None,
	from_date=None,
	to_date=None,
	timespan=None,
	time_interval=None,
	heatmap_year=None,
):
	filters = frappe.parse_json(filters) or {}
	company = filters.get("company") or erpnext.get_default_company()
	fiscal_year = filters.get("fiscal_year") or get_fiscal_year(today(), company=company)[0]

	data = run(
		REPORT_RENTABILITE_CC,
		filters={"company": company, "fiscal_year": fiscal_year},
		ignore_prepared_report=1,
	)
	rows = [row for row in (data.get("result") or []) if isinstance(row, dict) and row.get("project")]
	rows = sorted(rows, key=lambda row: abs(row.get("total") or 0), reverse=True)[:MAX_PROJECTS]
	rows.sort(key=lambda row: row.get("total") or 0, reverse=True)

	return {
		"labels": [row.get("project_name") or row["project"] for row in rows],
		"datasets": [{"name": "Résultat net", "values": [row.get("total") or 0 for row in rows]}],
	}
