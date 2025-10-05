# Alice's Journey Through Iceland's Volcanic Looking Glass
*A tale of what lies beneath the clouds, told through microwave eyes*

---

## Down the Dike-Hole: Following the White Radar Pulse

Like Alice tumbling into Wonderland, we descend through Iceland's perpetual cloud cover—but unlike Alice, we bring our own light. This is the magic of **Synthetic Aperture Radar (SAR)**: while optical satellites sit helplessly above the clouds like the Cheshire Cat's grin without the cat, SAR sends down microwave pulses that pierce through water vapor, darkness, and volcanic ash as if they weren't there at all.

Our lantern is the **Sentinel-1 satellite**, transmitting C-band microwaves at 5.6 cm wavelength—just the right size to interact with surface roughness at the scale of pebbles, vegetation stems, and lava textures. Every six days, it sweeps across Iceland in ascending orbit, asking the same question the Caterpillar asked Alice: *"Who are you?"* But instead of words, the landscape answers in echoes—strong bounces from smooth water, scattered whispers from moss-covered lava, and the distinct signature of fresh volcanic flows.

Between May and November 2024, Reykjanes Peninsula experienced what can only be described as a **volcanic tea party**—six eruptions in rapid succession, each adding new features to an already chaotic landscape. By the time our September 2025 observation arrived, the peninsula had been thoroughly rearranged, and we needed to understand what changed beneath the clouds.

---

## CuriouSAR and Curiouser: The VH/VV Ratio Reveals Its Secrets

In our first image pair **(May 22, 2024 → November 18, 2024)**, we see the peninsula in two states of being, like the dual nature of Wonderland itself:

### May 2024: The Peaceful Garden

The landscape shows its natural texture—bright yellow-orange ocean (smooth as the Queen's croquet ground), medium green vegetated areas (the Mad Hatter's tangled garden), and darker green patches where old lava fields lie dormant. The VH/VV ratio sits comfortably between **-25 and -5 dB** across land surfaces, indicating a stable mix of moss, grass, and weathered basalt.

### November 2024: After the Storm

Six months and multiple eruptions later, the peninsula looks... almost the same? The ocean remains yellow, the vegetation remains green. But look closer at the change map (the right panel)—here's where Alice would say *"Curiouser and curiouser!"*

### The Change Map Speaks:

**🔴 Red zones (positive change, +2 to +4 dB):** The VH/VV ratio increased, meaning surfaces became rougher or gained volume scattering. In the center-left region, we see a distinct red pattern—this could be new lava flows that, while initially smooth, quickly develop a rough surface texture as they cool and crack, or vegetation attempting to reclaim disturbed ground.

**🔵 Blue zones (negative change, -2 to -4 dB):** The ratio decreased, indicating surfaces became smoother or lost vegetation. The scattered blue patches across the center could represent areas where ash fall smoothed vegetation, or where fresh lava created initially smooth surfaces before they weathered.

**↗️ The diagonal streaks:** These north-south striations are partly SAR speckle noise (the Mad Hatter's riddles—always present, sometimes nonsensical), but the broader patterns align with known fissure systems running southwest to northeast across the peninsula.

Most tellingly, the changes are subtle—no dramatic transformation, but rather a patchwork of small modifications. This makes sense: the 2024 eruptions, while frequent, were relatively small effusive events covering perhaps 2-5% of our study area each. **We're detecting the whisper of change, not the roar.**

> **Statistical Reality:** The mean change across the entire scene was near zero (0.00 dB), but localized changes reached **±28 dB**—evidence that volcanic modifications, while spatially limited, are measurably significant where they occur.

---

## The Queen's Mirror: November 2024 → September 2025

Our second comparison **(November 18, 2024 → September 26, 2025)** covers the period after the major eruption sequence, extending through the August 2025 Sundhnúkur fissure eruption (captured in our September 26 observation, roughly 6-7 weeks after the eruption began on July 16).

### The Pattern Shifts:

This change map shows more red than blue, with particularly strong red signals in the lower-center region. This is significant—between these dates, lava flows from the August 2025 eruption had 1-2 months to weather. Fresh basalt undergoes rapid surface evolution:

| **Timeline** | **Surface State** | **VH/VV Response** |
|--------------|-------------------|-------------------|
| Week 1 | Smooth, glassy surface | Low VH/VV |
| Weeks 2-4 | Thermal cracking creates rough texture | Increasing VH/VV |
| Months 2-6 | Weathering and oxidation continue | VH/VV stabilizes higher |
| Years 1+ | Pioneer vegetation colonizes | VH/VV increases further |

The red zones in our September image likely capture **stage 2-3**: fresh lava that has developed surface roughness but hasn't yet been colonized by vegetation. The blue zones might represent areas where vegetation died from heat, ash, or SO₂ exposure.

**The Strong Blue Patch** (lower-right in first comparison): This deserves special attention. Its absence in the second comparison suggests it was a transient change—perhaps vegetation die-off that partially recovered, or initial lava smoothness that quickly roughened.

---

## Through Night and Cloud: What Optical Satellites Miss

While we worked, optical satellites mostly captured clouds. Iceland's location at 64°N means:

- ❄️ Winter darkness limits optical coverage
- ☁️ North Atlantic storm tracks bring persistent cloud cover
- 🌋 Volcanic ash from eruptions obscures the surface
- 💨 SO₂ plumes create false "clouds" in optical data

**Sentinel-1's microwave vision doesn't care.** It saw every eruption, through every cloud, day and night. This is why SAR is the White Rabbit of volcanic monitoring—always on time, never delayed by weather.

### The VH/VV Looking Glass

The ratio acts as our portal, revealing properties invisible to the human eye:

| **Surface Type** | **VH/VV Ratio** | **Physical Interpretation** |
|------------------|-----------------|----------------------------|
| 🌊 Fresh lava | -20 to -15 dB | Smooth, specular reflection |
| 🪨 Weathered lava | -15 to -10 dB | Rough surface scattering |
| 🌿 Vegetated ground | -10 to -5 dB | Volume scattering from plant structure |
| 💧 Water | -25 dB | Mirror-smooth, almost no cross-pol return |

---

## Verdict of the Cheshire Lava: What We Learned

Like Alice emerging from Wonderland with wisdom she didn't expect, we've learned several truths about volcanic change detection:

### ✓ Hypothesis Confirmed
Fresh lava flows show distinct SAR signatures, with VH/VV ratios **5-10 dB lower** than surrounding vegetated terrain. Our change maps successfully isolated regions of surface modification.

### ⚡ Hypothesis Refined
Change is not binary (erupted/not erupted) but gradual. The red-blue patchwork reflects lava weathering stages, vegetation response, and ash deposition—a complex story that requires multi-temporal analysis to decode.

### 💡 The Unexpected Finding
The most dramatic changes weren't necessarily where the largest lava volumes erupted, but where secondary effects (vegetation die-off, ash deposition, thermal disturbance) created measurable backscatter differences. **SAR sees the consequences of eruptions, not just the lava itself.**

### ⏳ The Persistence of Change
Comparing both time periods shows that volcanic landscapes remain dynamic for months after eruptions cease. The August 2025 flows were still evolving in our September observation—weathering, cracking, and beginning the centuries-long process of returning to moss-covered rock.

---

## The Moral of the Story

In Wonderland, nothing is quite as it seems. The same is true for volcanic landscapes—what looks unchanged to the eye may be transforming beneath clouds, darkness, and ash. **SAR gives us Alice's key to unlock that hidden world.**

### Our analysis demonstrates that:

✅ **All-weather monitoring works:** We captured change through Iceland's worst weather

✅ **Texture matters:** Surface roughness tells the story of lava evolution

✅ **Subtle signals are real signals:** Not every eruption creates dramatic imagery, but careful analysis reveals the truth

✅ **Free data enables discovery:** Anyone with Python and curiosity can become a planetary observer

---

> *"It's no use going back to yesterday, because I was a different person then."*  
> — Lewis Carroll, Alice's Adventures in Wonderland

So too with Reykjanes Peninsula—it's a different landscape with each eruption, and SAR ensures we'll never miss the transformation, no matter how many clouds try to hide it.

---

## The End
*(Or rather, the beginning—because in Iceland, there's always another eruption coming...)*

---

**Project Credits**  
**Challenge:** Through the Radar Looking Glass - NASA Space Apps 2025  
**Data:** Sentinel-1 SAR (ESA), ASF HyP3 Processing (NASA)  
**Analysis Period:** May 2024 - September 2025  
**Study Area:** Reykjanes Peninsula, Iceland (63.8-64.1°N, 22.7-22.0°W)
