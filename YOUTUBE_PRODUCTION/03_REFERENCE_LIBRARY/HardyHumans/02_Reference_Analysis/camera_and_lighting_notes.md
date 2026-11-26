# Camera and Lighting Notes: Hardy Humans (wqMaepNXeBc)

All camera notes describe **framing in still samples**. Camera *movement* was not observable; see `motion_notes.md`. Estimates are labelled.

## 1. Shot vocabulary [VERIFIED counts, 225 samples]

| Shot | Share | Typical use | Apparent lens (estimate) |
|---|---|---|---|
| Wide / establishing | 48% | Locations, passage of time, characters small in the world | 24–35 mm equivalent; deep focus |
| Graphic | 31% | Facts, numbers, maps | n/a (flat) |
| Close-up | 13% | Emotion beats, character introductions, reading notes | 50–85 mm look; **background strongly defocused** (edge density 0.083 vs 0.24–0.28 on plates [MEASURED]) |
| Medium | 5% | Two-shots by a fire or radio, cockpit | 35–50 mm look |
| Aerial | 2% | Fjords, ice sheet, Manhattan at dusk | High oblique, 30–45° down |
| Rear / over-the-shoulder | 1% | Walking into the vault, looking at the sky | Eye level from behind |
| POV hands (counted within the close-ups and graphics) | about 3% | Turning a tap, holding a sign, seed packets, a honey jar | First person, hands entering from the bottom or right |

## 2. Camera height and angle [VERIFIED by eye]

- **Eye level** is the default for streets, interiors and runways. The horizon sits on the upper third, leaving a "floor" for characters.
- **Low angle** is used for heroic or vulnerable beats: the hero on a taxi roof with the dog pack below, the abandoned taxis at 0:59.
- **Rear views** of the hero looking out over the city appear on the rooftop at night (several samples). This is the "contemplation" shot.
- **One-point perspective centring** is used for the subway car, the Brooklyn Bridge, the vault tunnel and the highway. The hero sits on the vanishing axis and is often small and walking away.

## 3. Composition rules observed

1. **Hero small, world big.** In 48% wide shots the hero is often under 15% of frame height.
2. **A clear stage.** The plate is composed with an empty lower-middle zone where flat characters stand; the action stays inside the title-safe area.
3. **Close-ups fill 35–55% of height**, set slightly off-centre, with defocused background shapes still readable for location.
4. **Negative space for numbers.** Call-out numerals ("1883", "625", "22,500") sit in sky or wall areas on the upper right.
5. **Graphics are centred and symmetric**, with one focal element and a label below.

## 4. Lighting [VERIFIED by eye; all values descriptive estimates]

| Condition | Key light | Fill / ambient | Accents | Mood |
|---|---|---|---|---|
| Sunrise / day 1 | Low warm sun from frame right or the back, long shadows | Cool blue sky fill | Lens-like glow at the light source | Eerie calm |
| Golden hour (Day 50) | Warm, low, side-lit facades | Warm bounce off brick | Rim light on trees | Melancholy beauty |
| Overcast (Day 12, 21) | Soft, diffuse from above | Grey, low contrast | None | Decay, threat |
| Night city / rooftop | Moon/sky ambient (cool indigo) | Very low | Warm practicals: windows, fire barrels; stars, Milky Way | Isolation |
| Storm (Day 160) | Lightning flash | Dark blue | Rain streaks | Danger |
| Fire night (Day 160) | Orange point sources across rooftops | Deep blue | Smoke | Hope / signal |
| Interior at night | Fireplace or lamp as key (warm, 2000–2700 K look) | Deep shadow | Candle | Comfort, loneliness |
| Snow day | High, soft, bright | Blue-white bounce | None | Hardship |
| Arctic polar night | Street-lamp sodium pools + aurora green | Deep blue | Stars | Wonder |
| Midnight sun / final sunrise | Low sun on the horizon, strong backlight | Pink-violet sky | Flare halo around the sun | Resolution |

**General lighting traits**
- Painterly global illumination: soft contact shadows and ambient occlusion in corners.
- No harsh specular highlights; materials read as matte.
- Atmospheric perspective: distant buildings and mountains are lighter and bluer. Haze is used for depth.
- Flat characters get **no cast shadow**, or only a very faint one, which keeps them graphic against the painted plates [VERIFIED in most samples].
- **Night is never pure black:** it is a lifted blue base with warm accents. Exposure keeps silhouettes readable.

## 5. Depth of field [VERIFIED + MEASURED]

- Wide plates have deep focus.
- Character close-ups, POV hands and "graphic over plate" shots use a **strong gaussian-style blur** on the plate behind them. The blur is strong enough to drop edge density by about 70%.
- The same plate is reused, blurred, as the background for an infographic or close-up. This **ties the graphic to the location** without drawing a new image.

## 6. Recommendations for our 3D/hybrid build

| Reference trait | Blender equivalent |
|---|---|
| Wide deep-focus plates | Camera lens 24–35 mm, f/8+, or DOF off |
| Close-ups with heavy blur | 50–85 mm, f/1.4–2.0, focus on the character. Or render the plate once, then blur it in the compositor or FFmpeg (much cheaper) |
| Matte painterly GI look | Eevee with soft shadows, ambient occlusion and bloom; or Cycles with ≥128 samples. Note: Ubuntu's Blender has **no denoiser** (see the capability report) |
| Time-of-day sets | Save sun angle, colour, world colour and practical lights as named **lighting presets** in one environment .blend, e.g. `ENV01_dawn`, `ENV01_golden`, `ENV01_overcast`, `ENV01_night` |
| Recurring evolving location | One master environment .blend with collection or geometry-node toggles for vegetation density, decay, snow and so on, rendered from **fixed camera presets** |
