import { useMemo, useState } from "react";
import { useEndgameHistory, type EndgameRow } from "@/hooks/useEndgameHistory";
import { EmptyState } from "@/components/stats/EmptyState";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Doodle } from "@/components/decor/Doodle";
import { cn } from "@/lib/utils";

const MODE_FAMILY_PREFIXES = [
  "Memory of Chaos",
  "Apocalyptic Shadow",
  "Pure Fiction",
  "Anomaly Arbitration",
];

const MODE_COLORS: Record<string, string> = {
  "Memory of Chaos": "var(--tab-endfield)",
  "Apocalyptic Shadow": "var(--tab-hsr)",
  "Pure Fiction": "var(--tab-genshin)",
  "Anomaly Arbitration": "var(--tab-home)",
};

function modeFamily(mode: string): string {
  return MODE_FAMILY_PREFIXES.find((prefix) => mode.startsWith(prefix)) ?? mode;
}

function IconCell({ url, name }: { url: string; name: string }) {
  if (!url) return <td className="w-10" />;
  return (
    <td className="w-10 p-1">
      <img src={url} alt={name} referrerPolicy="no-referrer" className="size-8 rounded-full border border-border" />
    </td>
  );
}

export function Endgame() {
  const { rows, loading, error } = useEndgameHistory();
  const [selectedModes, setSelectedModes] = useState<Set<string>>(new Set());
  const [selectedCharacters, setSelectedCharacters] = useState<Set<string>>(new Set());
  const [bossFilter, setBossFilter] = useState("");
  const [characterSearch, setCharacterSearch] = useState("");

  const modes = useMemo(() => [...new Set(rows.map((row) => modeFamily(row.Mode)))], [rows]);

  const characters = useMemo(() => {
    const names = new Set<string>();
    for (const row of rows) {
      for (let i = 1; i <= 4; i++) {
        const name = row[`Member ${i}`];
        if (name) names.add(name);
      }
    }
    return [...names].sort();
  }, [rows]);

  const bossNameToIcon = useMemo(() => {
    const map = new Map<string, string>();
    for (const row of rows) {
      if (row.Boss && row["Boss Icon"]) map.set(row.Boss, row["Boss Icon"]);
    }
    return map;
  }, [rows]);

  const matchingBossIcons = useMemo(() => {
    if (!bossFilter) return null;
    const query = bossFilter.trim().toLowerCase();
    if (!query) return null;
    const icons = new Set<string>();
    for (const [name, icon] of bossNameToIcon) {
      if (name.toLowerCase().includes(query)) icons.add(icon);
    }
    return icons;
  }, [bossFilter, bossNameToIcon]);

  const filtered = useMemo(() => {
    return rows.filter((row) => {
      if (selectedModes.size > 0 && !selectedModes.has(modeFamily(row.Mode))) return false;
      if (matchingBossIcons && (!row["Boss Icon"] || !matchingBossIcons.has(row["Boss Icon"]))) return false;
      if (selectedCharacters.size > 0) {
        const members = [row["Member 1"], row["Member 2"], row["Member 3"], row["Member 4"]];
        if (!members.some((name) => selectedCharacters.has(name))) return false;
      }
      return true;
    });
  }, [rows, selectedModes, matchingBossIcons, selectedCharacters]);

  function toggleMode(mode: string) {
    setSelectedModes((prev) => {
      const next = new Set(prev);
      if (next.has(mode)) next.delete(mode);
      else next.add(mode);
      return next;
    });
  }

  function toggleCharacter(name: string, checked: boolean) {
    setSelectedCharacters((prev) => {
      const next = new Set(prev);
      if (checked) next.add(name);
      else next.delete(name);
      return next;
    });
  }

  const visibleCharacters = characterSearch
    ? characters.filter((c) => c.toLowerCase().includes(characterSearch.toLowerCase()))
    : characters;

  return (
    <div className="relative">
      <Doodle kind="heart" color="var(--tab-hsr)" className="top-0 right-10" rotate="10deg" size={20} />
      <h1 className="inline-block -rotate-2 text-5xl" style={{ fontFamily: "var(--font-heading)" }}>
        endgame log
      </h1>

      {loading && <p className="mt-6 text-sm text-muted-foreground">Loading endgame history…</p>}
      {error && <p className="mt-6 text-sm text-destructive">Couldn't load endgame history: {error}</p>}

      {!loading && !error && (
        <div className="mt-8 space-y-6">
          <div className="relative rounded-sm border border-border bg-card p-5 pt-7 shadow-[3px_5px_0_rgba(0,0,0,0.1)]">
            <div
              className="absolute -top-3 left-8 h-6 w-16 -rotate-2 opacity-80"
              style={{ backgroundColor: "var(--tab-hsr)" }}
            />

            <div>
              <div className="text-xs font-semibold tracking-wide text-muted-foreground uppercase">Mode</div>
              <div className="mt-2 flex flex-wrap gap-2">
                {modes.map((mode) => (
                  <button
                    key={mode}
                    type="button"
                    onClick={() => toggleMode(mode)}
                    className={cn(
                      "rounded-full border px-3 py-1 text-sm transition-colors",
                      selectedModes.has(mode)
                        ? "border-transparent text-white"
                        : "border-border text-muted-foreground hover:text-foreground"
                    )}
                    style={selectedModes.has(mode) ? { backgroundColor: MODE_COLORS[mode] ?? "var(--tab-home)" } : undefined}
                  >
                    {mode}
                  </button>
                ))}
              </div>
            </div>

            <div className="mt-4">
              <div className="text-xs font-semibold tracking-wide text-muted-foreground uppercase">Boss</div>
              <Input
                value={bossFilter}
                onChange={(e) => setBossFilter(e.target.value)}
                placeholder="Search boss name…"
                className="mt-2 max-w-xs"
              />
            </div>

            <div className="mt-4">
              <div className="text-xs font-semibold tracking-wide text-muted-foreground uppercase">Team member</div>
              <Input
                value={characterSearch}
                onChange={(e) => setCharacterSearch(e.target.value)}
                placeholder="Filter character list…"
                className="mt-2 max-w-xs"
              />
              <div className="mt-2 grid max-h-40 grid-cols-2 gap-x-4 gap-y-1 overflow-y-auto sm:grid-cols-3 lg:grid-cols-4">
                {visibleCharacters.map((name) => (
                  <label key={name} className="flex items-center gap-2 text-sm">
                    <Checkbox
                      checked={selectedCharacters.has(name)}
                      onCheckedChange={(checked) => toggleCharacter(name, checked === true)}
                    />
                    {name}
                  </label>
                ))}
              </div>
            </div>
          </div>

          <p className="text-sm text-muted-foreground">
            Showing {filtered.length} of {rows.length} entries
          </p>

          {filtered.length === 0 ? (
            <EmptyState message="No matching endgame runs found." />
          ) : (
            <div className="overflow-x-auto rounded-sm border border-border bg-card">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border text-left text-xs tracking-wide text-muted-foreground uppercase">
                    <th className="p-2">Date</th>
                    <th className="p-2">Version</th>
                    <th className="p-2">Mode</th>
                    <th className="p-2">Side</th>
                    <th className="p-2">Season ID</th>
                    <th className="p-2">Boss</th>
                    <th className="w-10" />
                    <th className="w-10" />
                    <th className="w-10" />
                    <th className="w-10" />
                    <th className="w-10" />
                    <th className="p-2">Score</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((row, i) => (
                    <EndgameTableRow key={i} row={row} />
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function EndgameTableRow({ row }: { row: EndgameRow }) {
  return (
    <tr className="border-b border-border last:border-0">
      <td className="p-2">{row.Date}</td>
      <td className="p-2">{row.Version}</td>
      <td className="p-2">{row.Mode}</td>
      <td className="p-2">{row.Side}</td>
      <td className="p-2">{row["Season ID"]}</td>
      <td className={cn("p-2", !row.Boss && "text-muted-foreground italic")}>
        {row.Boss || "Not yet recorded"}
      </td>
      <IconCell url={row["Boss Icon"]} name={row.Boss} />
      <IconCell url={row["Member 1 Icon"]} name={row["Member 1"]} />
      <IconCell url={row["Member 2 Icon"]} name={row["Member 2"]} />
      <IconCell url={row["Member 3 Icon"]} name={row["Member 3"]} />
      <IconCell url={row["Member 4 Icon"]} name={row["Member 4"]} />
      <td className="p-2">{row.Score}</td>
    </tr>
  );
}
