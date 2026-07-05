/* =========================
   Data
========================= */

class StatsStore {
  async load() {
    const response = await fetch("data/stats.json");
    if (!response.ok) throw new Error("Failed to fetch JSON");
    this.data = await response.json();
    return this.data;
  }
}

/* =========================
   Navigation
========================= */

class Router {
  constructor() {
    document.querySelectorAll(".sidebar nav button[data-page]").forEach((button) => {
      button.addEventListener("click", () => this.show(button.dataset.page));
    });
  }

  show(pageId) {
    document.querySelectorAll(".page").forEach((p) => {
      p.classList.remove("active");
    });
    document.getElementById(pageId).classList.add("active");
  }
}

/* =========================
   Shared rendering helpers
========================= */

class SectionRenderer {
  renderProfileCard(container, { title, avatarUrl, nickname, subtitle, stats }) {
    container.innerHTML = `
      <div class="card">
        ${title ? `<h2>${title}</h2>` : ""}
        <div class="avatar">
          <img src="${avatarUrl}" alt="${nickname}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;">
        </div>
        <div class="nickname">${nickname}</div>
        <div class="server-level">${subtitle}</div>
        <div class="stats">
          ${stats.map((s) => `<div class="stat">${s.label}<br><strong>${s.value}</strong></div>`).join("")}
        </div>
      </div>
    `;
  }

  renderMiniCard(container, title, lines) {
    container.innerHTML = `
      <div class="mini-card">
        <h3>${title}</h3>
        ${lines.map((l) => `<div class="line">${l.label} <strong>${l.value}</strong></div>`).join("")}
      </div>
    `;
  }

  renderCharacterCard({ iconUrl, name, badge, meta, level, weapon }) {
    return `
      <div class="endfield-char-card">
        <div class="endfield-char-avatar">
          <img src="${iconUrl}" alt="${name}">
          <div class="endfield-potential-badge">${badge}</div>
        </div>
        <div class="endfield-char-info">
          <div class="endfield-char-name">${name}</div>
          <div class="endfield-char-meta">${meta}</div>
          <div class="endfield-char-level">Lv. ${level}</div>
          ${
            weapon
              ? `<div class="endfield-char-weapon">
              <img src="${weapon.iconUrl}" alt="${weapon.name}">
              <span>${weapon.name}</span>
            </div>`
              : ""
          }
        </div>
      </div>
    `;
  }
}

/* =========================
   Home
========================= */

class HomeRenderer extends SectionRenderer {
  render(data) {
    const sr = data.hsr_data;
    const gi = data.genshin_data;
    const ef = data.endfield_data;

    if (sr) {
      this.renderProfileCard(document.getElementById("home-hsr"), {
        title: "Honkai: Star Rail",
        avatarUrl: sr.avatar_url,
        nickname: sr.nickname,
        subtitle: `Level ${sr.level}`,
        stats: [
          { label: "MoC Stars", value: sr.memory_of_chaos?.total_stars ?? 0 },
          { label: "TB Power", value: `${sr.stamina ?? 0}/300` },
        ],
      });
    }

    if (gi) {
      this.renderProfileCard(document.getElementById("home-genshin"), {
        title: "Genshin Impact",
        avatarUrl: gi.avatar_url,
        nickname: gi.nickname,
        subtitle: `AR ${gi.level}`,
        stats: [
          { label: "Achievements", value: gi.achievements },
          { label: "Resin", value: `${gi.resin ?? 0}/200` },
        ],
      });
    }

    if (ef) {
      this.renderProfileCard(document.getElementById("home-endfield"), {
        title: "Arknights: Endfield",
        avatarUrl: ef.avatar_url,
        nickname: ef.nickname,
        subtitle: `Level ${ef.level}`,
        stats: [
          { label: "Achievements", value: ef.achievements },
          { label: "Sanity", value: `${ef.stamina ?? 0}/240` },
        ],
      });
    }
  }
}

/* =========================
   Honkai: Star Rail
========================= */

class HsrRenderer extends SectionRenderer {
  render(data) {
    const sr = data.hsr_data;
    if (!sr) return;

    this.renderProfile(sr);
    this.renderCharacters(sr);
    this.renderMoc(sr);
  }

  renderProfile(sr) {
    this.renderProfileCard(document.getElementById("hsr-profile"), {
      avatarUrl: sr.avatar_url,
      nickname: sr.nickname,
      subtitle: `NA · Level ${sr.level}`,
      stats: [
        { label: "Active Days", value: sr.active_days },
        { label: "Achievements", value: sr.achievements },
        { label: "Characters", value: sr.avatar_count },
        { label: "Chests", value: sr.chest_count },
      ],
    });

    const loggedIn = (sr.current_train_score ?? 0) !== 0;
    this.renderMiniCard(document.getElementById("trailblaze-card"), "Today's Status", [
      { label: "Trailblaze Power", value: `${sr.stamina ?? 0}/300` },
      { label: "Daily Training", value: `${sr.current_train_score ?? 0}/500` },
      { label: "Logged In Today", value: loggedIn ? "Yes" : "No" },
    ]);
  }

  renderCharacters(sr) {
    const chars = sr?.five_star_characters;
    if (!chars) return;

    const container = document.getElementById("hsr-characters");
    container.innerHTML = Object.entries(chars)
      .map(([name, char]) =>
        this.renderCharacterCard({
          iconUrl: char.icon,
          name,
          badge: `E${char.eidolon}`,
          meta: ` ${char.element} · ${char.path}`,
          level: char.level,
          weapon: char.lc ? { iconUrl: char.lc.icon, name: char.lc.name } : null,
        })
      )
      .join("");
  }

  renderMoc(sr) {
    const moc = sr?.memory_of_chaos;
    if (!moc || !moc.floor_data) return;

    const floor = moc.floor_data;
    const container = document.getElementById("moc-content");

    container.innerHTML = `
      <div class="moc-card">
        <div class="moc-header">
          <div class="moc-floor">${floor.floor}</div>
          <div class="moc-cycles">${floor.cycles} cycles · ⭐ ${moc.total_stars}</div>
        </div>
        <div class="moc-node-row">
          ${this._renderMocNode("Node 1", floor.first_half)}
          ${this._renderMocNode("Node 2", floor.second_half)}
        </div>
      </div>
    `;
  }

  _renderMocNode(title, characters) {
    return `
      <div class="moc-node">
        <div class="moc-node-title">${title}</div>
        <div class="moc-avatars">
          ${characters
            .map(
              (char) => `
            <div class="moc-avatar">
              <img src="https://stardb.gg/api/static/StarRailResWebp/icon/character/${char.id}.webp" alt="Character ${char.id}">
              <div class="eidolon-badge">E${char.eidolon}</div>
            </div>
          `
            )
            .join("")}
        </div>
      </div>
    `;
  }
}

/* =========================
   Genshin Impact
========================= */

class GenshinRenderer extends SectionRenderer {
  render(data) {
    const gi = data.genshin_data;
    if (!gi) return;

    this.renderProfileCard(document.getElementById("genshin-profile"), {
      avatarUrl: gi.avatar_url,
      nickname: gi.nickname,
      subtitle: `AR ${gi.level}`,
      stats: [
        { label: "Achievements", value: gi.achievements },
        { label: "Active Days", value: gi.active_days },
        { label: "Characters", value: gi.avatar_count },
        { label: "Oculus", value: gi.oculus },
        { label: "Chests", value: gi.chest_count },
      ],
    });

    const loggedIn = (gi.daily_task ?? 0) !== 0;
    this.renderMiniCard(document.getElementById("genshin-notes"), "Today's Status", [
      { label: "Resin", value: `${gi.resin ?? 0}/200` },
      { label: "Daily Tasks", value: `${gi.daily_task ?? 0}/4` },
      { label: "Logged In Today", value: loggedIn ? "Yes" : "No" },
    ]);
  }
}

/* =========================
   Arknights: Endfield
========================= */

class EndfieldRenderer extends SectionRenderer {
  render(data) {
    const ef = data.endfield_data;
    if (!ef) return;

    this.renderProfileCard(document.getElementById("endfield-profile"), {
      avatarUrl: ef.avatar_url,
      nickname: ef.nickname,
      subtitle: `Level ${ef.level}`,
      stats: [
        { label: "Active Days", value: ef.active_days },
        { label: "Achievements", value: ef.achievements },
        { label: "Characters", value: ef.avatar_count },
        { label: "Chests", value: ef.chest_count },
      ],
    });

    const loggedIn = ef.daily_mission > 0;
    this.renderMiniCard(document.getElementById("endfield-status"), "Today's Status", [
      { label: "Sanity", value: `${ef.stamina ?? 0}/240` },
      { label: "Daily Missions", value: `${ef.daily_mission ?? 0}/100` },
      { label: "Logged In Today", value: loggedIn ? "Yes" : "No" },
    ]);

    this.renderRoster(ef);
  }

  renderRoster(ef) {
    const roster = document.getElementById("endfield-roster");
    roster.innerHTML = "";

    const chars = ef.six_star_characters;
    if (!chars) return;

    // Only show rarity 6 characters, sorted by level desc
    const sixStars = Object.entries(chars)
      .filter(([, c]) => c.rarity === "6")
      .sort(([, a], [, b]) => b.level - a.level);

    roster.innerHTML = sixStars
      .map(([name, char]) =>
        this.renderCharacterCard({
          iconUrl: char.avatarSqUrl,
          name,
          badge: `P${char.potential}`,
          meta: `${char.profession} · ${char.property}`,
          level: char.level,
          weapon: char.weapon ? { iconUrl: char.weapon.iconUrl, name: char.weapon.name } : null,
        })
      )
      .join("");
  }
}

/* =========================
   App
========================= */

class App {
  constructor() {
    this.store = new StatsStore();
    this.router = new Router();
    this.renderers = [new HomeRenderer(), new HsrRenderer(), new GenshinRenderer(), new EndfieldRenderer()];
  }

  async init() {
    try {
      const data = await this.store.load();
      this.renderers.forEach((renderer) => renderer.render(data));
    } catch (err) {
      console.error("Stats load error:", err);
    }
  }
}

new App().init();
