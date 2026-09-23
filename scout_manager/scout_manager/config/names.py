"""Shared identifiers for reports, widgets, and custom fields."""

APP_MODULE = "Scout Manager"
APP_NAME = "scout_manager"

WORKSPACE_SCOUT_TREASURER = "Scout Treasurer"
ROLE_SCOUT_TREASURER = "Scout Treasurer"

REPORT_ARGENT_DISPONIBLE = "Available Funds per Unit"
REPORT_BALANCE_SHEET_CC = "Balance sheet by cost center"
REPORT_RENTABILITE_CC = "Project Profitability by Cost Center"

ARGENT_DISPONIBLE_BLOCK = "Available Funds"
# Workspace content key; Frappe matches this to Workspace Custom Block.label via __().
ARGENT_DISPONIBLE_BLOCK_LABEL = "Argent disponible"
ARGENT_DISPONIBLE_CSS = "argent_disponible_widget.css"
ARGENT_DISPONIBLE_JS = "argent_disponible_widget.js"

COST_CENTER_DISPLAY_ORDER_FIELD = "custom_ordre_affichage"
GROUP_COST_CENTER_FIELD = "custom_centre_de_cout"
CUSTOMER_BIRTHDATE_FIELD = "custom_date_de_naissance"
CUSTOMER_AGE_FIELD = "custom_age"
INVOICE_SENT_FIELD = "custom_is_sent"
PAYMENT_SENT_FIELD = "custom_is_sent"
COMPANY_FACEBOOK_FIELD = "custom_facebook"

TROOP_CUSTOM_FIELDS = {
	"Customer": (CUSTOMER_BIRTHDATE_FIELD, CUSTOMER_AGE_FIELD),
	"Customer Group": (GROUP_COST_CENTER_FIELD,),
	"Supplier Group": (GROUP_COST_CENTER_FIELD,),
	"Sales Invoice": (INVOICE_SENT_FIELD,),
	"Payment Entry": (PAYMENT_SENT_FIELD,),
	"Company": (COMPANY_FACEBOOK_FIELD,),
	"Cost Center": (COST_CENTER_DISPLAY_ORDER_FIELD,),
}

TROOP_PROPERTY_SETTER_DOCTYPES = ("Customer", "Customer Group", "Supplier Group")

SERVER_SCRIPT_COTISATION = "Création facture de cotisation"
SERVER_SCRIPT_LINK_CONTACTS = "lier les contacts au client"

TROOP_SERVER_SCRIPTS = (
	SERVER_SCRIPT_COTISATION,
	SERVER_SCRIPT_LINK_CONTACTS,
)

TROOP_PRINT_FORMATS = (
	"Facture perso",
	"Facture html",
	"Facture with builder",
	"Reçu",
	"État de compte",
)

TROOP_LETTER_HEADS = ("188", "AABP")
DEFAULT_LETTER_HEAD = "188"

RETIRED_CLIENT_SCRIPTS = (
	"Calcul age",
	"email payment entry",
	"expanse claim item cost center and project",
	"set cost center",
	"set cost center payment",
	"set unit",
	"purchase invoice header dimensions",
)

RETIRED_CUSTOM_FIELDS = (
	"Customer Group-custom_dimension",
	"Contact-custom_date_de_naissance",
)

# Site cleanup: drop site-built copies before fixture sync.
APP_REPORTS = (
	REPORT_ARGENT_DISPONIBLE,
	REPORT_BALANCE_SHEET_CC,
	REPORT_RENTABILITE_CC,
)

APP_WORKSPACES = (WORKSPACE_SCOUT_TREASURER,)

APP_DASHBOARD_CHARTS = (
	REPORT_ARGENT_DISPONIBLE,
	"Flux de trésorerie (12 mois)",
	"Pertes et profits (mensuel)",
	"Rentabilité par projet",
)

APP_DASHBOARD_CHART_SOURCES = (
	"Scout Cash by Unit",
	"Scout Cash Flow",
	"Scout Project Profitability",
)

APP_NUMBER_CARDS = (
	"Factures clients en retard",
	"Factures fournisseurs à payer",
	"Solde banque et caisse",
	"Total des factures fournisseurs",
	"Total décaissé",
	"Total encaissé",
	"Total facturé",
	"Transactions bancaires à réconcilier",
)

# French names before English rename (workspace links, patches).
RENAMED_LINK_TARGETS = {
	"Argent disponible par unité": REPORT_ARGENT_DISPONIBLE,
	"Rentabilité par projet par centre de coût": REPORT_RENTABILITE_CC,
	"Argent disponible": ARGENT_DISPONIBLE_BLOCK,
}

FRENCH_ASSET_RENAMES = (
	("Report", "Argent disponible par unité", REPORT_ARGENT_DISPONIBLE),
	("Report", "Rentabilité par projet par centre de coût", REPORT_RENTABILITE_CC),
	("Custom HTML Block", "Argent disponible", ARGENT_DISPONIBLE_BLOCK),
	("Dashboard Chart", "Argent disponible par unité", REPORT_ARGENT_DISPONIBLE),
)
