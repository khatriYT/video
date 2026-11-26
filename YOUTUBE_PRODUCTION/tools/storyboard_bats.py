#!/usr/bin/env python3
"""Episode 4 storyboard + script source of truth: "What If All Bats Disappeared?"

Each scene: (section, narration, visual, claims)
  visual types:
    ("plate", shot_id, move, extras)   v3 layered shot: detailed 3D plate + animated character pass + camera move
    ("card",  card_type, params)       evidence/infographic card over a defocused 3D backdrop
  Shot specs (environment, camera, lighting, actors) live in tools/bats3d/shots4.py, keyed by shot_id.
  moves: push, pull, pan_l, pan_r, rise, sink, hold
  tags:  STRONG, DEBATED, ESTIMATE, HYPOTHESIS, INFERENCE

Run: python3 tools/storyboard_bats.py 01_PROJECTS/what_if_bats_disappeared
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import storyboard_vultures as base  # noqa: E402  (re-uses the writer; we replace its scene list)

TITLE = "What If All Bats Disappeared?"
VOICE = "am_michael"
RESPELL = {"Pseudogymnoascus destructans": "Soodo-jimno-askus de-struck-tunz",
           "Eyal": "Eye-al", "Bracken": "Brakken", "Kitaka": "Kee-tah-kah"}

S = []


def sc(section, narration, visual, claims=()):
    S.append(dict(section=section, narration=narration, visual=visual, claims=list(claims)))


plate, card = base.plate, base.card

# ---------------------------------------------------------------- COLD OPEN
A = "Cold open"
sc(A, "February, 2006. A cave west of Albany, New York. A caver's light falls on a cluster of sleeping bats, and something is wrong.",
   plate("HIB_ENTER", "push", tab="FEBRUARY 2006 · Cave near Albany, New York"), ["C01"])
sc(A, "Their noses are dusted with white, as if they'd been dipped in powdered sugar. At first, nobody knew what it was.",
   plate("HIB_FUNGUS_CU", "push"), ["C01"])
sc(A, "Within a few winters, caves that had held thousands of bats were almost silent.",
   plate("HIB_EMPTY", "pull", tab="A FEW WINTERS LATER"))
sc(A, "The white fuzz was a fungus. Since then, it has killed millions of bats across North America.",
   card("bignum", value="MILLIONS", label="bats killed by white-nose syndrome since 2006", tag="STRONG",
        icons="bats_fade"), ["C04"])
sc(A, "Which means we don't have to imagine a world without bats. In parts of America, it has already started. And people paid a price nobody expected.",
   plate("FARM_DUSK_WIDE", "push"))
sc(A, "So what really happens when the bats disappear?",
   plate("EMERGE_TITLE", "rise", text=dict(style="title", main="WHAT IF ALL BATS", sub="DISAPPEARED?")))
sc(A, "Welcome to The Disappearance Files, where we find out what the world loses when an animal nobody likes is suddenly gone.",
   plate("EMERGE_PIP_WAVE", "push"))

# ---------------------------------------------------------------- 1 NIGHT SHIFT
A = "The night shift"
sc(A, "First, meet the night shift.",
   plate("EMERGE_SUNSET", "push", text=dict(style="chapter", main="THE NIGHT SHIFT", sub="Chapter 1")))
sc(A, "There are more than fourteen hundred species of bats. That's roughly one in every five kinds of mammal on Earth.",
   card("fraction", value="1 in 5", label="mammal species is a bat · 1,400+ species", tag="STRONG", icon="bat"),
   ["C07"])
sc(A, "They're also the only mammals that can truly fly. Look closely at a wing, and you'll see why. It's a hand.",
   plate("STUDIO_WING", "push"), ["C08"])
sc(A, "Long finger bones, with a thin, living skin stretched between them. A bat flies by moving its fingers.",
   plate("STUDIO_XRAY", "hold", xray=True), ["C08"])
sc(A, "Most bats hunt insects in the dark, using echolocation. They call out, and listen for the echo.",
   plate("FARM_SONAR", "pan_r", fx=["sonar"]))
sc(A, "Others eat fruit, or drink nectar. Out of all those species, only three drink blood.",
   card("diets", tag="STRONG"), ["C29"])
sc(A, "To see what we'd lose, follow three jobs that bats do every night: pest control, pollination, and planting forests.",
   card("jobs"))

# ---------------------------------------------------------------- 2 WHITE NOSE
A = "The white nose"
sc(A, "So what happened in that cave?",
   plate("HIB_CHAPTER", "push", text=dict(style="chapter", main="THE WHITE NOSE", sub="Chapter 2")))
sc(A, "Bats in the northern United States survive winter by hibernating. They hang in cold caves for months, living on the fat they built up in autumn.",
   plate("HIB_CLUSTER", "pan_l"))
sc(A, "A hibernating bat's heart can slow from a few hundred beats a minute to about ten, and its body cools to nearly the temperature of the cave.",
   plate("HIB_HEART", "push", meter="HEART RATE", tag="STRONG"), ["C33"])
sc(A, "The fungus, called Pseudogymnoascus destructans, loves the cold. It grows on their noses, ears and wings while they sleep.",
   plate("HIB_FUNGUS_CU2", "push", label="Pseudogymnoascus destructans"), ["C02"])
sc(A, "Infected bats keep waking up. Every time they do, they burn fat they can't replace.",
   plate("HIB_WAKE", "hold", meter="FAT RESERVES", tag="STRONG"), ["C03"])
sc(A, "By late winter, many have nothing left.",
   plate("HIB_SNOW_EXIT", "push"))
sc(A, "Little brown bats, northern long-eared bats and tricolored bats fell by more than ninety percent, in under ten years.",
   card("decline3", tag="STRONG"), ["C05"])
sc(A, "And the fungus kept spreading, county by county, state by state. It's now been confirmed in more than forty US states, and parts of Canada.",
   card("spread", tag="STRONG"), ["C06"])

# ---------------------------------------------------------------- 3 EXPERIMENT
A = "The experiment nobody wanted"
sc(A, "That slow, steady spread created something scientists almost never get: a natural experiment.",
   plate("FARM_DAY_CHAPTER", "push", text=dict(style="chapter", main="THE EXPERIMENT NOBODY WANTED",
                                                   sub="Chapter 3")), ["C09"])
sc(A, "Economist Eyal Frank compared farming counties the fungus had reached with similar counties it hadn't reached yet.",
   card("paper", title="The economic impacts of ecosystem disruptions: Costs from substituting biological pest control",
        who="E. Frank · Science · 2024", tag="STRONG", split=True), ["C09"])
sc(A, "Without bats eating their pests, farmers had to fight insects another way.",
   plate("FARM_MOTHS", "push", fx=["moths"]))
sc(A, "In the counties that lost their bats, insecticide use went up by thirty-one percent.",
   plate("FARM_SPRAY", "pan_r", text=dict(style="callout", main="+31%", sub="insecticide use"), tag="STRONG"),
   ["C10"])
sc(A, "Then he looked at something far more serious: babies.",
   card("quiet", main="Infant health"))
sc(A, "In those same counties, infant deaths from internal causes, like illness, rose by about eight percent.",
   card("compare", left=["Before the fungus", 100], right=["After bats declined", 107.9], unit="infant deaths (index)",
        tag="STRONG"), ["C11"])
sc(A, "His estimate: about thirteen hundred extra infant deaths, in two hundred and forty-five counties, between 2006 and 2017.",
   card("bignum", value="≈1,334", label="additional infant deaths · 245 counties · 2006–2017", tag="ESTIMATE",
        icons="none"), ["C12"])
sc(A, "It's one study, and it's a statistical estimate, not a list of names. But it was published in the journal Science, and the pattern follows the fungus, county by county.",
   card("paper", title="Natural experiment: the fungus arrived in different counties in different years",
        who="Infant deaths rose after bats declined, not before", tag="ESTIMATE"), ["C12"])
sc(A, "Farmers paid too. Lost crops and extra pesticide added up to an estimated twenty-seven billion dollars.",
   plate("FARM_DAY_CORN", "pull", text=dict(style="callout", main="≈$26.9 billion", sub="farm losses · 2006–2017"),
         tag="ESTIMATE"), ["C13"])

# ---------------------------------------------------------------- 4 BUG HUNTERS
A = "The bug hunters"
sc(A, "So how much work were those bats really doing?",
   plate("EMERGE_CHAPTER", "push", text=dict(style="chapter", main="THE BUG HUNTERS", sub="Chapter 4")))
sc(A, "Come to Texas, just before sunset. Bracken Cave holds somewhere between fifteen and twenty million Mexican free-tailed bats. It's the biggest bat colony known on Earth.",
   plate("EMERGE_WIDE", "pull", tab="BRACKEN CAVE · Texas", swarm="emerge"), ["C15"])
sc(A, "On summer evenings, they pour out in a living river that can take hours to drain.",
   plate("EMERGE_PIP", "push", swarm="column"), ["C15"])
sc(A, "And they're hungry. A nursing mother can eat insects weighing more than half her own body weight, in a single night.",
   plate("EMERGE_HUNGRY", "push", swarm="column", text=dict(style="callout", main="39–73%", sub="of body weight in insects per night · nursing mothers"), tag="STRONG"), ["C34"])
sc(A, "They climb hundreds of metres into the sky to hunt moths migrating on the wind. Many of those moths are corn earworms, one of America's worst crop pests.",
   plate("SKY_HUNT", "rise", swarm="high", fx=["moths"]), ["C16"])
sc(A, "In eight Texas counties, scientists valued the bats' pest control for cotton farmers at about seven hundred and forty thousand dollars a year.",
   plate("COTTON_DUSK", "pan_l", text=dict(style="callout", main="≈$741,000 / year", sub="cotton · 8 Texas counties"),
         tag="ESTIMATE"), ["C17"])
sc(A, "In Illinois, researchers tried something simple. At night, they covered patches of corn with nets, so bats couldn't get in.",
   plate("CORN_NET", "push"), ["C18"])
sc(A, "Under the nets, there were nearly sixty percent more earworms, and fifty-six percent more damaged kernels.",
   card("corn_compare", tag="STRONG"), ["C18"])
sc(A, "Across North America, one estimate puts bats' pest control at more than three point seven billion dollars a year, and possibly over twenty billion.",
   card("range", lo=3.7, mid=22.9, hi=53, unit="billion $ / year", label="Value of bats to North American farms",
        tag="ESTIMATE"), ["C14"])
sc(A, "For corn alone, worldwide, it may be worth more than a billion dollars a year.",
   plate("CORN_NIGHT_BATS", "pan_r", text=dict(style="callout", main="> $1 billion / year", sub="corn, worldwide"),
         tag="ESTIMATE"), ["C19"])
sc(A, "And mosquitoes? Bats do eat them. But for most bats, mosquitoes are a side dish. The main course is moths and beetles.",
   card("menu", tag="DEBATED"), ["C20"])

# ---------------------------------------------------------------- 5 GARDENERS
A = "The night gardeners"
sc(A, "Pest control is only one of their jobs.",
   plate("AGAVE_CHAPTER", "push", text=dict(style="chapter", main="THE NIGHT GARDENERS", sub="Chapter 5")))
sc(A, "More than five hundred kinds of plants rely on bats to pollinate their flowers.",
   plate("AGAVE_WIDE", "pull", text=dict(style="callout", main="500+", sub="plant species pollinated by bats"),
         tag="STRONG"), ["C21"])
sc(A, "In the deserts of Mexico, the lesser long-nosed bat pushes its face into agave flowers to drink nectar, and comes out dusted with pollen.",
   plate("AGAVE_BAT_CU", "push"), ["C22"])
sc(A, "Agave is the plant tequila comes from. Tequila farms grow agave from clones, so they don't actually need bats to make tequila.",
   plate("AGAVE_FARM", "pan_r"), ["C22"])
sc(A, "But clones have almost no genetic variety. Bat pollination keeps wild agave diverse, and better able to survive new diseases. Some growers now let part of their crop flower, just for the bats.",
   plate("AGAVE_BLUE_HOUR", "pull", tag="STRONG"), ["C22"])
sc(A, "The lesser long-nosed bat is also a comeback story. In 1988, fewer than a thousand were known, at just fourteen roosts. Thirty years later there were about two hundred thousand, and it became the first bat ever taken off the US endangered list because it had recovered.",
   plate("AGAVE_RECOVERY", "pull", swarm="agave", text=dict(style="callout", main="<1,000 → ≈200,000", sub="lesser long-nosed bats · 1988 → 2018"), tag="STRONG"), ["C35"])
sc(A, "In Southeast Asia, durian, the famously smelly king of fruits, is pollinated mainly by cave nectar bats. Farms farther from bat caves get less fruit.",
   plate("DURIAN_NIGHT", "push", tag="STRONG"), ["C23"])
sc(A, "And fruit bats plant forests. They eat fruit in one place, and drop the seeds somewhere else, often in open, cleared land.",
   plate("TROPIC_FIG", "pan_l"), ["C24"])
sc(A, "Many of those seeds are pioneer plants: the first trees that turn a bare clearing back into forest.",
   plate("CLEARING_GROW", "push", grow=True), ["C24"])

# ---------------------------------------------------------------- 6 DANGEROUS?
A = "Aren't bats dangerous?"
sc(A, "Of course, bats have a scary reputation. Some carry viruses that can make people sick.",
   plate("MOON_CHAPTER", "push", text=dict(style="chapter", main="AREN'T BATS DANGEROUS?", sub="Chapter 6")),
   ["C30"])
sc(A, "So why not just get rid of them? People have tried.",
   plate("MOON_SILHOUETTE", "hold"))
sc(A, "In Peru, vampire bats spread rabies to livestock, and colonies have been culled for years. A study of twenty colonies found culling didn't reduce rabies exposure. Where bats were culled now and then, exposure actually went up.",
   card("paper", title="Culling did not reduce rabies exposure in vampire bats",
        who="Streicker et al. · Proc. R. Soc. B · 2012 · 20 colonies, Peru", tag="STRONG"), ["C31", "C25"])
sc(A, "In Uganda, after miners caught Marburg virus in a gold mine, the bats there were wiped out. Years later, bats moved back in, and more of them carried the virus than before.",
   plate("MINE_RETURN", "push", tag="STRONG"), ["C26"])
sc(A, "Scientists suspect culling leaves behind more young bats that have never met the virus, so it can spread faster. For people, the safest bat is usually one that's left alone.",
   card("cull_cycle", tag="HYPOTHESIS"), ["C32"])

# ---------------------------------------------------------------- 7 WORLD WITHOUT BATS
A = "A world without bats"
sc(A, "So, what if all bats disappeared?",
   plate("FARM_DUSK_EMPTY", "push", text=dict(style="chapter", main="A WORLD WITHOUT BATS", sub="Chapter 7")))
sc(A, "Night skies would fill with crop pests, and farmers would fight them with more chemicals.",
   plate("FARM_SPRAY2", "pan_l", fx=["moths"]))
sc(A, "Wild agave and durian flowers would wait for pollinators that never come.",
   plate("AGAVE_NIGHT_EMPTY", "push"))
sc(A, "Cleared land in the tropics would take longer to grow back into forest.",
   plate("CLEARING_BARE", "pull"))
sc(A, "And as those American counties showed, some of that cost lands on people, even on babies.",
   plate("FARM_HOUSE_NIGHT", "push"), ["C11"])
sc(A, "But there is some good news. In parts of New York, some little brown bat colonies stopped crashing. They seem to be resisting the fungus. Recovery will be slow, though. A little brown bat usually raises just one pup a year.",
   plate("HIB_HOPE", "push", tag="DEBATED"), ["C27", "C36"])
sc(A, "Wind farms also kill bats: estimates for the United States run from hundreds of thousands to more than a million a year. But just pausing the turbines on low-wind nights, when bats fly most, can cut those deaths by about sixty percent.",
   plate("WIND_RIDGE", "pan_r", text=dict(style="callout", main="≈ −60%", sub="bat deaths with curtailment"),
         tag="ESTIMATE"), ["C37", "C28"])
sc(A, "Bat-friendly farms, protected caves and dark skies give the survivors room to come back.",
   plate("FARM_BATHOUSE", "push"))
sc(A, "Bats aren't spooky. They're the night shift that keeps our fields, our forests and our families safer while we sleep.",
   plate("EMERGE_MOON_PIP", "rise", swarm="moon"))
sc(A, "Thanks for watching The Disappearance Files.",
   plate("EMERGE_END", "pull", text=dict(style="end", main="THE DISAPPEARANCE FILES", sub="Episode 4 · Bats")))


if __name__ == "__main__":
    import json
    base.S[:] = S
    base.TITLE, base.VOICE = TITLE, VOICE
    proj = sys.argv[1]
    base.main(proj)
    p = os.path.join(proj, "06_Storyboard", "storyboard.json")
    d = json.load(open(p))
    d["respell"] = RESPELL
    json.dump(d, open(p, "w"), indent=1, ensure_ascii=False)
