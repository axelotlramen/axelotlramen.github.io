/* =========================
   CSV parsing
========================= */

function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let inQuotes = false;

  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (inQuotes) {
      if (c === '"') {
        if (text[i + 1] === '"') {
          field += '"';
          i++;
        } else {
          inQuotes = false;
        }
      } else {
        field += c;
      }
    } else if (c === '"') {
      inQuotes = true;
    } else if (c === ",") {
      row.push(field);
      field = "";
    } else if (c === "\n" || c === "\r") {
      if (c === "\r" && text[i + 1] === "\n") i++;
      row.push(field);
      rows.push(row);
      row = [];
      field = "";
    } else {
      field += c;
    }
  }
  if (field.length > 0 || row.length > 0) {
    row.push(field);
    rows.push(row);
  }
  return rows.filter((r) => r.some((cell) => cell !== ""));
}

/* =========================
   Data
========================= */

const MODE_FAMILY_PREFIXES = ["Memory of Chaos", "Apocalyptic Shadow", "Pure Fiction", "Anomaly Arbitration"];

function modeFamily(mode) {
  return MODE_FAMILY_PREFIXES.find((prefix) => mode.startsWith(prefix)) || mode;
}

class EndgameHistoryStore {
  async load() {
    const response = await fetch("/data/endgame_history.csv");
    if (!response.ok) throw new Error("Failed to fetch endgame history CSV");
    const text = await response.text();
    const [header, ...data] = parseCsv(text);
    return data.map((row) => Object.fromEntries(header.map((key, i) => [key, row[i] ?? ""])));
  }
}

/* =========================
   App
========================= */

class EndgameHistoryApp {
  constructor() {
    this.store = new EndgameHistoryStore();
    this.rows = [];
    this.selectedModes = new Set();
    this.selectedCharacters = new Set();
    this.bossFilter = "";
  }

  async init() {
    const results = document.getElementById("endgame-results");
    try {
      this.rows = await this.store.load();
    } catch (err) {
      console.error("Endgame history load error:", err);
      results.innerHTML = '<p class="mode-empty">Could not load endgame history.</p>';
      return;
    }

    this.bossNameToIcon = this._buildBossNameToIcon();

    this.renderModeFilters();
    this.renderCharacterOptions();
    this.attachFilterEvents();
    this.renderResults();
  }

  // Different Boss names can point at the same underlying monster (e.g. a boss with an
  // alternate title, or one that's also known by the character it mimics) - grouping by
  // icon lets a search for one name surface every row using any of its aliases.
  _buildBossNameToIcon() {
    const nameToIcon = new Map();
    for (const row of this.rows) {
      if (row.Boss && row["Boss Icon"]) nameToIcon.set(row.Boss, row["Boss Icon"]);
    }
    return nameToIcon;
  }

  _matchingBossIcons(query) {
    const icons = new Set();
    for (const [name, icon] of this.bossNameToIcon) {
      if (name.toLowerCase().includes(query)) icons.add(icon);
    }
    return icons;
  }

  get modes() {
    return [...new Set(this.rows.map((row) => modeFamily(row.Mode)))];
  }

  get characters() {
    const names = new Set();
    for (const row of this.rows) {
      for (let i = 1; i <= 4; i++) {
        const name = row[`Member ${i}`];
        if (name) names.add(name);
      }
    }
    return [...names].sort();
  }

  renderModeFilters() {
    const container = document.getElementById("endgame-mode-filters");
    container.innerHTML = this.modes
      .map((mode) => `<button type="button" class="endgame-mode-btn" data-mode="${mode}">${mode}</button>`)
      .join("");

    container.querySelectorAll(".endgame-mode-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const mode = btn.dataset.mode;
        if (this.selectedModes.has(mode)) {
          this.selectedModes.delete(mode);
          btn.classList.remove("active");
        } else {
          this.selectedModes.add(mode);
          btn.classList.add("active");
        }
        this.renderResults();
      });
    });
  }

  renderCharacterOptions() {
    const container = document.getElementById("endgame-character-options");
    container.innerHTML = this.characters
      .map(
        (name) => `
        <label class="endgame-character-option">
          <input type="checkbox" value="${name}">
          <span>${name}</span>
        </label>
      `
      )
      .join("");

    container.querySelectorAll("input[type=checkbox]").forEach((checkbox) => {
      checkbox.addEventListener("change", () => {
        if (checkbox.checked) this.selectedCharacters.add(checkbox.value);
        else this.selectedCharacters.delete(checkbox.value);
        this.renderResults();
      });
    });
  }

  attachFilterEvents() {
    const bossInput = document.getElementById("endgame-boss-filter");
    bossInput.addEventListener("input", () => {
      this.bossFilter = bossInput.value.trim().toLowerCase();
      this.renderResults();
    });

    const characterSearch = document.getElementById("endgame-character-search");
    characterSearch.addEventListener("input", () => {
      const query = characterSearch.value.trim().toLowerCase();
      document.querySelectorAll(".endgame-character-option").forEach((label) => {
        const name = label.textContent.trim().toLowerCase();
        label.style.display = name.includes(query) ? "" : "none";
      });
    });
  }

  renderResults() {
    const matchingBossIcons = this.bossFilter ? this._matchingBossIcons(this.bossFilter) : null;
    const filtered = this.rows.filter((row) => this._matches(row, matchingBossIcons));
    const container = document.getElementById("endgame-results");

    document.getElementById("endgame-result-count").textContent =
      `Showing ${filtered.length} of ${this.rows.length} entries`;

    if (filtered.length === 0) {
      container.innerHTML = '<p class="mode-empty">No matching endgame runs found.</p>';
      return;
    }

    container.innerHTML = `
      <div class="endgame-table-wrapper">
        <table class="endgame-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Version</th>
              <th>Mode</th>
              <th>Side</th>
              <th>Season ID</th>
              <th>Boss</th>
              <th class="endgame-icon-col">Boss Icon</th>
              <th class="endgame-icon-col">1</th>
              <th class="endgame-icon-col">2</th>
              <th class="endgame-icon-col">3</th>
              <th class="endgame-icon-col">4</th>
              <th>Score</th>
            </tr>
          </thead>
          <tbody>
            ${filtered.map((row) => this._renderRow(row)).join("")}
          </tbody>
        </table>
      </div>
    `;
  }

  _matches(row, matchingBossIcons) {
    if (this.selectedModes.size > 0 && !this.selectedModes.has(modeFamily(row.Mode))) return false;

    if (matchingBossIcons && (!row["Boss Icon"] || !matchingBossIcons.has(row["Boss Icon"]))) {
      return false;
    }

    if (this.selectedCharacters.size > 0) {
      const members = [row["Member 1"], row["Member 2"], row["Member 3"], row["Member 4"]];
      if (!members.some((name) => this.selectedCharacters.has(name))) return false;
    }

    return true;
  }

  _renderIconCell(iconUrl, name) {
    if (!iconUrl) return '<td class="endgame-icon-col"></td>';
    return `<td class="endgame-icon-col"><img class="endgame-icon" src="${iconUrl}" alt="${name || ""}" referrerpolicy="no-referrer"></td>`;
  }

  _renderRow(row) {
    return `
      <tr>
        <td>${row.Date}</td>
        <td>${row.Version}</td>
        <td>${row.Mode}</td>
        <td>${row.Side}</td>
        <td>${row["Season ID"]}</td>
        <td class="endgame-boss-cell${row.Boss ? "" : " endgame-boss-unknown"}">${row.Boss || "Not yet recorded"}</td>
        ${this._renderIconCell(row["Boss Icon"], row.Boss)}
        ${this._renderIconCell(row["Member 1 Icon"], row["Member 1"])}
        ${this._renderIconCell(row["Member 2 Icon"], row["Member 2"])}
        ${this._renderIconCell(row["Member 3 Icon"], row["Member 3"])}
        ${this._renderIconCell(row["Member 4 Icon"], row["Member 4"])}
        <td>${row.Score}</td>
      </tr>
    `;
  }
}

new EndgameHistoryApp().init();
