import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";

export interface CharacterCardProps {
  iconUrl: string;
  name: string;
  badge: string;
  meta: string;
  level: number;
  weapon?: { iconUrl: string; name: string } | null;
  recruitedAt?: string | null;
}

export function CharacterCard({
  iconUrl,
  name,
  badge,
  meta,
  level,
  weapon,
  recruitedAt,
}: CharacterCardProps) {
  return (
    <div className="flex items-center gap-3 rounded-md border border-border bg-card p-3">
      <Avatar className="size-12 shrink-0 border border-border">
        <AvatarImage src={iconUrl} alt={name} referrerPolicy="no-referrer" />
        <AvatarFallback>{name.slice(0, 2).toUpperCase()}</AvatarFallback>
      </Avatar>
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <span className="truncate font-medium">{name}</span>
          <Badge
            className="shrink-0 text-[0.65rem]"
            style={{ backgroundColor: "var(--tab-hsr)", color: "white" }}
          >
            {badge}
          </Badge>
        </div>
        <div className="truncate text-xs text-muted-foreground">{meta}</div>
        <div className="text-xs text-muted-foreground">
          Lv. {level}
          {recruitedAt ? ` · Recruited ${recruitedAt}` : ""}
        </div>
      </div>
      {weapon && (
        <div className="flex shrink-0 flex-col items-center gap-1">
          <img
            src={weapon.iconUrl}
            alt={weapon.name}
            referrerPolicy="no-referrer"
            className="size-9 rounded border border-border object-cover"
          />
        </div>
      )}
    </div>
  );
}
