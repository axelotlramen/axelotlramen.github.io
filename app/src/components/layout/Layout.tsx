import { Outlet } from "react-router-dom";
import { Sidebar } from "@/components/layout/Sidebar";

export function Layout() {
  return (
    <div className="flex min-h-screen bg-background text-foreground">
      <Sidebar />
      <main className="flex-1 px-8 py-8">
        <Outlet />
      </main>
    </div>
  );
}
