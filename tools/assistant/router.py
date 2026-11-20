#!/usr/bin/env python3
"""
router.py — tier router for the Western Heart assistant tool suite.

Picks the right tier for a task: tries Tier 2 (free) first, escalates to
Tier 1 (token-based) when quality demands it.

Usage:
    from router import route, Tier

    # Get the recommended tier for a tool
    tier = route("image-edit-generative", quality="high")
    # -> Tier.TIER1

    tier = route("image-edit-generative", quality="standard")
    # -> Tier.TIER2

    # Check what each tier offers for a tool
    info = describe("image-edit-generative")
"""
import json
import os

REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "tiers.json")


class Tier:
    TIER1 = "tier1"  # Token-based (assistant's own budget)
    TIER2 = "tier2"  # Free (no tokens, no cost)


def _load_registry():
    with open(REGISTRY_PATH) as f:
        return json.load(f)


def describe(tool_name):
    """Return the full registry entry for a tool."""
    reg = _load_registry()
    for tool in reg["tools"]:
        if tool["name"] == tool_name:
            return tool
    raise ValueError(f"unknown tool: {tool_name}")


def list_tools():
    """Return all registered tool names."""
    reg = _load_registry()
    return [t["name"] for t in reg["tools"]]


def route(tool_name, quality="standard", force_tier=None):
    """Pick a tier for a tool.

    Args:
        tool_name: registered tool name (see list_tools())
        quality: "standard" (default, try free first) or "high"
                 (go straight to token-based)
        force_tier: override with Tier.TIER1 or Tier.TIER2

    Returns:
        Tier.TIER1 or Tier.TIER2
    """
    if force_tier:
        if force_tier not in (Tier.TIER1, Tier.TIER2):
            raise ValueError(f"bad tier: {force_tier}")
        return force_tier

    tool = describe(tool_name)

    # No Tier 1 option — always free
    if not tool.get("tier1"):
        return Tier.TIER2
    # No Tier 2 option — always token-based
    if not tool.get("tier2"):
        return Tier.TIER1

    if quality == "high":
        return Tier.TIER1
    return Tier.TIER2


def tier_info(tier):
    """Return description and cost info for a tier."""
    reg = _load_registry()
    t = reg["tiers"].get(tier)
    if not t:
        raise ValueError(f"unknown tier: {tier}")
    return t


def routing_policy():
    """Return the routing policy text."""
    reg = _load_registry()
    return reg.get("routing_policy", "")
