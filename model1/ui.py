# ─────────────────────────────────────────────────────────────────────────────
# ui.py — Button, CheckBox widgets and the scrollable OptionsMenu overlay
# ─────────────────────────────────────────────────────────────────────────────

import pygame

from constants import (
    TEXT_BRIGHT, TEXT_DIM,
    ACCENT, GRAPH_AXIS,
    BTN_NORMAL, BTN_HOVER, BTN_ACTIVE,
    GRAPH_GRID, GRAPH_LABELS,
    PANEL_BG,
    TIMESTEP_OPTIONS, FPS_OPTIONS, CONST_FIELDS,
)


# ─────────────────────────────────────────────────────────────────────────────
# Small helpers
# ─────────────────────────────────────────────────────────────────────────────

def _sec_label(surface, font, text, x, y, color=None):
    """Render a dim section header onto surface."""
    col = color if color is not None else TEXT_DIM
    lbl = font.render(text, True, col)
    surface.blit(lbl, (x, y))


def _fmt_const(val):
    """Format a constant value for display: integer-valued floats without '.0'."""
    if val == int(val):
        return str(int(val))
    return f"{val:g}"


def _const_valid(txt):
    """Return True if txt parses as a float greater than zero."""
    try:
        return float(txt) > 0
    except (ValueError, TypeError):
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Button widget
# ─────────────────────────────────────────────────────────────────────────────

class Button:
    def __init__(self, rect, label, toggle=False, active=False):
        self.rect     = pygame.Rect(rect)
        self.label    = label
        self.toggle   = toggle
        self.active   = active
        self.disabled = False
        self._hover   = False

    def handle_event(self, event, mapped_pos=None):
        """Return True on click; always False when disabled."""
        if self.disabled:
            return False

        pos = mapped_pos if mapped_pos is not None else getattr(event, 'pos', None)
        if pos is None:
            return False

        if event.type == pygame.MOUSEMOTION:
            self._hover = self.rect.collidepoint(pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pos):
                if self.toggle:
                    self.active = not self.active
                return True
        return False

    def draw(self, surface, font):
        if self.disabled:
            col        = (30, 32, 42)
            border_col = (55, 58, 72)
            txt_col    = (80, 82, 98)
        elif self.active:
            col        = BTN_ACTIVE
            border_col = ACCENT
            txt_col    = TEXT_BRIGHT
        elif self._hover:
            col        = BTN_HOVER
            border_col = GRAPH_AXIS
            txt_col    = TEXT_BRIGHT
        else:
            col        = BTN_NORMAL
            border_col = GRAPH_AXIS
            txt_col    = TEXT_BRIGHT

        pygame.draw.rect(surface, col,        self.rect, border_radius=5)
        pygame.draw.rect(surface, border_col, self.rect, 1, border_radius=5)
        txt = font.render(self.label, True, txt_col)
        surface.blit(txt, txt.get_rect(center=self.rect.center))


# ─────────────────────────────────────────────────────────────────────────────
# CheckBox widget
# ─────────────────────────────────────────────────────────────────────────────

class CheckBox:
    def __init__(self, x, y, label, checked=True):
        self.rect    = pygame.Rect(x, y, 18, 18)
        self.label   = label
        self.checked = checked
        self._hover  = False

    def handle_event(self, event, mapped_pos=None):
        pos = mapped_pos if mapped_pos is not None else getattr(event, 'pos', None)
        if pos is None:
            return False

        if event.type == pygame.MOUSEMOTION:
            self._hover = self.rect.collidepoint(pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pos):
                self.checked = not self.checked
                return True
        return False

    def draw(self, surface, font):
        col = BTN_HOVER if self._hover else BTN_NORMAL
        pygame.draw.rect(surface, col,   self.rect, border_radius=3)
        pygame.draw.rect(surface, ACCENT, self.rect, 1, border_radius=3)
        if self.checked:
            pygame.draw.line(surface, ACCENT,
                             (self.rect.x + 3,  self.rect.y + 9),
                             (self.rect.x + 7,  self.rect.y + 14), 2)
            pygame.draw.line(surface, ACCENT,
                             (self.rect.x + 7,  self.rect.y + 14),
                             (self.rect.x + 15, self.rect.y + 4),  2)
        txt = font.render(self.label, True, TEXT_BRIGHT)
        surface.blit(txt, (self.rect.right + 8, self.rect.y))


# ─────────────────────────────────────────────────────────────────────────────
# Options menu (scrollable overlay panel)
# ─────────────────────────────────────────────────────────────────────────────

class OptionsMenu:
    # Layout constants
    _PW      = 560
    _ROW     = 34    # button height
    _GAP     = 20    # vertical gap between rows
    _SEC_GAP = 18    # gap between sections

    def __init__(self, sim):
        self.sim      = sim
        self.visible  = False
        self.scroll_y = 0
        self.panel_x  = 10
        self.panel_y  = 10
        self.panel    = pygame.Rect(0, 0, 0, 0)

        # Track pending constant edits  {attr: text_string}
        self._const_texts   = {f[1]: _fmt_const(f[3]) for f in CONST_FIELDS}
        self._const_editing = None
        self._const_dirty   = False
        self._build()

    # ── internal helpers ──────────────────────────────────────────────────────

    def _all_non_reset_btns(self):
        """Yield every button that must be grayed-out when constants are dirty."""
        for _, btn in self._ts_buttons:
            yield btn
        for _, btn in self._fps_buttons:
            yield btn
        yield self._btn_full
        yield self._btn_comb
        yield self._btn_kb
        yield self._btn_ctrl
        yield self._btn_close

    def _apply_dirty(self):
        for btn in self._all_non_reset_btns():
            btn.disabled = self._const_dirty

    def _is_const_dirty(self):
        s = self.sim
        for _name, attr, _unit, _default in CONST_FIELDS:
            try:
                val = float(self._const_texts.get(attr, ""))
                if val > 0 and abs(val - getattr(s.car, attr)) > 1e-9:
                    return True
            except ValueError:
                pass
        return False

    # ── build widget layout ───────────────────────────────────────────────────

    def _build(self):
        s  = self.sim
        pw = self._PW
        R  = self._ROW
        G  = self._GAP
        SG = self._SEC_GAP

        px = 0
        y  = 46

        # Timestep
        self._ts_buttons = []
        for i, (dt, label) in enumerate(TIMESTEP_OPTIONS):
            btn = Button((px + 10, y + i * (R + G), pw - 20, R),
                         label, toggle=True, active=(dt == s.dt))
            self._ts_buttons.append((dt, btn))
        y += len(TIMESTEP_OPTIONS) * (R + G) + SG

        # FPS
        col_w = (pw - 20) // len(FPS_OPTIONS)
        self._fps_buttons = []
        for i, fps in enumerate(FPS_OPTIONS):
            btn = Button((px + 10 + i * col_w, y, col_w - 6, R),
                         str(fps), toggle=True, active=(fps == s.target_fps))
            self._fps_buttons.append((fps, btn))
        y += R + G + SG

        # Graph mode
        self._btn_full = Button((px + 10,  y, 130, R), "Full Mode",
                                toggle=True, active=(s.graph_mode == "full"))
        self._btn_comb = Button((px + 150, y, 150, R), "Combined Mode",
                                toggle=True, active=(s.graph_mode == "combined"))
        y += R + G

        # Combined channel checkboxes
        self._comb_checks = []
        for i, lbl in enumerate(GRAPH_LABELS):
            cb = CheckBox(px + 16 + (i % 2) * 260, y + (i // 2) * 26, lbl,
                          checked=s.combined_channels[i])
            self._comb_checks.append(cb)
        y += ((len(GRAPH_LABELS) + 1) // 2) * 26 + G + SG

        # Throttle ramp
        self._ramp_rect    = pygame.Rect(px + 140, y, pw - 150, R)
        self._ramp_editing = False
        self._ramp_text    = str(s.throttle_ramp)
        y += R + G + SG

        # Control mode
        self._btn_kb   = Button((px + 10,  y, 160, R), "Keyboard",
                                toggle=True, active=(s.control_mode == "keyboard"))
        self._btn_ctrl = Button((px + 180, y, 200, R), "Xbox Controller",
                                toggle=True, active=(s.control_mode == "controller"))
        y += R + G + SG

        # Divider
        self._divider_y = y
        y += 2 + SG

        # Physics constants input rows
        field_row_h = R + G
        col_label_w = 130
        col_input_w = 110
        self._const_rects = {}
        for i, (_name, attr, _unit, _default) in enumerate(CONST_FIELDS):
            iy = y + i * field_row_h
            self._const_rects[attr] = pygame.Rect(
                px + 10 + col_label_w + 8, iy, col_input_w, R)
        y += len(CONST_FIELDS) * field_row_h + G

        # Reset Scenario button
        self._btn_reset = Button(
            (px + pw // 2 - 100, y, 200, R + 4), "Reset Scenario")
        y += R + 4 + G

        # Controls guide
        self._tooltip_y = y
        y += 48

        # Close button
        self._btn_close = Button((px + pw // 2 - 60, y, 120, R), "Close")
        y += R + 14

        self._total_height = y + 10
        self._apply_dirty()

    @property
    def editing_active(self):
        """True while a text input field inside the menu is being edited."""
        return self._ramp_editing or self._const_editing is not None

    def toggle(self):
        self.visible = not self.visible
        if self.visible:
            self.scroll_y = 0
            self._build()

    # ── event handling ────────────────────────────────────────────────────────

    def handle_event(self, event):
        if not self.visible:
            return False

        s = self.sim

        viewport_h = min(self._total_height, s.screen_h - 40)
        self.panel = pygame.Rect(self.panel_x, self.panel_y, self._PW, viewport_h)

        pos        = getattr(event, 'pos', None)
        mapped_pos = None
        if pos and self.panel.collidepoint(pos):
            mapped_pos = (pos[0] - self.panel.x,
                          pos[1] - self.panel.y + self.scroll_y)

        # Mouse-wheel scrolling
        if event.type == pygame.MOUSEWHEEL:
            if self.panel.collidepoint(pygame.mouse.get_pos()):
                self.scroll_y -= event.y * 30
                max_scroll     = max(0, self._total_height - viewport_h)
                self.scroll_y  = max(0, min(self.scroll_y, max_scroll))
                return True

        # Reset Scenario (always active, applies pending constants)
        if self._btn_reset.handle_event(event, mapped_pos):
            if self._const_dirty:
                for _name, attr, _unit, _default in CONST_FIELDS:
                    txt = self._const_texts.get(attr, "")
                    try:
                        val = float(txt)
                        if val > 0:
                            setattr(s.car, attr, val)
                    except ValueError:
                        pass
                self._const_dirty = False
                self._apply_dirty()
            s.reset_scenario()
            return True

        # All other buttons are blocked while constants are dirty
        if not self._const_dirty:
            for dt, btn in self._ts_buttons:
                if btn.handle_event(event, mapped_pos):
                    for dt2, b2 in self._ts_buttons:
                        b2.active = (dt2 == dt)
                    if dt != s.dt:
                        s.dt = dt
                        s.reset_scenario()
                    return True

            for fps, btn in self._fps_buttons:
                if btn.handle_event(event, mapped_pos):
                    for fps2, b2 in self._fps_buttons:
                        b2.active = (fps2 == fps)
                    s.target_fps = fps
                    return True

            if self._btn_full.handle_event(event, mapped_pos):
                s.graph_mode          = "full"
                self._btn_full.active = True
                self._btn_comb.active = False
                return True
            if self._btn_comb.handle_event(event, mapped_pos):
                s.graph_mode          = "combined"
                self._btn_full.active = False
                self._btn_comb.active = True
                return True

            for i, cb in enumerate(self._comb_checks):
                if cb.handle_event(event, mapped_pos):
                    s.combined_channels[i] = cb.checked
                    return True

            if self._btn_kb.handle_event(event, mapped_pos):
                s.control_mode        = "keyboard"
                self._btn_kb.active   = True
                self._btn_ctrl.active = False
                return True
            if self._btn_ctrl.handle_event(event, mapped_pos):
                s.control_mode        = "controller"
                self._btn_kb.active   = False
                self._btn_ctrl.active = True
                return True

            if self._btn_close.handle_event(event, mapped_pos):
                self.visible = False
                return True

        # Constants input boxes (always interactive)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if mapped_pos:
                self._ramp_editing = self._ramp_rect.collidepoint(mapped_pos)
                clicked_attr = None
                for attr, rect in self._const_rects.items():
                    if rect.collidepoint(mapped_pos):
                        clicked_attr = attr
                        break
                self._const_editing = clicked_attr
                if clicked_attr:
                    self._ramp_editing = False
            else:
                self._ramp_editing  = False
                self._const_editing = None

        # Throttle ramp text input
        if self._ramp_editing and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._ramp_editing = False
                try:
                    val = float(self._ramp_text)
                    if val > 0:
                        s.throttle_ramp = val
                except ValueError:
                    self._ramp_text = str(s.throttle_ramp)
            elif event.key == pygame.K_BACKSPACE:
                self._ramp_text = self._ramp_text[:-1]
            elif event.key == pygame.K_ESCAPE:
                self._ramp_editing = False
                self._ramp_text    = str(s.throttle_ramp)
            else:
                if len(self._ramp_text) < 10:
                    self._ramp_text += event.unicode
            return True

        # Physics constant text input
        if self._const_editing is not None and event.type == pygame.KEYDOWN:
            attr = self._const_editing
            cur  = self._const_texts.get(attr, "")
            if event.key in (pygame.K_RETURN, pygame.K_TAB):
                self._const_editing = None
                if event.key == pygame.K_TAB:
                    attrs = [f[1] for f in CONST_FIELDS]
                    idx   = attrs.index(attr) if attr in attrs else -1
                    if 0 <= idx < len(attrs) - 1:
                        self._const_editing = attrs[idx + 1]
            elif event.key == pygame.K_BACKSPACE:
                self._const_texts[attr] = cur[:-1]
            elif event.key == pygame.K_ESCAPE:
                self._const_editing     = None
                self._const_texts[attr] = _fmt_const(getattr(s.car, attr))
            else:
                if len(cur) < 12:
                    self._const_texts[attr] = cur + event.unicode
            self._const_dirty = self._is_const_dirty()
            self._apply_dirty()
            return True

        return True  # swallow all events while the menu is open

    # ── drawing ───────────────────────────────────────────────────────────────

    def draw(self, surface, font_sm, font_md):
        if not self.visible:
            return

        s  = self.sim
        pw = self._PW
        R  = self._ROW
        G  = self._GAP
        SG = self._SEC_GAP

        viewport_h    = min(self._total_height, surface.get_height() - 40)
        self.panel    = pygame.Rect(self.panel_x, self.panel_y, pw, viewport_h)
        max_scroll    = max(0, self._total_height - viewport_h)
        self.scroll_y = max(0, min(self.scroll_y, max_scroll))

        # Semi-transparent backdrop
        overlay = pygame.Surface((surface.get_width(), surface.get_height()),
                                 pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surface.blit(overlay, (0, 0))

        # Panel background with rounded border
        panel_bg = pygame.Surface((pw, viewport_h), pygame.SRCALPHA)
        pygame.draw.rect(panel_bg, PANEL_BG,  panel_bg.get_rect(), border_radius=6)
        pygame.draw.rect(panel_bg, ACCENT,    panel_bg.get_rect(), 1, border_radius=6)
        surface.blit(panel_bg, self.panel.topleft)

        # Full-height content surface (scrolled into the viewport)
        content = pygame.Surface((pw, self._total_height), pygame.SRCALPHA)

        px = 0
        y  = 46

        title = font_md.render("Options", True, TEXT_BRIGHT)
        content.blit(title, (px + 16, 12))

        # Timestep
        _sec_label(content, font_sm, "Timestep", px + 10, y - 16)
        for _, btn in self._ts_buttons:
            btn.draw(content, font_sm)
        y += len(TIMESTEP_OPTIONS) * (R + G) + SG

        # FPS
        _sec_label(content, font_sm, "Target FPS", px + 10, y - 16)
        for _, btn in self._fps_buttons:
            btn.draw(content, font_sm)
        y += R + G + SG

        # Graph mode
        _sec_label(content, font_sm, "Graph Mode", px + 10, y - 16)
        self._btn_full.draw(content, font_sm)
        self._btn_comb.draw(content, font_sm)
        y += R + G

        # Combined channel checkboxes
        _sec_label(content, font_sm, "Combined Channels", px + 10, y - 16)
        for cb in self._comb_checks:
            cb.draw(content, font_sm)
        y += ((len(GRAPH_LABELS) + 1) // 2) * 26 + G + SG

        # Throttle ramp
        _sec_label(content, font_sm, "Throttle Ramp (s)", px + 10, y + 7)
        border_col = ACCENT if self._ramp_editing else GRAPH_AXIS
        pygame.draw.rect(content, BTN_NORMAL, self._ramp_rect, border_radius=4)
        pygame.draw.rect(content, border_col, self._ramp_rect, 1, border_radius=4)
        rt = font_sm.render(
            self._ramp_text + ("|" if self._ramp_editing else ""),
            True, TEXT_BRIGHT)
        content.blit(rt, (self._ramp_rect.x + 8, self._ramp_rect.y + 8))
        y += R + G + SG

        # Control mode
        _sec_label(content, font_sm, "Control Mode", px + 10, y - 16)
        self._btn_kb.draw(content, font_sm)
        self._btn_ctrl.draw(content, font_sm)
        y += R + G + SG

        # Divider
        pygame.draw.line(content, GRAPH_GRID,
                         (px + 10, self._divider_y),
                         (px + pw - 10, self._divider_y), 1)
        y = self._divider_y + 2 + SG

        # Physics constants
        warn_col = (255, 180, 50)
        sec_txt  = "Physics Constants"
        if self._const_dirty:
            sec_txt += "pending - press Reset Scenario to apply"
        _sec_label(content, font_sm, sec_txt, px + 10, y - 16,
                   color=warn_col if self._const_dirty else TEXT_DIM)

        field_row_h = R + G
        for i, (name, attr, unit, _default) in enumerate(CONST_FIELDS):
            iy  = y + i * field_row_h
            lbl = font_sm.render(f"{name}  [{unit}]", True, TEXT_DIM)
            content.blit(lbl, (px + 10, iy + 8))

            rect      = self._const_rects[attr]
            is_active = (self._const_editing == attr)
            txt_str   = self._const_texts.get(attr, "")
            valid     = _const_valid(txt_str)

            if is_active:
                box_col    = (30, 40, 60)
                border_col = ACCENT
            elif not valid:
                box_col    = (55, 20, 20)
                border_col = (200, 60, 60)
            elif self._const_dirty and abs(
                    float(txt_str) - getattr(s.car, attr)) > 1e-9:
                box_col    = (40, 35, 15)
                border_col = warn_col
            else:
                box_col    = BTN_NORMAL
                border_col = GRAPH_AXIS

            pygame.draw.rect(content, box_col,    rect, border_radius=4)
            pygame.draw.rect(content, border_col, rect, 1, border_radius=4)
            tv = font_sm.render(txt_str + ("|" if is_active else ""),
                                True, TEXT_BRIGHT)
            content.blit(tv, (rect.x + 6, rect.y + 8))
            u_lbl = font_sm.render(unit, True, TEXT_DIM)
            content.blit(u_lbl, (rect.right + 8, rect.y + 8))

        y += len(CONST_FIELDS) * field_row_h + G

        # Reset Scenario / Close
        self._btn_reset.draw(content, font_md)

        # Controls Guide
        _sec_label(content, font_sm, "Controls Guide", content.get_width() / 2 - 50, self._tooltip_y - 10)
        tooltip_text = [
            "Keyboard: space for throttle, b for brake",
            "xbox: rt for throttle, lt for brake (still binary)",
        ]
        for i, line in enumerate(tooltip_text):
            lbl = font_sm.render(line, True, TEXT_DIM)
            content.blit(lbl, lbl.get_rect(center=(content.get_width() / 2, self._tooltip_y + 15 + i * 20)))

        self._btn_close.draw(content, font_sm)

        # Blit the scrolled slice of the content surface
        surface.blit(content, self.panel.topleft,
                     area=pygame.Rect(0, self.scroll_y, pw, viewport_h))

        # Scroll bar
        if max_scroll > 0:
            bar_w = 6
            bar_h = max(20, int(viewport_h * (viewport_h / self._total_height)))
            bar_x = self.panel.right - 10
            bar_y = self.panel.y + int(
                (self.scroll_y / max_scroll) * (viewport_h - bar_h))
            pygame.draw.rect(surface, GRAPH_AXIS,
                             (bar_x, bar_y, bar_w, bar_h), border_radius=3)
