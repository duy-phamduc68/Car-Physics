# ─────────────────────────────────────────────────────────────────────────────
# renderer.py — All pygame drawing: scene, car, HUD, graphs, clouds
# ─────────────────────────────────────────────────────────────────────────────

import pygame

from constants import (
    SKY_TOP, SKY_BOTTOM,
    ROAD_COLOR, MARKER_COLOR,
    CAR_BODY, CAR_ROOF, CAR_WINDOW, CAR_WHEEL, CAR_WHEEL_RIM,
    CLOUD_COLOR,
    GRAPH_BG, GRAPH_GRID, GRAPH_AXIS,
    PANEL_BG, ACCENT,
    TEXT_BRIGHT, TEXT_DIM,
    BTN_NORMAL, BTN_HOVER,
    GRAPH_COLORS, GRAPH_LABELS,
    PIXELS_PER_METER, MARKER_INTERVAL,
)
from physics import GraphBuffer


# ─────────────────────────────────────────────────────────────────────────────
# Module-level render caches
# ─────────────────────────────────────────────────────────────────────────────

_sky_cache: dict = {}          # keyed by (horizon_y, screen_w)
_marker_label_cache: dict = {} # keyed by distance in metres


# ─────────────────────────────────────────────────────────────────────────────
# Cloud entity
# ─────────────────────────────────────────────────────────────────────────────

class Cloud:
    def __init__(self, x, y, scale):
        self.x     = float(x)
        self.y     = float(y)
        self.scale = scale   # 0.5 - 1.5

    def draw(self, surface, draw_x=None):
        s = self.scale
        cx = int(draw_x if draw_x is not None else self.x)
        cy = int(self.y)
        circles = [
            (cx,               cy,               int(28*s)),
            (cx + int(24*s),   cy - int(10*s),   int(22*s)),
            (cx - int(22*s),   cy - int(8*s),    int(20*s)),
            (cx + int(8*s),    cy - int(18*s),   int(18*s)),
        ]
        for rx, ry, rr in circles:
            pygame.draw.circle(surface, CLOUD_COLOR, (rx, ry), rr)


# ─────────────────────────────────────────────────────────────────────────────
# Scene drawing
# ─────────────────────────────────────────────────────────────────────────────

def draw_sky(surface, horizon_y, screen_w):
    """Draw a vertical gradient sky from top to horizon (cached per size)."""
    key = (horizon_y, screen_w)
    if key not in _sky_cache:
        sky_surf = pygame.Surface((screen_w, horizon_y))
        for y in range(horizon_y):
            t = y / max(horizon_y, 1)
            r = int(SKY_TOP[0] + (SKY_BOTTOM[0] - SKY_TOP[0]) * t)
            g = int(SKY_TOP[1] + (SKY_BOTTOM[1] - SKY_TOP[1]) * t)
            b = int(SKY_TOP[2] + (SKY_BOTTOM[2] - SKY_TOP[2]) * t)
            pygame.draw.line(sky_surf, (r, g, b), (0, y), (screen_w, y))
        _sky_cache.clear()   # keep only the most-recent size
        _sky_cache[key] = sky_surf
    surface.blit(_sky_cache[key], (0, 0))


def draw_clouds(surface, clouds, cam_x, screen_w):
    """Render world-space clouds at parallax speed (30% of car speed)."""
    parallax_offset = cam_x * 0.3
    for c in clouds:
        screen_x = c.x - parallax_offset
        if -200 < screen_x < screen_w + 200:
            c.draw(surface, screen_x)


def draw_road(surface, road_rect, road_y, screen_w, cam_x, font_sm):
    """Draw road fill, dashed centre line, and distance markers."""
    pygame.draw.rect(surface, ROAD_COLOR, road_rect)

    # Dashed centre line
    dash_len   = 60
    gap_len    = 50
    period     = dash_len + gap_len
    road_mid_y = road_y + road_rect.height // 3
    offset_px  = int(cam_x * PIXELS_PER_METER) % period
    x = -offset_px
    while x < screen_w + period:
        pygame.draw.rect(surface, (120, 120, 120),
                         (x, road_mid_y - 2, dash_len, 4))
        x += period

    # Distance markers every MARKER_INTERVAL metres
    cam_px         = cam_x * PIXELS_PER_METER
    first_marker_m = int(cam_x / MARKER_INTERVAL) * MARKER_INTERVAL
    m = first_marker_m
    while True:
        world_px = m * PIXELS_PER_METER
        screen_x = int(world_px - cam_px + screen_w // 2)
        if screen_x > screen_w + 10:
            break
        if screen_x < -10:
            m += MARKER_INTERVAL
            continue
        pygame.draw.line(surface, MARKER_COLOR,
                         (screen_x, road_y),
                         (screen_x, road_y + 14), 2)
        lbl = _marker_label_cache.get(m)
        if lbl is None:
            lbl = font_sm.render(f"{m}m", True, MARKER_COLOR)
            _marker_label_cache[m] = lbl
        surface.blit(lbl, (screen_x - lbl.get_width() // 2, road_y + 16))
        m += MARKER_INTERVAL


def draw_car(surface, cx, wy, body_w, body_h, wheel_r):
    """Draw a simple geometric car centred at (cx, wy)."""
    # Wheels
    wheel_xs = [cx - body_w // 2 + wheel_r + 8,
                cx + body_w // 2 - wheel_r - 8]
    wheel_y  = wy - wheel_r
    for wx in wheel_xs:
        pygame.draw.circle(surface, CAR_WHEEL,     (wx, wheel_y), wheel_r)
        pygame.draw.circle(surface, CAR_WHEEL_RIM, (wx, wheel_y), wheel_r // 3)

    # Body
    body_top  = wy - wheel_r * 2 - body_h
    body_rect = pygame.Rect(cx - body_w // 2, body_top, body_w, body_h)
    pygame.draw.rect(surface, CAR_BODY, body_rect, border_radius=8)

    # Roof / cabin
    roof_w    = int(body_w * 0.55)
    roof_h    = int(body_h * 0.70)
    roof_rect = pygame.Rect(cx - roof_w // 2, body_top - roof_h, roof_w, roof_h)
    pygame.draw.rect(surface, CAR_ROOF, roof_rect, border_radius=6)

    # Window
    win_margin = 6
    win_rect   = pygame.Rect(roof_rect.x + win_margin,
                             roof_rect.y + win_margin,
                             roof_w - 2 * win_margin,
                             roof_h - 2 * win_margin)
    pygame.draw.rect(surface, CAR_WINDOW, win_rect, border_radius=4)

    # Headlight and taillight
    pygame.draw.circle(surface, (255, 240, 180),
                       (cx + body_w // 2 - 10, body_top + body_h // 2), 6)
    pygame.draw.circle(surface, (255, 60, 60),
                       (cx - body_w // 2 + 10, body_top + body_h // 2), 5)


def draw_hud(surface, font_sm, font_lg, menu_btn,
             fps_display, sim_time, car, throttle, brake,
             paused, horizon_y, screen_w):
    """Draw the HUD: options button, FPS, telemetry stats, paused banner."""
    # Menu button
    hover = menu_btn.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(surface, BTN_HOVER if hover else BTN_NORMAL,
                     menu_btn, border_radius=5)
    pygame.draw.rect(surface, ACCENT, menu_btn, 1, border_radius=5)
    lbl = font_sm.render("Options", True, TEXT_BRIGHT)
    surface.blit(lbl, lbl.get_rect(center=menu_btn.center))

    # FPS counter (top-right)
    fps_txt = font_sm.render(f"FPS: {fps_display:.0f}", True, TEXT_BRIGHT)
    surface.blit(fps_txt, (screen_w - fps_txt.get_width() - 8, 8))

    # Telemetry stats (top-centre)
    stats = [
        f"t = {sim_time:06.2f} s",
        f"v = {car.v:.2f} m/s  ({car.v * 3.6:.1f} km/h)",
        f"x = {car.x:.1f} m",
        f"T = {throttle:.2f}   B = {brake}",
    ]
    for i, s in enumerate(stats):
        t = font_sm.render(s, True, (0, 0, 0))
        surface.blit(t, (screen_w // 2 - t.get_width() // 2, 8 + i * 17))

    # Paused banner
    if paused:
        pb = font_lg.render("── PAUSED (Options open) ──", True, (255, 220, 60))
        surface.blit(pb, pb.get_rect(centerx=screen_w // 2, y=horizon_y - 36))


# ─────────────────────────────────────────────────────────────────────────────
# Graph renderers
# ─────────────────────────────────────────────────────────────────────────────

def _downsample(data: list, max_pts: int) -> list:
    """Return at most max_pts evenly-spaced elements from data.

    Avoids drawing more points than there are pixels in the plot area,
    keeping graph rendering O(pixels) instead of O(buffer_size).
    """
    n = len(data)
    if n <= max_pts:
        return data
    step = (n - 1) / (max_pts - 1)
    return [data[int(round(i * step))] for i in range(max_pts)]


def draw_graph_full(surface, rect, graph_buf, font_sm):
    """Draw 7 individual channel plots side by side inside rect."""
    n      = GraphBuffer.CHANNELS
    w_each = rect.width // n
    margin = 4

    pygame.draw.rect(surface, GRAPH_BG, rect)

    for ch in range(n):
        r = pygame.Rect(rect.x + ch * w_each + margin,
                        rect.y + margin,
                        w_each - 2 * margin,
                        rect.height - 2 * margin)
        pygame.draw.rect(surface, GRAPH_BG,   r)
        pygame.draw.rect(surface, GRAPH_GRID, r, 1)

        data = graph_buf.get(ch)
        if len(data) < 2:
            lbl = font_sm.render(GRAPH_LABELS[ch], True, GRAPH_COLORS[ch])
            surface.blit(lbl, (r.x + 4, r.y + 4))
            continue
        data = _downsample(data, max(2, r.width))

        mn, mx = min(data), max(data)
        if mx == mn:
            mid = (mn + mx) / 2
            mn  = mid - 1.0
            mx  = mid + 1.0

        # Horizontal grid lines
        for gi in range(5):
            gy = r.bottom - int((gi / 4) * r.height)
            pygame.draw.line(surface, GRAPH_GRID, (r.x, gy), (r.right, gy))
            val_lbl = font_sm.render(f"{mn + (mx - mn) * (gi / 4):.1f}",
                                     True, GRAPH_AXIS)
            surface.blit(val_lbl, (r.x + 2, gy - 9))

        # Curve
        pts = []
        for i, v in enumerate(data):
            px_ = r.x + int(i / (len(data) - 1) * r.width)
            py_ = r.bottom - int((v - mn) / (mx - mn) * r.height)
            py_ = max(r.y, min(r.bottom, py_))
            pts.append((px_, py_))
        if len(pts) >= 2:
            pygame.draw.lines(surface, GRAPH_COLORS[ch], False, pts, 2)

        lbl = font_sm.render(GRAPH_LABELS[ch], True, GRAPH_COLORS[ch])
        surface.blit(lbl, (r.x + 4, r.y + 4))


def draw_graph_combined(surface, rect, graph_buf, font_sm, channels_active):
    """Draw all active channels normalized 0→1 on a single plot."""
    pygame.draw.rect(surface, GRAPH_BG,   rect)
    pygame.draw.rect(surface, GRAPH_GRID, rect, 1)

    r = rect.inflate(-8, -8)

    # Grid
    for gi in range(5):
        gy = r.bottom - int((gi / 4) * r.height)
        pygame.draw.line(surface, GRAPH_GRID, (r.x, gy), (r.right, gy))
        val_lbl = font_sm.render(f"{gi / 4:.2f}", True, GRAPH_AXIS)
        surface.blit(val_lbl, (r.x + 2, gy - 9))

    legend_x = rect.x + 8
    legend_y = rect.y + 10

    for ch in range(GraphBuffer.CHANNELS):
        if not channels_active[ch]:
            continue
        data = graph_buf.get(ch)
        if len(data) < 2:
            continue
        data = _downsample(data, max(2, r.width))
        mn, mx = min(data), max(data)
        if mx == mn:
            mn -= 1.0
            mx += 1.0

        pts = []
        for i, v in enumerate(data):
            px_  = r.x + int(i / (len(data) - 1) * r.width)
            norm = (v - mn) / (mx - mn)
            py_  = r.bottom - int(norm * r.height)
            py_  = max(r.y, min(r.bottom, py_))
            pts.append((px_, py_))
        if len(pts) >= 2:
            pygame.draw.lines(surface, GRAPH_COLORS[ch], False, pts, 2)

        # Legend swatch + label
        pygame.draw.line(surface, GRAPH_COLORS[ch],
                         (legend_x, legend_y + 6),
                         (legend_x + 18, legend_y + 6), 2)
        lbl = font_sm.render(GRAPH_LABELS[ch], True, GRAPH_COLORS[ch])
        surface.blit(lbl, (legend_x + 22, legend_y))
        legend_x += lbl.get_width() + 36
        if legend_x > rect.right - 120:
            legend_x  = rect.x + 8
            legend_y += 18

    note = font_sm.render("Normalized 0.0 → 1.0 per channel", True, TEXT_DIM)
    surface.blit(note, (rect.x + rect.width - note.get_width() - 8,
                        rect.bottom - note.get_height() - 4))
