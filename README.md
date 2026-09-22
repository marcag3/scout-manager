# Scout Manager

Custom ERPNext app for scout troop management (Troop 188e Montréal-Nord).

## Development (devcontainer)

This repo includes a VS Code / Cursor devcontainer based on the [official Frappe Docker development setup](https://frappe.github.io/frappe_docker/05-development/01-development.html).

### Prerequisites

- Docker
- Dev Containers extension

### Getting started

1. Open this repository in VS Code or Cursor.
2. Run **Dev Containers: Reopen in Container**.
3. Wait for the first-time bootstrap (bench init + ERPNext v16 site creation can take several minutes).
4. Start the dev server:

```bash
cd /workspace/development/frappe-bench
bench start
```

5. Open http://localhost:8000 and log in:

- **User:** Administrator
- **Password:** admin

The local app source lives at `/workspace` and is linked into the bench as `apps/scout_manager`. Edits in this repo are picked up immediately; restart `bench start` after Python changes, or let the asset watcher handle frontend changes.

### Useful commands

```bash
cd /workspace/development/frappe-bench

# Frappe console
bench --site development.localhost console

# Run migrations after pulling app changes
bench --site development.localhost migrate

# Export fixtures (developer mode must be on)
bench --site development.localhost export-fixtures

# Run app tests
bench --site development.localhost run-tests --app scout_manager
```

### Debugging

Use the **Honcho + Web debug** launch configuration in VS Code. It starts socketio, watch, schedule, and workers via honcho, then attaches the Python debugger to the web process.

## Production install

For the self-hosted Docker stack in `erpnext-docker`, add this app to `apps.json`, rebuild the image, and install it on the site with `bench install-app scout_manager`.

## Contributing

This app uses `pre-commit` for code formatting and linting:

```bash
pre-commit install
```

Tools: ruff, eslint, prettier, pyupgrade.

## License

MIT
