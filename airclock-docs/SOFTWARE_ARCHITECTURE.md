# Software Architecture

Main application: airclock_ui.py

Components:

UI Engine
- Draws screens to LCD
- Handles menus

Sensor Thread
- Reads SCD40 values
- Updates shared variables

Input System
- Rotary encoder navigation
- Button actions

Alarm System
- Time comparison with RTC
- Sound playback

Pomodoro Engine
- Work/break cycle timer