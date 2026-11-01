"use client";

import React, { useState, useEffect } from "react";
import {
  Accordion,
  AccordionItem,
  AccordionTrigger,
  AccordionContent,
} from "@/components/ui/accordion";
import { BookOpen, ExternalLink, HelpCircle } from "lucide-react";

export function Methodology() {
  const [defaultItem, setDefaultItem] = useState<string | undefined>("item-1");

  useEffect(() => {
    // On mobile, collapse by default
    if (window.innerWidth < 768) {
      setDefaultItem(undefined);
    }
  }, []);

  return (
    <div className="bg-white rounded-xl shadow-md border border-gray-100 p-6 sm:p-8">
      {/* Section Title */}
      <div className="flex items-center gap-3 mb-6 pb-4 border-b border-gray-100">
        <div className="p-2.5 rounded-xl bg-green-50 text-green-700 border border-green-200/60">
          <BookOpen className="w-5 h-5 text-green-600" />
        </div>
        <div>
          <h3 className="font-bold text-gray-900 text-lg sm:text-xl tracking-tight">
            Methodology — How Was This Calculated?
          </h3>
          <p className="text-xs text-gray-400">
            Peer-reviewed remote sensing equations, datasets, and uncertainty bounds
          </p>
        </div>
      </div>

      {/* Accordion Component */}
      <Accordion
        type="single"
        defaultValue={defaultItem}
        collapsible
        className="w-full space-y-2"
      >
        {/* Item 1: Data Sources */}
        <AccordionItem value="item-1" className="border rounded-xl px-4 py-1">
          <AccordionTrigger className="text-base font-semibold text-gray-900 hover:text-green-700">
            Data Sources &amp; Spaceborne Constellations
          </AccordionTrigger>
          <AccordionContent className="text-gray-600 space-y-3 pt-2">
            <p className="leading-relaxed">
              Our automated MRV pipeline fuses multiple remote sensing constellations
              to overcome cloud cover and capture 3D canopy geometry:
            </p>
            <ul className="list-disc pl-5 space-y-1.5 text-sm">
              <li>
                <strong>Sentinel-2 MSI (10m):</strong> European Space Agency
                Copernicus constellation providing multi-spectral reflectance
                (Red, Green, Blue, NIR, Red Edge bands) at 5-day revisit cycles.{" "}
                <a
                  href="https://sentinels.copernicus.eu"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-green-600 hover:underline inline-flex items-center gap-0.5"
                >
                  ESA Sentinel Hub <ExternalLink className="w-3 h-3" />
                </a>
              </li>
              <li>
                <strong>NASA GEDI L4A (25m footprint):</strong> Spaceborne
                full-waveform LiDAR on the International Space Station
                measuring vertical canopy profile and Relative Height (RH50, RH75, RH98)
                tracks.{" "}
                <a
                  href="https://gedi.umd.edu"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-green-600 hover:underline inline-flex items-center gap-0.5"
                >
                  NASA GEDI Science Team <ExternalLink className="w-3 h-3" />
                </a>
              </li>
              <li>
                <strong>Dynamic World &amp; ESA WorldCover (10m):</strong> Deep learning
                land use classification classifying trees, shrub, flooded vegetation,
                and crop mosaics.
              </li>
            </ul>
          </AccordionContent>
        </AccordionItem>

        {/* Item 2: Carbon Estimation Equations */}
        <AccordionItem value="item-2" className="border rounded-xl px-4 py-1">
          <AccordionTrigger className="text-base font-semibold text-gray-900 hover:text-green-700">
            Carbon Estimation Equations &amp; Allometry
          </AccordionTrigger>
          <AccordionContent className="text-gray-600 space-y-3 pt-2">
            <p className="leading-relaxed">
              Biomass and equivalent carbon stocks are derived using IPCC Tier 3
              equations parameterized for tropical moist and dry broadleaf ecozones:
            </p>
            <div className="bg-gray-50 p-4 rounded-xl border border-gray-200 font-mono text-xs space-y-2 text-gray-800">
              <p>
                <strong>1. Above-Ground Biomass (AGB):</strong> Chave et al. (2014)
                allometric pantropical model:
                <br />
                <span className="text-green-700">
                  AGB = 0.0673 × (ρ × D² × H)^0.976
                </span>
                <br />
                where H = GEDI RH98 canopy height, ρ = wood specific gravity (0.58 g/cm³), and D = estimated DBH.
              </p>
              <p>
                <strong>2. Below-Ground Biomass (BGB):</strong> IPCC Tier 1 root-to-shoot ratio:
                <br />
                <span className="text-green-700">BGB = 0.205 × AGB</span>
              </p>
              <p>
                <strong>3. Carbon Stock:</strong> Standard IPCC default carbon fraction:
                <br />
                <span className="text-green-700">Carbon (tC) = Total Biomass × 0.47</span>
              </p>
              <p>
                <strong>4. CO₂ Equivalent:</strong> Stoichiometric ratio of CO₂ to elemental C (molecular weights 44/12):
                <br />
                <span className="text-green-700">CO₂e = Carbon × 3.667</span>
              </p>
            </div>
          </AccordionContent>
        </AccordionItem>

        {/* Item 3: Confidence & Uncertainty */}
        <AccordionItem value="item-3" className="border rounded-xl px-4 py-1">
          <AccordionTrigger className="text-base font-semibold text-gray-900 hover:text-green-700">
            Confidence &amp; Uncertainty Bounds
          </AccordionTrigger>
          <AccordionContent className="text-gray-600 space-y-3 pt-2">
            <p className="leading-relaxed">
              Our automated Bayesian uncertainty quantification model assesses error
              margins across 4 spatial criteria:
            </p>
            <ul className="list-disc pl-5 space-y-1.5 text-sm">
              <li>
                <strong>Spatial LiDAR Density:</strong> Density of valid GEDI beam
                returns intersecting the target AOI within ±12 months.
              </li>
              <li>
                <strong>Atmospheric Correction &amp; Clouds:</strong> Percentage of
                sub-pixel cirrus or cloud shadowing across multi-temporal composites.
              </li>
              <li>
                <strong>Confidence Interval (±22%):</strong> Represents the 95%
                confidence bounds calculated using Monte Carlo bootstrapping on the
                calibrated Chave allometry dataset.
              </li>
            </ul>
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  );
}

export default Methodology;

