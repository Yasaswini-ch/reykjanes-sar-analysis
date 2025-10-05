# Hypotheses Framework

This document defines testable hypotheses for Reykjanes SAR analysis. For each hypothesis, we state the expectation, a test method using available datasets, and provide placeholders for results.

## Hypothesis 1: Fresh Lava Backscatter Signature
- **Expectation**
  - VV: Moderate to high depending on surface roughness at radar wavelength; rough ʻaʻā lava higher than smooth pāhoehoe.
  - VH: Generally low due to limited volume/dihedral scattering immediately after emplacement; increases with weathering/roughness change.
  - Ratio (VH/VV in dB): Negative values (e.g., -6 to -2 dB) expected for fresh lava; trend towards 0 dB with aging/weathering.
- **Test Method**
  - Use HyP3 RTC GRD: select a fresh post-eruption date and a pre-eruption baseline.
  - Compute VH/VV ratio maps (`src/grd_ratio_analysis.py`) and Delta (Post - Pre).
  - Extract statistics over mapped lava polygons or manual AOIs on flows.
  - Compare roughness proxies (optical texture if available) to VV.
- **Results (Placeholder)**
  - [INSERT FINDINGS: median VV/VH/Ratio for fresh lava vs control surfaces]
  - [INSERT PLOTS: tripanel and delta]

## Hypothesis 2: Vegetation vs Bare Rock Differences
- **Expectation**
  - Vegetation increases VH via volume scattering; VV may be moderate.
  - Bare rock exhibits stronger VV than VH; ratio more negative than vegetated areas.
- **Test Method**
  - Identify vegetated patches vs bare rock using optical imagery or landcover masks.
  - Sample VV, VH, Ratio distributions for both classes; compare means with t-test.
- **Results (Placeholder)**
  - [INSERT FINDINGS: distribution comparisons, p-values]
  - [INSERT PLOTS: boxplots/histograms]

## Hypothesis 3: Temporal Coherence Loss
- **Expectation**
  - During eruptive episodes, rapid surface change yields reduced interferometric coherence compared to quiescent periods.
  - Coherence may partially recover post-eruption.
- **Limitations**
  - Full InSAR not automated in this repo; coherence analysis depends on external processing (SNAP/ISCE2/ARIA + MintPy).
- **Test Method**
  - If coherence rasters are available, include as layers in web map and compute AOI stats.
- **Results (Placeholder)**
  - [INSERT FINDINGS: coherence change over time and areas of interest]

## Hypothesis 4: Water Body Signatures
- **Expectation**
  - Open water exhibits specular reflection away from the sensor; very low VV and VH.
  - Wet soils adjacent to water show reduced VV and elevated VH relative to dry rock/soil.
- **Test Method**
  - Delineate lakes/ponds from optical imagery; buffer zones to capture shore effects.
  - Compare VV/VH/Ratio across water, shore buffer, and background rock.
- **Results (Placeholder)**
  - [INSERT FINDINGS: mean dB levels per class]
  - [INSERT PLOTS: profile across shoreline]
