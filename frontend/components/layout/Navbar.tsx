"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { TreePine, Menu, X, ChevronDown, User as UserIcon, LogOut, Settings, LayoutDashboard } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { cn } from "@/lib/utils";

interface NavbarProps {
  transparent?: boolean;
}

export function Navbar({ transparent: propTransparent }: NavbarProps) {
  const pathname = usePathname();
  const { user, isAuthenticated, signOut } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 20) {
        setScrolled(true);
      } else {
        setScrolled(false);
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const navLinks = [
    { label: "Analyze", href: "/analyze" },
    { label: "Dashboard", href: "/dashboard" },
    { label: "Reports", href: "/reports" },
  ];

  return (
    <header
      className={cn(
        "fixed top-0 left-0 right-0 z-50 h-16 transition-all duration-300",
        scrolled
          ? "bg-[#061B0B]/80 backdrop-blur-2xl border-b border-white/15 text-white shadow-xl shadow-black/25"
          : "bg-black/35 backdrop-blur-xl border-b border-white/10 text-white"
      )}
    >
      <div className="max-w-7xl mx-auto h-full px-4 sm:px-6 lg:px-8 flex items-center justify-between">
        {/* Left: Logo */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="p-1.5 rounded-xl bg-green-500/20 border border-green-400/30 text-green-300 group-hover:bg-green-500/30 transition-all shadow-inner">
            <TreePine className="h-6 w-6 text-emerald-400" />
          </div>
          <span className="font-bold text-xl tracking-tight text-white drop-shadow-sm font-sans">
            CanopyAI
          </span>
        </Link>

        {/* Center: Navigation Links */}
        <nav className="hidden md:flex items-center gap-2">
          {navLinks.map((link) => {
            const isActive = pathname === link.href || pathname.startsWith(`${link.href}/`);
            return (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  "text-sm font-medium transition-all duration-150 px-3.5 py-1.5 rounded-xl",
                  isActive
                    ? "bg-white/15 text-white border border-white/20 shadow-xs"
                    : "text-white/80 hover:text-white hover:bg-white/10"
                )}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>

        {/* Right: Authentication or User Profile */}
        <div className="hidden md:flex items-center gap-3">
          {isAuthenticated ? (
            <div className="relative">
              <button
                type="button"
                onClick={() => setUserDropdownOpen(!userDropdownOpen)}
                className="flex items-center gap-2.5 p-1 px-2.5 rounded-full bg-white/10 hover:bg-white/20 border border-white/20 transition-all"
              >
                {user?.avatar_url ? (
                  <img
                    src={user.avatar_url}
                    alt={user.full_name || "User Avatar"}
                    className="w-7 h-7 rounded-full object-cover border border-white/30"
                  />
                ) : (
                  <div className="w-7 h-7 rounded-full bg-emerald-600 text-white flex items-center justify-center font-bold text-xs shadow-xs">
                    {user?.full_name?.charAt(0) || user?.email?.charAt(0) || "U"}
                  </div>
                )}
                <span className="text-xs font-medium text-white max-w-[120px] truncate">
                  {user?.full_name || "User"}
                </span>
                <ChevronDown
                  className={cn(
                    "w-3.5 h-3.5 text-white/80 transition-transform",
                    userDropdownOpen && "rotate-180"
                  )}
                />
              </button>

              {/* User Dropdown Menu */}
              {userDropdownOpen && (
                <div
                  className="absolute right-0 mt-2 w-56 rounded-2xl glass-panel-dark py-2 z-50 text-white animate-in fade-in zoom-in-95 duration-150"
                  onMouseLeave={() => setUserDropdownOpen(false)}
                >
                  <div className="px-4 py-2 border-b border-white/10">
                    <p className="text-xs font-semibold text-white truncate">
                      {user?.full_name || "Canopy Researcher"}
                    </p>
                    <p className="text-xs text-gray-300 truncate">{user?.email}</p>
                  </div>

                  <Link
                    href="/dashboard"
                    onClick={() => setUserDropdownOpen(false)}
                    className="flex items-center gap-2.5 px-4 py-2 text-xs font-medium text-gray-200 hover:bg-white/15 hover:text-white transition-colors"
                  >
                    <LayoutDashboard className="w-4 h-4 text-emerald-400" />
                    Dashboard
                  </Link>
                  <Link
                    href="/dashboard?tab=settings"
                    onClick={() => setUserDropdownOpen(false)}
                    className="flex items-center gap-2.5 px-4 py-2 text-xs font-medium text-gray-200 hover:bg-white/15 hover:text-white transition-colors"
                  >
                    <Settings className="w-4 h-4 text-emerald-400" />
                    Settings
                  </Link>

                  <div className="border-t border-white/10 mt-1 pt-1">
                    <button
                      type="button"
                      onClick={() => {
                        setUserDropdownOpen(false);
                        signOut();
                      }}
                      className="w-full flex items-center gap-2.5 px-4 py-2 text-xs font-medium text-red-400 hover:bg-red-500/20 transition-colors text-left"
                    >
                      <LogOut className="w-4 h-4" />
                      Sign Out
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center gap-2.5">
              <Link
                href="/login"
                className="text-sm font-medium px-3.5 py-1.5 text-white/85 hover:text-white hover:bg-white/10 rounded-xl transition-all"
              >
                Log In
              </Link>
              <Link
                href="/login?mode=signup"
                className="bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold px-4 py-2 rounded-xl shadow-lg shadow-emerald-950/40 border border-emerald-400/30 transition-all hover:scale-105 active:scale-95"
              >
                Get Started
              </Link>
            </div>
          )}
        </div>

        {/* Mobile Hamburger Toggle */}
        <div className="flex md:hidden items-center">
          <button
            type="button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 rounded-xl text-white hover:bg-white/10 transition-colors"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Slide-Out Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden glass-panel-dark px-4 pt-3 pb-6 border-b border-white/15 shadow-2xl animate-in slide-in-from-top-4 duration-200">
          <nav className="flex flex-col space-y-2">
            {navLinks.map((link) => {
              const isActive = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={cn(
                    "text-sm font-medium px-3 py-2 rounded-xl transition-colors",
                    isActive
                      ? "bg-white/20 text-white font-semibold"
                      : "text-white/80 hover:bg-white/10 hover:text-white"
                  )}
                >
                  {link.label}
                </Link>
              );
            })}
          </nav>

          <div className="border-t border-white/10 mt-4 pt-4">
            {isAuthenticated ? (
              <div className="space-y-3">
                <div className="flex items-center gap-3 px-3">
                  <div className="w-8 h-8 rounded-full bg-emerald-700 text-white flex items-center justify-center font-bold text-xs">
                    {user?.full_name?.charAt(0) || "U"}
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-white">{user?.full_name}</p>
                    <p className="text-xs text-gray-300">{user?.email}</p>
                  </div>
                </div>

                <div className="flex flex-col gap-1 px-3">
                  <Link
                    href="/dashboard"
                    onClick={() => setMobileMenuOpen(false)}
                    className="text-xs text-gray-200 hover:text-white py-1"
                  >
                    Dashboard
                  </Link>
                  <button
                    type="button"
                    onClick={() => {
                      setMobileMenuOpen(false);
                      signOut();
                    }}
                    className="text-left text-xs text-red-400 hover:text-red-300 py-1"
                  >
                    Sign Out
                  </button>
                </div>
              </div>
            ) : (
              <div className="flex flex-col gap-2">
                <Link
                  href="/login"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full text-center text-sm font-medium text-white border border-white/20 py-2 rounded-xl hover:bg-white/10"
                >
                  Log In
                </Link>
                <Link
                  href="/login?mode=signup"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full text-center bg-emerald-600 text-white text-sm font-semibold py-2 rounded-xl hover:bg-emerald-500 shadow-md"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>
        </div>
      )}
    </header>
  );
}

export default Navbar;
