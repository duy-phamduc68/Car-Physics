# ─────────────────────────────────────────────────────────────────────────────
# physics.py — CarModel and GraphBuffer
# ─────────────────────────────────────────────────────────────────────────────

import math
import collections

from constants import (
    M,
    C_RR,
    C_DRAG,
    C_BRAKING,
    MU,
    g,
    L,
    h,
    b,
    c,
)
from engine import EngineModel


class CarModel:
    """1-D longitudinal vehicle dynamics model."""

    def __init__(self):
        self.x = 0.0
        self.v = 0.0
        self.wheel_angle = 0.0
        self.engine = EngineModel()
        # Instance-level constants so options menu can vary them per scenario
        self.M            = M
        self.C_RR         = C_RR
        self.C_DRAG       = C_DRAG
        self.C_BRAKING    = C_BRAKING
        self.MU           = MU
        self.g            = g
        self.L            = L
        self.h            = h
        self.b            = b
        self.c            = c

        # Model 3 derived state (updated every step and available to renderer)
        self.W            = self.M * self.g
        self.dW           = 0.0
        self.Wf_static    = (self.c / self.L) * self.W
        self.Wr_static    = (self.b / self.L) * self.W
        self.Wf           = self.Wf_static
        self.Wr           = self.Wr_static

    def _update_load_state(self, a):
        self.W         = self.M * self.g
        self.dW        = (self.h / self.L) * self.M * a
        self.Wf_static = (self.c / self.L) * self.W
        self.Wr_static = (self.b / self.L) * self.W
        self.Wf        = self.Wf_static - self.dW
        self.Wr        = self.Wr_static + self.dW

    def reset(self):
        """Reset kinematic state only; constants are preserved."""
        self.x = 0.0
        self.v = 0.0
        self.wheel_angle = 0.0
        self.engine.reset()
        self._update_load_state(0.0)

    @property
    def gear(self):
        return self.engine.gear

    @gear.setter
    def gear(self, value):
        self.engine.gear = value

    @property
    def rpm(self):
        return self.engine.rpm

    @rpm.setter
    def rpm(self, value):
        self.engine.rpm = value

    @property
    def R_W(self):
        return self.engine.R_W

    @R_W.setter
    def R_W(self, value):
        self.engine.R_W = value

    @property
    def FINAL_DRIVE(self):
        return self.engine.FINAL_DRIVE

    @FINAL_DRIVE.setter
    def FINAL_DRIVE(self, value):
        self.engine.FINAL_DRIVE = value

    @property
    def ETA(self):
        return self.engine.ETA

    @ETA.setter
    def ETA(self, value):
        self.engine.ETA = value

    @property
    def GEAR_RATIOS(self):
        return self.engine.GEAR_RATIOS

    @GEAR_RATIOS.setter
    def GEAR_RATIOS(self, value):
        self.engine.GEAR_RATIOS = dict(value)

    @property
    def RPM_IDLE(self):
        return self.engine.RPM_IDLE

    @RPM_IDLE.setter
    def RPM_IDLE(self, value):
        self.engine.RPM_IDLE = value

    @property
    def RPM_REDLINE(self):
        return self.engine.RPM_REDLINE

    @RPM_REDLINE.setter
    def RPM_REDLINE(self, value):
        self.engine.RPM_REDLINE = value

    @property
    def TORQUE_CURVE(self):
        return self.engine.TORQUE_CURVE

    @TORQUE_CURVE.setter
    def TORQUE_CURVE(self, value):
        self.engine.TORQUE_CURVE = list(value)

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
        v_prev = self.v
        F_engine, _rpm, _gear = self.engine.update(v_prev, u, B, dt)

        F_rr     = self.C_RR  * v_prev
        F_drag   = self.C_DRAG * v_prev * abs(v_prev)

        # Analog brake always opposes current direction of motion.
        if abs(v_prev) > 1e-6:
            F_brake = self.C_BRAKING * B * math.copysign(1.0, v_prev)
        else:
            F_brake = 0

        F_net = F_engine - F_rr - F_drag - F_brake
        a     = F_net / self.M

        self.v = v_prev + dt * a

        # If braking causes a sign flip, settle exactly at rest.
        if B > 0 and v_prev * self.v < 0:
            self.v = 0.0

        # Low-speed numerical settle to avoid lingering tiny +/- velocities.
        if abs(self.v) < 0.03 and abs(u) < 0.03:
            self.v = 0.0
        if abs(self.v) < 0.15 and B > 0.05 and abs(u) < 0.08:
            self.v = 0.0

        omega_wheel = self.v / max(self.engine.R_W, 1e-6)
        self.wheel_angle += omega_wheel * dt
        self.wheel_angle %= (2.0 * math.pi)
            
        self.x = self.x + dt * self.v

        self._update_load_state(a)

        return a, F_engine, F_rr, F_drag, F_brake, self.Wf, self.Wr, self.dW


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
