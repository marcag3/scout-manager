frappe.provide("frappe.dashboards.chart_sources");

frappe.dashboards.chart_sources["Scout Cash Flow"] = {
	method: "scout_manager.scout_manager.dashboard_chart_source.scout_cash_flow.scout_cash_flow.get",
	filters: [
		{
			fieldname: "company",
			label: __("Compagnie"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1,
		},
	],
};
