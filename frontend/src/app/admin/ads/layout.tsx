"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import {
  LayoutDashboard,
  Cpu,
  Users,
  Megaphone,
  Shield,
  BookOpen,
  ChevronLeft,
  Wand2,
  Settings,
  Map,
} from "lucide-react";

const navItems = [
  { path: "/admin/ads", label: "Dashboard", icon: LayoutDashboard, exact: true },
  { path: "/admin/ads/ai-modules", label: "AI ADS", icon: Cpu },
  { path: "/admin/ads/clients", label: "Clienti", icon: Users },
  { path: "/admin/ads/campaigns", label: "Campagne", icon: Megaphone },
  { path: "/admin/ads/wizard", label: "Crea Campagna", icon: Wand2 },
  { path: "/admin/ads/supervision", label: "Supervisione", icon: Shield },
  { path: "/admin/ads/knowledge", label: "Knowledge Base", icon: BookOpen },
  { path: "/admin/ads/setup", label: "Setup", icon: Settings },
  { path: "/admin/ads/roadmap", label: "Roadmap", icon: Map },
];

export default function AdsLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="flex min-h-screen bg-[#0a0a0f]">
      {/* Sidebar */}
      <aside className="w-64 border-r border-white/5 flex flex-col shrink-0">
        {/* Header */}
        <div className="p-5 border-b border-white/5">
          <Link
            href="/admin"
            className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors text-sm mb-4"
          >
            <ChevronLeft className="w-4 h-4" />
            Torna ad Admin
          </Link>
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center">
              <Cpu className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="font-bold text-white text-sm">Ads Manager</h2>
              <p className="text-xs text-gray-500">AI ADS Ecosystem</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = item.exact
              ? pathname === item.path
              : pathname.startsWith(item.path);

            return (
              <Link
                key={item.path}
                href={item.path}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all text-sm ${
                  isActive
                    ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                    : "text-gray-400 hover:bg-white/5 hover:text-white"
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? "text-amber-400" : ""}`} />
                <span className="font-medium">{item.label}</span>
                {isActive && (
                  <div className="ml-auto w-1.5 h-1.5 rounded-full bg-amber-400" />
                )}
              </Link>
            );
          })}
        </nav>
      </aside>

      {/* Main content */}
      <main className="flex-1 p-8 overflow-auto">{children}</main>
    </div>
  );
}
