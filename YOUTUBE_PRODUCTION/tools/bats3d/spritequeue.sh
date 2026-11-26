#!/bin/bash
cd "$(dirname "$0")/../.."
R="$1"
for P in freetail:dusk freetail:moon myotis:dusk myotis:moon nectar:dusk nectar:moon flyingfox:dawn flyingfox:dusk; do
  sp=${P%%:*}; pr=${P##*:}
  timeout 3600 blender -b --python tools/bats3d/render4.py -- "$R" sprites $sp $pr > "$R/../logs/sprite_${sp}_${pr}.log" 2>&1
  echo "sprites $sp $pr: $(ls $R/sprites/${sp}_${pr} 2>/dev/null | wc -l) files; $(grep -c Traceback $R/../logs/sprite_${sp}_${pr}.log) tracebacks"
done
echo SPRITES DONE
