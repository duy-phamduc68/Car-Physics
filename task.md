Implement Model 3 in the existing simulator codebase.

Goal:
Upgrade the car model from a constant-force engine to a torque-curve + gearing drivetrain model, while preserving the current simulator structure, fixed-timestep loop, load transfer visualization, and overall rendering layout.

Do not rewrite the whole project.
Do not change the simulation architecture unless necessary.
Prefer small, local edits with clear separation between physics, controls, and rendering.

Target files:
- constants.py
- physics.py
- controls.py
- simulator.py
- renderer.py

--------------------------------------------------
MODEL 3 PHYSICS REQUIREMENTS
--------------------------------------------------

Replace the current engine force model:

    F_engine = u * F_ENGINE_MAX

with a drivetrain pipeline based on:

- throttle input u in [0, 1]
- vehicle speed v
- current gear
- gear ratio
- final drive ratio
- drivetrain efficiency
- wheel radius
- torque curve lookup by RPM

Use this model:

1) wheel angular speed from vehicle speed
    omega_wheel = v / R_w

2) engine RPM from wheel speed and gearing
    rpm = omega_wheel * gear_ratio * final_drive * 60 / (2*pi)

3) clamp idle RPM where appropriate
    rpm = max(rpm, RPM_IDLE)

4) lookup max engine torque from a torque curve table
    T_engine_max = get_max_torque(rpm)

5) apply throttle
    T_engine = u * T_engine_max

6) convert to wheel torque
    T_wheel = T_engine * gear_ratio * final_drive * eta

7) convert to drive force
    F_engine = T_wheel / R_w

Keep the rest of the longitudinal physics the same:
- rolling resistance
- drag
- braking
- forward Euler integration
- load transfer calculations

Add persistent state to CarModel:
- self.gear
- self.rpm

Update reset() so those fields return to their default values.

--------------------------------------------------
GEAR AND ENGINE CONSTANTS
--------------------------------------------------

Move drivetrain-related configuration into constants.py.

Add:
- gear ratios for forward gears 1 through 5
- reverse gear ratio
- final drive ratio
- drivetrain efficiency
- wheel radius
- RPM_IDLE
- RPM_REDLINE
- torque curve lookup table

Keep these constants easy to inspect and use from the rest of the codebase.

Recommended data shape:
- gears as a list or dict
- torque curve as a list of (rpm, torque) points
- a helper function for interpolation if useful

--------------------------------------------------
CONTROLS REQUIREMENTS
--------------------------------------------------

Current input behavior already exists; extend it for Model 3.

Throttle and brake:
- keep throttle analog-feeling
- keep brake analog-feeling from Model 3 onward
- preserve keyboard + Xbox controller support

Gear shifting:
- add manual gear shift commands
- support at least gear up / gear down
- make sure gear changes affect CarModel.gear

Controller mappings:
- use the existing XInput path
- add bumper or button mappings for gear up/down
- keep trigger inputs for throttle and brake

Keyboard mappings:
- use a clear pair of keys for gear up/down
- preserve current throttle and brake keys

Reverse gear:
- add a dedicated reverse mode or reverse gear path
- keep it simple and safe
- reverse should only be usable at low speed or from rest

Do not add clutch simulation yet.

--------------------------------------------------
SIMULATOR / ORCHESTRATION REQUIREMENTS
--------------------------------------------------

Keep the fixed timestep loop intact.
Do not change the main update structure unless unavoidable.

Make sure the simulator passes the right inputs into CarModel.update():
- throttle
- brake
- gear commands or gear state updates

If needed, store gear input handling in the simulator layer, but keep the physics state in CarModel.

--------------------------------------------------
RENDERING / HUD REQUIREMENTS
--------------------------------------------------

Preserve the current car scene and load transfer visualization.

Add a dedicated dashboard region for Model 3 presentation.

The dashboard should include:
- gear indicator: R | 1 | 2 | 3 | 4 | 5
- RPM bar with clear tick marks from idle to redline
- analog throttle gauge
- analog brake gauge

The main force subplot should show:
- engine force
- current gear label in the legend or title
- clear indication when gear changes affect the curve

Add an envelope overlay for the force-vs-speed view:
- show the maximum available drive force across gears at each speed
- render it as a separate overlay curve, not as a GraphBuffer history series

Keep the existing load transfer info in Model 3.

--------------------------------------------------
GRAPH / TELEMETRY REQUIREMENTS
--------------------------------------------------

Preserve the existing 7-channel graph history for time-series values.

Do not force the envelope into GraphBuffer unless absolutely necessary.
Treat the envelope as a speed-domain overlay computed from:
- gear ratios
- final drive
- wheel radius
- torque curve
- rpm limits

If you need a new helper for this, add it cleanly.

--------------------------------------------------
IMPLEMENTATION STYLE
--------------------------------------------------

Prefer these principles:
- minimal disruption to current code
- clear function boundaries
- readable state names
- preserve the existing simulator feel
- no clutch yet
- no traction limits yet
- no wheel slip yet

--------------------------------------------------
OUTPUT EXPECTED
--------------------------------------------------

When finished, provide:
1. a concise summary of the files changed
2. the new Model 3 data flow
3. any assumptions made
4. any follow-up work still needed for UI polish or controls