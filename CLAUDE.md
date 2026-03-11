# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Airclock is a Raspberry Pi-based smart clock running on physical hardware. It drives an ILI9341 SPI display (320×240) and reads from a rotary encoder, three physical buttons, and an SCD40 CO2/temperature/humidity sensor. Audio is played via `aplay` to a USB audio device.

The entire application lives in a single file: `airclock_ui.py`.

## Running the Application

The app must run on the Raspberry Pi (requires GPIO, SPI display, I2C sensor):

```bash
python3 airclock_ui.py
```

Config is loaded from and saved to `config.json` in the same directory as the script.

## Hardware Test Scripts

Standalone test scripts for individual hardware components (run on the Pi):

```bash
python3 airclock-docs/display_test.py   # ILI9341 SPI display
python3 airclock-docs/encoder_test.py   # Rotary encoder (GPIO 17/27)
python3 scd40_test.py                   # SCD40 sensor over I2C (/dev/i2c-1)
python3 audio_test.py                   # Audio via aplay (plughw:2,0)
```

## Architecture

`airclock_ui.py` is structured as a single-file event loop running at ~20 FPS (0.05s sleep). Key sections:

- **Display** — `luma.lcd` + `luma.core` driving ILI9341 over SPI. All drawing uses `canvas(device)` context manager with PIL `ImageDraw`. Fonts are DejaVu TTF loaded at module level.
- **Sensor loop** — runs in a background `Thread`, polling SCD40 every 5s over I2C. Data is shared via globals protected by `sensor_lock`.
- **Inputs** — polled each iteration (not interrupt-driven): `RotaryEncoder` on GPIO 17/27, three `Button` instances (Select=22, Back=23, Snooze=5). State transitions are edge-detected by comparing `*_now` vs `last_*` booleans.
- **Screens** — four screens (`SCREEN_HOME`, `SCREEN_ALARM`, `SCREEN_POMODORO`, `SCREEN_AIR`) controlled by `current_screen` global. Each screen has its own `draw_*` and `handle_encoder_*` function.
- **Alarm** — tracks `alarm_ringing`, `alarm_snooze_until`, and `last_alarm_trigger_minute` to prevent re-triggering within the same minute. Sound plays in a separate daemon thread via `aplay` subprocess.
- **Pomodoro** — state machine (`POMO_IDLE` → `POMO_WORK` → `POMO_BREAK` → ...) using `datetime` for countdowns.
- **Config** — JSON file persisted on "Save & Exit" from alarm/pomodoro screens. Stores alarm time, enabled flag, and pomodoro durations.

## Key GPIO / Hardware Pinout

| Component | GPIO / Interface |
|-----------|-----------------|
| Display (ILI9341) | SPI0, DC=GPIO25, RST=GPIO24 |
| Rotary encoder | A=GPIO17, B=GPIO27 |
| Select button | GPIO22 |
| Back button | GPIO23 |
| Snooze button | GPIO5 |
| SCD40 sensor | I2C-1 (/dev/i2c-1) |
| Audio output | plughw:2,0 (USB audio) |

## Dependencies

Python packages (install on Pi):
- `luma.lcd`, `luma.core`
- `gpiozero`
- `Pillow`
- `sensirion-i2c-driver`, `sensirion-i2c-scd`

System: `aplay` (ALSA), DejaVu fonts at `/usr/share/fonts/truetype/dejavu/`
