import React from "react";
import Link from "next/link";
import { ArrowRight, Trees } from "lucide-react";
import { Button } from "@/components/ui/button";

export function HeroSection() {
  return (
    <section className="py-20 px-4 text-center">
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-forest-50 text-forest text-xs font-semibold">
          <Trees className="h-4 w-4" /> Next-Gen Forest MRV & Carbon Accounting
        </div>
        <h1 className="text-5xl font-extrabold tracking-tight text-forest sm:text-6xl">
          High-Resolution Forest Carbon Intelligence
        </h1>
        <p className="text-lg text-slate max-w-2xl mx-auto">
          Accurate biomass estimation, canopy height analysis, and Verra-compliant carbon stock verification powered by Sentinel-2, GEDI, and AI models.
        </p>
        <div className="flex justify-center gap-4 pt-4">
          <Button asChild size="lg">
            <Link href="/analyze" className="flex items-center gap-2">
              Launch Analysis <ArrowRight className="h-4 w-4" />
            </Link>
          </Button>
        </div>
      </div>
    </section>
  );
}

export default HeroSection;

