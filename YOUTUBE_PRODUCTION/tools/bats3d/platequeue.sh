#!/bin/bash
# Plate render queue worker: bash platequeue.sh <renders4_root> <worker_id>
cd "$(dirname "$0")/../.."
R="$1"; W="$2"
IDS=$(python3 -c "
import sys; sys.path.insert(0,'tools/bats3d')
import importlib.util
src=open('tools/bats3d/shots4.py').read().replace('from mathutils import Vector','Vector=tuple')
ns={}; exec(src, ns)
order=['HIB_ENTER','EMERGE_TITLE','FARM_DUSK_WIDE','AGAVE_WIDE','TROPIC_FIG','SKY_HUNT','MINE_RETURN','WIND_RIDGE','DURIAN_NIGHT','CORN_NET','AGAVE_BAT_CU','HIB_FUNGUS_CU']
ids=[k for k,v in ns['SHOTS'].items() if not v['full']]
print(' '.join(order+[i for i in ids if i not in order]))
")
for S in $IDS; do
  mkdir "$R/claims/plate_$S" 2>/dev/null || continue
  timeout 2400 blender -b --python tools/bats3d/render4.py -- "$R" plate "$S" > "$R/../logs/plate_$S.log" 2>&1
  grep -E "PLATE|Error|Traceback" "$R/../logs/plate_$S.log" | grep -v "Not freed" | head -3 | sed "s/^/[w$W] /"
done
echo "[w$W] DONE"
