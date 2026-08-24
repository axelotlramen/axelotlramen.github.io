import { useEffect, useState } from "react";
import type { Stats } from "@/types/stats";

interface UseStatsResult {
  data: Stats | null;
  loading: boolean;
  error: string | null;
}

export function useStats(): UseStatsResult {
  const [data, setData] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    fetch("/data/stats.json")
      .then((response) => {
        if (!response.ok) throw new Error("Failed to fetch stats.json");
        return response.json() as Promise<Stats>;
      })
      .then((stats) => {
        if (!cancelled) setData(stats);
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return { data, loading, error };
}
