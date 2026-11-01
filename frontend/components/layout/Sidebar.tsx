"use client";

import React from "react";
import Link from "next/link";
import { LayoutDashboard, Compass, FileText, Settings } from "lucide-react";

export function Sidebar() {
  return (
    <aside className="w-64 border-r border-border bg-white min-h-[calc(100vh-4rem)] p-4">
      <nav className="space-y-1">
        <Link
          href="/dashboard"
          className="flex items-center gap-3 px-3 py-2 rounded-button text-sm font-medium text-charcoal hover:bg-muted"
        >
          <LayoutDashboard className="h-4 w-4 text-forest" />
          Dashboard
        </Link>
        <Link
          href="/analyze"
          className="flex items-center gap-3 px-3 py-2 rounded-button text-sm font-medium text-charcoal hover:bg-muted"
        >
          <Compass className="h-4 w-4 text-forest" />
          Analyze Forest
        </Link>
        <Link
          href="/reports"
          className="flex items-center gap-3 px-3 py-2 rounded-button text-sm font-medium text-charcoal hover:bg-muted"
        >
          <FileText className="h-4 w-4 text-forest" />
          Saved Reports
        </Link>
        <div className="pt-4 mt-4 border-t border-border">
          <Link
            href="/pricing"
            className="flex items-center gap-3 px-3 py-2 rounded-button text-sm font-medium text-charcoal hover:bg-muted"
          >
            <Settings className="h-4 w-4 text-slate" />
            Plans & Upgrades
          </Link>
        </div>
      </nav>
    </aside>
  );
}

export default Sidebar;

