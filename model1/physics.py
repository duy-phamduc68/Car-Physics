# ─────────────────────────────────────────────────────────────────────────────
# physics.py — CarModel and GraphBuffer
# ─────────────────────────────────────────────────────────────────────────────

import collections

from constants import M, F_ENGINE_MAX, C_RR, C_DRAG, C_BRAKING


class CarModel:
    """1-D longitudinal vehicle dynamics model."""

    def __init__(self):
        self.x = 0.0
        self.v = 0.0
        # Instance-level constants so options menu can vary them per scenario
        self.M            = M
        self.F_ENGINE_MAX = F_ENGINE_MAX
        self.C_RR         = C_RR
        self.C_DRAG       = C_DRAG
        self.C_BRAKING    = C_BRAKING

    def reset(self):
        """Reset kinematic state only; constants are preserved."""
        self.x = 0.0
        self.v = 0.0

    def update(self, dt, u, B):
        """
        Advance physics by dt seconds.

        Parameters
        ----------
        u : float  throttle in [0, 1]
        B : int    brake flag (0 or 1)

        Returns
        -------
        (a, F_engine, F_rr, F_drag, F_brake)
        """
        F_engine = u * self.F_ENGINE_MAX
        F_rr     = self.C_RR  * self.v
        F_drag   = self.C_DRAG * self.v * abs(self.v)
        F_brake  = self.C_BRAKING if (self.v > 0 and B == 1) else 0

        F_net = F_engine - F_rr - F_drag - F_brake
        a     = F_net / self.M

        self.v = self.v + dt * a
        if self.v < 0:
            self.v = 0.0
        self.x = self.x + dt * self.v

        return a, F_engine, F_rr, F_drag, F_brake


class GraphBuffer:
    """Circular buffer holding the last WINDOW seconds of telemetry per channel."""

    CHANNELS = 7
    WINDOW   = 30.0   # seconds

    def __init__(self, dt):
        self._dt      = dt
        self._max_pts = max(1, int(self.WINDOW / dt) + 10)
        self._bufs    = [collections.deque(maxlen=self._max_pts)
                         for _ in range(self.CHANNELS)]
        self._times   = collections.deque(maxlen=self._max_pts)

    def reset(self, new_dt=None):
        if new_dt is not None:
            self._dt      = new_dt
            self._max_pts = max(1, int(self.WINDOW / new_dt) + 10)
            self._bufs    = [collections.deque(maxlen=self._max_pts)
                             for _ in range(self.CHANNELS)]
            self._times   = collections.deque(maxlen=self._max_pts)
        else:
            for b in self._bufs:
                b.clear()
            self._times.clear()

    def push(self, t, values):
        """Push one sample; values = [v, a, x, F_eng, F_drag, F_rr, F_brake]."""
        self._times.append(t)
        for i, val in enumerate(values[:self.CHANNELS]):
            self._bufs[i].append(val)

    def get(self, channel):
        return list(self._bufs[channel])

    def get_times(self):
        return list(self._times)
