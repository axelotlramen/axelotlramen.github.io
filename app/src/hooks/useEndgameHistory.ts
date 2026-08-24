import { useEffect, useState } from "react";

export type EndgameRow = Record<string, string>;

function parseCsv(text: string): string[][] {
  const rows: string[][] = [];
  let row: string[] = [];
  let field = "";
  let inQuotes = false;

  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (inQuotes) {
      if (c === '"') {
        if (text[i + 1] === '"') {
          field += '"';
          i++;
        } else {
          inQuotes = false;
        }
      } else {
        field += c;
      }
    } else if (c === '"') {
      inQuotes = true;
    } else if (c === ",") {
      row.push(field);
      field = "";
    } else if (c === "\n" || c === "\r") {
      if (c === "\r" && text[i + 1] === "\n") i++;
      row.push(field);
      rows.push(row);
      row = [];
      field = "";
    } else {
      field += c;
    }
  }
  if (field.length > 0 || row.length > 0) {
    row.push(field);
    rows.push(row);
  }
  return rows.filter((r) => r.some((cell) => cell !== ""));
}

interface UseEndgameHistoryResult {
  rows: EndgameRow[];
  loading: boolean;
  error: string | null;
}

export function useEndgameHistory(): UseEndgameHistoryResult {
  const [rows, setRows] = useState<EndgameRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    fetch("/data/endgame_history.csv")
      .then((response) => {
        if (!response.ok) throw new Error("Failed to fetch endgame history CSV");
        return response.text();
      })
      .then((text) => {
        if (cancelled) return;
        const [header, ...data] = parseCsv(text);
        setRows(data.map((row) => Object.fromEntries(header.map((key, i) => [key, row[i] ?? ""]))));
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

  return { rows, loading, error };
}
