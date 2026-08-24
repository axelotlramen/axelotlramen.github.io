interface DoodleProps {
  kind?: "star" | "heart";
  className?: string;
  color?: string;
  size?: number;
  rotate?: string;
}

// Small decorative sticker accents — purely cosmetic, scattered near the
// washi-tape cards to match the strawpage-style scrapbook look.
export function Doodle({
  kind = "star",
  className = "",
  color = "var(--tab-hsr)",
  size = 24,
  rotate = "0deg",
}: DoodleProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      className={`pointer-events-none absolute ${className}`}
      style={{ transform: `rotate(${rotate})`, fill: color }}
      aria-hidden="true"
    >
      {kind === "star" ? (
        <path d="M12 1.5l2.6 6.6 7.1.4-5.6 4.5 2 6.9L12 15.9 5.9 19.9l2-6.9-5.6-4.5 7.1-.4z" />
      ) : (
        <path d="M12 21s-7.5-4.6-10-9.2C.4 8.6 2 5 5.5 5c2 0 3.4 1 4.5 2.5C11.1 6 12.5 5 14.5 5 18 5 19.6 8.6 22 11.8 19.5 16.4 12 21 12 21z" />
      )}
    </svg>
  );
}
