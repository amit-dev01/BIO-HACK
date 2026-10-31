# CanopyAI Platform Limitations & Honest Scientific Disclosures

> **IMPORTANT DISCLOSURE**
>
> **CanopyAI is a hackathon project built in 48 hours. It is a proof of concept, not a production-ready scientific instrument. All results should be treated as preliminary estimates requiring validation.**

---

## 1. Technical Limitations

1. **Absence of Soil Organic Carbon (SOC) Accounting**:
   - CanopyAI quantifies only living above-ground and below-ground arboreal biomass. Soil carbon—which can store between 30% and 75% of total ecosystem carbon in peat swamp forests, mangroves, and high-latitude boreal permafrost—is completely excluded from current calculations.
2. **Exclusion of Dead Wood & Leaf Litter Pools**:
   - Coarse woody debris (standing dead snags, fallen logs) and the organic forest litter layer are not measured by spaceborne optical or LiDAR sensors and are omitted from carbon accounting totals.
3. **Impossibility of Species-Level Taxonomic Identification**:
   - At 10-meter optical and 25-meter LiDAR resolution, spaceborne sensors cannot identify individual tree species, distinguish invasive vs. endemic timber, or resolve specific wood gravity variations.
4. **Spatial Resolution Constraints ($10\text{--}25\text{ m}$)**:
   - While adequate for landscape-level screening ($> 10\text{ ha}$), the resolution cannot resolve individual canopy gaps, selective low-impact logging trails, or smallholder agroforestry arrangements below 1 hectare.
5. **GEDI LiDAR Spatial Sparsity**:
   - GEDI is a sampling LiDAR instrument consisting of 8 parallel ground tracks, not an exhaustive wall-to-wall scanner. Polygons under $50\text{ ha}$ may receive fewer than 5 footprint shots, leading to statistical sampling sparsity.
6. **Optical Atmospheric Interference & Persistent Cloud Decks**:
   - Cloud cover, persistent tropical haze, and volcanic plumes obstruct Sentinel-2 imagery. In perpetually cloudy regions (e.g., Gabon, northwestern Borneo), multi-month composite windows are required to acquire cloud-free observations.
7. **Orbital Latitudinal Cut-Off ($> 51.6^\circ\text{ N/S}$)**:
   - Due to the orbital inclination of the International Space Station, GEDI collects no data poleward of $51.6^\circ\text{ N}$ or $51.6^\circ\text{ S}$. Extreme boreal and arctic taiga forests (northern Scandinavia, Siberia, Alaska, Canada) cannot be profiled directly with GEDI LiDAR.

---

## 2. Scientific & Ecological Limitations

1. **Inherent Remote Sensing Uncertainty ($\pm 25\text{--}40\%$)**:
   - Spaceborne above-ground biomass estimates carry an empirical uncertainty of $\pm 25\%$ to $\pm 40\%$ when evaluated without localized ground-truth destructive harvest plots.
2. **Heuristic Confidence Index vs. Formal Statistical Variance**:
   - The CanopyAI Confidence Score ($0\text{--}100$) represents a multi-criteria data quality and environmental suitability index (accounting for cloud cover, shot count, variance, and classification confidence), rather than a formal frequentist or Bayesian posterior probability distribution.
3. **Generic Carbon Fraction ($0.47$)**:
   - Dry biomass is converted to carbon using the universal IPCC Tier 1 default of $47\%$. While actual wood carbon fractions vary from $44\%$ in pioneer softwoods to $52\%$ in dense tropical hardwoods, species-specific fractions are not applied.
4. **Ecosystem-Average Root-to-Shoot Ratios**:
   - Below-Ground Biomass (BGB) is calculated via IPCC Tier 1 ecozone averages ($R = 0.21\text{--}0.26$). Actual root biomass varies dramatically with soil moisture, bedrock depth, and water table fluctuations.
5. **Lack of Dynamic Forest Growth Modeling**:
   - Annual sequestration projections are linear heuristic estimates based on regional averages rather than calibrated forest stand yield tables or physiological carbon-flux modeling.

---

## 3. Operational & Regulatory Boundaries

1. **Not a Replacement for Certified Field Forest Mensuration**:
   - CanopyAI is engineered for early-stage project origination, pre-feasibility screening, risk diligence, and deforestation alerts. It cannot substitute for certified ground cruise surveys.
2. **Not Certified for Carbon Credit Issuance**:
   - Verified Carbon Standard (Verra VCS VM0047 / VM0015), Gold Standard, and Climate Action Reserve (CAR) methodologies mandate rigorous third-party validation, permanent sample plots, and strict additionality demonstration that automated satellite screening alone cannot satisfy.
3. **Not a Legal or Regulatory Instrument**:
   - CanopyAI reports and data outputs do not constitute legally binding environmental impact statements, land title warranties, or regulatory compliance filings.
4. **Latency and Satellite Processing Lag**:
   - Spaceborne data streams have processing latencies ranging from 24 hours (Dynamic World) to several months (harmonized GEDI release cycles). Real-time ground activity (e.g., active timber felling yesterday) will not reflect immediately.

---

## 4. Ethical & Social Governance Disclosures

1. **No Assessment of Indigenous & Customary Land Rights**:
   - Satellite sensors observe vegetative surface cover only. CanopyAI does not and cannot verify ancestral domain, community land tenure, Free Prior and Informed Consent (FPIC), or territorial boundary disputes.
2. **Omission of Non-Carbon Ecological Co-Benefits**:
   - Forest value extends far beyond metric tonnes of $\text{CO}_2$. CanopyAI does not measure biodiversity richness, endemic wildlife habitat, watershed stabilization, microclimate moderation, or cultural ecosystem values.
3. **Imperative for Community Consultation**:
   - Algorithmic carbon estimates must never be used to override local community stewardship or displace forest-dwelling populations in the pursuit of carbon offsets.
