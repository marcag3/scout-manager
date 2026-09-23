"""Troop-wide defaults shared by reports, widgets, and APIs."""

DEFAULT_COMPANY = "188e Montréal-Nord"
LETTER_HEAD = "188"

# Short names used for workspace widget ordering.
UNIT_ORDER = ["Groupe", "Colonie", "Louvette", "Meute", "Troupe", "Clan"]

# Full Cost Center names used in SQL pivot reports.
COST_CENTERS = [f"{unit} - {LETTER_HEAD}" for unit in UNIT_ORDER]

ACCOUNT_NUMBERS = {
	"banque": "1011",
	"caisse": "1012",
	"realloc": "1030",
	"ar": "1021",
}

PASSIF_ACCOUNT_NUMBERS = ["2010", "100301464RT0001", "1006141893TQ0001"]

ARGENT_DISPONIBLE_ACCOUNTS = list(ACCOUNT_NUMBERS.values()) + PASSIF_ACCOUNT_NUMBERS
