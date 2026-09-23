frappe.provide("scout_manager");

const API_METHOD =
	"scout_manager.scout_manager.api.argent_disponible.get_argent_disponible_by_unit";

const SELECTORS = {
	root: "#fonds-live-root",
	grid: "#fonds-live-grid",
	meta: "#fonds-live-meta",
	error: "#fonds-live-error",
	refresh: "#fonds-live-refresh",
};

const CSS_CLASS = {
	negative: " is-neg",
	card: "fonds-live__card",
	name: "fonds-live__name",
	hero: "fonds-live__hero",
	ar: "fonds-live__ar",
	total: "fonds-live__total",
	details: "fonds-live__details",
	loading: "fonds-live__loading",
};

scout_manager.init_argent_disponible_widget = function (root_element) {
	const root = root_element.querySelector(SELECTORS.root) || root_element;
	if (root.dataset.bound === "1") return;
	root.dataset.bound = "1";

	const grid = root_element.querySelector(SELECTORS.grid);
	const meta = root_element.querySelector(SELECTORS.meta);
	const errBox = root_element.querySelector(SELECTORS.error);
	const btn = root_element.querySelector(SELECTORS.refresh);

	let currency = frappe.defaults.get_default("currency");

	function money(value) {
		return format_currency(value || 0, currency);
	}

	function setError(message) {
		errBox.hidden = !message;
		errBox.textContent = message || "";
	}

	function cardHtml(item) {
		const hasAr = Math.abs(item.ar) >= 0.01;
		const negative = item.disponible < 0 ? CSS_CLASS.negative : "";
		const negativeAr = item.disponible_ar < 0 ? CSS_CLASS.negative : "";
		const arLine = hasAr
			? `<div class="${CSS_CLASS.ar}">+ ${money(item.ar)} ${__("à recevoir")} → <strong class="${CSS_CLASS.total}${negativeAr}">${money(item.disponible_ar)}</strong></div>`
			: "";
		const passifLine =
			item.passif >= 0.01 ? ` · ${__("Passif")} ${money(item.passif)}` : "";

		return `
			<div class="${CSS_CLASS.card}">
				<div class="${CSS_CLASS.name}">${frappe.utils.escape_html(item.name)}</div>
				<div class="${CSS_CLASS.hero}${negative}">${money(item.disponible)}</div>
				${arLine}
				<div class="${CSS_CLASS.details}">
					${__("Banque")} ${money(item.banque)} · ${__("Caisse")} ${money(item.caisse)}${passifLine}
				</div>
			</div>
		`;
	}

	function renderMeta(data) {
		const totals = data.totals || {};
		const includeReceivables =
			Math.abs((totals.disponible_ar || 0) - (totals.disponible || 0)) >= 0.01;
		const receivablesSuffix = includeReceivables
			? ` (${money(totals.disponible_ar)} ${__("incl. créances")})`
			: "";

		meta.textContent = `${frappe.datetime.str_to_user(data.to_date)} · ${__("total")} ${money(totals.disponible)}${receivablesSuffix}`;
	}

	async function refresh() {
		setError("");
		btn.disabled = true;
		meta.textContent = __("Calcul en cours…");
		grid.innerHTML = `<div class='${CSS_CLASS.loading}'>${__("Chargement des soldes…")}</div>`;

		try {
			const response = await frappe.call({
				method: API_METHOD,
				args: {
					to_date: frappe.datetime.get_today(),
				},
			});
			const data = response.message;
			currency = data.currency || currency;
			const units = data.units || [];

			if (!units.length) {
				throw new Error(__("Aucun centre de coût trouvé."));
			}

			renderMeta(data);
			grid.innerHTML = units.map(cardHtml).join("");
		} catch (error) {
			console.error(error);
			grid.innerHTML = "";
			meta.textContent = __("Erreur");
			setError((error && error.message) || String(error));
		} finally {
			btn.disabled = false;
		}
	}

	btn.addEventListener("click", refresh);
	refresh();
};
