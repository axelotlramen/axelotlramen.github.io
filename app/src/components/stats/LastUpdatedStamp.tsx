export function LastUpdatedStamp({ isoDate }: { isoDate: string }) {
  const date = new Date(isoDate);
  const formatted = Number.isNaN(date.getTime())
    ? isoDate
    : date.toLocaleString(undefined, {
        month: "short",
        day: "numeric",
        year: "numeric",
        hour: "numeric",
        minute: "2-digit",
      });

  return (
    <div
      className="inline-block rounded-sm border-2 border-dashed px-3 py-1 text-xs tracking-wide uppercase opacity-70"
      style={{
        borderColor: "var(--ink)",
        color: "var(--ink)",
        transform: "rotate(-2deg)",
        fontFamily: "var(--font-hand)",
      }}
    >
      last updated · {formatted}
    </div>
  );
}
