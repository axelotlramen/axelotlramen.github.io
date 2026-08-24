import { useStats } from "@/hooks/useStats";
import { ProfileCard } from "@/components/stats/ProfileCard";
import { MiniCard } from "@/components/stats/MiniCard";
import { CharacterCard } from "@/components/stats/CharacterCard";
import { EmptyState } from "@/components/stats/EmptyState";
import { LastUpdatedStamp } from "@/components/stats/LastUpdatedStamp";
import { Doodle } from "@/components/decor/Doodle";
import { Skeleton } from "@/components/ui/skeleton";

export function Genshin() {
  const { data, loading, error } = useStats();
  const gi = data?.genshin_data;

  return (
    <div className="relative">
      <Doodle kind="heart" color="var(--tab-home)" className="top-0 right-10" rotate="-12deg" size={20} />
      <div className="flex flex-wrap items-baseline justify-between gap-3">
        <h1
          className="inline-block -rotate-2 text-5xl"
          style={{ fontFamily: "var(--font-heading)" }}
        >
          genshin impact
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

      {data && !gi && <EmptyState message="Genshin Impact data unavailable." />}

      {gi && (
        <div className="mt-8 space-y-10">
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 sm:items-start">
            <ProfileCard
              avatarUrl={gi.avatar_url}
              nickname={gi.nickname}
              subtitle={`AR ${gi.level}`}
              stats={[
                { label: "Achievements", value: gi.achievements },
                { label: "Active Days", value: gi.active_days },
                { label: "Characters", value: gi.avatar_count },
                { label: "Oculus", value: gi.oculus },
                { label: "Chests", value: gi.chest_count },
              ]}
              rotate="1deg"
              tapeColor="var(--tab-genshin)"
            />
            <MiniCard
              title="Today's Status"
              tapeColor="var(--tab-home)"
              lines={[
                { label: "Resin", value: `${gi.resin ?? 0}/200` },
                { label: "Daily Tasks", value: `${gi.daily_task ?? 0}/4` },
                { label: "Logged In Today", value: (gi.daily_task ?? 0) !== 0 ? "Yes" : "No" },
              ]}
            />
          </div>

          {gi.five_star_characters && (
            <section>
              <h2 className="text-2xl" style={{ fontFamily: "var(--font-heading)" }}>
                characters
              </h2>
              <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {Object.entries(gi.five_star_characters)
                  .sort(([, a], [, b]) => b.level - a.level)
                  .map(([name, char]) => (
                    <CharacterCard
                      key={name}
                      iconUrl={char.icon}
                      name={name}
                      badge={`C${char.constellation}`}
                      meta={`${char.element} · ${char.weaponType}`}
                      level={char.level}
                      weapon={char.weapon ? { iconUrl: char.weapon.icon, name: char.weapon.name } : null}
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
