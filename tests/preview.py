"""
Desktop preview for AirClock — stubs Pi hardware, renders to a pygame window.

Install:   pip install pygame pillow
Run:       python3 preview.py

Controls:
  Up / Down   Rotate encoder (navigate menus / adjust values)
  Enter       Select button
  Esc         Back button
  Space       Snooze button
  T           Cycle background theme
  Q           Quit
"""

import sys
import types
import importlib.util
import json
import threading
from pathlib import Path
from unittest.mock import MagicMock

# ── 1. Stub hardware libraries before airclock-ui.py loads ───────────────────


class _Encoder:
    def __init__(self, *a, **kw):
        self.steps = 0


class _Button:
    def __init__(self, *a, **kw):
        self.is_pressed = False


_gpiozero = types.ModuleType("gpiozero")
_gpiozero.RotaryEncoder = _Encoder
_gpiozero.Button = _Button
sys.modules["gpiozero"] = _gpiozero

_fake_device = MagicMock()

_luma_serial = types.ModuleType("luma.core.interface.serial")
_luma_serial.spi = MagicMock(return_value=MagicMock())
_luma_lcd_dev = types.ModuleType("luma.lcd.device")
_luma_lcd_dev.ili9341 = MagicMock(return_value=_fake_device)

for _name, _mod in [
    ("luma",                       MagicMock()),
    ("luma.core",                  MagicMock()),
    ("luma.core.interface",        MagicMock()),
    ("luma.core.interface.serial", _luma_serial),
    ("luma.lcd",                   MagicMock()),
    ("luma.lcd.device",            _luma_lcd_dev),
    ("sensirion_i2c_driver",       MagicMock()),
    ("sensirion_i2c_scd",          MagicMock()),
]:
    sys.modules[_name] = _mod


# ── 2. Point BASE_PATH at the local repo root via environment variable ────────

_ROOT = Path(__file__).parent
import os
os.environ["AIRCLOCK_BASE"] = str(_ROOT)


# ── 3. Load airclock-ui.py ───────────────────────────────────────────────────

_spec = importlib.util.spec_from_file_location("airclock_ui", _ROOT / "airclock-ui.py")
ui = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ui)


# ── 4. Wire display output to pygame ─────────────────────────────────────────

import pygame
from PIL import ImageDraw as _ImageDraw

pygame.init()
_screen   = pygame.display.set_mode((800, 480))
_pg_clock = pygame.time.Clock()

# Mock screen is 320x240, centered on the 800x480 canvas
_SCREEN_W, _SCREEN_H = 320, 240
_SCREEN_X = (800 - _SCREEN_W) // 2   # 240
_SCREEN_Y = (480 - _SCREEN_H) // 2   # 120
_BEZEL    = 6

_COLOR_BG    = (30, 30, 30)
_COLOR_BEZEL = (60, 60, 60)
_COLOR_TEXT  = (160, 160, 160)

pygame.font.init()
_font_ui = pygame.font.SysFont("monospace", 13)


def _draw_canvas(theme_name):
    _screen.fill(_COLOR_BG)
    pygame.draw.rect(
        _screen, _COLOR_BEZEL,
        (_SCREEN_X - _BEZEL, _SCREEN_Y - _BEZEL,
         _SCREEN_W + _BEZEL * 2, _SCREEN_H + _BEZEL * 2),
        border_radius=4,
    )
    hints = [
        f"Theme: {theme_name}   |   T = next theme",
        "Up/Down = encoder    Enter = Select    Esc = Back    Space = Snooze    Q = Quit",
    ]
    y = _SCREEN_Y + _SCREEN_H + _BEZEL + 12
    for line in hints:
        surf = _font_ui.render(line, True, _COLOR_TEXT)
        _screen.blit(surf, surf.get_rect(centerx=400, top=y))
        y += 18


_active_theme_name = ""


def _show(img):
    surf = pygame.image.fromstring(img.tobytes(), img.size, img.mode)
    _draw_canvas(_active_theme_name)
    _screen.blit(surf, (_SCREEN_X, _SCREEN_Y))
    pygame.display.flip()


_fake_device.display = _show


# ── 5. Patch draw_air_screen (missing device.display call in Pi file) ─────────

def _draw_air_screen_fixed():
    with ui.sensor_lock:
        current_co2      = ui.co2_ppm
        current_temp     = ui.temp_c
        current_humidity = ui.humidity_rh
        current_sensor_status = ui.sensor_status

    img  = ui.BG_AIR.copy()
    draw = _ImageDraw.Draw(img)
    ui.draw_text_shadow(draw, (10, 8), "Air Quality", ui.font_title)

    if current_co2 is None or current_temp is None or current_humidity is None:
        ui.draw_text_shadow(draw, (10, 40), current_sensor_status, ui.font_big)
    else:
        temp_f = ui.c_to_f(current_temp)
        ui.draw_text_shadow(draw, (10, 38),   f"{current_co2} ppm",             ui.font_big)
        ui.draw_text_shadow(draw, (150, 46),  ui.co2_status_text(current_co2),  ui.font_body_bold)
        ui.draw_text_shadow(draw, (10, 86),   "Temperature",                    ui.font_body_bold)
        ui.draw_text_shadow(draw, (10, 104),  f"{temp_f:.1f} F",                ui.font_big)
        ui.draw_text_shadow(draw, (150, 86),  "Humidity",                       ui.font_body_bold)
        ui.draw_text_shadow(draw, (150, 104), f"{current_humidity:.1f} %",      ui.font_big)
        ui.draw_text_shadow(draw, (10, 150),  "CO2 Guide",                      ui.font_body_bold)
        ui.draw_text_shadow(draw, (10, 168),  "<800 Good",                      ui.font_body)
        ui.draw_text_shadow(draw, (10, 184),  "800-1200 Moderate",              ui.font_body)
        ui.draw_text_shadow(draw, (10, 200),  ">1200 Poor",                     ui.font_body)

    ui.footer(draw, "Back=Home")
    ui.device.display(img)


ui.draw_air_screen = _draw_air_screen_fixed


# ── 6. Theme switcher ─────────────────────────────────────────────────────────

_CONFIG_PATH = _ROOT / "config.json"
_THEMES      = sorted(d.name for d in (_ROOT / "background").iterdir() if d.is_dir())


def _load_theme(name):
    global _active_theme_name
    ui.BG_HOME, ui.BG_ALARM, ui.BG_POMODORO, ui.BG_AIR = ui.load_backgrounds(name)
    _active_theme_name = name
    pygame.display.set_caption(f"AirClock Preview  [{name}]")
    print(f"[preview] theme → {name}")


def _save_theme(name):
    try:
        data = json.loads(_CONFIG_PATH.read_text())
        data["theme"] = name
        _CONFIG_PATH.write_text(json.dumps(data, indent=2))
    except Exception:
        pass


# ── 7. Run ────────────────────────────────────────────────────────────────────

ui.load_config()
ui.last_steps = ui.enc.steps
threading.Thread(target=ui.sensor_loop, daemon=True).start()

_theme_idx = _THEMES.index(ui.config_data["theme"]) if hasattr(ui, "config_data") else 0
try:
    _active = json.loads(_CONFIG_PATH.read_text()).get("theme", _THEMES[0])
    _theme_idx = _THEMES.index(_active) if _active in _THEMES else 0
except Exception:
    _theme_idx = 0

_load_theme(_THEMES[_theme_idx])
print(f"Themes: {', '.join(_THEMES)}")
print("Up/Down=encoder  Enter=Select  Esc=Back  Space=Snooze  T=cycle theme  Q=quit")

running = True
while running:
    ui.btn_select.is_pressed = False
    ui.btn_back.is_pressed   = False
    ui.btn_snooze.is_pressed = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if   event.key == pygame.K_q:      running = False
            elif event.key == pygame.K_UP:     ui.enc.steps -= 1
            elif event.key == pygame.K_DOWN:   ui.enc.steps += 1
            elif event.key == pygame.K_RETURN: ui.btn_select.is_pressed = True
            elif event.key == pygame.K_ESCAPE: ui.btn_back.is_pressed   = True
            elif event.key == pygame.K_SPACE:  ui.btn_snooze.is_pressed = True
            elif event.key == pygame.K_t:
                _theme_idx = (_theme_idx + 1) % len(_THEMES)
                _load_theme(_THEMES[_theme_idx])
                _save_theme(_THEMES[_theme_idx])

    ui.check_alarm()
    ui.update_pomodoro_state()
    ui.handle_inputs()
    ui.draw_screen()
    _pg_clock.tick(20)

ui.stop_alarm_sound()
pygame.quit()
