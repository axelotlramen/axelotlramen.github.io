import type { ChallengeNode } from "@/types/stats";

export interface FloorNode {
  title: string;
  characters: ChallengeNode[];
}

export function FloorCard({
  floorLabel,
  badge,
  nodes,
  tapeColor = "var(--accent)",
}: {
  floorLabel: string;
  badge: string;
  nodes: FloorNode[];
  tapeColor?: string;
}) {
  return (
    <div className="relative rounded-sm border border-border bg-card p-5 pt-7 shadow-[3px_5px_0_rgba(0,0,0,0.1)]">
      <div
        className="absolute -top-3 left-8 h-6 w-16 -rotate-2 opacity-80"
        style={{ backgroundColor: tapeColor }}
      />
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <div className="text-lg font-medium">{floorLabel}</div>
        <div className="text-sm text-muted-foreground">{badge}</div>
      </div>

      <div className="mt-4 flex flex-wrap gap-6">
        {nodes.map((node) => (
          <div key={node.title}>
            <div className="text-xs font-semibold tracking-wide text-muted-foreground uppercase">
              {node.title}
            </div>
            <div className="mt-2 flex gap-2">
              {node.characters.map((char, i) => (
                <div key={`${char.id}-${i}`} className="relative">
                  <img
                    src={`https://stardb.gg/api/static/StarRailResWebp/icon/character/${char.id}.webp`}
                    alt={`Character ${char.id}`}
                    className="size-11 rounded-full border border-border bg-muted object-cover"
                  />
                  <span className="absolute -right-1 -bottom-1 rounded-full bg-[var(--ink)] px-1 text-[0.6rem] font-medium text-[var(--card)]">
                    E{char.eidolon}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
