import React from "react";

export function MetricsPreview() {
  return (
    <section className="py-12 px-4 bg-forest-50/60">
      <div className="max-w-6xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
        <div>
          <div className="text-3xl font-mono font-bold text-forest">10m</div>
          <div className="text-xs uppercase tracking-wider text-slate mt-1">Spatial Resolution</div>
        </div>
        <div>
          <div className="text-3xl font-mono font-bold text-forest">94.2%</div>
          <div className="text-xs uppercase tracking-wider text-slate mt-1">LiDAR-Calibrated Accuracy</div>
        </div>
        <div>
          <div className="text-3xl font-mono font-bold text-forest">&lt; 15s</div>
          <div className="text-xs uppercase tracking-wider text-slate mt-1">Analysis Run Time</div>
        </div>
        <div>
          <div className="text-3xl font-mono font-bold text-forest">Tier 3</div>
          <div className="text-xs uppercase tracking-wider text-slate mt-1">IPCC Standard Compliance</div>
        </div>
      </div>
    </section>
  );
}

export default MetricsPreview;

