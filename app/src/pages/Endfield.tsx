import { useStatsContext } from "@/context/StatsContext";
import { ProfileCard } from "@/components/stats/ProfileCard";
import { MiniCard } from "@/components/stats/MiniCard";
import { CharacterCard } from "@/components/stats/CharacterCard";
import { EmptyState } from "@/components/stats/EmptyState";
import { LastUpdatedStamp } from "@/components/stats/LastUpdatedStamp";
import { Doodle } from "@/components/decor/Doodle";
import { Skeleton } from "@/components/ui/skeleton";

function formatRecruitedDate(ownedAt: number | undefined): string | null {
  if (!ownedAt) return null;
  return new Date(ownedAt * 1000).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function Endfield() {
  const { data, loading, error } = useStatsContext();
  const ef = data?.endfield_data;

  return (
    <div className="relative">
      <Doodle kind="star" color="var(--tab-genshin)" className="top-0 right-10" rotate="-8deg" size={20} />
      <div className="flex flex-wrap items-baseline justify-between gap-3">
        <h1
          className="inline-block -rotate-2 text-5xl"
          style={{ fontFamily: "var(--font-heading)" }}
        >
          arknights: endfield
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

      {data && !ef && <EmptyState message="Arknights: Endfield data unavailable." />}

      {ef && (
        <div className="mt-8 space-y-10">
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 sm:items-start">
            <ProfileCard
              avatarUrl={ef.avatar_url}
              nickname={ef.nickname}
              subtitle={`Level ${ef.level}`}
              stats={[
                { label: "Active Days", value: ef.active_days },
                { label: "Achievements", value: ef.achievements },
                { label: "Characters", value: ef.avatar_count },
                { label: "Chests", value: ef.chest_count },
              ]}
              rotate="-1.5deg"
              tapeColor="var(--tab-endfield)"
            />
            <MiniCard
              title="Today's Status"
              tapeColor="var(--tab-endgame)"
              lines={[
                { label: "Sanity", value: `${ef.stamina ?? 0}/240` },
                { label: "Daily Missions", value: `${ef.daily_mission ?? 0}/100` },
                { label: "Logged In Today", value: (ef.daily_mission ?? 0) > 0 ? "Yes" : "No" },
              ]}
            />
          </div>

          {ef.six_star_characters && (
            <section>
              <h2 className="text-2xl" style={{ fontFamily: "var(--font-heading)" }}>
                roster
              </h2>
              <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {Object.entries(ef.six_star_characters)
                  .filter(([, char]) => char.rarity === "6")
                  .sort(([, a], [, b]) => b.level - a.level)
                  .map(([name, char]) => (
                    <CharacterCard
                      key={name}
                      iconUrl={char.avatarSqUrl}
                      name={name}
                      badge={`P${char.potential}`}
                      meta={`${char.profession} · ${char.property}`}
                      level={char.level}
                      weapon={char.weapon ? { iconUrl: char.weapon.iconUrl, name: char.weapon.name } : null}
                      recruitedAt={formatRecruitedDate(char.owned_at)}
                    />
                  ))}
              </div>
            </section>
          )}
        </div>
      )}
    </div>
  );
}
