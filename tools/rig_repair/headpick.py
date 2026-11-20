"""Canonical head-joint identification, shared by the head-bleed tools
(head_bleed_measure / head_debleed / head_distortion).

Mirrors the game's own canonBoneName strips (game/js/t3anims.js): the
namespace prefix (mixamorig:) and the Sketchfab index suffix (_010) are
stripped before comparing to the canonical name 'Head'. When several
joints canonicalize to Head — Rigify exports carry control + deform
heads side by side — the winner is the one whose subtree actually
carries the skin weights, scored by total head-chain weight over the
skin's primitives. No per-model constants anywhere.
"""
import re
import numpy as np


def canon_bone(name):
    n = re.sub(r'^mixamorig[:_]?', '', str(name), flags=re.I)
    while re.search(r'_\d+$', n):
        n = re.sub(r'_\d+$', '', n)
    m = re.match(r'^Bip0*1[ _](.*)$', n)   # Biped family (game canon has
    if m:                                  # the underscore spelling; the
        n = m.group(1)                     # space spelling is the same rig)
    return n


def head_candidates(jname):
    exact = [ji for ji, nm in jname.items() if canon_bone(nm) == 'Head']
    if exact:
        return exact
    return [ji for ji, nm in jname.items() if canon_bone(nm).lower() == 'head']


def chain_of(head_node, descendants, node2joint):
    return {node2joint[n] for n in
            ({head_node} | set(descendants(head_node))) if n in node2joint}


def pick_head(jname, joint_nodes, descendants, node2joint, prim_JW):
    """prim_JW: iterable of (J, W) arrays covering the skin's primitives.
    Returns (head_joint_index, chain_set) or (None, None)."""
    cands = head_candidates(jname)
    if not cands:
        return None, None
    prim_JW = list(prim_JW)
    best, best_score = None, -1.0
    for hj in cands:
        chain = chain_of(joint_nodes[hj], descendants, node2joint)
        if not chain:
            continue
        if len(cands) == 1:
            return hj, chain
        score = 0.0
        cl = list(chain)
        for J, W in prim_JW:
            score += float(np.where(np.isin(J, cl), W, 0.0).sum())
        if score > best_score:
            best, best_score = hj, score
    if best is None:
        return None, None
    return best, chain_of(joint_nodes[best], descendants, node2joint)
