import { useState } from "react";
import { Outlet } from "react-router-dom";
import { Menu } from "lucide-react";
import { Sidebar } from "@/components/layout/Sidebar";
import { DegradedBanner } from "@/components/stats/DegradedBanner";
import { profile } from "@/content/profile";

export function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-background text-foreground">
      <Sidebar open={sidebarOpen} onNavigate={() => setSidebarOpen(false)} />

      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/30 md:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        <div className="flex items-center gap-3 border-b border-border bg-card px-4 py-3 md:hidden">
          <button
            type="button"
            onClick={() => setSidebarOpen(true)}
            aria-label="Open menu"
            className="rounded-md p-1.5"
          >
            <Menu className="size-5" />
          </button>
          <span className="text-lg" style={{ fontFamily: "var(--font-heading)" }}>
            {profile.username}
          </span>
        </div>

        <main className="min-w-0 flex-1 px-4 py-6 sm:px-8 sm:py-8">
          <DegradedBanner />
          <Outlet />
        </main>
      </div>
    </div>
  );
}
