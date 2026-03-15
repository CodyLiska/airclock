# AirClock – Hardware Documentation

## Overview

AirClock is a Raspberry Pi–based desktop device that combines several functions:

- Pomodoro productivity timer
- Alarm clock
- CO₂ air quality monitor
- Environmental display (temperature + humidity)
- Rotary encoder–controlled UI
- Color LCD display with retro UI

This document describes all hardware components used in the build.

---

## Core Controller

### Raspberry Pi 3 Model B

The Raspberry Pi acts as the central controller for the system.

#### Responsibilities

- Runs the AirClock Python application
- Drives the SPI LCD display
- Communicates with sensors via I²C
- Handles GPIO input from buttons and rotary encoder
- Outputs alarm sounds through USB audio

#### Key Interfaces Used

| Interface | Purpose |
|---|---|
| SPI | LCD display communication |
| I²C | CO₂ sensor + RTC |
| GPIO | Buttons and rotary encoder |
| USB | Audio adapter |

---

## Display

### 2.8" TFT SPI LCD Display (ILI9341)

**Resolution:** 320 × 240

This display provides the graphical interface for the device.

#### Functions

- Clock display
- Pomodoro timer
- Alarm configuration
- Air quality information
- Menu navigation

#### Interface

SPI connection to Raspberry Pi.

#### GPIO Connections

| LCD Pin | Raspberry Pi Pin |
|---|---|
| VCC | 3.3V |
| GND | GND |
| CS | CE0 |
| RESET | GPIO24 |
| DC | GPIO25 |
| MOSI | GPIO10 |
| SCK | GPIO11 |
| LED | 3.3V (always-on backlight) |

---

## Air Quality Sensor

### Sensirion SCD40 CO₂ Sensor

The SCD40 measures:

- CO₂ concentration (ppm)
- Temperature
- Relative humidity

#### Interface

I²C

#### Connections

| Sensor Pin | Raspberry Pi |
|---|---|
| VDD | 3.3V |
| GND | GND |
| SDA | GPIO2 (SDA) |
| SCL | GPIO3 (SCL) |

#### Typical Readings

- CO₂: 400–1000 ppm
- Temperature: ambient room temperature
- Humidity: relative humidity %

---

## Real Time Clock

### DS3231 RTC Module

Provides accurate timekeeping even when the Pi is powered off.

The module contains:

- DS3231 RTC chip
- AT24C32 EEPROM
- Backup battery (CR2032)

#### Purpose

- Maintains time without internet
- Enables alarm reliability

#### Interface

I²C

#### Connections

| RTC Pin | Raspberry Pi |
|---|---|
| VCC | 3.3V |
| GND | GND |
| SDA | GPIO2 |
| SCL | GPIO3 |

The RTC shares the same I²C bus as the SCD40.

---

## Input Controls

### Rotary Encoder (EC11)

Primary navigation control.

#### Functions

- Rotate: navigate menus
- Press: select option

#### Connections

| Encoder Pin | Raspberry Pi |
|---|---|
| S1 | GPIO17 |
| S2 | GPIO27 |
| KEY | GPIO22 |
| 5V | 3.3V |
| GND | GND |

### Push Buttons (2)

Two tactile switches provide additional control.

#### Back / Dismiss Button

Returns to previous screen or dismisses alarm.

#### Snooze / Mode Button

Snoozes alarm or toggles Pomodoro state.

#### Connections

| Button | Raspberry Pi |
|---|---|
| Button 1 | GPIO23 |
| Button 2 | GPIO18 |
| Other leg | GND |

Buttons use internal pull-up resistors.

---

## Audio Output

### USB Audio Adapter

Used to output alarm sounds.

The Raspberry Pi 3 headphone output works, but USB audio provides better compatibility.

#### Connection

USB → 3.5mm audio jack

### Mini 3.5mm Speaker

Small amplified speaker for alarm sounds.

#### Connection

USB audio adapter → speaker

---

## Prototyping Components

### Breadboard

Used for prototyping and connecting components without soldering.

- 400 point breadboard
- Power rails used for 3.3V and GND distribution

### Dupont Jumper Wires

Used to connect components.

Types used:

- Male → Female
- Male → Male
- Female → Female

---

## System Architecture

```text
             +----------------------+
             | Raspberry Pi 3B      |
             |                      |
             | SPI → LCD Display    |
             | I2C → SCD40 Sensor   |
             | I2C → DS3231 RTC     |
             | GPIO → Encoder       |
             | GPIO → Buttons       |
             | USB → Audio Adapter  |
             +----------+-----------+
                        |
                        v
                 Mini Speaker
```

---

## Power

The Raspberry Pi is powered via:

- 5V Micro-USB Power Supply

The Pi distributes 3.3V power to:

- LCD logic
- SCD40 sensor
- RTC module
- Rotary encoder module

---

## Current Hardware Status

| Component | Status |
|---|---|
| Raspberry Pi | Installed |
| LCD display | Working |
| Rotary encoder | Working |
| Buttons | Working |
| SCD40 sensor | Working |
| RTC module | Working |
| Audio output | Working |
| Pomodoro timer | Working |
| Alarm clock | Working |

---

## Future Hardware Additions (Optional)

Possible upgrades:

- PM2.5 particulate sensor (PMS5003)
- Light sensor for auto brightness
- RGB status LED
- Case-mounted speaker
- LiPo battery + UPS module
- Capacitive touch buttons
- OLED secondary status display

---

## Final Hardware Summary

| Component | Quantity |
|---|---|
| Raspberry Pi 3B | 1 |
| 2.8" SPI TFT LCD (ILI9341) | 1 |
| Sensirion SCD40 CO₂ Sensor | 1 |
| DS3231 RTC Module | 1 |
| Rotary Encoder (EC11) | 1 |
| Push Buttons | 2 |
| USB Audio Adapter | 1 |
| Mini Speaker | 1 |
| Breadboard | 1 |
| Dupont Jumper Wires | many |

---

## Result

The completed device functions as a self-contained productivity and environmental monitoring station with physical controls and a retro graphical interface.
