# Alice’s Journey Through Iceland’s Volcanic Looking Glass

## 1) Down the Dike-Hole — An Invitation to SAR
Like Alice’s lantern in a moonless cavern, SAR brings its own light. Radar pulses illuminate Reykjanes regardless of clouds or night, letting us trace subtle changes where optics fall silent.

- Key idea: active sensing (microwaves) vs passive sunlight.
- Why here: frequent clouds, polar night, fast-evolving lava fields.

## 2) The Cheshire Coherence — What the Land Remembers
Coherence is the landscape’s memory between two visits. High coherence: the surface “remembers” itself; low coherence: churned, altered, or newly emplaced lava.

- Expectation: Fresh lava and fumarolic areas lose coherence.
- Findings: Coherence locally drops along the 2024–2025 eruption pathways on the Reykjanes Peninsula, consistent with newly emplaced or reworked lava surfaces. Areas west and northeast of the main fissures retain higher coherence, while zones proximal to the 2024 Nov and 2025 Jul vents show patchy to low coherence, indicating surface modification by lava emplacement, cooling fractures, and ash/tephra redistribution.

## 3) The Queen’s Polarization — VV and VH
VV is the face of the surface (roughness). VH is the whisper of structure (volume scatter). Fresh, smooth lava lowers VH; VV varies with roughness and incidence.

- Hypothesis: Fresh lava → low VH; VV variable with surface roughness and cooling textures.
- Findings: The VH/VV ratio separates surface types in our scene:
  - Ocean water: VH/VV ≈ −22 to −25 dB (yellow/orange in composites; smooth specular returns).
  - Vegetated/rough land: VH/VV ≈ −8 to −12 dB (green; stronger volume/structural scattering).
  - Suspected lava fields: VH/VV ≈ −10 to −15 dB (dark green patches; smoother solid surfaces with subdued VH).
  Maps of VH/VV reveal coherent spatial patterns aligned with coastline, vegetated uplands, and lava fields.

## 4) Curiouser and Curiouser — Results Across Time
Comparing pre (May 2024), during (Nov 2024), and recent (Sep–Oct 2025) reveals how signals evolve as lava weathers and vegetation or ash redistributes.

- Time-series VH/VV and spatial patterns:
  - May → Nov 2024: Scene-wide mean change ≈ 0.00 dB, but localized changes up to ±28 dB clustered near eruptive pathways and margins. Most areas remain stable, consistent with lava covering a small fraction of the total extent.
  - Nov 2024 → Sept 2025: Similar behavior—near-zero mean yet concentrated pockets of change, indicating ongoing texture evolution (cooling, fracturing, sediment/ash reworking, vegetation dieback/regrowth).
  - Interpretation of change maps: red hues = surface roughening or vegetation growth (relative VH increase or VV modulation); blue hues = surface smoothing or vegetation loss (relative VH decrease).
  - Visual patterns in figures:
    - `outputs/comparison_may2024_nov2024.png`: Clear separation of ocean (yellow/orange), land/vegetation (green), and dark-green suspected lava; change hotspots align with 2024 activity zones.
    - `outputs/comparison_nov2024_sept2025.png`: Persistent separation of classes with new localized patches of change around 2025 eruptive features.
  - Statistics summary:
    - May→Nov 2024: Mean change 0.00 dB; localized ±28 dB.
    - Nov 2024→Sept 2025: Near-zero mean; concentrated localized changes.
    - Majority of the scene unchanged, as expected.
  - Figures and products:
    - Dual-map and change PNGs: see `outputs/comparison_may2024_nov2024.png` and `outputs/comparison_nov2024_sept2025.png`.
    - Delta GeoTIFFs and statistics CSVs: `outputs/delta_ratio_may_nov.tif`, `outputs/delta_ratio.tif`, `outputs/stats_delta_may_nov.csv`, `outputs/stats_delta_nov_sept.csv`.

## 5) The Verdict of the Lava — Hypotheses and Implications
- Fresh lava: low VH, variable VV, strong C vs L-band differences in coherence persistence.
- Vegetated margins: L-band penetrates deeper; distinct backscatter response vs C-band.
- SAR sees through cloud and night, providing continuity during hazardous episodes.

- Conclusions: SAR polarimetry (VH/VV) effectively detects subtle surface texture changes on Reykjanes. The VH/VV ratio is sensitive to physical properties: smooth lava exhibits lower VH relative to VV than vegetated terrain. Multi-temporal analysis reveals localized volcanic changes even when overall mean change is ~0 dB, underscoring SAR’s utility through persistent cloud cover typical of Iceland.
- Limitations: Small lava flows are subtle within large scenes, so signal changes are spatially sparse. Cropping to common extents and incidence-angle differences can reduce coverage and add variability. Higher spatial resolution or targeted windows would enhance flow delineation.
- Future Work: Integrate L-band to probe deeper into vegetation/soil, apply InSAR for deformation, and expand to full time-series analysis and polarimetric decompositions (where available) for improved discrimination of surface classes and eruption progression.
