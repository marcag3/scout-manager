frappe.ui.form.on("Scout Bank Import", {
	refresh(frm) {
		frm.events.ensure_import_config(frm);

		if (!frm.is_new() && frm.doc.status === "Draft") {
			frm.add_custom_button(__("Import Transactions"), () => frm.events.run_import(frm), __("Actions"));
		}

		if (frm.doc.import_file) {
			frm.add_custom_button(__("Preview"), () => frm.events.run_preview(frm));
		}
	},

	import_file(frm) {
		if (!frm.doc.import_file) {
			return;
		}

		// Wait for Frappe's attach upload/save to finish before previewing.
		frappe.after_ajax(() => {
			frm.events.ensure_import_config(frm).then((config) => {
				if (!config) {
					frappe.msgprint(
						__(
							"No import config available. Ask an administrator to set up a default Bank Import Config."
						)
					);
					return;
				}
				frm.events.run_preview(frm);
			});
		});
	},

	ensure_import_config(frm) {
		const current = frm.doc.import_config;
		if (current && !frm.events.is_legacy_import_config(current)) {
			return Promise.resolve(current);
		}

		return frappe.db
			.get_value("Bank Import Config", { is_default: 1, disabled: 0 }, "name")
			.then(({ message }) => {
				if (message?.name) {
					frm.set_value("import_config", message.name);
					return message.name;
				}
				return null;
			});
	},

	is_legacy_import_config(value) {
		return Boolean(value && (value.includes("/") || value.endsWith(".json")));
	},

	run_preview(frm) {
		if (!frm.doc.import_file) {
			return;
		}

		frm.events.ensure_import_config(frm).then((config) => {
			if (!config) {
				return;
			}

			frappe.call({
				method:
					"scout_manager.scout_manager.doctype.scout_bank_import.scout_bank_import.preview_bank_import",
				args: {
					import_file: frm.doc.import_file,
					import_config: config,
					bank_account: frm.doc.bank_account,
				},
				freeze: true,
				freeze_message: __("Parsing bank statement..."),
				callback({ message }) {
					if (!message) {
						return;
					}

					frm.events.apply_preview_fields(frm, message);
					frm.events.render_preview(frm, message);
				},
			});
		});
	},

	apply_preview_fields(frm, message) {
		if (message.suggested_bank_account && !frm.doc.bank_account) {
			frm.set_value("bank_account", message.suggested_bank_account);
			frappe.show_alert({
				message: __("Bank account matched from file"),
				indicator: "green",
			});
		}
		if (message.account_number) {
			frm.set_value("detected_account_number", message.account_number);
		}
		if (message.statement_from_date) {
			frm.set_value("statement_from_date", message.statement_from_date);
		}
		if (message.statement_to_date) {
			frm.set_value("statement_to_date", message.statement_to_date);
		}
		if (message.opening_balance != null) {
			frm.set_value("opening_balance", message.opening_balance);
		}
		if (message.closing_balance != null) {
			frm.set_value("closing_balance", message.closing_balance);
		}
	},

	render_preview(frm, data) {
		const rows = (data.transactions || [])
			.map(
				(row) => `
				<tr>
					<td>${frappe.datetime.str_to_user(row.date)}</td>
					<td>${frappe.utils.escape_html(row.description || "")}</td>
					<td class="text-right">${format_currency(row.withdrawal || 0)}</td>
					<td class="text-right">${format_currency(row.deposit || 0)}</td>
				</tr>`
			)
			.join("");

		const total_note =
			data.total_transactions > (data.transactions || []).length
				? `<p class="text-muted">${__(
						"Showing first {0} of {1} transactions",
						[(data.transactions || []).length, data.total_transactions]
					)}</p>`
				: `<p class="text-muted">${__("{0} transactions", [data.total_transactions || 0])}</p>`;

		const html = `
			${total_note}
			<div class="table-responsive">
				<table class="table table-bordered table-sm">
					<thead>
						<tr>
							<th>${__("Date")}</th>
							<th>${__("Description")}</th>
							<th class="text-right">${__("Withdrawal")}</th>
							<th class="text-right">${__("Deposit")}</th>
						</tr>
					</thead>
					<tbody>${rows || `<tr><td colspan="4">${__("No transactions found")}</td></tr>`}</tbody>
				</table>
			</div>`;

		frm.fields_dict.preview_html.$wrapper.html(html);
	},

	run_import(frm) {
		if (!frm.doc.bank_account) {
			frappe.msgprint(__("Select a bank account before importing"));
			return;
		}

		frappe.confirm(__("Create bank transactions from this file?"), () => {
			frm.call({
				method: "import_transactions",
				doc: frm.doc,
				freeze: true,
				freeze_message: __("Importing bank transactions..."),
				callback({ message }) {
					if (!message) {
						return;
					}

					frappe.show_alert({
						message: __("Created {0}, skipped {1}", [message.created, message.skipped]),
						indicator: message.created ? "green" : "orange",
					});
					frm.reload_doc();
				},
			});
		});
	},
});
