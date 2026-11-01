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

  // Auto-detect if on landing page and should be transparent before scroll
  const isLanding = pathname === "/";
  const isTransparent =
    propTransparent !== undefined
      ? propTransparent
      : isLanding && !scrolled;

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
    { label: "Pricing", href: "/pricing" },
    { label: "Dashboard", href: "/dashboard" },
    { label: "Reports", href: "/reports" },
  ];

  return (
    <header
      className={cn(
        "fixed top-0 left-0 right-0 z-50 h-16 transition-colors duration-200",
        isTransparent
          ? "bg-transparent text-white border-transparent"
          : "bg-white/90 backdrop-blur-md text-gray-900 border-b border-gray-200 shadow-xs"
      )}
    >
      <div className="max-w-7xl mx-auto h-full px-4 sm:px-6 lg:px-8 flex items-center justify-between">
        {/* Left: Logo */}
        <Link href="/" className="flex items-center gap-2 group">
          <div className="p-1.5 rounded-lg bg-green-50 text-forest group-hover:bg-green-100 transition-colors">
            <TreePine className="h-6 w-6 text-[#1B5E20]" />
          </div>
          <span
            className={cn(
              "font-bold text-xl tracking-tight font-sans transition-colors",
              isTransparent ? "text-white" : "text-[#1B5E20]"
            )}
          >
            CanopyAI
          </span>
        </Link>

        {/* Center: Navigation Links */}
        <nav className="hidden md:flex items-center gap-8">
          {navLinks.map((link) => {
            const isActive = pathname === link.href || pathname.startsWith(`${link.href}/`);
            return (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  "text-sm font-medium transition-colors duration-150 py-1",
                  isTransparent
                    ? isActive
                      ? "text-white border-b-2 border-white"
                      : "text-white/80 hover:text-white"
                    : isActive
                    ? "text-green-700 font-semibold border-b-2 border-green-600"
                    : "text-gray-600 hover:text-green-600"
                )}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>

        {/* Right: Authentication or User Profile */}
        <div className="hidden md:flex items-center gap-4">
          {isAuthenticated ? (
            <div className="relative">
              <button
                type="button"
                onClick={() => setUserDropdownOpen(!userDropdownOpen)}
                className="flex items-center gap-2.5 p-1 rounded-full hover:ring-2 hover:ring-green-500/40 transition-all"
              >
                {user?.avatar_url ? (
                  <img
                    src={user.avatar_url}
                    alt={user.full_name || "User Avatar"}
                    className="w-8 h-8 rounded-full object-cover border border-gray-200 shadow-xs"
                  />
                ) : (
                  <div className="w-8 h-8 rounded-full bg-green-700 text-white flex items-center justify-center font-bold text-xs shadow-xs">
                    {user?.full_name?.charAt(0) || user?.email?.charAt(0) || "U"}
                  </div>
                )}
                <ChevronDown
                  className={cn(
                    "w-4 h-4 transition-transform",
                    isTransparent ? "text-white/80" : "text-gray-500",
                    userDropdownOpen && "rotate-180"
                  )}
                />
              </button>

              {/* User Dropdown Menu */}
              {userDropdownOpen && (
                <div
                  className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-xl border border-gray-100 py-2 z-50 text-gray-800 animate-in fade-in zoom-in-95 duration-150"
                  onMouseLeave={() => setUserDropdownOpen(false)}
                >
                  <div className="px-4 py-2 border-b border-gray-100">
                    <p className="text-xs font-semibold text-gray-900 truncate">
                      {user?.full_name || "Canopy Researcher"}
                    </p>
                    <p className="text-xs text-gray-500 truncate">{user?.email}</p>
                  </div>

                  <Link
                    href="/dashboard"
                    onClick={() => setUserDropdownOpen(false)}
                    className="flex items-center gap-2.5 px-4 py-2 text-xs font-medium text-gray-700 hover:bg-green-50 hover:text-green-700 transition-colors"
                  >
                    <LayoutDashboard className="w-4 h-4 text-gray-400" />
                    Dashboard
                  </Link>
                  <Link
                    href="/dashboard?tab=settings"
                    onClick={() => setUserDropdownOpen(false)}
                    className="flex items-center gap-2.5 px-4 py-2 text-xs font-medium text-gray-700 hover:bg-green-50 hover:text-green-700 transition-colors"
                  >
                    <Settings className="w-4 h-4 text-gray-400" />
                    Settings
                  </Link>

                  <div className="border-t border-gray-100 mt-1 pt-1">
                    <button
                      type="button"
                      onClick={() => {
                        setUserDropdownOpen(false);
                        signOut();
                      }}
                      className="w-full flex items-center gap-2.5 px-4 py-2 text-xs font-medium text-red-600 hover:bg-red-50 transition-colors text-left"
                    >
                      <LogOut className="w-4 h-4" />
                      Sign Out
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <Link
                href="/login"
                className={cn(
                  "text-sm font-medium px-3 py-1.5 transition-colors",
                  isTransparent
                    ? "text-white/90 hover:text-white"
                    : "text-gray-700 hover:text-green-700"
                )}
              >
                Log In
              </Link>
              <Link
                href="/login?mode=signup"
                className="bg-green-600 hover:bg-green-700 text-white text-sm font-medium px-4 py-2 rounded-lg shadow-sm hover:shadow transition-all"
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
            className={cn(
              "p-2 rounded-lg transition-colors",
              isTransparent ? "text-white hover:bg-white/10" : "text-gray-700 hover:bg-gray-100"
            )}
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Slide-Out Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-white border-b border-gray-200 px-4 pt-3 pb-6 shadow-xl animate-in slide-in-from-top-4 duration-200">
          <nav className="flex flex-col space-y-3">
            {navLinks.map((link) => {
              const isActive = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={cn(
                    "text-sm font-medium px-3 py-2 rounded-md transition-colors",
                    isActive
                      ? "bg-green-50 text-green-700 font-semibold"
                      : "text-gray-700 hover:bg-gray-50 hover:text-green-700"
                  )}
                >
                  {link.label}
                </Link>
              );
            })}
          </nav>

          <div className="border-t border-gray-200 mt-4 pt-4">
            {isAuthenticated ? (
              <div className="space-y-3">
                <div className="flex items-center gap-3 px-3">
                  {user?.avatar_url ? (
                    <img
                      src={user.avatar_url}
                      alt={user.full_name || "User"}
                      className="w-8 h-8 rounded-full object-cover"
                    />
                  ) : (
                    <div className="w-8 h-8 rounded-full bg-green-700 text-white flex items-center justify-center font-bold text-xs">
                      {user?.full_name?.charAt(0) || "U"}
                    </div>
                  )}
                  <div>
                    <p className="text-xs font-semibold text-gray-900">{user?.full_name}</p>
                    <p className="text-xs text-gray-500">{user?.email}</p>
                  </div>
                </div>

                <div className="flex flex-col gap-1 px-3">
                  <Link
                    href="/dashboard"
                    onClick={() => setMobileMenuOpen(false)}
                    className="text-xs text-gray-600 hover:text-green-700 py-1"
                  >
                    Dashboard
                  </Link>
                  <button
                    type="button"
                    onClick={() => {
                      setMobileMenuOpen(false);
                      signOut();
                    }}
                    className="text-left text-xs text-red-600 hover:text-red-700 py-1"
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
                  className="w-full text-center text-sm font-medium text-gray-700 border border-gray-200 py-2 rounded-lg hover:bg-gray-50"
                >
                  Log In
                </Link>
                <Link
                  href="/login?mode=signup"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full text-center bg-green-600 text-white text-sm font-medium py-2 rounded-lg hover:bg-green-700 shadow-sm"
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
