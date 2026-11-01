import React from "react";

const steps = [
  {
    step: "01",
    title: "Define Area of Interest",
    description: "Draw your polygon directly on Mapbox satellite imagery or upload a GeoJSON / Shapefile.",
  },
  {
    step: "02",
    title: "Automated Data Ingestion",
    description: "Our pipeline pulls multi-temporal Sentinel-2 imagery and GEDI LiDAR canopy height tracks.",
  },
  {
    step: "03",
    title: "AI Biomass Calculation",
    description: "Estimates Above-Ground & Below-Ground Biomass, calculating Total CO2 Equivalent.",
  },
  {
    step: "04",
    title: "Export & Verification",
    description: "Download verified audit reports and estimate potential carbon credit revenue.",
  },
];

export function HowItWorksSection() {
  return (
    <section className="py-16 px-4">
      <div className="max-w-7xl mx-auto">
        <h2 className="text-3xl font-bold text-center text-forest mb-12">
          How CanopyAI Works
        </h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((item, idx) => (
            <div key={idx} className="p-6 bg-white rounded-card border border-border">
              <span className="text-3xl font-mono font-bold text-leaf">{item.step}</span>
              <h3 className="text-lg font-semibold text-charcoal mt-2 mb-2">{item.title}</h3>
              <p className="text-slate text-sm">{item.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default HowItWorksSection;

