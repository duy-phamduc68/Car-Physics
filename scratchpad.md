You previously upgraded the simulator to Model 3 (gears + RPM + torque curve), but there are **two critical issues**:

1. **Gear shifting does not work**
2. **RPM grows unrealistically (tens of thousands), ignoring redline behavior**

Your task is to **fix these issues only**, while preserving the existing architecture.

---

## 1. Fix Control Mapping (STRICT REQUIREMENT)

### Keyboard (must match this exactly):

* `W` → Throttle (analog ramp, already exists)
* `Space` → Brake (upgrade to analog)
* `A` → Shift DOWN
* `D` → Shift UP

### Xbox Controller:

* `RT` → Throttle (analog)
* `LT` → Brake (analog)
* `X` → Shift DOWN
* `B` → Shift UP

### Implementation details:

* Handle keyboard gear shifting in `Simulator._handle_events()` using `KEYDOWN`
* Handle controller gear shifting using **edge detection** (single press = one shift)
* Do NOT use UP/DOWN arrows or LB/RB anymore

### Gear constraints:

```python
GEAR_MIN = -1   # Reverse
GEAR_MAX = 5
```

```python
self.car.gear = max(GEAR_MIN, min(GEAR_MAX, self.car.gear))
```

---

## 2. Fix RPM and Drivetrain Logic (CORE BUG)

Right now RPM is exploding → this means the drivetrain pipeline is incorrect or incomplete.

### You MUST enforce this pipeline inside `CarModel.update()`:

### Step 1: Compute wheel angular speed

```python
omega_wheel = self.v / R_W   # rad/s
```

### Step 2: Convert to engine RPM

```python
gear_ratio = GEAR_RATIOS[self.gear]

if self.gear == 0:  # Neutral
    rpm = RPM_IDLE
else:
    rpm = omega_wheel * gear_ratio * FINAL_DRIVE * 60 / (2 * math.pi)
    rpm = max(rpm, RPM_IDLE)

self.rpm = rpm
```

---

## 3. Enforce Redline (CRITICAL)

RPM should NOT be artificially clamped for display.

Instead:

### Redline behavior:

* If RPM exceeds `RPM_REDLINE` → engine produces **ZERO torque**

```python
if rpm >= RPM_REDLINE:
    T_engine = 0.0
else:
    T_engine = u * get_max_torque(rpm)
```

---

## 4. Compute Engine Force Properly

```python
T_wheel = T_engine * gear_ratio * FINAL_DRIVE * ETA
F_engine = T_wheel / R_W
```

---

## 5. Direction Safety (IMPORTANT)

Prevent invalid force directions:

```python
if self.gear > 0 and self.v < 0:
    F_engine = 0.0

if self.gear < 0 and self.v > 0:
    F_engine = 0.0
```

---

## 6. DO NOT MODIFY

* GraphBuffer structure
* Rendering layout (except using existing `car.gear` and `car.rpm`)
* Main loop / timestep logic
* Load transfer model

---

## 7. Output Requirements

After implementing, provide:

1. Exact code diff for:

   * `physics.py`
   * `simulator.py`
   * `controls.py` (only if needed)

2. Short verification checklist:

   * Can shift gears with A/D and X/B
   * RPM stays within realistic range (~800–6000)
   * RPM hits redline → acceleration stops
   * Higher gears reduce acceleration but increase top speed

---

Do NOT introduce new systems.
Do NOT refactor unrelated code.
Focus only on making Model 3 physically correct and controllable.