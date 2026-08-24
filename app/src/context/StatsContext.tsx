import { createContext, useContext, type ReactNode } from "react";
import { useStats } from "@/hooks/useStats";
import type { Stats } from "@/types/stats";

interface StatsContextValue {
  data: Stats | null;
  loading: boolean;
  error: string | null;
}

const StatsContext = createContext<StatsContextValue | null>(null);

export function StatsProvider({ children }: { children: ReactNode }) {
  const value = useStats();
  return <StatsContext.Provider value={value}>{children}</StatsContext.Provider>;
}

export function useStatsContext(): StatsContextValue {
  const value = useContext(StatsContext);
  if (!value) {
    throw new Error("useStatsContext must be used inside a StatsProvider");
  }
  return value;
}
