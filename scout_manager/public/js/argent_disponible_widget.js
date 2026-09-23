frappe.provide("scout_manager");

scout_manager.init_argent_disponible_widget = function (root_element) {
	const root = root_element.querySelector("#fonds-live-root") || root_element;
	if (root.dataset.bound === "1") return;
	root.dataset.bound = "1";

	const grid = root_element.querySelector("#fonds-live-grid");
	const meta = root_element.querySelector("#fonds-live-meta");
	const errBox = root_element.querySelector("#fonds-live-error");
	const btn = root_element.querySelector("#fonds-live-refresh");

	function money(value) {
		return format_currency(value || 0, "CAD");
	}

	function setError(message) {
		errBox.hidden = !message;
		errBox.textContent = message || "";
	}

	function cardHtml(item) {
		const hasAr = Math.abs(item.ar) >= 0.01;
		const negative = item.disponible < 0 ? " is-neg" : "";
		const negativeAr = item.disponible_ar < 0 ? " is-neg" : "";
		const arLine = hasAr
			? `<div class="fonds-live__ar">+ ${money(item.ar)} à recevoir → <strong class="fonds-live__total${negativeAr}">${money(item.disponible_ar)}</strong></div>`
			: "";
		const passifLine = item.passif >= 0.01 ? ` · Passif ${money(item.passif)}` : "";

		return `
			<div class="fonds-live__card">
				<div class="fonds-live__name">${frappe.utils.escape_html(item.name)}</div>
				<div class="fonds-live__hero${negative}">${money(item.disponible)}</div>
				${arLine}
				<div class="fonds-live__details">
					Banque ${money(item.banque)} · Caisse ${money(item.caisse)}${passifLine}
				</div>
			</div>
		`;
	}

	function renderMeta(data) {
		const totals = data.totals || {};
		const includeReceivables = Math.abs((totals.disponible_ar || 0) - (totals.disponible || 0)) >= 0.01;
		const receivablesSuffix = includeReceivables
			? ` (${money(totals.disponible_ar)} incl. créances)`
			: "";

		meta.textContent = `${frappe.datetime.str_to_user(data.to_date)} · total ${money(totals.disponible)}${receivablesSuffix}`;
	}

	async function refresh() {
		setError("");
		btn.disabled = true;
		meta.textContent = "Calcul en cours…";
		grid.innerHTML = "<div class='fonds-live__loading'>Chargement des soldes…</div>";

		try {
			const response = await frappe.call({
				method: "scout_manager.scout_manager.api.argent_disponible.get_argent_disponible_by_unit",
				args: {
					to_date: frappe.datetime.get_today(),
				},
			});
			const data = response.message;
			const units = data.units || [];

			if (!units.length) {
				throw new Error("Aucun centre de coût trouvé.");
			}

			renderMeta(data);
			grid.innerHTML = units.map(cardHtml).join("");
		} catch (error) {
			console.error(error);
			grid.innerHTML = "";
			meta.textContent = "Erreur";
			setError((error && error.message) || String(error));
		} finally {
			btn.disabled = false;
		}
	}

	btn.addEventListener("click", refresh);
	refresh();
};
