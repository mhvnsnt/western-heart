"""
SCRIPT I/O contract as code.

Implements the exact shapes published in SCRIPT (arXiv:2605.22894, Sec 3-4)
so the real weights plug in without changing the game side:

  text instruction c  -> CLIP text encoder -> (c_pool, c_txt tokens)
  state  s_t in R^358 : root height + per-joint local position,
                       6D rotation, linear velocity, angular velocity
  action a_t in R^69  : target joint angles for a PD controller
  policy             : (H_t history, c_pool, c_txt) -> H-step future
                       state-action chunk [a_{t+1:t+H}; s_{t+1:t+H}]
  execution          : receding horizon (execute first action, re-plan)

No torch dependency: this module validates shapes/ranges with numpy only.
The inference service (GPU) is specified in README.md and client.py.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np

# Published SCRIPT dimensions (paper Sec 3.1, 4.1)
STATE_DIM = 358
ACTION_DIM = 69
CLIP_TEXT_DIM = 512  # CLIP ViT-B/32 text width used by SCRIPT
DEFAULT_HORIZON = 16  # H: predicted future steps per chunk
DEFAULT_FPS = 30  # training rollout frame rate (resampled to 60fps for WH)


class ContractError(ValueError):
    """Raised when data does not satisfy the SCRIPT I/O contract."""


@dataclass
class ScriptState:
    """One proprioceptive state vector s_t in R^358."""

    vector: np.ndarray

    def validate(self) -> "ScriptState":
        v = np.asarray(self.vector, dtype=np.float64)
        if v.shape != (STATE_DIM,):
            raise ContractError(
                f"ScriptState must be ({STATE_DIM},), got {v.shape}"
            )
        if not np.all(np.isfinite(v)):
            raise ContractError("ScriptState contains NaN/inf")
        # root height is element 0 by convention (paper Sec 3.1); sanity range
        if not (-0.5 <= v[0] <= 3.0):
            raise ContractError(f"root height {v[0]:.3f} outside sane range")
        self.vector = v
        return self


@dataclass
class ScriptAction:
    """One action vector a_t in R^69: PD-controller target joint angles (radians)."""

    vector: np.ndarray

    def validate(self) -> "ScriptAction":
        v = np.asarray(self.vector, dtype=np.float64)
        if v.shape != (ACTION_DIM,):
            raise ContractError(
                f"ScriptAction must be ({ACTION_DIM},), got {v.shape}"
            )
        if not np.all(np.isfinite(v)):
            raise ContractError("ScriptAction contains NaN/inf")
        if np.any(np.abs(v) > np.pi * 2):
            raise ContractError("ScriptAction joint angle outside [-2pi, 2pi]")
        self.vector = v
        return self


@dataclass
class TextConditioning:
    """CLIP text conditioning: pooled embedding + penultimate-layer tokens."""

    c_pool: np.ndarray  # (CLIP_TEXT_DIM,)
    c_txt: np.ndarray  # (n_tokens, CLIP_TEXT_DIM)

    def validate(self) -> "TextConditioning":
        pool = np.asarray(self.c_pool, dtype=np.float64)
        txt = np.asarray(self.c_txt, dtype=np.float64)
        if pool.shape != (CLIP_TEXT_DIM,):
            raise ContractError(f"c_pool must be ({CLIP_TEXT_DIM},), got {pool.shape}")
        if txt.ndim != 2 or txt.shape[1] != CLIP_TEXT_DIM or txt.shape[0] < 1:
            raise ContractError(f"c_txt must be (n_tokens, {CLIP_TEXT_DIM}), got {txt.shape}")
        if not (np.all(np.isfinite(pool)) and np.all(np.isfinite(txt))):
            raise ContractError("TextConditioning contains NaN/inf")
        self.c_pool, self.c_txt = pool, txt
        return self


@dataclass
class ScriptRequest:
    """One generation request: prompt + conditioning + constraints."""

    prompt: str
    conditioning: TextConditioning
    history: List[ScriptState]  # H_t: nonlinearly-sampled state history
    horizon: int = DEFAULT_HORIZON
    seed: int = 0
    model: str = "script-base"  # script-base | script-large | script-huge
    constraints: Dict[str, object] = field(default_factory=dict)

    def validate(self) -> "ScriptRequest":
        if not self.prompt or not self.prompt.strip():
            raise ContractError("prompt must be non-empty")
        self.conditioning.validate()
        if not self.history:
            raise ContractError("history H_t must be non-empty")
        for s in self.history:
            s.validate()
        if self.horizon < 1 or self.horizon > 128:
            raise ContractError(f"horizon {self.horizon} outside [1, 128]")
        if self.model not in ("script-base", "script-large", "script-huge"):
            raise ContractError(f"unknown model {self.model!r}")
        return self


@dataclass
class ScriptTrajectory:
    """One generated chunk: H future states + H future actions."""

    states: np.ndarray  # (H, 358)
    actions: np.ndarray  # (H, 69)
    fps: int = DEFAULT_FPS
    prompt: str = ""
    seed: int = 0
    model: str = "script-base"
    metrics: Dict[str, float] = field(default_factory=dict)

    def validate(self) -> "ScriptTrajectory":
        st = np.asarray(self.states, dtype=np.float64)
        ac = np.asarray(self.actions, dtype=np.float64)
        if st.ndim != 2 or st.shape[1] != STATE_DIM:
            raise ContractError(f"states must be (H, {STATE_DIM}), got {st.shape}")
        if ac.ndim != 2 or ac.shape[1] != ACTION_DIM:
            raise ContractError(f"actions must be (H, {ACTION_DIM}), got {ac.shape}")
        if st.shape[0] != ac.shape[0] or st.shape[0] < 1:
            raise ContractError("states/actions horizon mismatch or empty")
        for row in st:
            ScriptState(row).validate()
        for row in ac:
            ScriptAction(row).validate()
        self.states, self.actions = st, ac
        return self

    @property
    def horizon(self) -> int:
        return int(self.states.shape[0])

    @property
    def duration_s(self) -> float:
        return self.horizon / float(self.fps)


def make_synthetic_trajectory(
    horizon: int = 16,
    seed: int = 0,
    prompt: str = "synthetic test motion",
) -> ScriptTrajectory:
    """Deterministic synthetic trajectory for plumbing tests.

    This is NOT model output — it is seeded sine-based joint motion used to
    prove the contract -> client -> retarget -> keyframes path. The real
    trajectories arrive with the SCRIPT weights.
    """
    rng = np.random.default_rng(seed)
    t = np.arange(horizon)[:, None]
    states = np.zeros((horizon, STATE_DIM))
    states[:, 0] = 0.95 + 0.02 * np.sin(2 * np.pi * t[:, 0] / horizon)  # root height
    states[:, 1:] = 0.05 * np.sin(2 * np.pi * t / horizon + rng.random(STATE_DIM - 1))
    actions = 0.3 * np.sin(2 * np.pi * t / horizon + rng.random(ACTION_DIM))
    traj = ScriptTrajectory(
        states=states,
        actions=actions,
        prompt=prompt,
        seed=seed,
        metrics={"synthetic": 1.0},
    )
    return traj.validate()
