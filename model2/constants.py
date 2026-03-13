# ─────────────────────────────────────────────────────────────────────────────
# constants.py — All named constants for the Car Physics Simulator
# ─────────────────────────────────────────────────────────────────────────────

# ── Physics defaults ──────────────────────────────────────────────────────────
M            = 1500    # kg
F_ENGINE_MAX = 3000    # N
C_RR         = 13.0    # kg/s  (rolling resistance coefficient)
C_DRAG       = 0.43    # kg/m  (aerodynamic drag coefficient)
C_BRAKING    = 12000   # N
g            = 9.81    # m/s^2
L            = 2.8     # m  wheelbase
h            = 0.5     # m  CG height above axle line
b            = 1.7     # m  CG -> front axle
c            = 1.1     # m  CG -> rear axle

PIXELS_PER_METER = 100   # 1 m = 100 px
MARKER_INTERVAL  = 25    # metres between road markers

# ── Colour palette ────────────────────────────────────────────────────────────
SKY_TOP        = (83, 60, 128)
SKY_BOTTOM     = (184, 93, 46)
ROAD_COLOR     = (80,  80,  80)
ROAD_LINE      = (200, 200, 200)
MARKER_COLOR   = (255, 255, 255)
CAR_BODY       = (230, 110,  20)
CAR_ROOF       = (200,  80,  10)
CAR_WINDOW     = (170, 210, 255)
CAR_WHEEL      = (30,   30,  30)
CAR_WHEEL_RIM  = (140, 140, 140)
CLOUD_COLOR    = (255, 255, 255)
GRAPH_BG       = (20,  20,  28)
GRAPH_GRID     = (50,  50,  60)
GRAPH_AXIS     = (120, 120, 130)
OVERLAY_BG     = (15,  15,  20, 210)
PANEL_BG       = (25,  28,  38, 240)
TEXT_BRIGHT    = (230, 235, 255)
TEXT_DIM       = (140, 145, 165)
ACCENT         = (80,  170, 255)
ACCENT2        = (255, 140,  50)
BTN_NORMAL     = (45,  50,  68)
BTN_HOVER      = (65,  72,  96)
BTN_ACTIVE     = (80, 170, 255)

GRAPH_COLORS = [
    (100, 220, 100),   # velocity      - green
    (255, 180,  60),   # acceleration  - orange
    ( 80, 180, 255),   # position      - blue
    (255, 100, 100),   # engine force  - red
    (180, 100, 255),   # drag force    - purple
    (255, 220,  80),   # rolling res   - yellow
    (255,  80, 140),   # braking force - pink
]

GRAPH_LABELS = [
    "Velocity (m/s)",
    "Accel (m/s²)",
    "Position (m)",
    "Engine Force (N)",
    "Drag Force (N)",
    "Rolling Res. (N)",
    "Braking Force (N)",
]

# ── Simulation option tables ──────────────────────────────────────────────────
TIMESTEP_OPTIONS = [
    (0.001,  "1 ms  - High Fidelity"),
    (0.01,   "10 ms - Good"),
    (0.016,  "16 ms - 60 Hz"),
    (0.1,    "100 ms - Low Precision"),
]

FPS_OPTIONS = [30, 60, 120, 144, 240]

THROTTLE_RAMP_DEFAULT = 1.0   # seconds to go 0→1

# ── Physics constants field table ─────────────────────────────────────────────
# Each entry: (display_name, CarModel_attr, unit_hint, default_value)
CONST_FIELDS = [
    ("M",            "M",            "kg",   M),
    ("F_ENGINE_MAX", "F_ENGINE_MAX", "N",    F_ENGINE_MAX),
    ("C_RR",         "C_RR",         "kg/s", C_RR),
    ("C_DRAG",       "C_DRAG",       "kg/m", C_DRAG),
    ("C_BRAKING",    "C_BRAKING",    "N",    C_BRAKING),
    ("g",            "g",            "m/s^2", g),
    ("L",            "L",            "m",     L),
    ("h",            "h",            "m",     h),
    ("b",            "b",            "m",     b),
    ("c",            "c",            "m",     c),
]


# ── Editable parameter limits ─────────────────────────────────────────────────
PARAM_LIMITS = {
    "g": (5.0, 15.0),
    "L": (2.0, 4.5),
    "h": (0.2, 1.2),
    "b": (0.5, 3.0),
    "c": (0.5, 3.0),
}
