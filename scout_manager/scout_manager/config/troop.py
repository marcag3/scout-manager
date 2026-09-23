"""Troop-wide defaults shared by reports, widgets, and APIs."""

ACCOUNT_NUMBERS = {
	"banque": "1011",
	"caisse": "1012",
	"realloc": "1030",
	"ar": "1021",
}

PASSIF_ACCOUNT_NUMBERS = ["2010", "100301464RT0001", "1006141893TQ0001"]

ARGENT_DISPONIBLE_ACCOUNTS = list(ACCOUNT_NUMBERS.values()) + PASSIF_ACCOUNT_NUMBERS
