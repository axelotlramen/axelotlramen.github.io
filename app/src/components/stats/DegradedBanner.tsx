import { useStatsContext } from "@/context/StatsContext";

const SECTION_LABELS: Record<string, string> = {
  hsr_data: "Honkai: Star Rail",
  genshin_data: "Genshin Impact",
  endfield_data: "Arknights: Endfield",
};

export function DegradedBanner() {
  const { data } = useStatsContext();

  if (!data || data.degraded_sections.length === 0) return null;

  const labels = data.degraded_sections.map((section) => SECTION_LABELS[section] ?? section);

  return (
    <div className="mb-6 rounded-sm border border-dashed border-destructive/50 bg-destructive/10 px-4 py-2 text-sm text-destructive">
      Showing the last successful data for {labels.join(", ")}, today's fetch didn't come through.
    </div>
  );
}
