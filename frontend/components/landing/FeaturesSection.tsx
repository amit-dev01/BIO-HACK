import React from "react";
import { Satellite, ShieldCheck, TrendingUp, Cpu } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";

const features = [
  {
    icon: Satellite,
    title: "Multi-Sensor Fusion",
    description:
      "Combines Sentinel-2 optical, GEDI LiDAR canopy profiles, and ALOS PALSAR radar data.",
  },
  {
    icon: Cpu,
    title: "AI Biomass Inversion",
    description:
      "Deep learning models trained on field-inventory plots deliver sub-hectare biomass estimates.",
  },
  {
    icon: ShieldCheck,
    title: "Verra & Gold Standard MRV",
    description:
      "Audit-ready carbon calculations mapped directly to VM0007, VM0047, and IPCC Tier 3 standards.",
  },
  {
    icon: TrendingUp,
    title: "NDVI Trend & Loss Alerts",
    description:
      "Continuous disturbance tracking and 5-year historical vegetation health trajectory.",
  },
];

export function FeaturesSection() {
  return (
    <section className="py-16 px-4 bg-white border-y border-border">
      <div className="max-w-7xl mx-auto">
        <h2 className="text-3xl font-bold text-center text-forest mb-12">
          Engineered for Rigorous Carbon Accounting
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, idx) => (
            <Card key={idx} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <feature.icon className="h-8 w-8 text-leaf mb-3" />
                <CardTitle className="text-lg text-charcoal">{feature.title}</CardTitle>
                <CardDescription>{feature.description}</CardDescription>
              </CardHeader>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}

export default FeaturesSection;

