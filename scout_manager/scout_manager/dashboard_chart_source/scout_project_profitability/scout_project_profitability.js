frappe.provide("frappe.dashboards.chart_sources");

frappe.dashboards.chart_sources["Scout Project Profitability"] = {
	method: "scout_manager.scout_manager.dashboard_chart_source.scout_project_profitability.scout_project_profitability.get",
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1,
		},
		{
			fieldname: "fiscal_year",
			label: __("Fiscal Year"),
			fieldtype: "Link",
			options: "Fiscal Year",
			default: (frappe.boot.current_fiscal_year || [])[0],
		},
	],
};
