const list = document.querySelector("#skill-list");
const status = document.querySelector("#catalog-status");
const sourceRoot = "https://github.com/FilhoRicardo/esg-skills-marketplace/tree/main/skills/";

function setState(message, detail, link) {
  const card = document.createElement("div");
  card.className = "state-card aster-inner";

  const heading = document.createElement("p");
  heading.className = "state-title";
  heading.textContent = message;
  card.append(heading);

  if (detail) {
    const copy = document.createElement("p");
    copy.textContent = detail;
    card.append(copy);
  }

  if (link) {
    const anchor = document.createElement("a");
    anchor.href = link;
    anchor.textContent = "Browse the source catalogue";
    card.append(anchor);
  }

  list.replaceChildren(card);
}

function createSkillCard(entry, index) {
  const article = document.createElement("article");
  article.className = "skill-card aster-inner";

  const meta = document.createElement("div");
  meta.className = "card-meta";

  const number = document.createElement("span");
  number.className = "aster-eyebrow";
  number.textContent = String(index + 1).padStart(2, "0");

  const category = document.createElement("span");
  category.className = "aster-badge";
  category.textContent = entry.category;
  meta.append(number, category);

  const title = document.createElement("h3");
  title.textContent = entry.title;

  const description = document.createElement("p");
  description.textContent = entry.description;

  const link = document.createElement("a");
  link.className = "aster-btn aster-btn--primary card-link";
  link.href = `${sourceRoot}${encodeURIComponent(entry.slug)}`;
  link.target = "_blank";
  link.rel = "noreferrer";
  link.textContent = "Inspect skill source";
  link.setAttribute("aria-label", `Inspect ${entry.title} source on GitHub`);

  article.append(meta, title, description, link);
  return article;
}

async function loadCatalogue() {
  try {
    const response = await fetch("./catalog.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`Catalogue request failed with ${response.status}`);

    const catalogue = await response.json();
    if (!Array.isArray(catalogue)) throw new TypeError("Catalogue data must be an array");

    status.textContent = `${catalogue.length} reviewed ${catalogue.length === 1 ? "skill" : "skills"}`;
    list.setAttribute("aria-busy", "false");

    if (catalogue.length === 0) {
      setState(
        "No approved skills yet.",
        "The catalogue stays empty until a skill passes the repository trust gate.",
        "https://github.com/FilhoRicardo/esg-skills-marketplace/tree/main/skills",
      );
      return;
    }

    list.replaceChildren(...catalogue.map(createSkillCard));
  } catch (error) {
    console.error("Unable to load catalogue", error);
    status.textContent = "Catalogue unavailable";
    list.setAttribute("aria-busy", "false");
    setState(
      "The catalogue could not be loaded.",
      "The reviewed source remains available on GitHub.",
      "https://github.com/FilhoRicardo/esg-skills-marketplace/tree/main/skills",
    );
  }
}

loadCatalogue();
