# Scout Manager — Bank Reconciliation Design

**Status:** Draft  
**Author:** Troop 188e Montréal-Nord  
**Last updated:** 2026-09-21

---

## 1. Executive Summary

Scout Manager is a custom ERPNext app for managing a scout troop's membership and finances. The invoicing workflow is already satisfactory: scouts are `Customer` records, parents are `Contact` records, and one invoice is issued per scout for annual registration, camp fees, and other charges.

The primary pain point is **bank reconciliation**, specifically importing Desjardins **CSV Accentué** statement files and matching bank transactions to payments with minimal manual steps. The troop previously used **Firefly III**, where a one-click import (community JSON config for Desjardins) worked reliably; **ERPNext has no equivalent** — stock Bank Statement Import expects manual column mapping and the reconciliation UX is far heavier.

The proposed solution centers on **invoice allocation as the primary treasurer action** on a **dedicated Scout Bank Reconciliation page** — party, dimensions, and Payment Entry creation are inferred from confirmed allocations, with Interac description templates and aliases narrowing suggestions. **Party Alias rows are auto-learned** each time a reconciliation is confirmed, so repeat Interac lines require less work over time.

Phase 1 targets the same import ease as Firefly III: a **config-driven CSV importer** that accepts the **community JSON bank-import configs** published for Firefly III (e.g. [ca/desjardins/account.json](https://github.com/firefly-iii/import-configurations/blob/main/ca/desjardins/account.json)) **without modification**. Upload the raw CSV Accentué file, zero column mapping, Bank Transactions created.

---



## 2. Domain Model (Confirmed)


| Concept                 | ERPNext entity                                         | Notes                                                   |
| ----------------------- | ------------------------------------------------------ | ------------------------------------------------------- |
| Scout member            | `Customer`                                             | One customer per scout                                  |
| Parent / guardian       | `Contact`                                              | Linked to scout customer                                |
| Annual registration fee | `Sales Invoice`                                        | One invoice per scout                                   |
| Camp fee                | `Sales Invoice`                                        | One invoice per scout per camp                          |
| Other fees              | `Sales Invoice`                                        | Optional, same pattern                                  |
| Payment                 | `Payment Entry`                                        | Parent pays; invoice is per scout                       |
| Expense reimbursement   | `Purchase Invoice` + `Payment Entry`                   | Parent as `Supplier` when reimbursed for troop expenses |
| Treasury                | Standard accounting (`Account`, `Journal Entry`, etc.) | Works as-is                                             |
| Unit / section tracking | `Cost Center`, `Project`                               | Already used in reports                                 |


**Dual-role parents:** Some contacts act as both payer (linked to scout `Customer` via fees) and payee (as `Supplier` for expense reimbursements). The same person can appear in Interac descriptions in both directions — direction and invoice type determine the role, not the name alone.

### Existing customizations (working well — migrate to app)

Two troop-specific reporting assets currently live **only in the ERPNext site database** (created via the UI). They work well and must not be disrupted by reconciliation work, but they should be **version-controlled in** `scout_manager` before bank-reconciliation phases ship.


| Asset                                         | ERPNext type      | Site record         | Purpose                                                                                             |
| --------------------------------------------- | ----------------- | ------------------- | --------------------------------------------------------------------------------------------------- |
| **Argent disponible par unité**               | Custom HTML Block | `Argent disponible` | Live dashboard widget: available cash per cost center (unit), derived from Trial Balance            |
| **Rentabilité par projet par centre de coût** | Query Report      | same name           | P&L-style matrix: project rows × cost-center columns (Clan, Colonie, Groupe, …) for the fiscal year |


**Widget (**`Argent disponible`**):** Client-side block embedded on a workspace. For each unit cost center (Groupe, Colonie, Meute, Troupe, Clan), runs stock **Trial Balance** and computes:

- `disponible` = Banque (1011 + 1030 realloc) + Caisse (1012) − Passif (2010 + tax accounts)
- `disponible_ar` = `disponible` + créances clients (1021) when non-zero

Hardcoded today: company `188e Montréal-Nord`, account numbers, unit display order. Role: **All**.

**Report (**`Rentabilité par projet par centre de coût`**):** SQL Query Report on `GL Entry` with `company` + `fiscal_year` filters. Pivots income/expense net (`credit − debit`) into columns per cost center (`Clan - 188`, `Colonie - 188`, `Groupe - 188`, `Louvette - 188`, `Meute - 188`, `Troupe - 188`, `Autres`, `Total`). Client JS adds **drill-down** from any amount cell → **General Ledger** filtered by project, cost center, and fiscal-year dates. Roles: Accounts User, Accounts Manager, Auditor, Projects User. Letter head: `188`.

See **§8.6** for migration into the app and **Phase 0** in §9.

---



## 3. Problem Statement

Bank reconciliation in stock ERPNext requires too many manual steps, redundant data entry, and CSV preprocessing before import. For a volunteer treasurer reconciling Desjardins transactions against scout invoices, the process is error-prone and slow.

**Prior art:** In Firefly III, Desjardins **Relevés → CSV Accentué (Microsoft Excel…)** imports worked out of the box via the [community import configuration](https://github.com/firefly-iii/import-configurations/tree/main/ca/desjardins) — upload file, done. That workflow is the benchmark for Phase 1.

### Core requirements

1. Import Desjardins **CSV Accentué** **as exported from Relevés** — no manual column mapping or file editing (same as Firefly III).
2. Detect **duplicate transactions** on import (overlapping date ranges, re-imports).
3. **Simplify reconciliation** — fewer screens, fewer defaults to override, less duplicated field entry.



### Non-goals (for now)

- Replacing ERPNext's accounting engine or Payment Entry document model.
- Building a custom column-mapping UI — bank format is defined by a JSON import config; new banks are new config files, not new parser code.
- Changing the one-invoice-per-scout billing model.
- Patching or extending ERPNext's stock **Bank Reconciliation Tool** — reconciliation UX lives on a dedicated Scout page instead.

---



## 4. Current Workflow (As-Is)

The treasurer currently follows this 15-step process for each bank transaction:


| Step | Action                                                                | Pain                                                                                                                         |
| ---- | --------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| 1    | Open Bank Reconciliation Tool                                         | Entry point is fine                                                                                                          |
| 2    | Change default **From Date** to include all unreconciled transactions | From Date hides older unreconciled items; no known use case for leaving past transactions unreconciled when a To Date is set |
| 3    | Fetch closing balance from Desjardins app                             | CSV already contains closing balance; minor hassle                                                                           |
| 4    | Click to match one transaction                                        | One-at-a-time flow                                                                                                           |
| 5    | Choose "Create Voucher"                                               | —                                                                                                                            |
| 6    | Choose party type: Customer or Supplier                               | Inferrable ~99% of the time from transaction direction and description                                                       |
| 7    | Fill quick entry form                                                 | Incomplete — missing required fields                                                                                         |
| 8    | Open full Payment Entry form                                          | Extra navigation                                                                                                             |
| 9    | Fetch unreconciled invoices                                           | —                                                                                                                            |
| 10   | Change default **From Date** on invoice list                          | Same From Date problem; hides older open invoices                                                                            |
| 11   | Select invoice allocation                                             | Expected step                                                                                                                |
| 12   | Enter Project and Cost Center                                         | Should inherit from selected invoices — currently duplicated work                                                            |
| 13   | Save and submit Payment Entry                                         | —                                                                                                                            |
| 14   | Return to Bank Reconciliation Tool                                    | Context switch                                                                                                               |
| 15   | Reconcile transaction with the payment                                | Should happen automatically after step 13                                                                                    |


**Net effect:** Reconciling a single deposit against one or more scout invoices can require 15 interactions across three UI surfaces, with the same date-filter and dimension-entry problems repeated every time.

---



## 5. Goals


| #   | Goal                           | Success criteria                                                                                                                  |
| --- | ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------- |
| G1  | Zero-touch bank import         | Upload raw CSV + JSON import config → Bank Transactions created without manual column mapping (reuse community configs as-is)     |
| G2  | Duplicate-safe imports         | Re-importing overlapping periods flags or skips duplicates; no double Bank Transactions                                           |
| G3  | Show all unreconciled work     | Default filters surface all unreconciled transactions up to To Date; no mandatory From Date                                       |
| G4  | Allocation-centric reconcile   | Treasurer confirms suggested invoice allocation → one or more Payment Entries submitted → Bank Transaction reconciled             |
| G5  | Smart allocation suggestions   | Open invoices pre-selected from amount match, Interac description, and alias lookup; party and dimensions inferred from selection |
| G6  | Closing balance from file      | Closing balance auto-populated from CSV metadata when present                                                                     |
| G7  | Dedicated reconciliation page  | Stock Bank Reconciliation Tool replaced as treasurer entry point; no client-script patches to ERPNext core UI                     |
| G8  | Learn from confirmed decisions | Each successful Confirm auto-creates or reinforces Party Alias rows from Interac descriptions + chosen party                      |


---



## 6. Proposed Workflow (To-Be)



### 6.1 Import

```
Relevés → CSV Accentué (unmodified; multiple months may be concatenated)
        │
        ▼
JSON import config (e.g. ca/desjardins/account.json — roles, date format, delimiter)
        │
        ▼
Config-driven CSV importer (scout_manager.bank_reconciliation.csv_importer)
        │
        ├── Apply roles[] → date, description, debit, credit, account-number, …
        ├── Extract metadata (account name/number per row, statement period, balances)
        ├── Normalize rows → Bank Transaction candidates (conversion, date parsing)
        ├── Duplicate check → skip / flag / merge (honor ignore_duplicate_lines when set)
        └── Bulk create submitted Bank Transactions
```



### 6.2 Reconcile — allocation-first (primary path)

Reconciliation collapses to **invoice allocation + manual validation**. Party type, party, project, cost center, and Payment Entry structure are **inferred from the selected invoices**, not entered separately.

The open invoice list (Sales and Purchase) is small enough to load globally; suggestions are ranked, not hidden behind filters.

```
Scout Bank Reconciliation (custom page)
        │
        ▼
Select unreconciled bank line
        │
        ▼
Allocation panel (single screen)
        │
        ├── Parse description → narrow invoice list (Interac patterns + Party Alias)
        ├── Suggest allocation (priority order below)
        ├── Treasurer confirms or adjusts checkboxes / amounts
        │
        ▼
"Confirm" action
        │
        ├── Validate: allocated total vs bank amount
        ├── Group allocations by party (+ party_type from invoice doc type)
        ├── For each group: create + submit Payment Entry (dimensions from invoices)
        ├── Link all Payment Entries to Bank Transaction
        └── Mark Bank Transaction Reconciled
```



#### Auto-suggestion priority


| Priority | Condition                                                   | Suggested allocation                                     |
| -------- | ----------------------------------------------------------- | -------------------------------------------------------- |
| 1        | One open invoice amount = bank amount exactly               | Pre-select that invoice                                  |
| 2        | Sum of one customer's open Sales Invoices = deposit exactly | Pre-select all for that customer                         |
| 3        | Interac / alias resolves party; amount matches subset       | Pre-select matching invoices (oldest first up to amount) |
| 4        | Interac / alias resolves party; partial or ambiguous amount | Show that party's open invoices only; treasurer selects  |
| 5        | No confident match                                          | Show full short open-invoice list; nothing pre-selected  |


Deposits suggest against `Sales Invoice`; withdrawals suggest against `Purchase Invoice`. Description parsing **filters the list**; the treasurer always validates allocation before submit.

#### What allocation infers (no separate entry)


| Selected invoice(s) | Inferred field                              |
| ------------------- | ------------------------------------------- |
| `Sales Invoice`     | `party_type = Customer`, `party = customer` |
| `Purchase Invoice`  | `party_type = Supplier`, `party = supplier` |
| Allocated lines     | Payment Entry references and amounts        |
| Invoice dimensions  | `project`, `cost_center` (warn if mixed)    |




### 6.3 Interac and repeated description matching

Desjardins Interac lines use **stable, repeated description templates**. The sender or recipient name is embedded in a fixed prefix/suffix, making reliable extraction possible without ML.

Typical patterns (FR):


| Direction  | Example description                            | Extracted token         |
| ---------- | ---------------------------------------------- | ----------------------- |
| Deposit    | `Virement Interac de: MARIE-CLAIRE TREMBLAY`   | `MARIE-CLAIRE TREMBLAY` |
| Deposit    | `Dépôt - Virement Interac reçu de Jean Dupont` | `Jean Dupont`           |
| Withdrawal | `Virement Interac à: NICOLAS BOIVIN`           | `NICOLAS BOIVIN`        |


Matching pipeline:

1. **Normalize** description (case, accents, whitespace, strip bank boilerplate).
2. **Extract** name via known Interac templates (regex per template, maintained in parser config).
3. **Resolve** via Party Alias table → `Customer` and/or `Supplier` (see §6.4).
4. **Filter** open invoices to resolved party(ies) and direction-appropriate doc type.
5. **Rank** by amount match (§6.2 priority table).

First match wins by alias `priority` (boosted by `hit_count` for learned aliases); unmatched names are resolved on first Confirm and persisted for future imports (§6.7).

### 6.7 Alias learning from confirmed reconciliations

When the treasurer **Confirm**s a reconciliation, the system **learns** from that decision by creating or updating **Party Alias** rows. Manual alias entry is optional — routine Interac lines self-train over time.

```
Confirm (successful reconcile)
        │
        ▼
Extract learnable token from bank description (Interac name, etc.)
        │
        ▼
Derive (party_type, party) from confirmed invoice allocations
        │
        ├── Single party in allocation → create or reinforce alias
        ├── Multi-party split → learn one alias per party group (same extracted name, different party_type/party/direction)
        └── Non-invoice / exception path → no alias learning
        │
        ▼
Next import: description_matcher + allocation_suggester use updated aliases
```



#### What gets stored


| Input from decision               | Alias field                                             |
| --------------------------------- | ------------------------------------------------------- |
| Normalized extracted Interac name | `extracted_name` (+ optional `pattern` substring match) |
| Deposit vs withdrawal             | `direction`                                             |
| Inferred from invoice doc type    | `party_type`, `party`                                   |
| —                                 | `source = Auto`, `learned_from` → Bank Transaction      |




#### Create vs update rules


| Situation                                                       | Action                                                                      |
| --------------------------------------------------------------- | --------------------------------------------------------------------------- |
| No matching alias for `(extracted_name, direction, party_type)` | **Create** new Party Alias                                                  |
| Alias exists, same `party`                                      | **Reinforce** — increment `hit_count`, set `last_used`                      |
| Alias exists, **different** `party`                             | **Do not overwrite** — log conflict; treasurer resolves in Party Alias list |
| Treasurer corrected a wrong suggestion                          | Learn the **confirmed** mapping (same create/reinforce rules)               |


Conflicts are rare once aliases stabilize; the UI surfaces them on the Party Alias DocType rather than silently picking a winner.

#### Scope and limits

- **Learnable descriptions:** Interac templates (primary), plus other parsed name patterns (e.g. `Paiement internet à {name}`) registered in `description_matcher.py`.
- **Not learned:** Bank fees, internal transfers, and other exception-path reconciliations with no extractable party name.
- **Dual-role parents:** Same extracted name on a **deposit** and **withdrawal** produces **separate** alias rows (Customer vs Supplier) — direction is part of the key.
- **Multi-scout deposit:** One Interac from a parent paying for two scouts creates **two** Customer aliases only if Confirm produced two party groups with the same extracted name — matching then filters to both customers' invoices. Prefer reinforcing existing aliases when the treasurer picks the same allocation again.



#### Treasurer feedback

- Optional toast on Confirm: *"Saved alias: MARIE-CLAIRE TREMBLAY → Luc Tremblay (Customer)"*.
- Party Alias list filter: **Auto-learned** vs **Manual**; disable mistaken rows without deleting history.



### 6.4 Dual-role parents (Customer + Supplier)

Some parents both **pay scout fees** (money in → `Sales Invoice` / `Customer`) and **receive reimbursements** for expenses they fronted (money out → `Purchase Invoice` / `Supplier`).


| Bank signal                         | Invoice type       | Role                             |
| ----------------------------------- | ------------------ | -------------------------------- |
| Deposit + Interac from parent name  | `Sales Invoice`    | Customer (scout fee payment)     |
| Withdrawal + Interac to parent name | `Purchase Invoice` | Supplier (expense reimbursement) |


**Direction disambiguates role** — the same normalized name in Party Alias may map to both a `Customer` (child's account) and a `Supplier` (parent as reimbursee). The matcher returns the role consistent with transaction direction unless the treasurer overrides in the allocation panel.

When a parent pays for **multiple scouts** (multiple `Customer` records), one deposit may allocate to Sales Invoices across customers → see §6.5.

### 6.5 Multi-payment split (one bank line → many Payment Entries)

ERPNext Payment Entry allows **one party per document**. A single bank transaction may therefore require **multiple Payment Entries**:


| Scenario                                                                | Split rule                                                         |
| ----------------------------------------------------------------------- | ------------------------------------------------------------------ |
| One deposit, multiple Sales Invoices, **same Customer**                 | Single Payment Entry with multiple invoice references              |
| One deposit, Sales Invoices for **different Customers** (e.g. siblings) | One Payment Entry **per Customer**, amounts from allocation groups |
| One withdrawal, multiple Purchase Invoices, same Supplier               | Single Payment Entry                                               |
| One withdrawal, mixed parties                                           | One Payment Entry per Supplier                                     |


Orchestration (`reconcile_bank_transaction`):

1. Accept allocation list: `[{invoice, amount}, …]`.
2. Group by `(party_type, party)`.
3. Create and submit one Payment Entry per group; each entry's paid amount = sum of its allocations.
4. Link **all** entries to the same Bank Transaction; mark reconciled only when allocated total equals bank amount.

The treasurer sees one Confirm action; splitting is automatic.

### 6.6 Exception path

When suggestion confidence is low or the line is not invoice-related:

- **Review panel** — pre-filled best allocation; treasurer adjusts checkboxes and amounts.
- **Non-invoice lines** — bank fees, internal transfers: separate "Other" action (Journal Entry or internal transfer); no invoice allocation.
- **Partial payment** — treasurer allocates less than invoice outstanding; remaining balance stays open.
- **Overpayment / unmatched remainder** — block Confirm until allocation equals bank amount, or treasurer adds/removes lines.

Still a single screen — no quick-form → full-form round trip.

---



## 7. Feature Specifications



### 7.1 Bank CSV Import (JSON import config)



#### Design principle: config-driven, format-compatible

The importer is **not** a hard-coded Desjardins parser. It reads a **JSON import config** that describes column roles, date format, delimiter, and number conversion. Configs follow the format used by the [Firefly III Data Importer](https://docs.firefly-iii.org/) (version 3), so files from the [import-configurations](https://github.com/firefly-iii/import-configurations) community repo work **without modification** — we adopt the format, not the product name in our code.

**Production config (troop):** [ca/desjardins/account.json](https://github.com/firefly-iii/import-configurations/blob/main/ca/desjardins/account.json) — vendored unchanged under `bank_reconciliation/configs/import/ca/desjardins/account.json`. Updating the bank format means syncing that file from upstream, not changing Python.

Treasurer workflow: export **Relevés → CSV Accentué (Microsoft Excel…)** , upload CSV + config (Desjardins config pre-selected), import. Multiple months may be concatenated in one file.

#### Config fields the importer honors


| Config key                   | Purpose                                                                                                                        |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `roles[]`                    | Positional column mapping (`date_transaction`, `description`, `amount_debit`, `amount_credit`, `account-number`, `_ignore`, …) |
| `headers`                    | Whether row 1 is a header (Desjardins: `false`)                                                                                |
| `delimiter`                  | `comma`, `semicolon`, `tab`, …                                                                                                 |
| `date`                       | PHP-style date format string (e.g. `Y/m/d`)                                                                                    |
| `conversion`                 | French/European number format (`1 234,56` → `1234.56`)                                                                         |
| `ignore_duplicate_lines`     | Skip duplicate rows within the same file                                                                                       |
| `duplicate_detection_method` | Inform ERPNext-side dedup strategy where applicable                                                                            |


Keys that only apply to other tools (`default_account`, `rules`, `add_import_tag`, `nordigen_*`, …) are **ignored** — they do not break parsing. No Scout-specific keys are added to the JSON; ERPNext mapping stays outside the config file.

#### Role → Bank Transaction mapping


| Config role        | Bank Transaction field             |
| ------------------ | ---------------------------------- |
| `date_transaction` | `date`                             |
| `description`      | `description`, `reference_number`  |
| `amount_debit`     | `withdrawal`                       |
| `amount_credit`    | `deposit`                          |
| `account-number`   | Match → `bank_account` (see below) |
| `account-name`     | Import metadata / log only         |
| `_ignore`          | Skipped                            |


`bank_account` resolution (ERPNext-side, not in JSON):

1. Match `account-number` column value against Bank Account records (full or suffix match).
2. Fallback: treasurer-selected `bank_account` on the import DocType.
3. Ambiguous match → block import until confirmed.

Always set `currency` = CAD for troop accounts. Generated hash → `transaction_id` for deduplication.

#### Desjardins CSV Accentué (reference — defined by bundled config)

The troop's production file is **14 columns, comma-delimited, no header row**. Layout comes entirely from the vendored `account.json` `roles` array:


| Col  | Role               |
| ---- | ------------------ |
| 0    | `account-name`     |
| 1    | `account-number`   |
| 2    | `_ignore`          |
| 3    | `date_transaction` |
| 4    | `_ignore`          |
| 5    | `description`      |
| 6    | `_ignore`          |
| 7    | `amount_debit`     |
| 8    | `amount_credit`    |
| 9–13 | `_ignore`          |


Additional handling (config-driven where possible):

- **Encoding** — UTF-8 with BOM (CSV Accentué); fallback Latin-1.
- **Statement metadata** — opening/closing balance and period from non-transaction rows when present (see regression fixtures).
- **Multi-month files** — one import batch; duplicate detection spans the full file.



#### Import entry point

**Custom DocType** `Scout Bank Import` (bank-agnostic; Desjardins is the default bundled config):


| Field                     | Purpose                                                                               |
| ------------------------- | ------------------------------------------------------------------------------------- |
| `import_file`             | Attach — raw CSV                                                                      |
| `import_config`           | Attach or Select — JSON import config (default: bundled `ca/desjardins/account.json`) |
| `bank_account`            | Link → Bank Account (auto-suggested from `account-number` role)                       |
| `detected_account_number` | Parsed from CSV                                                                       |
| Preview grid              | Parsed rows before commit                                                             |
| Import action             | Create Bank Transactions + summary log                                                |


Treasurer-facing label may say "Desjardins" in the workspace; implementation is a generic config-driven importer.

---



### 7.2 Duplicate Transaction Detection



#### Identity key

Each parsed row generates a deterministic fingerprint:

```
hash(bank_account, date, withdrawal, deposit, normalized_description)
```

Optionally include running balance if present (helps distinguish same-day identical amounts).

#### On import behavior


| Scenario                                        | Behavior                                                    |
| ----------------------------------------------- | ----------------------------------------------------------- |
| Exact fingerprint match, status = Reconciled    | **Skip** — log as "already imported"                        |
| Exact fingerprint match, status = Unreconciled  | **Skip** — log as "duplicate pending"                       |
| Same date + amount + similar description (>90%) | **Flag for review** — import with `status = Pending Review` |
| No match                                        | **Create** Bank Transaction                                 |




#### UI

- Import summary: `{created: N, skipped: N, flagged: N}` with downloadable log.
- Flagged duplicates visible in a "Review Duplicates" list before reconciliation.

---



### 7.3 Scout Bank Reconciliation page

**Decision:** Build a **dedicated custom Page** (`scout_bank_reconciliation`). Do **not** patch or extend ERPNext's stock Bank Reconciliation Tool.


| Approach                             | Verdict      | Rationale                                                                                                                                                                           |
| ------------------------------------ | ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Patch stock Bank Reconciliation Tool | **Rejected** | Allocation-first UX, multi-payment preview, and Interac suggestion panel fight the stock match → voucher → form flow; client scripts on core pages break easily on ERPNext upgrades |
| Dedicated Scout page                 | **Chosen**   | Full control over allocation panel, Confirm action, and exception paths; all logic in `scout_manager`; standard DocTypes unchanged underneath                                       |


The stock tool remains in ERPNext for reference or power users, but the **Scout Treasurer workspace** links only to the custom page. Section 4 describes the stock tool pain as motivation — not the implementation target.

#### Page responsibilities


| Area              | Custom page behavior                                                                                     |
| ----------------- | -------------------------------------------------------------------------------------------------------- |
| Entry point       | Workspace shortcut → `/app/scout-bank-reconciliation`                                                    |
| Unreconciled list | All unreconciled `Bank Transaction` rows for selected bank account up to To Date; no mandatory From Date |
| Closing balance   | Display statement closing balance from latest `Scout Bank Import` for the account (§F2)                  |
| Per-line panel    | Suggested invoice allocation, confidence badge, multi-payment preview                                    |
| Confirm           | Calls `reconcile_bank_transaction()` — no Payment Entry form round trip                                  |
| Exceptions        | Non-invoice lines (fees, transfers) via separate action on same page                                     |




#### F1 — No From Date gate on unreconciled work

- **Stock tool problem:** From Date defaults to a recent date, hiding older unreconciled transactions and invoices.
- **Scout page:** Load all unreconciled transactions for the bank account up to To Date. Optional From Date filter for edge cases only — never required.



#### F2 — Auto closing balance

- Parse closing balance from CSV metadata during import.
- Store on `Scout Bank Import`; display on Scout Bank Reconciliation page when reconciling that account / import batch.



#### F3 — Allocation-centric reconcile action

Replace the stock tool's match → create voucher → form chain with an **allocation panel** and single **Confirm** button per bank line on the custom page.

Backend orchestration (single whitelisted method):

```python
@frappe.whitelist()
def reconcile_bank_transaction(bank_transaction, allocations, overrides=None):
    """
    allocations: [{invoice_type, invoice, allocated_amount}, ...]

    1. Validate allocated total vs bank transaction amount
    2. Group allocations by (party_type, party) inferred from each invoice
    3. For each group: build + submit Payment Entry (dimensions from invoices)
    4. Link all Payment Entries to Bank Transaction
    5. Mark Bank Transaction Reconciled
    6. Learn / reinforce Party Alias rows from description + confirmed allocations (§6.7, F9)
    7. Return payment names + status
    """
```



#### F4 — Description matching (Interac + aliases)

Description parsing **narrows the invoice list**; it does not replace allocation.


| Signal                                         | Effect on suggestions                            |
| ---------------------------------------------- | ------------------------------------------------ |
| Interac deposit template + alias → Customer    | Filter to that customer's open Sales Invoices    |
| Interac withdrawal template + alias → Supplier | Filter to that supplier's open Purchase Invoices |
| `Paiement internet à {name}`                   | Supplier filter (non-Interac withdrawals)        |
| Known fee / transfer keywords                  | Route to exception path (no invoice allocation)  |


Maintain a **Party Alias** DocType for names that don't match ERPNext records exactly. A single contact may have **multiple alias rows** — one as Customer (fee payer), one as Supplier (reimbursee) — distinguished by `party_type` and matched together with transaction direction. Rows are **auto-created and reinforced on Confirm** (§6.7, F9); treasurers may also add or edit aliases manually.

#### F9 — Alias learning on Confirm

After a successful reconcile, `alias_learner.learn_from_reconciliation()` runs automatically (no extra treasurer step).

```python
def learn_from_reconciliation(bank_transaction, allocation_groups):
    """
    allocation_groups: [{party_type, party, invoices, allocated_amount}, ...]

    For each group with a learnable extracted name from bank_transaction.description:
      - upsert Party Alias (create, reinforce hit_count, or log conflict)
    """
```


| Behavior           | Detail                                                                          |
| ------------------ | ------------------------------------------------------------------------------- |
| Trigger            | Successful `reconcile_bank_transaction()` only                                  |
| Key                | `(normalized extracted_name, direction, party_type)`                            |
| Reinforce          | Same party → `hit_count += 1`, `last_used = now`                                |
| Conflict           | Different party for same key → `Party Alias` conflict flag; no silent overwrite |
| Suggestion ranking | Higher `hit_count` increases effective match priority in `allocation_suggester` |


Manual **Add alias** on the Scout page remains for pre-emptive setup (e.g. before first Interac arrives) and for fixing conflicts; Confirm is the primary learning path.

#### F5 — Open invoice discovery without From Date

Load the global open invoice pool for allocation (list stays short in practice):

- **Sales:** `outstanding_amount > 0`, `docstatus = 1`.
- **Purchase:** same filter for suppliers.
- **No From Date filter by default.**
- Optional narrow filter after description match (§F4).
- Sort: `posting_date ASC` for predictable partial-payment suggestions.



#### F6 — Dimension inheritance

When invoices are selected (manually or auto):

- `project` ← from allocated invoices (if all match) or blank with warning.
- `cost_center` ← from allocated invoices (if all match) or blank with warning.
- Never require manual re-entry when all selected invoices share the same dimensions.



#### F7 — Multi-payment split

When confirmed allocations span more than one `(party_type, party)`:

- Create one submitted Payment Entry per group automatically.
- Each entry receives only its group's invoice references and paid amount.
- All entries link to the same Bank Transaction before status → Reconciled.

Treasurer performs one Confirm; ERPNext's one-party-per-entry constraint is handled in orchestration.

#### F8 — Auto-reconcile after payment

After all Payment Entries for a bank line are submitted:

1. Create `Bank Transaction Payments` link for each entry.
2. Set Bank Transaction `status = Reconciled` when linked total equals bank amount.
3. Refresh reconciliation view — transaction disappears from unreconciled list.

No return trip to manually link payments.

---



## 8. Technical Design



### 8.1 App structure

```
scout_manager/
├── scout_manager/
│   ├── bank_reconciliation/
│   │   ├── configs/
│   │   │   └── import/               # Vendored bank configs (unchanged JSON; format compatible with Firefly III)
│   │   │       └── ca/desjardins/account.json
│   │   ├── csv_importer.py           # Config-driven CSV → normalized transaction rows
│   │   ├── import_config.py          # Load + validate JSON config; role → column index
│   │   ├── duplicate_detector.py     # Fingerprint + similarity
│   │   ├── description_matcher.py    # Interac templates + description → party hint
│   │   ├── allocation_suggester.py   # Open invoices + amount/alias ranking
│   │   ├── alias_learner.py          # Auto-create / reinforce Party Alias on Confirm
│   │   ├── reconcile.py              # Orchestration: split PEs + reconcile + learn
│   │   └── payment_builder.py        # PE from bank txn + invoice allocations
│   ├── doctype/
│   │   ├── scout_bank_import/        # Import wizard DocType (JSON config + CSV)
│   │   └── party_alias/              # Description → party mappings
│   ├── report/
│   │   └── rentabilite_par_projet_par_centre_de_cout/  # Migrated Query Report (§8.6)
│   │       ├── rentabilite_par_projet_par_centre_de_cout.json
│   │       └── rentabilite_par_projet_par_centre_de_cout.js
│   ├── public/
│   │   └── js/
│   │       └── argent_disponible_widget.js             # Widget logic extracted from Custom HTML Block
│   ├── page/
│   │   ├── scout_bank_reconciliation/  # Dedicated reconciliation UI (primary entry point)
│   │   │   ├── scout_bank_reconciliation.json
│   │   │   ├── scout_bank_reconciliation.js
│   │   │   └── scout_bank_reconciliation.py  # page context + whitelisted API wrappers
│   │   └── argent_disponible/          # Optional: standalone page if not kept as workspace block
│   └── patches/
│       ├── migrate_rentabilite_report.py
│       └── migrate_argent_disponible_block.py
├── fixtures/
│   └── custom_html_block.json          # "Argent disponible" shell HTML + role (script via app JS)
├── hooks.py                          # Workspace link, page registration, fixtures; no stock recon overrides
└── docs/
    └── design/
        └── bank-reconciliation.md    # This document
```



### 8.2 Key DocTypes



#### Scout Bank Import


| Field                     | Type                | Purpose                                                         |
| ------------------------- | ------------------- | --------------------------------------------------------------- |
| `import_config`           | Attach / Select     | JSON import config (default: bundled Desjardins `account.json`) |
| `import_file`             | Attach              | Raw CSV (CSV Accentué for Desjardins)                           |
| `bank_account`            | Link → Bank Account | Target account (auto-suggested from `account-number` role)      |
| `detected_account_number` | Data                | Parsed from CSV via config roles                                |
| `statement_from_date`     | Date                | Parsed from file                                                |
| `statement_to_date`       | Date                | Parsed from file                                                |
| `opening_balance`         | Currency            | Parsed from file                                                |
| `closing_balance`         | Currency            | Parsed from file                                                |
| `status`                  | Select              | Draft / Imported / Partial / Failed                             |
| `import_log`              | Long Text           | Created / skipped / flagged summary                             |




#### Party Alias (v1)


| Field            | Type                    | Purpose                                                                               |
| ---------------- | ----------------------- | ------------------------------------------------------------------------------------- |
| `extracted_name` | Data                    | Normalized name from Interac / parsed description (primary match key)                 |
| `pattern`        | Data                    | Optional regex or substring; auto-set to escaped `extracted_name` for substring match |
| `party_type`     | Select                  | Customer / Supplier                                                                   |
| `party`          | Dynamic Link            | Resolved party                                                                        |
| `direction`      | Select                  | Deposit / Withdrawal / Both                                                           |
| `priority`       | Int                     | Base match order; effective priority = `priority` + learned boost from `hit_count`    |
| `source`         | Select                  | Auto / Manual                                                                         |
| `learned_from`   | Link → Bank Transaction | Last reconciliation that created or reinforced this row                               |
| `hit_count`      | Int                     | Times this mapping was confirmed; used for ranking                                    |
| `last_used`      | Datetime                | Last successful Confirm using this alias                                              |
| `enabled`        | Check                   | Disable mistaken auto-learned rows without deleting                                   |
| `conflict_notes` | Small Text              | Set when a new Confirm disagrees with an existing mapping                             |


One person may have **two rows** (Customer for scout fees, Supplier for reimbursements). Matching uses `direction` together with bank line deposit/withdrawal.

Example: alias `MARIE-CLAIRE TREMBLAY` + Deposit → Customer *Luc Tremblay*; same name + Withdrawal → Supplier *Marie-Claire Tremblay*.

### 8.3 Hooks and integration

No overrides of ERPNext's stock Bank Reconciliation Tool or its whitelisted methods.

```python
# hooks.py (illustrative)

# Workspace — treasurer entry point
# Scout Treasurer workspace → Link to Page "Scout Bank Reconciliation"

# Optional: hide stock "Bank Reconciliation Tool" from Scout workspace
# (leave available elsewhere in ERPNext for admins)

doc_events = {
    # Prefer explicit orchestration in reconcile_bank_transaction() over
    # Payment Entry on_submit hooks — keeps bank-link logic in one place.
}
```

All reconciliation behavior is invoked from the custom page via `scout_manager.bank_reconciliation` APIs. Standard DocTypes (`Bank Transaction`, `Payment Entry`, invoices) are used as-is.

### 8.4 Scout Bank Reconciliation page (client)

Single-page app within Frappe Page framework:

- **Bank account selector** + optional To Date; unreconciled transaction list (no default From Date).
- **Statement closing balance** banner from latest import for selected account.
- **Allocation panel** per selected bank line:
  - Suggested open invoices (Sales + Purchase) with editable amounts.
  - Confidence badge (High / Review needed).
  - Multi-payment preview when Confirm would create more than one Payment Entry.
  - Optional toast when Confirm saves or reinforces an alias (§6.7).
  - Manual **Add alias** for pre-emptive setup or conflict fixes; routine Interac lines learn on Confirm.
- **Confirm** → `reconcile_bank_transaction()`; line leaves unreconciled list on success.
- **Other** action for non-invoice lines (fees, transfers) — exception path on same page.

Backend calls are whitelisted methods on the page controller or `bank_reconciliation` module — no dependency on stock recon client code.

### 8.5 Data migration / compatibility

- Existing Bank Transactions and Payment Entries are untouched.
- Duplicate detection applies only to new imports.
- Bank reconciliation features are independent of the reporting assets in §8.6 — no shared code paths.



### 8.6 Existing reports and widgets — migration to `scout_manager`

**Decision:** Move both assets from site-only DB records into the app repo. Keeps troop customizations reviewable, reproducible on fresh sites, and aligned with the bank-reconciliation work already planned under `scout_manager`.

#### 8.6.1 Report — Rentabilité par projet par centre de coût


| Property      | Current (site)                     | Target (app)                                                                  |
| ------------- | ---------------------------------- | ----------------------------------------------------------------------------- |
| Type          | Query Report                       | Query Report files in app                                                     |
| `ref_doctype` | `GL Entry`                         | unchanged                                                                     |
| `module`      | `Accounts`                         | `Scout Manager`                                                               |
| Filters       | `company`, `fiscal_year`           | unchanged                                                                     |
| SQL           | Inline on Report doc               | `rentabilite_par_projet_par_centre_de_cout.json` → `query` field              |
| Client JS     | Inline on Report doc               | `rentabilite_par_projet_par_centre_de_cout.js` (drill-down to General Ledger) |
| Cost centers  | Hardcoded in SQL (`Clan - 188`, …) | Keep as-is in v1; optional later: read from troop config                      |


**Migration steps:**

1. Export production Report definition (query, columns, filters, roles, letter head).
2. Create app report folder; set `module = Scout Manager`, `is_standard = Yes`.
3. `bench migrate` on dev site → verify output matches production for a known fiscal year.
4. Verify drill-down: click a cell → General Ledger opens with correct `project`, `cost_center`, date range.
5. Patch `migrate_rentabilite_report.py`: if a site Report with the same name exists under `Accounts`, disable or rename the DB copy after app report is confirmed (avoid duplicate menu entries).



#### 8.6.2 Widget — Argent disponible par unité


| Property         | Current (site)                                                     | Target (app)                                                                  |
| ---------------- | ------------------------------------------------------------------ | ----------------------------------------------------------------------------- |
| Type             | Custom HTML Block                                                  | Fixture shell + app JS asset                                                  |
| Record name      | `Argent disponible`                                                | Same name (workspace links unchanged)                                         |
| Display title    | `Argent disponible par unité`                                      | unchanged (in HTML)                                                           |
| Logic            | ~200 lines inline `script` on block                                | `public/js/argent_disponible_widget.js`, loaded by thin inline bootstrap      |
| Styles           | Inline `style` on block                                            | Move to `public/css/argent_disponible_widget.css` or keep in fixture          |
| Data source      | `frappe.desk.query_report.run` → Trial Balance per cost center     | unchanged in v1                                                               |
| Hardcoded config | Company, account nos. (1011, 1012, 1030, 1021, passif), unit order | Extract to `scout_manager/config/troop_accounts.py` or top of JS module in v1 |


**Migration steps:**

1. Extract `html`, `script`, `style` from production Custom HTML Block `Argent disponible`.
2. Move script/style to app `public/` files; fixture retains minimal HTML + `<script src="/assets/scout_manager/js/argent_disponible_widget.js">`.
3. Add fixture in `hooks.py`: `{"dt": "Custom HTML Block", "filters": [["name", "=", "Argent disponible"]]}`.
4. `bench export-fixtures` / commit → `fixtures/custom_html_block.json`.
5. Dev site: `bench migrate` → widget on workspace shows same cards and totals as production.
6. Patch disables duplicate site-only block if name collision on upgrade.

**Optional follow-up (not Phase 0):** Replace per–cost-center Trial Balance calls with one whitelisted API (`get_argent_disponible_by_unit`) to cut N+1 report runs; out of scope until widget is in git.

#### 8.6.3 Workspace and roles

- Export workspace layout that embeds the widget (if not already in a fixture) so new sites get the same treasurer dashboard.
- Preserve role assignments: widget → **All**; report → Accounts User, Accounts Manager, Auditor, Projects User.



#### 8.6.4 Verification checklist

- [ ] Report row/column totals match production export for FY 2025–2026 (or current year).
- [ ] Report drill-down opens General Ledger with correct filters.
- [ ] Widget shows all five units in order: Groupe, Colonie, Meute, Troupe, Clan.
- [ ] Widget `disponible` and `disponible_ar` match manual Trial Balance spot-check for one unit.
- [ ] No duplicate Report or Custom HTML Block entries in desk after patch runs.

---



## 9. Implementation Phases



### Phase 0 — Version-control existing reports and widgets (prerequisite)

Migrate the two working customizations from site DB into `scout_manager` **before** Phase 1 ships. Low risk, no impact on live accounting data; enables reproducible dev/staging sites for bank-reconciliation work.

- [ ] Scaffold `scout_manager` app report module (`rentabilite_par_projet_par_centre_de_cout`)
- [ ] Port Query Report SQL, columns, filters, roles, letter head from production
- [ ] Port client JS (fiscal-year cache + General Ledger drill-down)
- [ ] Extract widget script/style to `public/js/argent_disponible_widget.js` (+ CSS)
- [ ] Add `Custom HTML Block` fixture (`Argent disponible`) with thin HTML shell
- [ ] `hooks.py` fixtures list + workspace fixture if needed
- [ ] Patches: retire duplicate site-only Report / Custom HTML Block after app install
- [ ] Verification per §8.6.4 on dev site

**Deliverable:** Both assets install via `bench migrate` on a fresh site; git tracks all logic; production unchanged until deploy.

### Phase 1 — Import (highest value, lowest risk)

- [ ] `csv_importer.py` + `import_config.py` — parse CSV from JSON config (roles, date, delimiter, conversion)
- [ ] Vendor `ca/desjardins/account.json` unchanged from [import-configurations](https://github.com/firefly-iii/import-configurations)
- [ ] Regression test: troop CSV fixture + import config → expected Bank Transaction rows
- [ ] `Scout Bank Import` DocType + preview UI (config + CSV upload → preview → import)
- [ ] `account-number` role → auto-match Bank Account
- [ ] Duplicate detection on import (honor `ignore_duplicate_lines`; ERPNext fingerprint dedup)
- [ ] Import summary log (`created` / `skipped` / `flagged`)
- [ ] Auto-populate closing balance on import record when present in file

**Deliverable:** Treasurer exports CSV Accentué from Relevés and uploads with zero preprocessing — same one-step ease as before.

### Phase 2 — Scout Bank Reconciliation page (scaffold)

- [ ] `scout_bank_reconciliation` Page — bank account selector, unreconciled list, no From Date gate
- [ ] Global open invoice list API for allocation (no From Date filter)
- [ ] Closing balance display from latest `Scout Bank Import`
- [ ] Workspace link; stock Bank Reconciliation Tool removed from Scout Treasurer workspace

**Deliverable:** Treasurers open the Scout page instead of the stock tool; unreconciled work and closing balance visible without filter workarounds.

### Phase 3 — Allocation-centric reconcile

- [ ] Interac description templates + Party Alias matching (deposit and withdrawal)
- [ ] `allocation_suggester` — amount-based pre-selection on short open-invoice list
- [ ] Allocation panel + Confirm on Scout page
- [ ] `reconcile_bank_transaction()` — multi-payment split by party group
- [ ] `alias_learner` — auto-create / reinforce Party Alias on successful Confirm
- [ ] Dimension inheritance (project, cost center from invoices) in Payment Entry builder
- [ ] Auto-link all Payment Entries and reconcile Bank Transaction
- [ ] Review panel + non-invoice exception path on same page

**Deliverable:** Typical fee payment or reimbursement confirmed in one screen; multi-scout deposits split automatically; repeat Interac lines auto-suggest correctly after first Confirm.

### Phase 4 — Polish and learning

- [ ] Party Alias management UI (Auto vs Manual, conflicts, disable mistaken rows)
- [ ] Bulk reconcile (select multiple similar Interac deposits)
- [ ] Reconciliation dashboard (unreconciled count, oldest unreconciled date)
- [ ] Additional banks: drop in compatible community import configs (no parser code changes)

---



## 10. Open Questions


| #   | Question                                                                                                                                      | Impact                                    |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| Q1  | ~~Desjardins export format~~ → **Resolved:** Relevés → CSV Accentué (14 cols, no headers); validated in production via Firefly III            | —                                         |
| Q1b | Redacted CSV Accentué sample committed as regression fixture?                                                                                 | Parser tests, balance/metadata edge cases |
| Q2  | ~~Auto-allocation strategy~~ → **Resolved:** priority order in §6.2 (exact amount → customer sum → alias + partial → manual)                  | Phase 3 UX                                |
| Q3  | Partial payments — common? Auto-suggest oldest-first up to bank amount when alias matches?                                                    | Allocation suggester                      |
| Q4  | Are supplier payments always against Purchase Invoices, or sometimes Journal Entries?                                                         | Exception path for withdrawals            |
| Q5  | ~~Custom page vs extend stock Bank Reconciliation Tool?~~ → **Resolved:** dedicated `scout_bank_reconciliation` Page; do not patch stock tool | —                                         |
| Q6  | Should skipped duplicates be visible in ERPNext Error Log or a custom import log only?                                                        | Ops visibility                            |
| Q7  | Canonical Interac description templates from production CSV — complete regex set?                                                             | description_matcher.py                    |
| Q8  | When one parent pays for multiple scouts, is partial allocation per child ever intentional?                                                   | Multi-payment UX copy                     |


---



## 11. Risks and Mitigations


| Risk                                                               | Mitigation                                                                                              |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| Bank changes CSV format                                            | Sync updated config from upstream import-configurations repo; sample-file regression tests              |
| Wrong invoice auto-selected                                        | Treasurer always confirms allocation; amount must balance before Confirm                                |
| Wrong alias learned from bad Confirm                               | Do not overwrite on conflict; `enabled` flag + Party Alias review UI; reinforce only on repeat confirms |
| Dual-role parent matched to wrong party_type                       | Match alias with direction; show both roles in review if ambiguous                                      |
| Multi-customer deposit split incorrectly                           | Show grouped preview (N Payment Entries) before Confirm                                                 |
| ERPNext upgrade breaks Scout UI                                    | Reconciliation UI entirely in `scout_manager` page; no core client-script overrides                     |
| Duplicate hash collision (same day, same amount, same description) | Include balance or sequence in hash; flag for review                                                    |


---



## 12. Appendix: Example Desjardins Description Patterns

Observed in production Bank Transactions:


| Description                                    | Direction  | Suggested filter   | Notes                             |
| ---------------------------------------------- | ---------- | ------------------ | --------------------------------- |
| `Virement Interac de: MARIE-CLAIRE TREMBLAY`   | Deposit    | Customer via alias | Parent name ≠ scout customer name |
| `Dépôt - Virement Interac reçu de Jean Dupont` | Deposit    | Customer via alias | Template variant                  |
| `Virement Interac à: NICOLAS BOIVIN`           | Withdrawal | Supplier via alias | Reimbursement to parent           |
| `Paiement internet à Nicolas Boivin/cime`      | Withdrawal | Supplier           | Non-Interac supplier payment      |
| `Frais bancaires`                              | Withdrawal | —                  | Journal Entry / internal          |
| `Télé-paiement ...`                            | Withdrawal | Supplier           | Parse payee                       |




### Interac template maintenance

Collect **real CSV samples** and register each distinct Desjardins boilerplate as a template in `description_matcher.py`. Templates should capture the name group only; normalization handles accents and case.

### Dual-role example

Parent *Marie-Claire Tremblay*:

- Pays son *Luc Tremblay* registration → Deposit, alias → Customer *Luc Tremblay*
- Receives camp grocery reimbursement → Withdrawal, alias → Supplier *Marie-Claire Tremblay*

Same extracted name, different direction → different invoice pool and Payment Entry type.

---



## 13. Related Documents

- [import-configurations](https://github.com/firefly-iii/import-configurations) — upstream community bank configs (Desjardins: `ca/desjardins/account.json`); vendored as-is
- [Firefly III Data Importer docs](https://docs.firefly-iii.org/explanation/data-importer/) — reference for the JSON config schema we implement
- (Future) `docs/design/membership.md` — membership lifecycle
- (Future) `docs/design/domain-model.md` — full scout domain map

