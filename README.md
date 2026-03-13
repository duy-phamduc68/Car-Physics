# Car Physics

Main reference: [Macro Monster's Car Physics Guide](https://www.asawicki.info/Mirror/Car%20Physics%20for%20Games/Car%20Physics%20for%20Games.html).

Check out the learning journey on my blog: [yuk068.github.io](https://yuk068.github.io/).

I try to break down each model both mathematically (continuous math) and implement them in code.

## Roadmap

```
- [x] Model 1: Longitudinal Point Mass (1D)
    - Straight Line Physics
    - Magic Constants
    - Braking
- [x] Model 2: Load Transfer Without Traction Limits (1D)
    - Weight Transfer
- [ ] Model 3: Engine Torque + Gearing without Slip (1D)
    - Engine Force
    - Gear Ratios
    - Drive Wheel Acceleration (simplified)
- [ ] Model 4: Wheel Rotational Dynamics (1D)
    - Drive Wheel Acceleration (full)
- [ ] Model 5: Slip Ratio + Traction Curve (1D)
    - Slip Ratio & Traction Force
- [ ] Model 6: Low-Speed Kinematic Turning (2D)
    - Curves (low speed)
- [ ] Model 7: High-Speed Lateral Tire Model (2D)
    - High Speed Turning
- [ ] Model 8: Full Coupled Tire Model (2D)
```

## Showcase

### Model 1: Longitudinal Point Mass (1D)

[Technical Analysis](https://yuk068.github.io/2026/03/03/car-physics-model1).

![model1-thumbnail](media/model1-thumbnail.webp)

**Controls**

- **Space** – analog throttle (ramps 0 → 1 over 1s, adjustable)
- **F** – binary brake
- **Xbox Controller (optional)**
  - **RT** – throttle
  - **LT** – brake

**Interface**

- Side-view road with infinite scrolling environment
- Meter markers every **25 m**
- Car remains centered while the world scrolls
- **Live dashboard graphs** (30-second rolling window)

**Graph Modes**

- **Full mode:** velocity, acceleration, position, engine force, drag, rolling resistance, braking
- **Combined mode:** user-selectable normalized plots (0–1 scale)

**Options**

- Adjustable **physics timestep** (1 ms → 100 ms)
- Adjustable **render FPS** (60 → 240, simulation unaffected)
- **Control scheme selection**
- **Reset Scenario panel** to modify physical constants and restart the simulation

**Key constraint:** the car cannot move backward in this model.

### Model 2: Load Transfer Without Traction Limits (1D)

[Technical Analysis](https://yuk068.github.io/2026/03/12/car-physics-model2).

![model2-thumbnail](media/model2-thumbnail.webp)

**Controls**

Changed to seamless detect.

### Model 3: Engine Torque + Gearing without Slip (1D)

Coming soon.