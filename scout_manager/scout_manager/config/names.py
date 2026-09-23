"""Shared identifiers for reports, widgets, and custom fields."""

REPORT_ARGENT_DISPONIBLE = "Argent disponible par unité"
REPORT_BALANCE_SHEET_CC = "Balance sheet by cost center"
REPORT_RENTABILITE_CC = "Rentabilité par projet par centre de coût"

ARGENT_DISPONIBLE_BLOCK = "Argent disponible"
ARGENT_DISPONIBLE_CSS = "argent_disponible_widget.css"
ARGENT_DISPONIBLE_JS = "argent_disponible_widget.js"

COST_CENTER_DISPLAY_ORDER_FIELD = "custom_ordre_affichage"
CUSTOMER_GROUP_COST_CENTER_FIELD = "custom_centre_de_cout"
CUSTOMER_BIRTHDATE_FIELD = "custom_date_de_naissance"
CUSTOMER_AGE_FIELD = "custom_age"
CONTACT_BIRTHDATE_FIELD = "custom_date_de_naissance"
INVOICE_SENT_FIELD = "custom_is_sent"
PAYMENT_SENT_FIELD = "custom_is_sent"
COMPANY_FACEBOOK_FIELD = "custom_facebook"

TROOP_CUSTOM_FIELDS = {
	"Customer": (CUSTOMER_BIRTHDATE_FIELD, CUSTOMER_AGE_FIELD),
	"Customer Group": (CUSTOMER_GROUP_COST_CENTER_FIELD,),
	"Contact": (CONTACT_BIRTHDATE_FIELD,),
	"Sales Invoice": (INVOICE_SENT_FIELD,),
	"Payment Entry": (PAYMENT_SENT_FIELD,),
	"Company": (COMPANY_FACEBOOK_FIELD,),
	"Cost Center": (COST_CENTER_DISPLAY_ORDER_FIELD,),
}

TROOP_PROPERTY_SETTER_DOCTYPES = ("Customer", "Customer Group")

SERVER_SCRIPT_COTISATION = "Création facture de cotisation"
SERVER_SCRIPT_COST_CENTER = "modifier les cost center"
SERVER_SCRIPT_LINK_CONTACTS = "lier les contacts au client"

TROOP_SERVER_SCRIPTS = (
	SERVER_SCRIPT_COTISATION,
	SERVER_SCRIPT_COST_CENTER,
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

RETIRED_CLIENT_SCRIPTS = ("set cost center payment", "set unit", "purchase invoice header dimensions")
RETIRED_CUSTOM_FIELDS = ("Customer Group-custom_dimension",)
