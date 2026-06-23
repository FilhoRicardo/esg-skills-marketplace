const list = document.querySelector("#skill-list");
const status = document.querySelector("#catalog-status");
const submissionStatus = document.querySelector("#submission-status");
const form = document.querySelector("#submission-form");
const skillFileInput = document.querySelector("#skill-file");
const marketplaceTitleInput = document.querySelector("#marketplace-title");
const publicNameInput = document.querySelector("#public-name");
const publicContactInput = document.querySelector("#public-contact");
const rightsInput = document.querySelector("#rights-confirmed");
const boundaryInput = document.querySelector("#boundary-confirmed");
const submitButton = document.querySelector("#submit-button");
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

function slugifyTitle(title) {
  const slug = title
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  if (!SLUG_RE.test(slug)) {
    throw new Error("Public title must include letters or numbers that can form a URL slug.");
  }
  return slug;
}

function validateSkillMarkdown(text) {
  if (text.trim().length < intakeConfig.minSkillChars) {
    throw new Error(
      `Skill instructions must contain at least ${intakeConfig.minSkillChars} characters.`,
    );
  }
  const hasInvisibleControl = [...text].some(
    (character) => !"\n\r\t".includes(character) && /[\p{Cc}\p{Cf}]/u.test(character),
  );
  if (hasInvisibleControl) {
    throw new Error("Skill instructions contain unsupported invisible control characters.");
  }
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

  const keys = Object.keys(data);
  if (keys.length !== 1 || keys[0] !== "title") {
    throw new Error("Submission metadata may only contain the public title.");
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

  validateSkillMarkdown(skillText);
  const marketplace = parseMarketplace(marketplaceText);
  const title = typeof marketplace.title === "string" ? marketplace.title.trim() : "";
  if (
    title.length < intakeConfig.minTitleChars ||
    title.length > intakeConfig.maxTitleChars ||
    /[\r\n\t]/.test(title)
  ) {
    throw new Error(
      `Public title must contain ${intakeConfig.minTitleChars} to ${intakeConfig.maxTitleChars} characters on one line.`,
    );
  }

  return {
    slug: slugifyTitle(title),
    title,
  };
}

function updatePreview(nextPreview) {
  preview = nextPreview;
}

function syncSubmitButton() {
  submitButton.disabled = !(
    intakeConfig &&
    preview &&
    rightsInput.checked &&
    boundaryInput.checked
  );
}

async function readSubmissionValues() {
  const skillFile = skillFileInput.files?.[0];
  const title = marketplaceTitleInput.value.trim();
  if (!skillFile || !title) {
    return null;
  }

  return {
    skillText: await skillFile.text(),
    marketplaceText: JSON.stringify({ title }),
  };
}

async function refreshSubmissionPreview() {
  clearFeedback();

  if (!intakeConfig) {
    setSubmissionTone("Loading intake rules", "neutral");
    syncSubmitButton();
    return;
  }

  const submission = await readSubmissionValues();
  if (!submission) {
    updatePreview(null);
    setSubmissionTone("Add the file and title", "neutral");
    syncSubmitButton();
    return;
  }

  try {
    updatePreview(buildPreview(submission.skillText, submission.marketplaceText));
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
    setSubmissionTone("Ready for skill details", "neutral");
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

    const submission = await readSubmissionValues();
    if (!submission) {
      setFeedback(
        "Complete the skill details",
        "Choose `SKILL.md` and enter a public title before sending the submission.",
        "error",
      );
      return;
    }

    let nextPreview;
    try {
      nextPreview = buildPreview(submission.skillText, submission.marketplaceText);
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
        skill_md: submission.skillText,
        marketplace_json: submission.marketplaceText,
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
          "Your skill details passed the browser checks and entered the review queue. Automated checks and maintainer review still run before anything becomes public.",
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
          "The skill details passed browser checks, but local preview does not include the hidden intake proxy. The live published site will.",
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

  skillFileInput.addEventListener("change", () => {
    refreshSubmissionPreview();
  });

  marketplaceTitleInput.addEventListener("input", () => {
    refreshSubmissionPreview();
  });

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
