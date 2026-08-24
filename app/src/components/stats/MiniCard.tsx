export interface MiniCardLine {
  label: string;
  value: string | number;
}

export function MiniCard({
  title,
  lines,
  tapeColor = "var(--accent)",
}: {
  title: string;
  lines: MiniCardLine[];
  tapeColor?: string;
}) {
  return (
    <div className="relative rounded-sm border border-border bg-card p-4 pt-6 shadow-[3px_4px_0_rgba(0,0,0,0.1)]">
      <div
        className="absolute -top-2.5 left-6 h-5 w-14 -rotate-3 opacity-80"
        style={{ backgroundColor: tapeColor }}
      />
      <h3 className="text-lg" style={{ fontFamily: "var(--font-heading)" }}>
        {title}
      </h3>
      <div className="mt-2 flex flex-col gap-1.5">
        {lines.map((line) => (
          <div key={line.label} className="flex items-baseline justify-between text-sm">
            <span className="text-muted-foreground">{line.label}</span>
            <strong className="font-semibold">{line.value}</strong>
          </div>
        ))}
      </div>
    </div>
  );
}
