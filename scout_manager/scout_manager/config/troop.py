"""Account classification for Argent disponible and related treasurer reports.

Balances are resolved from ERPNext Account metadata (account_type, root_type),
not hardcoded account numbers. See docs/design/argent-disponible.md for setup.
"""

# Leaf accounts only (is_group = 0) matching these types are included.

BANQUE_ACCOUNT_TYPES = ("Bank",)
REALLOC_ACCOUNT_TYPES = ("Temporary",)
CAISSE_ACCOUNT_TYPES = ("Cash",)
RECEIVABLE_ACCOUNT_TYPES = ("Receivable",)
PASSIF_ROOT_TYPE = "Liability"
