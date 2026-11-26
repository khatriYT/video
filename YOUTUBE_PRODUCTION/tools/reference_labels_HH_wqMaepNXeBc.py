#!/usr/bin/env python3
"""Manual annotations for the 225 storyboard samples of the Hardy Humans reference
video wqMaepNXeBc ("What If You Were the Last Human on Earth for 3 Years?").

One row per sampled frame (every ~9.92 s). Annotated by eye from the contact
sheets on 2026-11-26. Samples are 320x180 scrub previews, so fine detail and
ALL motion are unobserved. 'caption' is the single burned-in caption word
visible in that sample ('' = none visible).

Merges with keyframe_metrics.csv (measured) and writes scene_timeline.csv.
Usage: python3 tools/reference_labels_HH_wqMaepNXeBc.py <02_Reference_Analysis dir>
"""
import collections
import csv
import os
import sys

# frame types
# PLATE_CHAR  character(s) inside a painted environment plate
# CU_CHAR     character close-up / two-shot, painted background defocused
# PLATE       painted environment, no character (establishing / atmosphere)
# POV         first-person hands/arms (Hardy's mustard sleeve + black mitten)
# INFO_DARK   flat vector infographic on dark navy/charcoal
# INFO_LIGHT  flat vector infographic on cream/paper or light background
# INFO_OVER   flat graphic/object floating over a defocused painted plate
# MAP         flat map / globe
# TITLE       "DAY N / subtitle" title card over a painted plate
# TEXT        typographic card
# INSERT      object close-up
# BLACK       end black
#
# shot: WS wide, MS medium, CU close-up, ECU extreme close-up, AERIAL, REAR (seen from behind), GFX graphic
L = [
 ("PLATE_CHAR","WS","subway_car","","1-pt perspective car full of round-head commuters; hero centre"),
 ("CU_CHAR","CU","subway_car","","hero face, car interior heavily defocused"),
 ("INFO_OVER","GFX","subway_car","ANNOUNCES","speaker grille + line-stop dots over blurred car"),
 ("PLATE_CHAR","WS","subway_car","EXCEPT","same car now empty; hero alone; dropped items"),
 ("POV","CU","dark","YOU","POV mitten holding phone in darkness"),
 ("INFO_DARK","GFX","tunnel_dark","","lightning-bolt icon over dark blurred tunnel"),
 ("PLATE","WS","street","","abandoned taxis, doors open, low angle"),
 ("PLATE_CHAR","WS","street","","HERO STREET plate (recurring), sunrise, hero small right"),
 ("INFO_DARK","GFX","dark","STILL","phone/clock icons on charcoal"),
 ("CU_CHAR","CU","cafe","SECONDS","hero smiling, cafe interior defocused"),
 ("CU_CHAR","CU","street","HOLDING","dog (Bagel) close-up, street defocused"),
 ("PLATE_CHAR","WS","street","CITY","street at dusk, hero + dog small; HUD stamp top-left"),
 ("PLATE_CHAR","WS","times_square","EMPTY","neon billboards, hero + dog centre"),
 ("MAP","GFX","map_dark","FIFTY","blackout map 50,000,000 with lit dots"),
 ("PLATE_CHAR","WS","rooftop","YORK","ROOFTOP plate (recurring): water tower, skyline at night, hero rear"),
 ("PLATE_CHAR","WS","rooftop","","same rooftop, stars brighter"),
 ("PLATE_CHAR","WS","rooftop","MANHATTAN","same rooftop"),
 ("PLATE","WS","night_sky","LIGHTS","Milky Way over dark city"),
 ("PLATE","WS","airport_terminal","GROUND","terminal window, grounded jets; '3 DAYS' tag"),
 ("PLATE_CHAR","WS","rooftop","","rooftop night"),
 ("POV","CU","kitchen","","mitten turning sink tap; HUD stamp"),
 ("MAP","GFX","map_light","MILES","reservoirs 100+ miles north of NYC"),
 ("INFO_LIGHT","GFX","diagram","THAT","building cross-section, water reaches ~6 floors, red X above"),
 ("INFO_OVER","GFX","kitchen","YOU","pot boiling on stove over blurred kitchen"),
 ("TITLE","WS","street","","DAY 5 / THE TUNNELS title card on street plate"),
 ("PLATE","WS","subway_tunnel","THE","flooded subway platform and train"),
 ("INFO_DARK","GFX","diagram","FLOODED","rising water line over pump circles"),
 ("PLATE_CHAR","WS","street","","hero + dog, steam from manhole"),
 ("PLATE_CHAR","WS","street","ANYTHING","hero with dogs on street"),
 ("INFO_LIGHT","GFX","fridge","AT","flat fridge interior, spoiled food"),
 ("INFO_LIGHT","GFX","pantry","SUGAR","icons: white rice, beans, salt, sugar"),
 ("TITLE","WS","street","","DAY 12 title dissolving over overcast street"),
 ("PLATE","WS","street","PACKS","dog pack crossing street"),
 ("INFO_DARK","GFX","diagram","RUNNING","NEVER RUN vs RUNNING = PREY pictograms"),
 ("PLATE_CHAR","WS","brownstones","AFTER","hero + dog on taxi roof, low angle"),
 ("PLATE_CHAR","WS","brownstones","","same"),
 ("PLATE_CHAR","WS","street","SILENCE","golden-hour street, hero walking; HUD"),
 ("PLATE_CHAR","WS","island_selkirk","ALONE","historical: castaway, hut, boat, cliffs"),
 ("INFO_OVER","GFX","island_selkirk","","split panels HUNTED / READ"),
 ("PLATE_CHAR","MS","apartment_night","ONE","dog at candlelit table, set plates"),
 ("TITLE","WS","street","","DAY 70 / THE GREEN on summer street"),
 ("PLATE_CHAR","WS","street","","summer street, hero + dog"),
 ("MAP","GFX","map_light","NORTHEAST","Northeast map ~30% less pollution"),
 ("PLATE","WS","street","LIKE","deer on the street"),
 ("INFO_DARK","GFX","diagram","","cell tower + empty battery"),
 ("INFO_OVER","CU","apartment","A","radio + dog over blurred room"),
 ("MAP","GFX","map_light","MAP","Manhattan map with pin"),
 ("PLATE_CHAR","WS","street","BICYCLE","hero walking bicycle, dog"),
 ("PLATE","WS","rooftop","LIGHTNING","rooftop in night storm, lightning; HUD"),
 ("PLATE","WS","historic_waterfront","BEFORE","historical: lantern-lit waterfront, tall ships, snow"),
 ("PLATE","WS","rooftop","THE","rooftop, red sun through smoke"),
 ("PLATE_CHAR","WS","rooftop","","night, fires on distant roofs, hero + dog rear"),
 ("INFO_OVER","GFX","street_snow","DEGREES","thermometer 20F over blurred snowy street"),
 ("INSERT","CU","fireplace","PIANO","piano chair burning in fireplace"),
 ("INFO_DARK","GFX","diagram","AFTER","rain clouds"),
 ("PLATE_CHAR","WS","apartment_night","","fireplace-lit living room, hero on sofa, dog"),
 ("PLATE_CHAR","WS","street_snow","THE","snowy street, smashed pharmacy window; HUD"),
 ("POV","CU","dark","","arm with scratch/bandage"),
 ("PLATE","WS","white_house","SON","historical: White House lawn tennis court (1924)"),
 ("INFO_DARK","GFX","diagram","INFECTION","BEFORE ANTIBIOTICS 1 IN 9 people icons"),
 ("INFO_DARK","GFX","diagram","YEARS","YEARS LATER pill bottles with ticks"),
 ("INFO_OVER","GFX","pharmacy","HOSPITALS","honey tube over blurred pharmacy shelves"),
 ("PLATE_CHAR","WS","apartment","","daylight living room, hero + dog"),
 ("PLATE","WS","street","DOWN","street one year on: weeds, rust; HUD"),
 ("PLATE","WS","subway_station","RAIL","subway train headlights, 625"),
 ("PLATE","WS","rooftop","NOBODY","rooftop by day, potted flowers"),
 ("PLATE","WS","sky","A","blue sky, jet contrail"),
 ("CU_CHAR","CU","rooftop","OR","hero worried, rooftop defocused"),
 ("PLATE","WS","subway_car","EARTH","empty subway car (callback); HUD DAY 366"),
 ("PLATE_CHAR","WS","rooftop","SKY","hero + dog watch contrail"),
 ("PLATE_CHAR","WS","rooftop","AGAINST","fire barrel, black smoke, hero signalling"),
 ("PLATE","WS","island_selkirk","ISLAND","historical castaway island + fire"),
 ("PLATE_CHAR","MS","rooftop","AT","hero + dog beside fire barrel"),
 ("PLATE_CHAR","WS","rooftop","PILOT","black smoke column, hero waving"),
 ("POV","CU","rooftop","CAN'T","mittens holding cardboard sign CAN / CAN'T"),
 ("TITLE","WS","bridge","","DAY 367 / THE BRIDGE, 1-pt perspective"),
 ("PLATE","WS","bridge","EIGHTY-THREE","bridge plate + '1883' number"),
 ("PLATE_CHAR","WS","bridge","AND","hero small, walking away down bridge"),
 ("INFO_DARK","GFX","diagram","FAIL","maintenance bar DECADES"),
 ("PLATE","WS","collapsed_highway","YEARS","collapsed elevated road, trucks, snow"),
 ("CU_CHAR","MS","street","NOBODY","hero cycling, background defocused"),
 ("CU_CHAR","CU","highway","UNDERSTAND","hero reading note: CAN'T LAND HERE. JFK. RUNWAY 4L"),
 ("MAP","GFX","map_light","EVERY","route Manhattan to JFK"),
 ("INFO_DARK","GFX","diagram","YEARS","EVERY DRAIN, CHECKED / AT LEAST EVERY 3 YEARS calendar"),
 ("PLATE_CHAR","WS","highway","","overgrown highway, abandoned cars, hero with bike"),
 ("PLATE","WS","airport_runway","RUNWAY","runway and terminal"),
 ("INFO_DARK","GFX","diagram","AND","runway 4L diagram"),
 ("CU_CHAR","CU","airport_runway","AROUND","Ruth intro: grey bun, glasses, headset, green coat"),
 ("PLATE","WS","forest_camp","FOR","flashback: tent camp in forest, MAINE label"),
 ("TEXT","GFX","dark","SLOWLY","big word WORDS on dark blur"),
 ("PLATE_CHAR","WS","airport_runway","","sunset runway, cargo plane, Ruth + hero + dog"),
 ("INFO_DARK","GFX","diagram","","FEDEX 200+ plane grid"),
 ("INFO_DARK","GFX","diagram","","radar scope SILENT"),
 ("INFO_DARK","GFX","diagram","CLEAR","4 RUNWAYS, one CLEAR"),
 ("CU_CHAR","CU","hangar","ME","Ruth surprised, hangar defocused"),
 ("PLATE_CHAR","WS","rooftop","SAW","rooftop seen from above/behind hero; plane in sky"),
 ("TITLE","WS","fuel_farm","","DAY 380 / THE FUEL over tank farm"),
 ("INFO_OVER","GFX","fuel_farm","YEAR","pipe + gauge 'A YEAR OLD', POV mitten"),
 ("INFO_LIGHT","GFX","diagram","COLLECTS","tank section, water settles at bottom"),
 ("PLATE_CHAR","WS","airport_runway","","Ruth checks fuel sample, hero + dog by plane"),
 ("INFO_LIGHT","GFX","diagram","","tank sump labelled WATER"),
 ("INFO_DARK","GFX","diagram","CHECK","FAA 85 DIDN'T CHECK PROPERLY plane grid"),
 ("PLATE_CHAR","WS","hangar_night","HANGAR","night hangar, fire barrel, Ruth + hero; HUD"),
 ("INFO_DARK","GFX","diagram","","RULE OF THUMB 50 people"),
 ("INFO_DARK","GFX","diagram","RESEARCHERS","paper icons"),
 ("PLATE","WS","tristan_da_cunha","ATLANTIC","remote island + globe inset"),
 ("PLATE_CHAR","MS","hangar_night","SIXTY-FOUR","Ruth + hero by fire barrel, dog asleep"),
 ("PLATE","WS","lab_freezers","BACKUP","lab with cryo tanks; HUD"),
 ("INFO_DARK","GFX","diagram","FAHRENHEIT","-320F freezer rack"),
 ("PLATE_CHAR","WS","lab_freezers","TANKS","hero, dog, Ruth among tanks"),
 ("INFO_DARK","GFX","diagram","TWENTY","2018 freezer + thermometer"),
 ("INFO_DARK","GFX","diagram","","4,000+ dot grid"),
 ("PLATE","WS","lab_freezers","","lab empty"),
 ("MAP","GFX","map_dark","","Svalbard / Norway"),
 ("INFO_LIGHT","GFX","diagram","","vault tunnel inside mountain cross-section"),
 ("INFO_DARK","GFX","diagram","DESIGNED","thermometer 5 YEARS freezing"),
 ("MAP","GFX","map_dark","BACK","globe 38,000 Aleppo to Svalbard"),
 ("PLATE","WS","seed_vault","","vault entrance in snowy mountain"),
 ("PLATE","WS","hangar","JFK","hangar door open onto airfield"),
 ("POV","CU","wood_table","STILL","mitten with seed packets on table"),
 ("INFO_LIGHT","GFX","wood_table","TOWEL","20 SEEDS on paper towel"),
 ("PLATE","WS","rooftop_garden","ROOF","rooftop garden, solar panels, skyline"),
 ("PLATE_CHAR","WS","rooftop_garden","GRID","hero tending garden"),
 ("PLATE_CHAR","WS","radio_room","BUILDS","night radio room, map on wall, hero + Ruth; HUD"),
 ("INFO_DARK","GFX","diagram","","line of sight 'A FEW MILES' over curved Earth"),
 ("INFO_DARK","GFX","diagram","OFF","radio wave bouncing off ionosphere"),
 ("MAP","GFX","map_dark","ABOUT","USA with dots"),
 ("PLATE_CHAR","WS","radio_room","CALLS","Ruth on headset, hero, dog"),
 ("PLATE_CHAR","WS","radio_room","","same"),
 ("CU_CHAR","CU","radio_room","RUTH","Ruth in beanie with headset"),
 ("PLATE","WS","airport_snow","THERE'S","snowed-in airport"),
 ("PLATE_CHAR","MS","hangar","THE","dog lying alone, water jugs"),
 ("CU_CHAR","CU","radio_room","WHEN","hero with headset at mic"),
 ("PLATE","WS","svalbard_town","","Arctic town at night, stars"),
 ("POV","CU","radio_room","","mitten keying microphone"),
 ("PLATE","WS","svalbard_town","NINE","same Arctic town"),
 ("PLATE","WS","street","","street two years on, overgrown; HUD DAY 730"),
 ("MAP","GFX","map_dark","GREENLAND","ISLAND-HOPPING route JFK-Goose Bay-Narsarsuaq-Svalbard"),
 ("MAP","GFX","map_dark","","900-1,000 NM range rings"),
 ("INFO_OVER","GFX","hangar","","checklist card: single-engine over the ocean"),
 ("INFO_DARK","GFX","diagram","","plane cutaway EXTRA TANKS"),
 ("PLATE","WS","sky","","contrail with bright point"),
 ("PLATE","WS","rooftop","COMMENTS","rooftop at dusk, empty"),
 ("PLATE_CHAR","MS","cockpit","IS","cockpit from behind Ruth + hero"),
 ("INSERT","ECU","cockpit","THE","airspeed gauge + mitten"),
 ("INFO_DARK","GFX","diagram","OR","route fork colder / warmer"),
 ("INFO_OVER","GFX","clouds","WORKING","stopwatch over blurred clouds"),
 ("PLATE_CHAR","WS","street","EXCEPT","callback: day-1 street, hero + dog centre"),
 ("CU_CHAR","CU","radio_room","","hero + Ruth two-shot by radio"),
 ("PLATE_CHAR","WS","airport_runway","","loading the plane; HUD DAY 731"),
 ("INFO_OVER","GFX","hangar","THEN","dish/sample with mitten"),
 ("INFO_OVER","GFX","hangar","TODAY","same sample, spots appeared"),
 ("INFO_DARK","GFX","diagram","TO","satellite + rising curve 'a few meters'"),
 ("POV","CU","hangar","HONEY","both mittens holding honey jar"),
 ("PLATE_CHAR","MS","cockpit","","dog between seats, hero with headset, clouds outside"),
 ("PLATE","WS","goose_bay","","snowy night airfield, parked military jets; 22,500 sign"),
 ("PLATE_CHAR","WS","goose_bay","","plane, Ruth + hero + dog; gauge inset"),
 ("INSERT","CU","goose_bay","A","fuel pump with taped note"),
 ("PLATE_CHAR","WS","goose_bay","TIRE","hero with tire"),
 ("PLATE_CHAR","WS","rooftop","AFTER","flashback rooftop, hero + dog"),
 ("TITLE","WS","ocean_ice","","DAY 733 / THE ICE over icy ocean"),
 ("PLATE_CHAR","WS","goose_bay","UGLY","same airfield"),
 ("INFO_DARK","GFX","diagram","ACCIDENTS","icing accidents 1987-2009 timeline, 26"),
 ("INFO_DARK","GFX","diagram","WHEN","ice building on wing leading edge"),
 ("PLATE","WS","clouds","AIR","small plane in grey cloud"),
 ("PLATE_CHAR","MS","cockpit","WINDSHIELD","iced windshield"),
 ("PLATE","AERIAL","greenland_fjord","GREENLAND","fjord + glacier aerial; HUD"),
 ("PLATE","AERIAL","greenland_fjord","PILOTS","same, tiny plane"),
 ("PLATE_CHAR","MS","cockpit","","cockpit facing snowy peaks"),
 ("PLATE_CHAR","WS","greenland_airstrip","MILES","airstrip in fjord, trio walking"),
 ("PLATE","WS","greenland_fjord","PITCH","historical Norse ship + inset of green Greenland"),
 ("PLATE","WS","norse_ruins","1450","ruins, church, translucent Norse figures"),
 ("TITLE","WS","ice_sheet","","DAY 734 over ice sheet"),
 ("INFO_DARK","GFX","diagram","OF","ice sheet dome 3 km cross-section"),
 ("PLATE","AERIAL","ice_sheet","TWO","historical sepia: 1942 planes on ice"),
 ("INFO_LIGHT","GFX","diagram","DUG","plane buried under ice layers"),
 ("TITLE","WS","reykjavik","","DAY 736 / ICELAND, dusk street + church"),
 ("INFO_DARK","GFX","diagram","","hydro dam + power lines"),
 ("PLATE","WS","geothermal","","geothermal pool landscape"),
 ("PLATE","WS","geothermal","","same, '75,000' sign"),
 ("PLATE_CHAR","WS","hot_river","FIRST","hero + Ruth bathing in hot river, boardwalk"),
 ("PLATE","WS","hot_river","","same river, steam, no characters"),
 ("MAP","GFX","map_dark","","Iceland-Svalbard route with X"),
 ("MAP","GFX","map_dark","OVER","polar map, Svalbard"),
 ("INSERT","CU","plane_window","SEA","sea ice through cabin window"),
 ("PLATE","WS","sea_ice","","polar bear on sea ice"),
 ("CU_CHAR","CU","cockpit","","Ruth + hero two-shot, sunset window"),
 ("PLATE_CHAR","WS","svalbard_airport","","nine strangers walk to the plane"),
 ("CU_CHAR","CU","svalbard_airport","UKRAINE","Olena intro + luggage-tag name label"),
 ("CU_CHAR","CU","svalbard_airport","OF","Pavel intro + luggage-tag name label"),
 ("MAP","GFX","globe","VANISHING","globe, Svalbard marked"),
 ("INFO_DARK","GFX","diagram","SIXTY-FIVE","people grid, 65+ highlighted"),
 ("INFO_OVER","GFX","diagram","BRING","card 1988: cat/dog/rabbit crossed out"),
 ("PLATE_CHAR","WS","dog_yard","ALL","sled-dog yard, characters"),
 ("CU_CHAR","CU","svalbard_town","","young person in fur hood"),
 ("PLATE_CHAR","REAR","seed_vault_tunnel","INSIDE","group walking into vault tunnel"),
 ("PLATE","WS","seed_vault_tunnel","NOBODY","frosted vault door"),
 ("INSERT","CU","seed_vault","FAHRENHEIT","box of seed packets + clock"),
 ("PLATE_CHAR","MS","seed_vault","YOURS","hero + elderly scientist by seed boxes"),
 ("INFO_DARK","GFX","diagram","COPY","archive device on dark"),
 ("PLATE","WS","satellite_station","POINT","radomes and dishes on snowy plateau"),
 ("PLATE","WS","fjord_sun","TWENTY-THIRD","midnight sun over fjord + clock inset; HUD"),
 ("INFO_DARK","GFX","diagram","MELATONIN","melatonin curve"),
 ("PLATE_CHAR","WS","greenhouse","CHEF","greenhouse dome, group at table"),
 ("PLATE_CHAR","WS","fjord_sun","RUN","dog + reindeer at midnight sun"),
 ("CU_CHAR","MS","hangar_dark","","Signe touching airliner fuselage"),
 ("PLATE","WS","hangar_dark","","airliner in dark hangar"),
 ("CU_CHAR","CU","hangar_dark","","Signe, airliner defocused"),
 ("INFO_DARK","GFX","diagram","","35,000 ft, -65F"),
 ("PLATE","AERIAL","nyc_aerial","SIGNE","Manhattan aerial at dusk, circling contrail"),
 ("CU_CHAR","CU","hangar_dark","EVERY","Signe with radio"),
 ("INSERT","CU","cockpit_window","FOR","Signe seen through oval cockpit window"),
 ("PLATE","WS","svalbard_town","POLAR","polar night town; HUD DAY 1000"),
 ("PLATE","WS","svalbard_town","DAYTIME","same with aurora"),
 ("PLATE_CHAR","WS","community_room","ALL","whole group + dog in lounge"),
 ("PLATE","WS","space","","space station over Earth"),
 ("CU_CHAR","REAR","svalbard_town","NIGHTS","back of fur hood, shooting star"),
 ("PLATE_CHAR","WS","sun_stairs","EIGHTH","group on hillside stairs, sun returning; HUD DAY 1095"),
 ("PLATE_CHAR","WS","sun_stairs","DAY","closer angle"),
 ("PLATE_CHAR","WS","sun_stairs","EARTH","same"),
 ("MAP","GFX","map_dark","SVALBARD","Svalbard map"),
 ("MAP","GFX","map_dark","","map zoomed in"),
 ("PLATE_CHAR","WS","sun_stairs","","final hold"),
 ("PLATE_CHAR","WS","sun_stairs","","final hold"),
 ("BLACK","GFX","black","","end"),
]


def main(ref_dir):
    metrics = list(csv.DictReader(open(os.path.join(ref_dir, "keyframe_metrics.csv"))))
    assert len(metrics) == len(L), (len(metrics), len(L))
    rows = []
    for m, (ftype, shot, env, cap, note) in zip(metrics, L):
        r = {"sample": int(m["keyframe"][2:5]), "timecode": m["timecode"], "time_s": m["time_s"],
             "chapter": m["chapter"], "frame_type": ftype, "shot": shot, "environment": env,
             "caption_word": cap, "description": note}
        for k in ("mean_luma", "mean_saturation", "warm_minus_cool", "edge_density", "quantised_colours"):
            r[k] = m[k]
        r["keyframe_file"] = m["keyframe"]
        rows.append(r)
    with open(os.path.join(ref_dir, "scene_timeline.csv"), "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        wr.writeheader()
        wr.writerows(rows)

    # summary stats for the report
    n = len(rows)
    print("samples", n)
    for k in ("frame_type", "shot"):
        c = collections.Counter(r[k] for r in rows)
        print(k, ", ".join(f"{a} {b} ({100 * b / n:.0f}%)" for a, b in c.most_common()))
    env = collections.Counter(r["environment"] for r in rows if r["frame_type"] in ("PLATE", "PLATE_CHAR", "TITLE", "CU_CHAR"))
    print("top environments", env.most_common(12))
    for t in ("PLATE", "PLATE_CHAR", "CU_CHAR", "INFO_DARK", "INFO_LIGHT", "MAP"):
        sub = [r for r in rows if r["frame_type"] == t]
        if sub:
            avg = lambda k: sum(float(r[k]) for r in sub) / len(sub)
            print(f"{t:11s} luma {avg('mean_luma'):.2f} sat {avg('mean_saturation'):.2f} "
                  f"warm-cool {avg('warm_minus_cool'):+.3f} edges {avg('edge_density'):.3f} colours {avg('quantised_colours'):.0f}")
    capd = sum(1 for r in rows if r["caption_word"])
    print(f"caption visible in {capd}/{n} samples ({100 * capd / n:.0f}%)")
    hud = sum(1 for r in rows if "HUD" in r["description"])
    print("HUD stamps noted", hud)


if __name__ == "__main__":
    main(sys.argv[1])
