# Reykjanes Peninsula Eruption Timeline (2024-2025)

## Study Period Context

Your SAR data covers:
- **Pre-eruption**: May 2024
- **Active period**: November 2024
- **Recent**: September 2025

## Complete Eruption Chronology

### 2024 Eruptions

**January 14, 2024** - Third eruption in series
- Marked the fifth volcanic event in the area within four years, occurring just outside the town of Grindavík
- Location: Near Grindavík town

**February 8, 2024** - Fourth eruption
- Sundhnukagigar became the site of a new eruption as a fissure emerged, spanning approximately 1.8 miles (3 kilometers) in length
- Fissure location shifted north from previous eruption

**March 16, 2024** - Fifth eruption (longest)
- Started on 16 March 2024 and became the longest in the series, spanning 54 days
- Duration: 54 days (longest of the series)
- Note: Magmatic intrusion earlier in month didn't reach surface

**May 29, 2024** - Sixth eruption
- The fifth eruption, which began on 29 May 2024, continued [into June]
- **CRITICAL: This overlaps with your "pre-eruption" baseline period**
- Your May 2024 scenes may show active lava

**August 22 - September 5, 2024** - Seventh eruption
- Sixth eruption lasted 14 days
- Duration: 14 days
- Between your baseline and "during" periods

**November 20 - December 8, 2024** - Eighth eruption (major)
- The seventh eruption in the same fissure zone began around midnight on the Reykjanes Peninsula. Lasting 18 days, it ended on December 8 and was the second-largest by produced lava flow
- **CRITICAL: Your "during" period (November 2024) captures this major eruption**
- Second-largest lava flow of entire series
- Duration: 18 days

### 2025 Eruptions

**April 1, 2025** - Ninth eruption (brief)
- The 11th eruption began at 9:44am on April 1, 2025, and was over within 24 hours
- Duration: Less than 24 hours
- Minimal impact

**July 16 - August 5, 2025** - Tenth eruption
- The most recent eruption on Iceland's Reykjanes Peninsula lasted from July 16 to August 5, 2025 along the Sundhnúksgígar (Sundhnúkur) crater row
- Duration: 20 days
- **Your September 2025 "recent" scenes show fresh lava from this event**
- This eruption was the 12th one since the eruptions began in March 2021, and the 9th one in the current location

**Current Status (October 2025)**
- There is currently no volcanic eruption in Iceland
- Flights, tours, and major routes are all running as normal

## Key Locations

**Sundhnúksgígar Crater Row**
- The eruption site is called Sundhnúkagígar
- Primary fissure zone for 2024-2025 eruptions
- Northeast of Grindavík town

**Infrastructure Impacts**
- Town of Grindavík repeatedly evacuated
- Blue Lagoon temporarily closed during events
- Hot water pipeline damaged (February 2024)

## Implications for Your SAR Analysis

### Expected Signatures in Your Data

**May 2024 scenes (labeled "pre"):**
- ⚠️ **Warning**: May 29 eruption means this isn't truly "pre-eruption"
- You may already see fresh lava from late May event
- Consider relabeling as "early summer 2024"

**November 2024 scenes (labeled "during"):**
- ✓ Should capture November 20-December 8 eruption
- Second-largest lava flow of the series
- Expect dramatic backscatter changes
- Fresh lava fields expanding

**September 2025 scenes (labeled "recent"):**
- Shows aftermath of July 16-August 5 eruption
- Fresh lava only 1-2 months old
- Still cooling (may affect thermal properties)

### Hypotheses to Test

1. **Fresh Lava Signature (July-August 2025)**
   - Smooth pahoehoe flows: Low VH (minimal volume scatter)
   - Rough aa flows: Higher VV (surface roughness)
   - VH/VV ratio should be lowest in freshest lava

2. **Temporal Evolution**
   - Compare May → November → September
   - Track progressive lava accumulation
   - Note: Complex because May already had active eruption

3. **Lava Flow Boundaries**
   - Sharp transitions in backscatter at flow edges
   - Older lava (pre-2024) vs new lava (2024-2025)

4. **Vegetation Loss**
   - Areas covered by lava: VH drops (no vegetation structure)
   - Surrounding areas: VH maintained

## Data Sources & References

- Guide to Iceland volcanic timeline
- Wikipedia: 2023-2025 Sundhnúkur eruptions
- Icelandair volcanic activity updates
- Adventures.is eruption tracker
- Visit Reykjanes official updates

## Action Items for Your Analysis

1. **Verify your scene dates against this timeline**
   - Check exact acquisition dates in manifest.csv
   - Note which eruptions were active during each scene

2. **Adjust your narrative framing**
   - May 2024 is NOT a true "pre-eruption" baseline
   - Better framing: "Early phase" vs "peak activity" vs "recent"

3. **Focus comparison on November → September**
   - November: Second-largest eruption active
   - September: Fresh lava from July eruption
   - This gives clearest change signal

4. **Validate with known lava extents**
   - Search for "Sundhnúksgígar lava flow maps 2024 2025"
   - Overlay with your SAR change detection

## Warning Signs in Your Data

**If you see minimal change between May and November:**
- May scene may be cloud-affected or during active eruption
- Consider using only November → September comparison

**If September shows less change than expected:**
- Fresh lava may be cooling/settling
- VH/VV ratio stabilizing after initial emplacement