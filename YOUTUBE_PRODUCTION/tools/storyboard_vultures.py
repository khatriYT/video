#!/usr/bin/env python3
"""Episode 3 storyboard + script source of truth: "What If Every Vulture Disappeared?"

Each scene: (section, narration, visual, claims)
  visual types:
    ("plate", shot_id, move, extras)   Blender still + eased camera move; extras: tab/tag/fx/text
    ("anim",  shot_id, extras)         Blender-rendered 3D sequence (12 fps, held on twos)
    ("card",  card_type, params)       flat evidence/infographic card (PIL)
  moves: push, pull, pan_l, pan_r, rise, sink, hold
  tags:  STRONG, DEBATED, ESTIMATE, HYPOTHESIS, INFERENCE (evidence pill on screen)

Run: python3 tools/storyboard_vultures.py 01_PROJECTS/what_if_vultures_disappeared
Writes 06_Storyboard/storyboard.json, storyboard.md, scene_list.csv, asset_requirements.md
       04_Script/script_draft.md, script_final.md, script_sources.md
"""
import csv
import json
import os
import sys

TITLE = "What If Every Vulture Disappeared?"
VOICE = "am_michael"

S = []   # scenes


def sc(section, narration, visual, claims=()):
    S.append(dict(section=section, narration=narration, visual=visual, claims=list(claims)))


def plate(shot, move="push", **kw):
    return dict(type="plate", shot=shot, move=move, **kw)


def anim(shot, **kw):
    return dict(type="anim", shot=shot, **kw)


def card(kind, **kw):
    return dict(type="card", card=kind, **kw)


# ---------------------------------------------------------------- COLD OPEN
A = "Cold open"
sc(A, "A cow dies at the edge of a village in India. By mid-morning, the heat is already working on it.",
   plate("P00", "push", tab="HOUR 0 · Village edge, India", fx=["heat"]))
sc(A, "Then the sky starts to move. One dark shape. Then ten. Then fifty.",
   anim("A01"))
sc(A, "Within about half an hour, there's almost nothing left. No smell. No swarm of flies. No disease left lying in the sun.",
   plate("P02", "push", fx=["dust"]), ["C15"])
sc(A, "For thousands of years, that's how it worked. Then, in the 1990s, the vultures of South Asia started dying.",
   plate("P15", "pan_r"))
sc(A, "Not slowly. In about ten years, more than ninety-five percent of them were gone.",
   card("bignum", value="−95%", label="South Asia's Gyps vultures, in about a decade", tag="STRONG",
        icons="vultures_fade"), ["C01"])
sc(A, "What happened next turned one of the world's most hated birds into one of its most expensive losses.",
   plate("P03", "pull", tab="DAY 1 · No vultures"))
sc(A, "So what really happens when the vultures disappear? We don't have to guess. India already ran the experiment.",
   plate("P12", "rise", text=dict(style="title", main="WHAT IF EVERY VULTURE", sub="DISAPPEARED?")))
sc(A, "Welcome to The Disappearance Files, where we find out what the world loses when an animal nobody likes is suddenly gone.",
   plate("P09", "push"))

# ---------------------------------------------------------------- 1 MEET THE CREW
A = "Meet the cleanup crew"
sc(A, "First, meet the cleanup crew.",
   plate("P13", "push", text=dict(style="chapter", main="THE CLEANUP CREW", sub="Chapter 1")))
sc(A, "Vultures are big, broad-winged birds built for one job: finding dead animals, and finishing them fast.",
   plate("P10", "pan_l"))
sc(A, "They barely flap. They ride columns of rising warm air, circling for hours while they scan the ground below.",
   card("thermal"))
sc(A, "They also watch each other. When one vulture drops toward a carcass, others see it and follow, so a single meal can pull in birds from kilometres around.",
   plate("P01", "pull"))
sc(A, "One Rüppell's vulture was hit by a plane at eleven thousand three hundred metres. That's higher than Mount Everest.",
   plate("P11", "push", text=dict(style="callout", main="11,300 m", sub="Rüppell's vulture · 1973")),
   ["C14"])
sc(A, "That bald head isn't a flaw. Bare skin stays cleaner when you feed inside a carcass, and it may help the bird shed heat.",
   plate("P14", "push", tag="HYPOTHESIS"))
sc(A, "And their stomachs are brutal. Harsh acid and specialised gut bacteria let them eat meat carrying germs like anthrax, which would sicken most other animals.",
   card("gut", tag="STRONG"), ["C13"])
sc(A, "In other words, a vulture isn't just eating garbage. It's taking disease out of circulation.",
   plate("P02", "pull", fx=["dust"]))

# ---------------------------------------------------------------- 2 THE COLLAPSE
A = "The collapse"
sc(A, "In India, vultures were part of everyday life: on rooftops, on old trees, circling over every town dump.",
   plate("P15", "push", text=dict(style="chapter", main="THE COLLAPSE", sub="Chapter 2")))
sc(A, "Then, through the 1990s, birdwatchers started noticing empty nests, and dead vultures lying under their roosts.",
   plate("P17", "push"))
sc(A, "Surveys showed losses of more than ninety-five percent. For the white-rumped vulture, by some estimates, ninety-nine point nine.",
   card("decline", tag="STRONG"), ["C01", "C02"])
sc(A, "Scientists suspected a virus. Pesticides. Something in the water.",
   card("suspects"))
sc(A, "The real killer was hiding in plain sight, in a medicine cabinet.",
   plate("P16", "push"))
sc(A, "Diclofenac: a cheap painkiller that farmers gave to sick and injured cattle.",
   plate("P19", "pan_r", text=dict(style="label", main="DICLOFENAC", sub="veterinary painkiller")), ["C03"])
sc(A, "When a treated cow died, traces of the drug stayed in its body. Harmless to the cow. Deadly to a vulture.",
   card("chain", tag="STRONG"), ["C03"])
sc(A, "Their kidneys failed within days, and a single contaminated carcass could poison dozens of birds at once.",
   plate("P17", "pull"), ["C03"])
sc(A, "And it took shockingly little. One study calculated that if fewer than one carcass in a hundred carried a lethal dose, that alone could explain the crash.",
   card("grid", tag="STRONG"), ["C20"])
sc(A, "Today, three of South Asia's vulture species are listed as critically endangered.",
   card("redlist", tag="STRONG"), ["C24"])
sc(A, "In 2004, researchers finally proved the link. India banned veterinary diclofenac in 2006.",
   card("timeline", items=[["2004", "Cause proven"], ["2006", "India bans vet diclofenac"]], tag="STRONG"),
   ["C03", "C04"])
sc(A, "But by then, the sky above India was already almost empty.",
   plate("P12", "sink"))

# ---------------------------------------------------------------- 3 THE EXPERIMENT (observation plate)
A = "A world without vultures"
sc(A, "So let's go back to that cow at the edge of the village. Same place. Same morning. But this time, no vultures come.",
   plate("P03", "push", tab="DAY 1 · No vultures",
         text=dict(style="chapter", main="NO VULTURES", sub="Chapter 3")))
sc(A, "A few crows peck at it. They can't open a carcass this big. So it just lies there, in the heat.",
   plate("P03C", "push", fx=["heat"]))
sc(A, "Day three. The flies arrive. Then thousands more.",
   plate("P04", "push", tab="DAY 3", fx=["flies"]))
sc(A, "This part has been tested. In a 2025 experiment in Costa Rica, carcasses that vultures couldn't reach took about twice as long to break down, and drew nearly twice as many flies.",
   card("compare", title="Costa Rica, 2025", rows=[["Time to decompose", "×2"], ["Flies at carcass", "×2"]],
        tag="STRONG"), ["C06"])
sc(A, "In Kenya, keeping vultures away made carcasses last nearly three times longer, and tripled the number of mammals that came to feed.",
   card("compare", title="Kenya, 2012", rows=[["Carcass lasts", "×3"], ["Mammal scavengers", "×3"]],
        tag="STRONG", map="KEN"), ["C07"])
sc(A, "And in India, the mammal that showed up most was this one.",
   plate("P08", "push"))
sc(A, "Week two. Stray dogs have found the dump. A meal that vultures would have finished in an afternoon is now a feast for the pack.",
   plate("P05", "push", tab="WEEK 2", fx=["flies"]))
sc(A, "More food means more puppies survive. By year one, the pack is bigger.",
   plate("P06", "pan_l", tab="YEAR 1", tag="DEBATED"), ["C08"])
sc(A, "Across India, researchers saw feral dog numbers rise as the vultures vanished. Whether one caused the other is still debated, but the timing lines up.",
   card("lines", tag="DEBATED"), ["C08"])
sc(A, "And dogs carry something vultures never spread: rabies.",
   plate("P18", "push", tab="YEAR 1 · The village"))
sc(A, "Dogs cause almost all human rabies cases, and India accounts for roughly a third of the world's rabies deaths.",
   card("fraction", value="≈ 1/3", label="of the world's rabies deaths occur in India (WHO)", tag="STRONG",
        map="IND"), ["C09"])
sc(A, "Year ten. The dump has become a field of bones, and the dogs own it.",
   plate("P07", "push", tab="YEAR 10", fx=["dust"]))

# ---------------------------------------------------------------- 4 THE BILL
A = "The bill"
sc(A, "So did losing the vultures actually cost human lives? In 2024, two economists, Eyal Frank and Anant Sudarshan, set out to measure it.",
   card("paper", title="The Social Costs of Keystone Species Collapse",
        sub="Frank & Sudarshan · American Economic Review · 2024",
        chapter=dict(main="THE BILL", sub="Chapter 4")), ["C11"])
sc(A, "They compared districts where vultures used to be common with districts where they never were, before and after the diclofenac years.",
   card("districts"), ["C11"])
sc(A, "Their finding: in former vulture country, human death rates rose by about four point seven percent.",
   card("bignum", value="+4.7%", label="human death rate in districts that lost their vultures", tag="ESTIMATE"),
   ["C11"])
sc(A, "Sales of rabies vaccine went up. Water quality got worse, as more carcasses were left to rot near rivers and wells.",
   card("icons2", left=["vaccine", "Rabies vaccine sales ↑"], right=["water", "Water quality ↓"], tag="STRONG"),
   ["C10"])
sc(A, "Their estimate: roughly a hundred thousand extra deaths a year. About half a million people between 2000 and 2005.",
   card("bignum", value="≈ 500,000", label="extra human deaths in India, 2000–2005 (estimate)", tag="ESTIMATE"),
   ["C11"])
sc(A, "That's a statistical estimate, not a body count. But it puts a price on the bird nobody wanted: about sixty-nine billion dollars, every year.",
   card("bignum", value="$69 bn", label="per year in mortality costs (estimate)", tag="ESTIMATE"), ["C12"])

# ---------------------------------------------------------------- 5 RIPPLES
A = "Ripples"
sc(A, "The loss reached places you might not expect.",
   plate("P20", "push", text=dict(style="chapter", main="RIPPLES", sub="Chapter 5")))
sc(A, "For centuries, India's Parsi community has laid its dead in Towers of Silence, open to the sky, where vultures returned the bodies to nature.",
   plate("P20", "pan_l"), ["C16"])
sc(A, "With the vultures gone, some towers now use solar concentrators instead. They struggle in the monsoon, when the sun disappears behind clouds.",
   plate("P20B", "push", fx=["rain"]), ["C16"])
sc(A, "Europe ran its own version of the experiment, by choice.",
   card("map", country="ESP", label="Spain"))
sc(A, "After the mad cow crisis, new rules meant dead livestock had to be collected and trucked away, instead of being left out for vultures.",
   card("trucks"), ["C17"])
sc(A, "One study found those trucks covered nearly fifty million kilometres a year, releasing about seventy-seven thousand tonnes of carbon dioxide. Work the vultures used to do for free.",
   card("trucks_numbers", tag="STRONG"), ["C17"])

# ---------------------------------------------------------------- 6 AFRICA
A = "It's happening again"
sc(A, "And right now, it's happening again. This time in Africa.",
   plate("P21", "push", tab="TODAY · Savanna, Africa",
         text=dict(style="chapter", main="AFRICA, NOW", sub="Chapter 6")))
sc(A, "A 2016 study found that eight African vulture species had fallen by an average of sixty-two percent. Seven of them by eighty percent or more, in just three generations.",
   card("africa", tag="STRONG"), ["C18"])
sc(A, "The main killer here isn't medicine. It's poison, often laced into carcasses, and the trade in vulture parts for traditional remedies.",
   plate("P22", "pull"), ["C18"])
sc(A, "Some poachers even poison elephant carcasses on purpose, because circling vultures can lead rangers straight to an illegal kill. In one case in Namibia, around five hundred vultures died at a single carcass.",
   card("poison", tag="STRONG"), ["C21"])
sc(A, "Together, those two threats account for about ninety percent of the vulture deaths that get reported.",
   card("bignum", value="90%", label="of reported vulture deaths in Africa: poisoning + trade in parts", tag="STRONG"),
   ["C18"])

# ---------------------------------------------------------------- 7 REPLACEMENTS
A = "Could anything replace them?"
sc(A, "So if vultures vanished everywhere, would something else simply step in?",
   plate("P09", "push", text=dict(style="chapter", main="REPLACEMENTS?", sub="Chapter 7")))
sc(A, "Partly. Dogs, jackals, hyenas, crows, rats, flies and bacteria would all take a share.",
   card("replacements"))
sc(A, "But none of them do all three things vultures do: spot a carcass from far away, strip it in minutes, and destroy the germs inside it.",
   card("checklist", tag="INFERENCE"), ["C19"])
sc(A, "The experiments point the same way. Without vultures, carcasses last longer, and the animals that replace them spread more disease, not less.",
   plate("P06", "push", fx=["flies"]), ["C06", "C07", "C19"])
sc(A, "Ecologists call that a keystone loss: pull out one stone, and the whole arch starts to lean.",
   card("keystone"))

# ---------------------------------------------------------------- 8 ENDING
A = "Holding the line"
sc(A, "The good news? We know exactly what killed them.",
   plate("P24", "push", text=dict(style="chapter", main="HOLDING THE LINE", sub="Chapter 8")))
sc(A, "India has banned veterinary diclofenac, and in 2023 it banned two more drugs that harm vultures: ketoprofen and aceclofenac.",
   card("bans", tag="STRONG"), ["C04", "C05"])
sc(A, "And vets have a safer option: a painkiller called meloxicam, which doesn't harm vultures.",
   plate("P16", "pull", text=dict(style="label", main="MELOXICAM", sub="vulture-safe alternative")), ["C23"])
sc(A, "In Nepal, conservationists opened vulture restaurants: feeding stations stocked with drug-free carcasses. Near some of them, nesting vultures have started to come back.",
   plate("P24", "pull", tab="NEPAL · Vulture restaurant"), ["C22"])
sc(A, "Breeding centres are raising vultures in captivity, and conservationists are pushing for vulture-safe zones, where harmful drugs aren't sold.",
   plate("P15", "pull"), ["C05"])
sc(A, "But the numbers haven't bounced back, and experts warn that drug bans alone won't be enough.",
   plate("P12", "push"), ["C05"])
sc(A, "Which brings us back to that cow at the edge of the village.",
   plate("P00", "push", tab="HOUR 0"))
sc(A, "Most people would look at the birds crowding around it and see something ugly.",
   plate("P02", "push", fx=["dust"]))
sc(A, "But what you're really watching is a public health service. A cleanup crew, and a firewall against disease, all working for free.",
   anim("A02"))
sc(A, "We tend to protect the animals that look beautiful. Vultures are a reminder that some of the most important ones don't.",
   plate("P13", "pull"))
sc(A, "India learned what it costs when that service shuts down. The rest of the world still has a chance to keep it running.",
   anim("A03"))
sc(A, "Which animal do you think we're quietly losing next? Tell me in the comments, and I'll investigate it.",
   plate("P09", "pull", text=dict(style="end", main="THE DISAPPEARANCE FILES", sub="Episode 3 · Vultures")))


def main(proj):
    P = lambda *x: os.path.join(proj, *x)
    scenes = []
    for i, s in enumerate(S, 1):
        d = dict(id=i, file=f"SC{i:03d}", **s)
        d["words"] = len(s["narration"].split())
        d["est_s"] = round(d["words"] / 2.5 + 0.7, 1)
        scenes.append(d)
    words = sum(s["words"] for s in scenes)
    os.makedirs(P("06_Storyboard"), exist_ok=True)
    json.dump(dict(title=TITLE, voice=VOICE, scenes=scenes), open(P("06_Storyboard", "storyboard.json"), "w"),
              indent=1, ensure_ascii=False)

    claims = {r["claim_id"]: r for r in csv.DictReader(open(P("03_Research", "claim_checklist.csv")))}

    # script docs
    def script_md(final):
        out = [f"# {TITLE}", "", f"{'Final' if final else 'Draft'} script · {words} words · "
               f"estimated {sum(s['est_s'] for s in scenes) / 60:.1f} min at about 150 wpm · voice: Kokoro `{VOICE}`", ""]
        sec = None
        for s in scenes:
            if s["section"] != sec:
                sec = s["section"]
                out += ["", f"## {sec}", ""]
            v = s["visual"]
            vis = v.get("shot") or v.get("card")
            cl = ", ".join(s["claims"])
            out.append(f"**{s['file']}** ({v['type']}: {vis}{'; claims ' + cl if cl else ''})  ")
            out.append(s["narration"])
            out.append("")
        return "\n".join(out)

    os.makedirs(P("04_Script"), exist_ok=True)
    open(P("04_Script", "script_draft.md"), "w").write(script_md(False))
    open(P("04_Script", "script_final.md"), "w").write(
        script_md(True).replace("Final script",
                                "Final script (produced end-to-end at the user's request on 2026-11-26; "
                                "script approval still open, revisions welcome)"))
    src = ["# Script Sources", "", "Every factual claim in the narration is mapped to the claim checklist "
           "(`03_Research/claim_checklist.csv`) and the source library (`03_Research/source_library.md`).", "",
           "| Scene | Claim | Evidence | Sources | Wording used |", "|---|---|---|---|---|"]
    for s in scenes:
        for c in s["claims"]:
            r = claims[c]
            src.append(f"| {s['file']} | {c} | {r['evidence_tag']} | {r['source_ids']} | {r['claim_as_used_in_script']} |")
    open(P("04_Script", "script_sources.md"), "w").write("\n".join(src) + "\n")

    # storyboard docs
    with open(P("06_Storyboard", "scene_list.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["scene", "section", "type", "shot_or_card", "move", "tab", "tag", "fx", "words", "est_s", "claims",
                    "narration"])
        for s in scenes:
            v = s["visual"]
            w.writerow([s["file"], s["section"], v["type"], v.get("shot") or v.get("card"), v.get("move", ""),
                        v.get("tab", ""), v.get("tag", ""), "+".join(v.get("fx", [])), s["words"], s["est_s"],
                        " ".join(s["claims"]), s["narration"]])
    md = [f"# Storyboard: {TITLE}", "", f"{len(scenes)} scenes · {words} words. Shot specs (3D environments, cameras, "
          "lighting, states) are in `tools/vulture3d/shots.py`; card designs in `tools/vulture3d/cards.py`.", ""]
    for s in scenes:
        v = s["visual"]
        md.append(f"### {s['file']} · {s['section']}")
        md.append(f"- **Narration:** {s['narration']}")
        md.append(f"- **Visual:** {v['type']} `{v.get('shot') or v.get('card')}`"
                  + (f", camera move `{v['move']}`" if v.get("move") else "")
                  + (f", time tab \"{v['tab']}\"" if v.get("tab") else "")
                  + (f", evidence tag {v['tag']}" if v.get("tag") else "")
                  + (f", fx {', '.join(v['fx'])}" if v.get("fx") else "")
                  + (f", on-screen text \"{v['text']['main']}\"" if v.get("text") else ""))
        if s["claims"]:
            md.append(f"- **Claims illustrated:** {', '.join(s['claims'])}")
        md.append(f"- **Estimated duration:** {s['est_s']} s")
        md.append("")
    open(P("06_Storyboard", "storyboard.md"), "w").write("\n".join(md))
    shots = sorted({s["visual"]["shot"] for s in scenes if s["visual"]["type"] in ("plate", "anim")})
    cards = sorted({s["visual"]["card"] for s in scenes if s["visual"]["type"] == "card"})
    open(P("06_Storyboard", "asset_requirements.md"), "w").write(
        "# Asset Requirements\n\n## 3D shots (Blender)\n" + "\n".join(f"- {x}" for x in shots) +
        "\n\n## Cards\n" + "\n".join(f"- {x}" for x in cards) +
        "\n\n## Recurring 3D assets\n- CHR_PIP (mascot)\n- CRE_VULTURE (Gyps, folded / feeding / soaring / fallen poses)\n"
        "- CRE_DOG (pariah dog)\n- CRE_CROW\n- OBJ_COW (standing / carcass)\n- OBJ_VIAL (diclofenac vial)\n"
        "- ENV_DUMP (observation plate with time-step states)\n- ENV_SKY\n- ENV_VILLAGE\n- ENV_TOWER (Tower of Silence)\n"
        "- ENV_SAVANNA\n")
    print(f"{len(scenes)} scenes, {words} words, est {sum(s['est_s'] for s in scenes) / 60:.1f} min; "
          f"{len(shots)} 3D shots, {len(cards)} card types")


if __name__ == "__main__":
    main(sys.argv[1])
