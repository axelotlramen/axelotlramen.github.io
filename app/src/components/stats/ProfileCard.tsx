import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";

export interface ProfileStat {
  label: string;
  value: string | number;
}

export interface ProfileCardProps {
  title?: string;
  avatarUrl: string;
  nickname: string;
  subtitle: string;
  stats: ProfileStat[];
  rotate?: string;
  tapeColor?: string;
}

export function ProfileCard({
  title,
  avatarUrl,
  nickname,
  subtitle,
  stats,
  rotate = "-1.5deg",
  tapeColor = "var(--accent)",
}: ProfileCardProps) {
  return (
    <div
      className="relative rounded-sm border border-border bg-card p-5 pt-8 shadow-[4px_6px_0_rgba(0,0,0,0.12)] transition-transform duration-150 hover:rotate-0"
      style={{ transform: `rotate(${rotate})` }}
    >
      {/* washi tape */}
      <div
        className="absolute -top-3 left-1/2 h-6 w-20 -translate-x-1/2 -rotate-2 opacity-80"
        style={{ backgroundColor: tapeColor }}
      />

      {/* header: avatar + name, tweet-style */}
      <div className="flex items-center gap-3">
        <Avatar className="size-14 shrink-0 border-2 border-card shadow-md">
          <AvatarImage src={avatarUrl} alt={nickname} referrerPolicy="no-referrer" />
          <AvatarFallback>{nickname.slice(0, 2).toUpperCase()}</AvatarFallback>
        </Avatar>
        <div className="min-w-0">
          <div
            className="truncate text-2xl leading-tight"
            style={{ fontFamily: "var(--font-heading)" }}
          >
            {nickname}
          </div>
          <div className="truncate text-xs text-muted-foreground">
            {title ? `${title} · ${subtitle}` : subtitle}
          </div>
        </div>
      </div>

      <div className="my-4 border-t border-dashed border-border" />

      <div className="flex flex-wrap justify-between gap-x-3 gap-y-3">
        {stats.map((stat) => (
          <div key={stat.label} className="text-center">
            <div className="text-[0.65rem] font-semibold tracking-wide text-muted-foreground uppercase">
              {stat.label}
            </div>
            <div className="mt-1 text-lg font-semibold">{stat.value}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
