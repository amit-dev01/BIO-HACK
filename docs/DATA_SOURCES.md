# CanopyAI External Data Sources & Scientific Citations

This document provides a quick reference for all spaceborne observations, land cover datasets, and scientific calibration standards integrated into the CanopyAI platform.

---

## 1. NASA GEDI L4A Footprint Aboveground Biomass Density

- **Full Citation**:
  Dubayah, R., et al. (2022). *GEDI L4A Footprint Level Aboveground Biomass Density, Version 2.1*. ORNL DAAC, Oak Ridge, Tennessee, USA. [https://doi.org/10.3334/ORNLDAAC/2056](https://doi.org/10.3334/ORNLDAAC/2056)
- **URL**: [https://daac.ornl.gov/GEDI/](https://daac.ornl.gov/GEDI/)
- **License**: NASA Open Data Policy / US Government Work (Public Domain)
- **Temporal Coverage**: 2019-04-18 to 2023-03-16
- **Spatial Coverage**: Global between $51.6^\circ\text{ N}$ and $51.6^\circ\text{ S}$ latitudes
- **Resolution**: $25\text{ m}$ circular footprint
- **Used For**: Primary above-ground biomass density (AGBD) retrieval in $\text{Mg/ha}$
- **Access Method**: Google Earth Engine Collection `LARSE/GEDI/GEDI04_A_002` (and `LARSE/GEDI/GEDI04_A_002_INDEX`)

---

## 2. NASA GEDI L2A Elevation & Height Metrics

- **Full Citation**:
  Dubayah, R., et al. (2021). *GEDI L2A Elevation and Height Metrics Data Global Footprint Level, Version 2*. NASA EOSDIS Land Processes DAAC. [https://doi.org/10.5067/GEDI/GEDI02_A.002](https://doi.org/10.5067/GEDI/GEDI02_A.002)
- **URL**: [https://lpdaac.usgs.gov/products/gedi02_av002/](https://lpdaac.usgs.gov/products/gedi02_av002/)
- **License**: NASA Open Data Policy (Public Domain)
- **Temporal Coverage**: 2019 to 2023
- **Spatial Coverage**: Global between $51.6^\circ\text{ N}$ and $51.6^\circ\text{ S}$
- **Resolution**: $25\text{ m}$ circular footprint
- **Used For**: Relative canopy height extraction (specifically $RH_{98}$, height at 98% waveform energy return)
- **Access Method**: Google Earth Engine Collection `LARSE/GEDI/GEDI02_A_002_INDEX`

---

## 3. Google Dynamic World (v1)

- **Full Citation**:
  Brown, C.F., Brumby, S.P., Guzder-Williams, B., et al. (2022). *Large-scale modern land cover mapping with the Dynamic World*. Nature Scientific Data, 9, 251. [https://doi.org/10.1038/s41597-022-01307-4](https://doi.org/10.1038/s41597-022-01307-4)
- **URL**: [https://dynamicworld.app/](https://dynamicworld.app/)
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Temporal Coverage**: June 2015 – Present (near real-time)
- **Spatial Coverage**: Global terrestrial land surface
- **Resolution**: $10\text{ m}$ per pixel
- **Used For**: Canopy cover percentage estimation (`trees` class) and non-forest edge-case discrimination (water, built-up, bare ground, cropland)
- **Access Method**: Google Earth Engine ImageCollection `GOOGLE/DYNAMICWORLD/V1`

---

## 4. ESA Sentinel-2 MSI (Multispectral Instrument) Level-2A

- **Full Citation**:
  European Space Agency (ESA) & Copernicus Programme (2024). *Sentinel-2 MSI Level-2A Surface Reflectance Products*. European Space Agency. [https://sentinels.copernicus.eu/web/sentinel/missions/sentinel-2](https://sentinels.copernicus.eu/web/sentinel/missions/sentinel-2)
- **URL**: [https://dataspace.copernicus.eu/](https://dataspace.copernicus.eu/)
- **License**: Copernicus Open Access Policy (Free and open access)
- **Temporal Coverage**: 2015 – Present (5-day constellation revisit)
- **Spatial Coverage**: Global terrestrial surface between $84^\circ\text{ N}$ and $56^\circ\text{ S}$
- **Resolution**: $10\text{ m}$ (Red Band 4, NIR Band 8)
- **Used For**: Normalized Difference Vegetation Index (NDVI), cloud masking, multi-year greenness trajectory, and vegetation anomaly detection
- **Access Method**: Google Earth Engine ImageCollection `COPERNICUS/S2_SR_HARMONIZED`

---

## 5. ESA WorldCover 2021 (v200)

- **Full Citation**:
  Zanaga, D., Van De Kerchove, R., Daems, D., et al. (2022). *ESA WorldCover 10 m 2021 v200*. European Space Agency. [https://doi.org/10.5281/zenodo.5571939](https://doi.org/10.5281/zenodo.5571939)
- **URL**: [https://esa-worldcover.org/](https://esa-worldcover.org/)
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Temporal Coverage**: 2021 baseline
- **Spatial Coverage**: Global terrestrial surface
- **Resolution**: $10\text{ m}$
- **Used For**: Secondary validation of land cover classification and ecoregion boundary determination
- **Access Method**: Google Earth Engine ImageCollection `ESA/WorldCover/v200`

---

## 6. Hansen Global Forest Change (v1.10)

- **Full Citation**:
  Hansen, M. C., et al. (2013). *High-Resolution Global Maps of 21st-Century Forest Cover Change*. Science, 342(6160), 850-853. [https://doi.org/10.1126/science.1244693](https://doi.org/10.1126/science.1244693)
- **URL**: [https://earthenginepartners.appspot.com/science-2013-global-forest](https://earthenginepartners.appspot.com/science-2013-global-forest)
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Temporal Coverage**: 2000 – 2022
- **Spatial Coverage**: Global terrestrial land cover
- **Resolution**: $30\text{ m}$
- **Used For**: Multi-year forest loss screening and deforestation trend detection in degraded stands
- **Access Method**: Google Earth Engine Image `UMD/hansen/global_forest_change_2022_v1_10`

---

## 7. IPCC Guidelines for National Greenhouse Gas Inventories

- **Full Citation**:
  IPCC (2006). *2006 IPCC Guidelines for National Greenhouse Gas Inventories, Prepared by the National Greenhouse Gas Inventories Programme*. Eggleston H.S., Buendia L., Miwa K., Ngara T., and Tanabe K. (eds). Published: IGES, Japan.
  *2019 Refinement to the 2006 IPCC Guidelines for National Greenhouse Gas Inventories*. Calvo Buendia, E., et al. (eds). Published: IPCC, Switzerland.
- **URL**: [https://www.ipcc-nggip.iges.or.jp/public/2006gl/vol4.html](https://www.ipcc-nggip.iges.or.jp/public/2006gl/vol4.html)
- **License**: Public scientific report / United Nations Intergovernmental Panel on Climate Change
- **Used For**:
  - Default carbon fraction of dry biomass ($CF = 0.47$)
  - Root-to-shoot ratios for Below-Ground Biomass by ecozone ($0.21\text{--}0.26$)
  - Stoichiometric carbon-to-carbon-dioxide molecular conversion factor ($44/12 \approx 3.6667$)
