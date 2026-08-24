import { useStats } from "@/hooks/useStats";
import { ProfileCard } from "@/components/stats/ProfileCard";
import { MiniCard } from "@/components/stats/MiniCard";
import { CharacterCard } from "@/components/stats/CharacterCard";
import { FloorCard, type FloorNode } from "@/components/stats/FloorCard";
import { EmptyState } from "@/components/stats/EmptyState";
import { LastUpdatedStamp } from "@/components/stats/LastUpdatedStamp";
import { Doodle } from "@/components/decor/Doodle";
import { Skeleton } from "@/components/ui/skeleton";

export function Hsr() {
  const { data, loading, error } = useStats();
  const sr = data?.hsr_data;

  return (
    <div className="relative">
      <Doodle kind="star" color="var(--tab-endfield)" className="top-0 right-10" rotate="10deg" size={20} />
      <div className="flex flex-wrap items-baseline justify-between gap-3">
        <h1
          className="inline-block -rotate-2 text-5xl"
          style={{ fontFamily: "var(--font-heading)" }}
        >
          honkai: star rail
        </h1>
        {data && <LastUpdatedStamp isoDate={data.last_updated} />}
      </div>

      {loading && (
        <div className="mt-8 space-y-6">
          <Skeleton className="h-56 w-full max-w-sm rounded-xl" />
        </div>
      )}

      {error && (
        <p className="mt-6 text-sm text-destructive">Couldn't load stats: {error}</p>
      )}

      {data && !sr && <EmptyState message="Honkai: Star Rail data unavailable." />}

      {sr && (
        <div className="mt-8 space-y-10">
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 sm:items-start">
            <ProfileCard
              avatarUrl={sr.avatar_url}
              nickname={sr.nickname}
              subtitle={`NA · Level ${sr.level}`}
              stats={[
                { label: "Active Days", value: sr.active_days },
                { label: "Achievements", value: sr.achievements },
                { label: "Characters", value: sr.avatar_count },
                { label: "Chests", value: sr.chest_count },
              ]}
              rotate="-1deg"
              tapeColor="var(--tab-hsr)"
            />
            <MiniCard
              title="Today's Status"
              tapeColor="var(--tab-endgame)"
              lines={[
                { label: "Trailblaze Power", value: `${sr.stamina ?? 0}/300` },
                { label: "Daily Training", value: `${sr.current_train_score ?? 0}/500` },
                { label: "Logged In Today", value: (sr.current_train_score ?? 0) !== 0 ? "Yes" : "No" },
              ]}
            />
          </div>

          {sr.five_star_characters && (
            <section>
              <h2 className="text-2xl" style={{ fontFamily: "var(--font-heading)" }}>
                characters
              </h2>
              <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {Object.entries(sr.five_star_characters).map(([name, char]) => (
                  <CharacterCard
                    key={name}
                    iconUrl={char.icon}
                    name={name}
                    badge={`E${char.eidolon}`}
                    meta={`${char.element} · ${char.path}`}
                    level={char.level}
                    weapon={char.lc ? { iconUrl: char.lc.icon, name: char.lc.name } : null}
                  />
                ))}
              </div>
            </section>
          )}

          <section>
            <h2 className="text-2xl" style={{ fontFamily: "var(--font-heading)" }}>
              apocalyptic shadow
            </h2>
            <div className="mt-3">
              {sr.apocalyptic_shadow?.floor_data ? (
                <FloorCard
                  tapeColor="var(--tab-hsr)"
                  floorLabel={sr.apocalyptic_shadow.floor_data.floor}
                  badge={`${sr.apocalyptic_shadow.floor_data.score} pts · ★ ${sr.apocalyptic_shadow.total_stars}`}
                  nodes={(
                    [
                      { title: "Node 1", characters: sr.apocalyptic_shadow.floor_data.node_1 },
                      { title: "Node 2", characters: sr.apocalyptic_shadow.floor_data.node_2 },
                      { title: "Node 3", characters: sr.apocalyptic_shadow.floor_data.node_3 },
                    ] as FloorNode[]
                  ).filter((n) => n.characters)}
                />
              ) : (
                <EmptyState message="I have not attempted Apocalyptic Shadow yet." />
              )}
            </div>
          </section>

          <section>
            <h2 className="text-2xl" style={{ fontFamily: "var(--font-heading)" }}>
              pure fiction
            </h2>
            <div className="mt-3">
              {sr.pure_fiction?.floor_data ? (
                <FloorCard
                  tapeColor="var(--tab-genshin)"
                  floorLabel={sr.pure_fiction.floor_data.floor}
                  badge={`${sr.pure_fiction.floor_data.score} pts · ★ ${sr.pure_fiction.total_stars}`}
                  nodes={(
                    [
                      { title: "Node 1", characters: sr.pure_fiction.floor_data.node_1 },
                      { title: "Node 2", characters: sr.pure_fiction.floor_data.node_2 },
                      { title: "Node 3", characters: sr.pure_fiction.floor_data.node_3 },
                    ] as FloorNode[]
                  ).filter((n) => n.characters)}
                />
              ) : (
                <EmptyState message="I have not attempted Pure Fiction yet." />
              )}
            </div>
          </section>

          <section>
            <h2 className="text-2xl" style={{ fontFamily: "var(--font-heading)" }}>
              memory of chaos
            </h2>
            <div className="mt-3">
              {sr.memory_of_chaos?.floor_data ? (
                <FloorCard
                  tapeColor="var(--tab-endfield)"
                  floorLabel={sr.memory_of_chaos.floor_data.floor}
                  badge={`${sr.memory_of_chaos.floor_data.cycles} cycles · ★ ${sr.memory_of_chaos.total_stars}`}
                  nodes={[
                    { title: "Node 1", characters: sr.memory_of_chaos.floor_data.first_half },
                    { title: "Node 2", characters: sr.memory_of_chaos.floor_data.second_half },
                  ]}
                />
              ) : (
                <EmptyState message="I have not attempted Memory of Chaos yet." />
              )}
            </div>
          </section>

          <section>
            <h2 className="text-2xl" style={{ fontFamily: "var(--font-heading)" }}>
              anomaly arbitration
            </h2>
            <div className="mt-3">
              {sr.anomaly_arbitration && Object.keys(sr.anomaly_arbitration).length > 0 ? (
                <FloorCard
                  tapeColor="var(--tab-home)"
                  floorLabel={sr.anomaly_arbitration.season || "Anomaly Arbitration"}
                  badge={`${sr.anomaly_arbitration.cycles_used} cycles · ★ ${
                    sr.anomaly_arbitration.boss_stars + sr.anomaly_arbitration.mini_boss_stars
                  }`}
                  nodes={[
                    ...(sr.anomaly_arbitration.boss_record
                      ? [{ title: "Boss", characters: sr.anomaly_arbitration.boss_record.characters }]
                      : []),
                    ...(sr.anomaly_arbitration.mini_boss_records ?? []).map((miniBoss, i) => ({
                      title: `Mini Boss ${i + 1}`,
                      characters: miniBoss.characters,
                    })),
                  ]}
                />
              ) : (
                <EmptyState message="I have not attempted Anomaly Arbitration yet." />
              )}
            </div>
          </section>
        </div>
      )}
    </div>
  );
}
