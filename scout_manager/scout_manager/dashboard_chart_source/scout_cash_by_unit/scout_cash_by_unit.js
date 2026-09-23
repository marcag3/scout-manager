frappe.provide("frappe.dashboards.chart_sources");

frappe.dashboards.chart_sources["Scout Cash by Unit"] = {
	method: "scout_manager.scout_manager.dashboard_chart_source.scout_cash_by_unit.scout_cash_by_unit.get",
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
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
	],
};
