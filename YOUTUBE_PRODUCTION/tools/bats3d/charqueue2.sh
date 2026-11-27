#!/bin/bash
# Character-pass / full-3D queue worker: bash charqueue.sh <project> <worker_id>
cd "$(dirname "$0")/../.."
P="$1"; W="$2"; R="$P/08_Scenes/renders4"
mkdir -p "$R/claims" "$P/08_Scenes/logs"
JOBS=$(python3 - "$P" <<'PY'
import json, sys
sys.path.insert(0, 'tools/bats3d')
from shots4 import SHOTS
P = sys.argv[1]
sb = json.load(open(P + '/06_Storyboard/storyboard.json'))['scenes']
tm = json.load(open(P + '/09_Animation/scene_timing.json'))
order = ['EMERGE_PIP_WAVE', 'HIB_ENTER', 'AGAVE_BAT_CU', 'HIB_FUNGUS_CU', 'EMERGE_PIP', 'CORN_NET', 'FARM_MOTHS',
         'STUDIO_WING', 'STUDIO_XRAY', 'HIB_WAKE', 'HIB_HEART', 'HIB_FUNGUS_CU2', 'DURIAN_NIGHT', 'AGAVE_FARM',
         'EMERGE_MOON_PIP', 'FARM_BATHOUSE', 'FARM_SPRAY', 'FARM_SPRAY2', 'WIND_RIDGE', 'CLEARING_GROW']
dur = {}
for s in sb:
    v = s['visual']
    if v['type'] == 'plate':
        dur[v['shot']] = tm[s['file']]['duration']
jobs = [k for k in order if k in dur and SHOTS[k]['actors']]
jobs += [k for k in dur if SHOTS[k]['actors'] and k not in jobs]
print(' '.join(f"{k}:{dur[k]:.2f}:{'full' if SHOTS[k]['full'] else 'chars'}" for k in jobs))
PY
)
for J in $JOBS; do
  S=${J%%:*}; rest=${J#*:}; D=${rest%%:*}; M=${rest##*:}
  mkdir "$R/claims/char_$S" 2>/dev/null || continue
  timeout 14400 blender -b --python tools/bats3d/render4.py -- "$R" $M "$S" "$D" > "$P/08_Scenes/logs/char_$S.log" 2>&1
  echo "[c$W] $S $M: $(grep -c FRAME $P/08_Scenes/logs/char_$S.log) frames, $(grep -c Traceback $P/08_Scenes/logs/char_$S.log) tracebacks"
  # an incomplete job (timeout / crash) releases its claim so a later worker resumes it (finished frames are kept)
  OUT="$R/$( [ "$M" = full ] && echo full || echo chars )/$S"
  NEED=$(python3 -c "import json;print(json.load(open(\"$OUT/meta.json\"))[\"frames\"])" 2>/dev/null || echo 0)
  HAVE=$(ls "$OUT" 2>/dev/null | grep -c "^char_")
  if [ "$HAVE" -lt "$NEED" ] || [ "$NEED" -eq 0 ]; then echo "[c$W] $S incomplete ($HAVE/$NEED): claim released"; rmdir "$R/claims/char_$S"; fi
done
echo "[c$W] DONE"
