"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { TreePine, Github, Twitter, Linkedin, Heart } from "lucide-react";

export function Footer() {
  const pathname = usePathname();

  // The footer should not appear on the /analyze page (full-screen map mode)
  if (pathname === "/analyze" || pathname?.startsWith("/analyze/")) {
    return null;
  }

  return (
    <footer className="bg-[#041407]/95 backdrop-blur-2xl text-gray-300 border-t border-white/10 relative z-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12">
          {/* Column 1: Brand & Mission */}
          <div className="space-y-4">
            <Link href="/" className="flex items-center gap-2 group">
              <div className="p-1.5 rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-400/30">
                <TreePine className="h-6 w-6" />
              </div>
              <span className="font-bold text-xl text-white tracking-tight">
                CanopyAI
              </span>
            </Link>
            <p className="text-sm text-gray-400 font-medium">
              AI-powered forest carbon estimation and high-integrity MRV verification.
            </p>
            <p className="text-xs text-gray-400 leading-relaxed">
              Empowering project developers, conservation trusts, and institutional investors with transparent, spaceborne ecological intelligence to protect global carbon sinks.
            </p>
          </div>

          {/* Column 2: Product */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-white mb-4">
              Product
            </h4>
            <ul className="space-y-2.5 text-sm">
              <li>
                <Link href="/analyze" className="hover:text-green-400 transition-colors">
                  Analyze Forest
                </Link>
              </li>

              <li>
                <Link href="/reports" className="hover:text-green-400 transition-colors">
                  MRV Reports
                </Link>
              </li>
              <li>
                <a
                  href="#api"
                  onClick={(e) => {
                    e.preventDefault();
                    alert("CanopyAI Developer REST API (v1) documentation available in Enterprise plan.");
                  }}
                  className="hover:text-green-400 transition-colors flex items-center gap-1.5"
                >
                  API Docs <span className="text-[10px] bg-gray-800 text-green-400 px-1.5 py-0.5 rounded">v1</span>
                </a>
              </li>
              <li>
                <a
                  href="#changelog"
                  onClick={(e) => {
                    e.preventDefault();
                    alert("CanopyAI 2.4: Enhanced GEDI 3D canopy profile fusion launched October 2024.");
                  }}
                  className="hover:text-green-400 transition-colors"
                >
                  Changelog
                </a>
              </li>
            </ul>
          </div>

          {/* Column 3: Resources */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-white mb-4">
              Resources
            </h4>
            <ul className="space-y-2.5 text-sm">
              <li>
                <a
                  href="#documentation"
                  onClick={(e) => {
                    e.preventDefault();
                    alert("User Guides and Technical Whitepaper can be downloaded from our documentation portal.");
                  }}
                  className="hover:text-green-400 transition-colors"
                >
                  Documentation
                </a>
              </li>
              <li>
                <a
                  href="#blog"
                  onClick={(e) => {
                    e.preventDefault();
                    alert("Canopy Research Blog: 'Validating Allometric Equations using Spaceborne LiDAR in the Amazon'.");
                  }}
                  className="hover:text-green-400 transition-colors"
                >
                  Research Blog
                </a>
              </li>
              <li>
                <a
                  href="#casestudies"
                  onClick={(e) => {
                    e.preventDefault();
                    alert("Case Study: How Pará REDD+ conserved 120,000 hectares using CanopyAI MRV verification.");
                  }}
                  className="hover:text-green-400 transition-colors"
                >
                  Case Studies
                </a>
              </li>
              <li>
                <a href="#methodology" onClick={(e) => { e.preventDefault(); alert("CanopyAI MRV methodology follows IPCC Tier 3 and Verra VCS standards."); }} className="hover:text-green-400 transition-colors">
                  Methodology &amp; Standards
                </a>
              </li>
            </ul>
          </div>

          {/* Column 4: Company */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-white mb-4">
              Company
            </h4>
            <ul className="space-y-2.5 text-sm">
              <li>
                <Link href="/about" className="hover:text-green-400 transition-colors">
                  About Us
                </Link>
              </li>
              <li>
                <a
                  href="#careers"
                  onClick={(e) => {
                    e.preventDefault();
                    alert("We're hiring Remote Sensing Scientists & Machine Learning Engineers! Reach out at jobs@canopyai.earth");
                  }}
                  className="hover:text-green-400 transition-colors flex items-center gap-1.5"
                >
                  Careers <span className="text-[10px] bg-green-900 text-green-300 px-1.5 py-0.5 rounded font-mono">We&apos;re hiring</span>
                </a>
              </li>
              <li>
                <a
                  href="mailto:contact@canopyai.earth"
                  className="hover:text-green-400 transition-colors"
                >
                  Contact
                </a>
              </li>
              <li>
                <a
                  href="#privacy"
                  onClick={(e) => {
                    e.preventDefault();
                    alert("CanopyAI respects data privacy and adheres to GDPR & SOC-2 compliance standards.");
                  }}
                  className="hover:text-green-400 transition-colors"
                >
                  Privacy Policy &amp; Terms
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="mt-12 pt-8 border-t border-gray-800 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-gray-400">
          <p>© 2024 CanopyAI. All rights reserved.</p>

          <div className="flex items-center gap-6">
            <a
              href="https://github.com"
              target="_blank"
              rel="noreferrer"
              className="text-gray-400 hover:text-white transition-colors"
              aria-label="GitHub"
            >
              <Github className="w-4 h-4" />
            </a>
            <a
              href="https://twitter.com"
              target="_blank"
              rel="noreferrer"
              className="text-gray-400 hover:text-white transition-colors"
              aria-label="Twitter / X"
            >
              <Twitter className="w-4 h-4" />
            </a>
            <a
              href="https://linkedin.com"
              target="_blank"
              rel="noreferrer"
              className="text-gray-400 hover:text-white transition-colors"
              aria-label="LinkedIn"
            >
              <Linkedin className="w-4 h-4" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
