// Shows the CV chosen with the controls, keeps the choice in the address, and follows the system's color scheme.

const manifest = JSON.parse(document.getElementById("manifest").textContent);
const root = document.documentElement.dataset.root;
const params = new URLSearchParams(location.search);

const variantIds = manifest.variants.map((variant) => variant.id);
const localeIds = manifest.locales.map((locale) => locale.id);

// The first of the browser's languages that has a CV, matched by its primary subtag.
function preferredLocale() {
  for (const language of navigator.languages ?? [navigator.language]) {
    const primary = language.toLowerCase().split("-")[0];
    if (localeIds.includes(primary)) return primary;
  }
  return localeIds[0];
}

const state = {
  variant: manifest.fixed ?? (variantIds.includes(params.get("variant")) ? params.get("variant") : variantIds[0]),
  locale: localeIds.includes(params.get("lang")) ? params.get("lang") : preferredLocale(),
};

function optionButtons(container, items, label, onSelect) {
  container.replaceChildren(
    ...items.map((item) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "option";
      button.dataset.id = item.id;
      button.textContent = label(item);
      button.addEventListener("click", () => onSelect(item.id));
      return button;
    }),
  );
}

function update() {
  const locale = manifest.locales.find((locale) => locale.id === state.locale);
  const variant = manifest.variants.find((variant) => variant.id === state.variant);
  const pdf = `${root}${state.variant}-${state.locale}.pdf`;

  document.documentElement.lang = state.locale;
  for (const element of document.querySelectorAll("[data-string]")) {
    element.textContent = locale.strings[element.dataset.string];
  }

  optionButtons(
    document.getElementById("variants"),
    manifest.variants,
    (item) => item.name[state.locale],
    select("variant"),
  );
  optionButtons(document.getElementById("locales"), manifest.locales, (item) => item.name, select("locale"));
  for (const button of document.querySelectorAll(".option")) {
    const current = button.parentElement.id === "variants" ? state.variant : state.locale;
    button.setAttribute("aria-pressed", String(button.dataset.id === current));
  }

  const frame = document.getElementById("pdf");
  frame.title = `${manifest.name} · ${variant.name[state.locale]}`;
  if (frame.getAttribute("src") !== pdf) frame.setAttribute("src", pdf);
  const download = document.getElementById("download");
  download.href = pdf;
  download.download = `${manifest.name.replaceAll(" ", "_")}_CV.pdf`;

  const query = new URLSearchParams({ ...(manifest.fixed ? {} : { variant: state.variant }), lang: state.locale });
  history.replaceState(null, "", `?${query}`);
}

function select(key) {
  return (id) => {
    state[key] = id;
    update();
  };
}

// lattice gates its dark polarity on an attribute, which the page sets on load and this keeps in step with the system.
matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (event) => {
  document.documentElement.dataset.theme = event.matches ? "dark" : "light";
});

document.getElementById("variant-group").hidden = Boolean(manifest.fixed);
update();
