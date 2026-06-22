const list = document.querySelector("#skill-list");
const status = document.querySelector("#catalog-status");
const submissionStatus = document.querySelector("#submission-status");
const form = document.querySelector("#submission-form");
const skillFileInput = document.querySelector("#skill-file");
const marketplaceFileInput = document.querySelector("#marketplace-file");
const publicNameInput = document.querySelector("#public-name");
const publicContactInput = document.querySelector("#public-contact");
const rightsInput = document.querySelector("#rights-confirmed");
const boundaryInput = document.querySelector("#boundary-confirmed");
const submitButton = document.querySelector("#submit-button");
const previewHeading = document.querySelector("#preview-title");
const previewSlug = document.querySelector("#preview-slug");
const previewTitle = document.querySelector("#preview-title-value");
const previewCategory = document.querySelector("#preview-category");
const previewDetail = document.querySelector("#preview-detail");
const feedbackCard = document.querySelector("#submission-feedback");
const feedbackTitle = document.querySelector("#feedback-title");
const feedbackDetail = document.querySelector("#feedback-detail");

const LOCAL_HOSTS = new Set(["127.0.0.1", "localhost", "0.0.0.0", "::1"]);
const LOCAL_PREVIEW_RESPONSE_CODES = new Set([404, 405, 501]);
const SLUG_RE = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

let intakeConfig = null;
let preview = null;

function setState(message, detail) {
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

  list.replaceChildren(card);
}

function setFeedback(title, detail, tone) {
  feedbackCard.hidden = false;
  feedbackCard.dataset.tone = tone;
  feedbackTitle.textContent = title;
  feedbackDetail.textContent = detail;
}

function clearFeedback() {
  feedbackCard.hidden = true;
  feedbackCard.dataset.tone = "";
  feedbackTitle.textContent = "Submission status";
  feedbackDetail.textContent = "";
}

function setSubmissionTone(message, tone = "neutral") {
  submissionStatus.textContent = message;
  submissionStatus.dataset.tone = tone;
}

function bytesLength(value) {
  return new TextEncoder().encode(value).length;
}

function normalizePublicField(value, maxChars) {
  return value.replace(/\s+/g, " ").trim().slice(0, maxChars);
}

function parseFrontmatter(text) {
  const lines = text.split(/\r?\n/);
  if (lines[0] !== "---") {
    throw new Error("SKILL.md must start with YAML frontmatter.");
  }

  const closing = lines.indexOf("---", 1);
  if (closing === -1) {
    throw new Error("SKILL.md frontmatter needs a closing --- line.");
  }

  const metadata = {};
  for (const line of lines.slice(1, closing)) {
    if (!line.trim() || /^\s*#/.test(line)) continue;
    if (!line.includes(":") || /^[\t ]/.test(line)) {
      throw new Error("SKILL.md frontmatter must use simple top-level key: value pairs.");
    }
    const [rawKey, ...rest] = line.split(":");
    const key = rawKey.trim();
    const value = rest.join(":").trim().replace(/^['"]|['"]$/g, "");
    if (!key || !value) {
      throw new Error("SKILL.md frontmatter keys and values cannot be empty.");
    }
    metadata[key] = value;
  }

  return {
    metadata,
    body: lines.slice(closing + 1).join("\n").trim(),
  };
}

function parseMarketplace(text) {
  let data;
  try {
    data = JSON.parse(text);
  } catch (_error) {
    throw new Error("marketplace.json must be valid JSON.");
  }

  if (typeof data !== "object" || data === null || Array.isArray(data)) {
    throw new Error("marketplace.json must be a JSON object.");
  }

  const keys = Object.keys(data).sort();
  if (keys.length !== 2 || keys[0] !== "category" || keys[1] !== "title") {
    throw new Error("marketplace.json may only contain title and category.");
  }

  return data;
}

function buildPreview(skillText, marketplaceText) {
  if (!intakeConfig) {
    throw new Error("Submission rules are still loading.");
  }

  if (bytesLength(skillText) > intakeConfig.maxSkillFileBytes) {
    throw new Error(
      `SKILL.md exceeds the site intake cap of ${intakeConfig.maxSkillFileBytes.toLocaleString()} bytes.`,
    );
  }
  if (bytesLength(marketplaceText) > intakeConfig.maxMarketplaceFileBytes) {
    throw new Error(
      `marketplace.json exceeds the site intake cap of ${intakeConfig.maxMarketplaceFileBytes.toLocaleString()} bytes.`,
    );
  }

  const { metadata, body } = parseFrontmatter(skillText);
  const slug = metadata.name || "";
  if (!SLUG_RE.test(slug)) {
    throw new Error("SKILL.md frontmatter name must be a lowercase hyphenated slug.");
  }

  const description = (metadata.description || "").trim();
  if (
    description.length < intakeConfig.minDescriptionChars ||
    description.length > intakeConfig.maxDescriptionChars
  ) {
    throw new Error(
      `SKILL.md description must contain ${intakeConfig.minDescriptionChars} to ${intakeConfig.maxDescriptionChars} characters.`,
    );
  }

  if (body.length < intakeConfig.minBodyChars) {
    throw new Error(
      `SKILL.md body must contain at least ${intakeConfig.minBodyChars} characters of meaningful instructions.`,
    );
  }

  const marketplace = parseMarketplace(marketplaceText);
  if (!intakeConfig.allowedCategories.includes(marketplace.category)) {
    throw new Error(
      `marketplace.json category must be one of: ${intakeConfig.allowedCategories.join(", ")}.`,
    );
  }

  if (typeof marketplace.title !== "string" || marketplace.title.trim().length < 4) {
    throw new Error("marketplace.json title must contain at least 4 characters.");
  }

  return {
    slug,
    title: marketplace.title.trim(),
    category: marketplace.category,
    description,
  };
}

function updatePreview(nextPreview) {
  preview = nextPreview;
  if (!nextPreview) {
    previewHeading.textContent = "Waiting for the two required files";
    previewSlug.textContent = "—";
    previewTitle.textContent = "—";
    previewCategory.textContent = "—";
    previewDetail.textContent =
      "Choose `SKILL.md` and `marketplace.json`, and the site will parse them before anything is queued.";
    return;
  }

  previewHeading.textContent = nextPreview.title;
  previewSlug.textContent = nextPreview.slug;
  previewTitle.textContent = nextPreview.title;
  previewCategory.textContent = nextPreview.category;
  previewDetail.textContent = nextPreview.description;
}

function syncSubmitButton() {
  submitButton.disabled = !(
    intakeConfig &&
    preview &&
    rightsInput.checked &&
    boundaryInput.checked
  );
}

async function readSelectedFiles() {
  const skillFile = skillFileInput.files?.[0];
  const marketplaceFile = marketplaceFileInput.files?.[0];
  if (!skillFile || !marketplaceFile) {
    return null;
  }

  return {
    skillText: await skillFile.text(),
    marketplaceText: await marketplaceFile.text(),
  };
}

async function refreshSubmissionPreview() {
  clearFeedback();

  if (!intakeConfig) {
    setSubmissionTone("Loading intake rules", "neutral");
    syncSubmitButton();
    return;
  }

  const files = await readSelectedFiles();
  if (!files) {
    updatePreview(null);
    setSubmissionTone("Choose the two required files", "neutral");
    syncSubmitButton();
    return;
  }

  try {
    updatePreview(buildPreview(files.skillText, files.marketplaceText));
    setSubmissionTone("Browser checks complete", "success");
  } catch (error) {
    updatePreview(null);
    setSubmissionTone("Fix the files before queueing", "error");
    setFeedback("Submission needs changes", error.message, "error");
  }

  syncSubmitButton();
}

function createSkillCard(entry, index) {
  const article = document.createElement("article");
  article.className = "skill-card";

  const number = document.createElement("span");
  number.className = "skill-number aster-mono";
  number.textContent = String(index + 1).padStart(2, "0");

  const category = document.createElement("span");
  category.className = "skill-category aster-badge";
  category.textContent = entry.category;

  const title = document.createElement("h3");
  title.className = "skill-title";
  title.textContent = entry.title;

  const description = document.createElement("p");
  description.className = "skill-description";
  description.textContent = entry.description;

  const link = document.createElement("a");
  link.className = "aster-btn aster-btn--primary card-link";
  link.href = `./downloads/${encodeURIComponent(entry.slug)}.zip`;
  link.download = `${entry.slug}.zip`;
  link.textContent = "Download .zip";
  link.setAttribute("aria-label", `Download the reviewed ${entry.title} bundle`);

  article.append(number, title, category, description, link);
  return article;
}

async function loadCatalogue() {
  try {
    const response = await fetch("./catalog.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`Catalogue request failed with ${response.status}`);

    const catalogue = await response.json();
    if (!Array.isArray(catalogue)) throw new TypeError("Catalogue data must be an array");

    status.textContent = `${catalogue.length} ${catalogue.length === 1 ? "skill" : "skills"}`;
    list.setAttribute("aria-busy", "false");

    if (catalogue.length === 0) {
      setState(
        "No approved bundles yet.",
        "The catalogue stays empty until a skill passes the checks and maintainer review.",
      );
      return;
    }

    list.replaceChildren(...catalogue.map(createSkillCard));
  } catch (error) {
    console.error("Unable to load catalogue", error);
    status.textContent = "Catalogue unavailable";
    list.setAttribute("aria-busy", "false");
    setState(
      "The reviewed bundles could not be loaded.",
      "Try again shortly. The live site may be redeploying updated catalogue data.",
    );
  }
}

async function loadSubmissionConfig() {
  try {
    const response = await fetch("./submission-config.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`Submission config request failed with ${response.status}`);

    intakeConfig = await response.json();
    setSubmissionTone("Ready for a two-file submission", "success");
  } catch (error) {
    console.error("Unable to load submission config", error);
    intakeConfig = null;
    setSubmissionTone("Submission unavailable", "error");
    setFeedback(
      "Submission is unavailable",
      "The public intake rules could not be loaded, so the site is not accepting new bundles right now.",
      "error",
    );
  }

  syncSubmitButton();
}

if (form) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearFeedback();

    const files = await readSelectedFiles();
    if (!files) {
      setFeedback(
        "Two files are required",
        "Choose `SKILL.md` and `marketplace.json` before queueing the submission.",
        "error",
      );
      return;
    }

    let nextPreview;
    try {
      nextPreview = buildPreview(files.skillText, files.marketplaceText);
      updatePreview(nextPreview);
    } catch (error) {
      setSubmissionTone("Fix the files before queueing", "error");
      setFeedback("Submission needs changes", error.message, "error");
      syncSubmitButton();
      return;
    }

    if (!rightsInput.checked || !boundaryInput.checked) {
      setFeedback(
        "Confirm both review statements",
        "The site only queues bundles when the redistribution and review-boundary statements are both confirmed.",
        "error",
      );
      syncSubmitButton();
      return;
    }

    submitButton.disabled = true;
    setSubmissionTone("Sending for review", "neutral");

    const payload = {
      ref: "main",
      inputs: {
        skill_md: files.skillText,
        marketplace_json: files.marketplaceText,
        public_name: normalizePublicField(publicNameInput.value, intakeConfig.maxPublicNameChars),
        public_contact: normalizePublicField(
          publicContactInput.value,
          intakeConfig.maxPublicContactChars,
        ),
        rights_confirmed: String(rightsInput.checked),
        boundary_confirmed: String(boundaryInput.checked),
      },
    };

    try {
      const response = await fetch(intakeConfig.dispatchPath, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (response.ok || response.status === 204) {
        form.reset();
        updatePreview(null);
        setSubmissionTone("Submission queued for intake", "success");
        setFeedback(
          "Submission queued",
          "Your files passed the browser checks and entered the review queue. Automated checks and maintainer review still run before anything becomes public.",
          "success",
        );
        syncSubmitButton();
        return;
      }

      if (
        LOCAL_HOSTS.has(window.location.hostname) &&
        LOCAL_PREVIEW_RESPONSE_CODES.has(response.status)
      ) {
        setSubmissionTone("Local preview cannot queue submissions", "neutral");
        setFeedback(
          "Local preview only",
          "The files passed browser checks, but local preview does not include the hidden intake proxy. The live published site will.",
          "neutral",
        );
        syncSubmitButton();
        return;
      }

      throw new Error(`Submission endpoint returned ${response.status}.`);
    } catch (error) {
      console.error("Unable to queue submission", error);
      setSubmissionTone("Submission unavailable", "error");
      setFeedback(
        "Submission could not be queued",
        "The site could not hand this bundle to the hidden intake service. Try again shortly or contact the maintainer if the problem persists.",
        "error",
      );
      syncSubmitButton();
    }
  });

  for (const field of [skillFileInput, marketplaceFileInput]) {
    field.addEventListener("change", () => {
      refreshSubmissionPreview();
    });
  }

  for (const field of [rightsInput, boundaryInput]) {
    field.addEventListener("change", () => {
      syncSubmitButton();
    });
  }

  updatePreview(null);
  loadSubmissionConfig();
}

if (list && status) {
  loadCatalogue();
}
