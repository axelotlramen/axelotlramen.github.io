import { NavLink } from "react-router-dom";
import { cn } from "@/lib/utils";
import { profile } from "@/content/profile";

const links = [
  { to: "/", label: "Home", end: true, color: "var(--tab-home)", rotate: "-2deg", dark: false },
  { to: "/hsr", label: "Star Rail", color: "var(--tab-hsr)", rotate: "1.5deg", dark: false },
  { to: "/genshin", label: "Genshin", color: "var(--tab-genshin)", rotate: "-1deg", dark: true },
  { to: "/endfield", label: "Endfield", color: "var(--tab-endfield)", rotate: "2deg", dark: true },
  { to: "/endgame", label: "Endgame Log", color: "var(--tab-endgame)", rotate: "-1.5deg", dark: false },
];

export function Sidebar() {
  return (
    <aside
      className="relative flex w-56 shrink-0 flex-col bg-sidebar pt-8 pl-6"
      style={{
        backgroundImage:
          "repeating-linear-gradient(to bottom, color-mix(in oklch, var(--sidebar-foreground) 25%, transparent) 0, color-mix(in oklch, var(--sidebar-foreground) 25%, transparent) 8px, transparent 8px, transparent 26px)",
        backgroundPosition: "10px 0",
        backgroundRepeat: "repeat-y",
        backgroundSize: "1px 100%",
        boxShadow: "inset -6px 0 10px -8px rgba(0,0,0,0.35)",
      }}
    >
      <h2
        className="mb-10 pl-4 text-4xl text-sidebar-foreground"
        style={{ fontFamily: "var(--font-heading)", transform: "rotate(-3deg)" }}
      >
        {profile.username}
      </h2>
      <nav className="flex flex-col gap-3">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.end}
            className={({ isActive }) =>
              cn(
                "notebook-tab relative py-2.5 pl-4 pr-5 text-lg transition-transform duration-150",
                "rounded-l-md rounded-r-xl shadow-[2px_3px_0_rgba(0,0,0,0.2)]",
                link.dark ? "text-[var(--ink)]" : "text-white",
                isActive && "is-active"
              )
            }
            style={
              {
                backgroundColor: link.color,
                fontFamily: "var(--font-hand)",
                "--tab-rotate": link.rotate,
                transform: "rotate(var(--tab-rotate)) translateX(0)",
              } as React.CSSProperties
            }
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
