frappe.provide("frappe.query_reports");

const REPORT_NAME = "Rentabilité par projet par centre de coût";

const COST_CENTER_BY_COLUMN = {
	clan: "Clan - 188",
	colonie: "Colonie - 188",
	groupe: "Groupe - 188",
	louvette: "Louvette - 188",
	meute: "Meute - 188",
	troupe: "Troupe - 188",
};

const DRILL_COLUMNS = new Set([
	...Object.keys(COST_CENTER_BY_COLUMN),
	"autres",
	"total",
]);

frappe.query_reports[REPORT_NAME] = {
	onload(report) {
		report.fy_dates = null;

		const refresh_fy_dates = () => {
			const fiscal_year = report.get_filter_value("fiscal_year");
			if (!fiscal_year) {
				report.fy_dates = null;
				return;
			}
			frappe.db.get_value(
				"Fiscal Year",
				fiscal_year,
				["year_start_date", "year_end_date"],
				(r) => {
					report.fy_dates = r;
				}
			);
		};

		refresh_fy_dates();
		if (report.page.fields_dict.fiscal_year) {
			report.page.fields_dict.fiscal_year.$input.on("change", refresh_fy_dates);
		}
	},

	open_general_ledger(project, column_fieldname) {
		const report = frappe.query_report;
		const company = report.get_filter_value("company");
		const fiscal_year = report.get_filter_value("fiscal_year");

		if (!company || !fiscal_year || !project) {
			frappe.msgprint(
				__("Veuillez sélectionner la compagnie et l'année financière.")
			);
			return;
		}

		const open_with_dates = (from_date, to_date) => {
			const route_options = {
				company,
				from_date,
				to_date,
				project,
			};

			const cost_center = COST_CENTER_BY_COLUMN[column_fieldname];
			if (cost_center) {
				route_options.cost_center = cost_center;
			}

			frappe.route_options = route_options;
			frappe.set_route("query-report", "General Ledger");
		};

		if (report.fy_dates?.year_start_date) {
			open_with_dates(
				report.fy_dates.year_start_date,
				report.fy_dates.year_end_date
			);
			return;
		}

		frappe.db.get_value(
			"Fiscal Year",
			fiscal_year,
			["year_start_date", "year_end_date"],
			(r) => {
				report.fy_dates = r;
				open_with_dates(r.year_start_date, r.year_end_date);
			}
		);
	},

	formatter(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (!data || !data.project || data.is_total_row || row.is_total_row) {
			return value;
		}

		if (!DRILL_COLUMNS.has(column.fieldname)) {
			return value;
		}

		const amount = flt(data[column.fieldname]);
		if (!amount || Math.abs(amount) <= 0.005) {
			return value;
		}

		const project = frappe.utils.escape_html(data.project);
		const fieldname = frappe.utils.escape_html(column.fieldname);

		return `<span class="text-primary" style="cursor: pointer;" onclick="frappe.query_reports['${REPORT_NAME}'].open_general_ledger('${project}', '${fieldname}');">${value}</span>`;
	},
};
