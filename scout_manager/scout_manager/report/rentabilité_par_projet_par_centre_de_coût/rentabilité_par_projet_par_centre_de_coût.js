frappe.provide("frappe.query_reports");

const REPORT_NAME = "Rentabilité par projet par centre de coût";
const DOCTYPE_FISCAL_YEAR = "Fiscal Year";
const REPORT_GENERAL_LEDGER = "General Ledger";
const DRILL_SUFFIX_COLUMNS = new Set(["autres", "total"]);
const DRILLDOWN_CLASS = "rentabilite-drilldown";

frappe.query_reports[REPORT_NAME] = {
	filters: [
		{
			fieldname: "company",
			label: __("Compagnie"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1,
		},
		{
			fieldname: "fiscal_year",
			label: __("Année financière"),
			fieldtype: "Link",
			options: "Fiscal Year",
			default: (frappe.boot.current_fiscal_year || [])[0],
			reqd: 1,
		},
	],

	onload(report) {
		report.fy_dates = null;

		const refresh_fy_dates = () => {
			const fiscal_year = report.get_filter_value("fiscal_year");
			if (!fiscal_year) {
				report.fy_dates = null;
				return;
			}
			frappe.db.get_value(
				DOCTYPE_FISCAL_YEAR,
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

		this.bind_drilldown_clicks(report);
	},

	bind_drilldown_clicks(report) {
		if (report._rentabilite_drilldown_bound) {
			return;
		}
		report._rentabilite_drilldown_bound = true;

		report.page.main.on("click", `a.${DRILLDOWN_CLASS}`, (e) => {
			e.preventDefault();
			e.stopPropagation();
			const link = e.currentTarget;
			frappe.query_reports[REPORT_NAME].open_general_ledger(
				link.dataset.project,
				link.dataset.fieldname,
				link.dataset.costCenter || null
			);
		});
	},

	open_general_ledger(project, fieldname, cost_center = null) {
		const report = frappe.query_report;
		const company = report.get_filter_value("company");
		const fiscal_year = report.get_filter_value("fiscal_year");

		if (!company || !fiscal_year || !project) {
			frappe.msgprint(
				__("Veuillez sélectionner la compagnie et l'année financière.")
			);
			return;
		}

		if (!cost_center) {
			const column = report.columns?.find((col) => col.fieldname === fieldname);
			cost_center = column?.cost_center || null;
		}

		const open_with_dates = (from_date, to_date) => {
			const route_options = {
				company,
				from_date,
				to_date,
				project,
			};

			if (cost_center) {
				route_options.cost_center = cost_center;
			}

			frappe.route_options = route_options;
			frappe.set_route("query-report", REPORT_GENERAL_LEDGER);
		};

		if (report.fy_dates?.year_start_date) {
			open_with_dates(
				report.fy_dates.year_start_date,
				report.fy_dates.year_end_date
			);
			return;
		}

		frappe.db.get_value(
			DOCTYPE_FISCAL_YEAR,
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

		const is_drillable =
			column.cost_center || DRILL_SUFFIX_COLUMNS.has(column.fieldname);
		if (!is_drillable) {
			return value;
		}

		const amount = flt(data[column.fieldname]);
		if (!amount || Math.abs(amount) <= 0.005) {
			return value;
		}

		const attrs = [
			`class="${DRILLDOWN_CLASS} text-primary"`,
			`data-project="${frappe.utils.escape_html(data.project)}"`,
			`data-fieldname="${frappe.utils.escape_html(column.fieldname)}"`,
		];
		if (column.cost_center) {
			attrs.push(
				`data-cost-center="${frappe.utils.escape_html(column.cost_center)}"`
			);
		}

		return `<a href="#" ${attrs.join(" ")} style="cursor:pointer;display:block;text-decoration:none;color:var(--primary);">${value}</a>`;
	},
};
