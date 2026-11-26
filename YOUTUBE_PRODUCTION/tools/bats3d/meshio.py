"""Load SDF-modelled meshes (written by sdf.py) into Blender, with tint attributes and skin weights."""
import os
import struct
from array import array

import bpy

from core import fix_texspace, link, smooth


def read(path):
    with open(path, "rb") as fh:
        nv, nf, na = struct.unpack("<iii", fh.read(12))
        V = array("f")
        V.frombytes(fh.read(nv * 12))
        F = array("i")
        F.frombytes(fh.read(nf * 16))
        A = array("f")
        A.frombytes(fh.read(nv * na * 4))
    return nv, nf, na, V, F, A


def load(path, name, mat=None, tint=0, offset=None, bone_names=None):
    nv, nf, na, V, F, A = read(path)
    me = bpy.data.meshes.new(name)
    if offset is not None:
        ox, oy, oz = offset
        for i in range(0, len(V), 3):
            V[i] += ox
            V[i + 1] += oy
            V[i + 2] += oz
    me.vertices.add(nv)
    me.vertices.foreach_set("co", V)
    me.loops.add(nf * 4)
    me.loops.foreach_set("vertex_index", F)
    me.polygons.add(nf)
    me.polygons.foreach_set("loop_start", array("i", range(0, nf * 4, 4)))
    me.update(calc_edges=True)
    me.validate(clean_customdata=False)
    ob = link(bpy.data.objects.new(name, me))
    if mat:
        me.materials.append(mat)
    smooth(ob)
    fix_texspace(ob)
    if tint:
        ca = me.color_attributes.new("tint", "FLOAT_COLOR", "POINT")
        col = array("f", [1.0]) * (nv * 4)
        for i in range(nv):
            for c in range(min(3, tint)):
                col[4 * i + c] = A[i * na + c]
        ca.data.foreach_set("color", col)
    if bone_names is not None and na - tint >= 6:
        k = (na - tint) // 2
        groups = {}
        buckets = {}
        for i in range(nv):
            base = i * na + tint
            for j in range(k):
                w = A[base + k + j]
                if w <= 1e-3:
                    continue
                bid = int(A[base + j])
                key = (bid, round(w, 3))
                buckets.setdefault(key, []).append(i)
        for (bid, w), idx in buckets.items():
            bn = bone_names[bid]
            vg = groups.get(bn) or ob.vertex_groups.get(bn) or ob.vertex_groups.new(name=bn)
            groups[bn] = vg
            vg.add(idx, w, "REPLACE")
    return ob
