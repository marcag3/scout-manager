# Bank import configs

JSON configs in this tree follow the [Firefly III Data Importer](https://docs.firefly-iii.org/explanation/data-importer/) format (version 3). Files are vendored unchanged from the [import-configurations](https://github.com/firefly-iii/import-configurations) community repository.

## Updating

To sync a config from upstream:

```bash
curl -o ca/desjardins/account.json \
  https://raw.githubusercontent.com/firefly-iii/import-configurations/main/ca/desjardins/account.json
```

Do not add Scout-specific keys to these JSON files; ERPNext mapping stays in Python.

The Desjardins config includes `encoding` and a `balance` column role (column N) — extensions required for CSV Accentué exports that upstream Firefly configs omit.
