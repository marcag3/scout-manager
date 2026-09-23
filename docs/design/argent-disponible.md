# Argent disponible — account tagging

The **Argent disponible par unité** report and workspace widget compute available funds per cost center (scout unit). Balances come from GL entries filtered by **Account Type** and **Root Type**, not hardcoded account numbers.

Company scope uses ERPNext defaults (`erpnext.get_default_company()` / user default Company filter).

## Formulas

Per cost center:

| Metric | Formula |
|--------|---------|
| **Banque** (displayed) | Bank balances + Temporary (realloc) balances |
| **Caisse** | Cash balances |
| **À recevoir** | Receivable balances |
| **Passif** | Credit balances on Liability accounts |
| **Disponible** | Banque + Caisse − Passif |
| **Disponible incl. créances** | Disponible + À recevoir |

Asset-side amounts use `debit − credit`. Passif sums **net credit balances per liability account** (`GREATEST(SUM(credit − debit), 0)` grouped by account), so only amounts still **owed** reduce disponible. Paid invoices no longer count, and debit balances on tax or payable accounts contribute zero.

## How to tag accounts

Open **Accounting → Chart of Accounts**, edit each leaf account, and set **Account Type** (and ensure **Root Type** is correct).

| Report column | ERPNext field | Value | Notes |
|---------------|---------------|-------|-------|
| Banque | Account Type | **Bank** | All bank accounts for the company are included. Link the account to a **Bank Account** for reconciliation. |
| Realloc (rolled into Banque) | Account Type | **Temporary** | Inter-unit transfer / clearing account. **Do not** use Bank — internal journal entries would appear unreconciled in bank reconciliation. |
| Caisse | Account Type | **Cash** | Petty cash and unit cash boxes. |
| À recevoir | Account Type | **Receivable** | Customer / scout fee receivables. |
| Passif | Root Type | **Liability** | Payables, tax remittances, deposits held, etc. Any liability with a credit balance counts. |

Only **leaf** accounts (`Is Group` unchecked) are included.

### Realloc account (Temporary)

Use a single clearing account (e.g. historically account `1030`) for journal entries that move balances between units without moving money at the bank:

1. Create or identify the clearing account in the chart of accounts.
2. Set **Account Type** = `Temporary`.
3. Keep **Root Type** = `Asset` (typical for a clearing account).
4. Post inter-unit transfers as journal entries debiting/crediting this account with the appropriate **Cost Center** on each line.

The report adds Temporary balances into the **Banque** column (same as the previous hardcoded `1011 + 1030` behaviour).

### Passif (Liability)

All liability accounts with a net credit balance per cost center reduce disponible. This replaces a hand-picked list of account numbers (e.g. `2010` + GST/QST remittance accounts).

Typical accounts that should have **Root Type** = `Liability`:

- Supplier payables (`Account Type`: Payable)
- Sales tax owed (`Account Type`: Tax)
- Member deposits or obligations held (`Account Type`: Payable, Current Liability, or Liability)

Accounts with a debit balance (e.g. input tax credits) do not reduce disponible because of the credit-only filter.

## Configuration reference

Constants live in `scout_manager/scout_manager/config/troop.py`:

```python
BANQUE_ACCOUNT_TYPES = ("Bank",)
REALLOC_ACCOUNT_TYPES = ("Temporary",)
CAISSE_ACCOUNT_TYPES = ("Cash",)
RECEIVABLE_ACCOUNT_TYPES = ("Receivable",)
PASSIF_ROOT_TYPE = "Liability"
```

Change these only if your chart uses non-standard typing; prefer fixing account tags in the COA first.

## Migration from hardcoded account numbers

Previously the report matched specific account numbers (`1011`, `1012`, `1030`, `1021`, passif list). After this refactor:

1. Tag existing accounts as in the table above (especially the realloc account → **Temporary**).
2. Run **Argent disponible par unité** and spot-check one unit against the old widget totals.
3. Small differences are expected if receivable or liability accounts were previously excluded.

## Related assets

- Query report: `Argent disponible par unité`
- API: `scout_manager.scout_manager.api.argent_disponible.get_argent_disponible_by_unit`
- Workspace widget: Custom HTML Block `Argent disponible`
