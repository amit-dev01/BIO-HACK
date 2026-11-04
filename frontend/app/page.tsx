import React from "react";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/layout/Footer";
import HeroSection from "@/components/landing/HeroSection";
import FeaturesSection from "@/components/landing/FeaturesSection";
import HowItWorksSection from "@/components/landing/HowItWorksSection";
import MetricsPreview from "@/components/landing/MetricsPreview";
import CtaSection from "@/components/landing/CtaSection";

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen bg-[#061409] text-white relative overflow-hidden">
      {/* Living Wild Jungle Background (Ultra HD 4K Rainforest Across Entire Page) */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden select-none z-0">
        <div
          className="absolute inset-0 bg-cover bg-center opacity-85 will-change-transform animate-canopy-breathe"
          style={{ backgroundImage: "url('/images/jungle-dense.jpg')" }}
        />
        {/* Transparent Atmospheric Depth Wash (Preserves full vivid HD green nature) */}
        <div className="absolute inset-0 bg-gradient-to-b from-[#061409]/50 via-[#061409]/25 to-[#061409]/70" />
        {/* Ambient Emerald Glow Meshes */}
        <div className="absolute -top-32 left-1/2 -translate-x-1/2 w-[900px] h-[600px] bg-gradient-to-b from-emerald-500/20 via-emerald-600/10 to-transparent blur-3xl rounded-full" />
        <div className="absolute bottom-0 right-0 w-[700px] h-[500px] bg-gradient-to-t from-green-500/15 via-emerald-500/5 to-transparent blur-3xl rounded-full" />
      </div>

      <Navbar />

      <main className="flex-1 relative z-10 space-y-16">
        <HeroSection />
        <MetricsPreview />
        <FeaturesSection />
        <HowItWorksSection />
        <CtaSection />
      </main>

      <Footer />
    </div>
  );
}
