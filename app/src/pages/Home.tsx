import { useStats } from "@/hooks/useStats";
import { ProfileCard } from "@/components/stats/ProfileCard";
import { IntroCard } from "@/components/stats/IntroCard";
import { EmptyState } from "@/components/stats/EmptyState";
import { LastUpdatedStamp } from "@/components/stats/LastUpdatedStamp";
import { Doodle } from "@/components/decor/Doodle";
import { Skeleton } from "@/components/ui/skeleton";

export function Home() {
  const { data, loading, error } = useStats();

  return (
    <div className="relative">
      <Doodle kind="star" color="var(--tab-hsr)" className="top-0 right-4 rotate-12" size={22} />
      <Doodle kind="heart" color="var(--tab-endgame)" className="top-14 right-24" rotate="-15deg" size={18} />

      <div className="flex flex-wrap items-baseline justify-between gap-3">
        <h1
          className="inline-block -rotate-2 text-5xl"
          style={{ fontFamily: "var(--font-heading)" }}
        >
          home
        </h1>
        {data && <LastUpdatedStamp isoDate={data.last_updated} />}
      </div>

      <div className="mt-8">
        <IntroCard />
      </div>

      {loading && (
        <div className="mt-6 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {[0, 1, 2].map((i) => (
            <Skeleton key={i} className="h-72 rounded-xl" />
          ))}
        </div>
      )}

      {error && (
        <p className="mt-6 text-sm text-destructive">
          Couldn't load stats: {error}
        </p>
      )}

      {data && (
        <div className="mt-10 grid grid-cols-1 gap-x-8 gap-y-12 sm:grid-cols-2 lg:grid-cols-3">
          {data.hsr_data ? (
            <ProfileCard
              title="Honkai: Star Rail"
              avatarUrl={data.hsr_data.avatar_url}
              nickname={data.hsr_data.nickname}
              subtitle={`Level ${data.hsr_data.level}`}
              stats={[
                { label: "Achievements", value: data.hsr_data.achievements },
                { label: "TB Power", value: `${data.hsr_data.stamina ?? 0}/300` },
              ]}
              rotate="-2deg"
              tapeColor="var(--tab-hsr)"
            />
          ) : (
            <EmptyState message="Honkai: Star Rail data unavailable." />
          )}

          {data.genshin_data ? (
            <ProfileCard
              title="Genshin Impact"
              avatarUrl={data.genshin_data.avatar_url}
              nickname={data.genshin_data.nickname}
              subtitle={`AR ${data.genshin_data.level}`}
              stats={[
                { label: "Achievements", value: data.genshin_data.achievements },
                { label: "Resin", value: `${data.genshin_data.resin ?? 0}/200` },
              ]}
              rotate="1.5deg"
              tapeColor="var(--tab-genshin)"
            />
          ) : (
            <EmptyState message="Genshin Impact data unavailable." />
          )}

          {data.endfield_data ? (
            <ProfileCard
              title="Arknights: Endfield"
              avatarUrl={data.endfield_data.avatar_url}
              nickname={data.endfield_data.nickname}
              subtitle={`Level ${data.endfield_data.level}`}
              stats={[
                { label: "Achievements", value: data.endfield_data.achievements },
                { label: "Sanity", value: `${data.endfield_data.stamina ?? 0}/240` },
              ]}
              rotate="-1deg"
              tapeColor="var(--tab-endfield)"
            />
          ) : (
            <EmptyState message="Arknights: Endfield data unavailable." />
          )}
        </div>
      )}
    </div>
  );
}
