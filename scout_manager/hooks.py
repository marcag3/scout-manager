app_name = "scout_manager"
app_title = "Scout Manager"
app_publisher = "Troop 188e"
app_description = "Custom ERPNext app for scout troop management"
app_email = "admin@example.com"
app_license = "mit"

from scout_manager.scout_manager.config.names import ARGENT_DISPONIBLE_BLOCK

fixtures = [
	{
		"dt": "Custom HTML Block",
		"filters": [["name", "=", ARGENT_DISPONIBLE_BLOCK]],
	},
	{
		"dt": "Client Script",
		"filters": [["module", "=", "Scout Manager"], ["enabled", "=", 1]],
	},
	{
		"dt": "Custom Field",
		"filters": [["fieldname", "=", "custom_ordre_affichage"], ["dt", "=", "Cost Center"]],
	},
]

after_migrate = [
	"scout_manager.scout_manager.utils.widget.cleanup_retired_client_scripts",
	"scout_manager.scout_manager.utils.widget.sync_argent_disponible_block",
	"scout_manager.scout_manager.utils.cost_centers.seed_cost_center_display_order",
	"scout_manager.scout_manager.setup.treasurer.setup_scout_treasurer",
]

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "scout_manager",
# 		"logo": "/assets/scout_manager/logo.png",
# 		"title": "Scout Manager",
# 		"route": "/scout_manager",
# 		"has_permission": "scout_manager.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/scout_manager/css/scout_manager.css"
# app_include_js = "/assets/scout_manager/js/scout_manager.js"

# include js, css files in header of web template
# web_include_css = "/assets/scout_manager/css/scout_manager.css"
# web_include_js = "/assets/scout_manager/js/scout_manager.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "scout_manager/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "scout_manager/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "scout_manager.utils.jinja_methods",
# 	"filters": "scout_manager.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "scout_manager.install.before_install"
# after_install = "scout_manager.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "scout_manager.uninstall.before_uninstall"
# after_uninstall = "scout_manager.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "scout_manager.utils.before_app_install"
# after_app_install = "scout_manager.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "scout_manager.utils.before_app_uninstall"
# after_app_uninstall = "scout_manager.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "scout_manager.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "scout_manager.notifications.get_notification_config"

# Awesome Bar
# -----------
# Extra search results: list of dicts with label, description, route, index.
# route: ["List", "ToDo"], "/desk/docs/some/page", or "https://example.com"
# awesomebar_search = ["scout_manager.search.awesomebar_results"]

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Payment Entry": {
		"before_validate": "scout_manager.scout_manager.accounting.payment_entry.inherit_dimensions_from_references",
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"scout_manager.tasks.all"
# 	],
# 	"daily": [
# 		"scout_manager.tasks.daily"
# 	],
# 	"hourly": [
# 		"scout_manager.tasks.hourly"
# 	],
# 	"weekly": [
# 		"scout_manager.tasks.weekly"
# 	],
# 	"monthly": [
# 		"scout_manager.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "scout_manager.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "scout_manager.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "scout_manager.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "scout_manager.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["scout_manager.utils.before_request"]
# after_request = ["scout_manager.utils.after_request"]

# Job Events
# ----------
# before_job = ["scout_manager.utils.before_job"]
# after_job = ["scout_manager.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"scout_manager.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

