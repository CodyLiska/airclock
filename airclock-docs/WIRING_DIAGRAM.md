
# AirClock – Wiring Diagram & GPIO Map

This document describes how every component in the AirClock device is wired to the Raspberry Pi 3B.
It includes the GPIO mapping, wiring explanations, and a logical diagram to make rebuilding or modifying the project easy.

---

# Raspberry Pi GPIO Reference

The AirClock project uses the 40‑pin GPIO header on the Raspberry Pi 3 Model B.

```
 3.3V  (1) (2) 5V
 GPIO2 (3) (4) 5V
 GPIO3 (5) (6) GND
 GPIO4 (7) (8) GPIO14
 GND   (9) (10)GPIO15
 GPIO17(11)(12)GPIO18
 GPIO27(13)(14)GND
 GPIO22(15)(16)GPIO23
 3.3V  (17)(18)GPIO24
 GPIO10(19)(20)GND
 GPIO9 (21)(22)GPIO25
 GPIO11(23)(24)GPIO8
 GND   (25)(26)GPIO7
```

---

# Complete GPIO Map

| GPIO | Pin | Function | Connected Device |
|-----|-----|----------|------------------|
| GPIO2 | Pin 3 | I²C SDA | SCD40 + DS3231 |
| GPIO3 | Pin 5 | I²C SCL | SCD40 + DS3231 |
| GPIO17 | Pin 11 | Encoder A | Rotary Encoder |
| GPIO27 | Pin 13 | Encoder B | Rotary Encoder |
| GPIO22 | Pin 15 | Encoder Button | Rotary Encoder |
| GPIO23 | Pin 16 | Back Button | Push Button |
| GPIO18 | Pin 12 | Snooze Button | Push Button |
| GPIO25 | Pin 22 | LCD DC | LCD Display |
| GPIO24 | Pin 18 | LCD RESET | LCD Display |
| GPIO10 | Pin 19 | SPI MOSI | LCD Display |
| GPIO11 | Pin 23 | SPI Clock | LCD Display |
| GPIO8 | Pin 24 | SPI CE0 | LCD Display |
| 3.3V | Pin 1/17 | Power | Sensors / LCD |
| GND | Multiple | Ground | All devices |

---

# I²C Bus Devices

The AirClock uses a shared I²C bus.

| Device | Address |
|------|------|
| SCD40 CO₂ sensor | `0x62` |
| DS3231 RTC | `0x68` |

Connections:

| Pi Pin | Device Pin |
|------|------|
| SDA (GPIO2) | SDA |
| SCL (GPIO3) | SCL |
| 3.3V | VDD |
| GND | GND |

---

# LCD Display Wiring

Display: **2.8" SPI TFT (ILI9341)**

| LCD Pin | Raspberry Pi Pin |
|------|------|
| VCC | 3.3V |
| GND | GND |
| CS | GPIO8 (CE0) |
| RESET | GPIO24 |
| DC | GPIO25 |
| MOSI | GPIO10 |
| SCK | GPIO11 |
| LED | 3.3V (always on) |

---

# Rotary Encoder Wiring

| Encoder Pin | Pi Connection |
|------|------|
| S1 | GPIO17 |
| S2 | GPIO27 |
| KEY | GPIO22 |
| VCC | 3.3V |
| GND | GND |

Actions:

| Action | Result |
|------|------|
| Rotate clockwise | Menu down |
| Rotate counter‑clockwise | Menu up |
| Press knob | Select |

---

# Push Buttons

### Back / Dismiss Button

| Button Leg | Connection |
|------|------|
| Leg 1 | GPIO23 |
| Leg 2 | GND |

### Snooze / Mode Button

| Button Leg | Connection |
|------|------|
| Leg 1 | GPIO18 |
| Leg 2 | GND |

Internal pull‑up resistors are enabled in software.

---

# Breadboard Layout Concept

```
+--------------------------------------+
| Breadboard                           |
|                                      |
| 3.3V Rail  -> Sensors / Encoder      |
| GND Rail   -> All components         |
|                                      |
| Rotary Encoder                       |
| Buttons                              |
| I²C Sensors                          |
+--------------------------------------+
```

---

# Audio Wiring

```
Raspberry Pi USB
        ↓
USB Audio Adapter
        ↓
3.5mm Speaker
```

Audio playback example:

```
aplay -D plughw:2,0 /usr/share/sounds/alsa/Front_Center.wav
```

---

# System Wiring Overview

+-----------------------+
| Raspberry Pi 3B       |
|                       |
| SPI → LCD Display     |
| I2C → SCD40 Sensor    |
| I2C → DS3231 RTC      |
| GPIO → Rotary Encoder |
| GPIO → Buttons        |
| USB → Audio Adapter   |
+-----------+-----------+
            |
            v
        Mini Speaker

---

# Power Distribution

```
5V Micro‑USB → Raspberry Pi
```

The Pi distributes **3.3V** to:

- LCD display
- SCD40 sensor
- RTC module
- Rotary encoder
- Buttons

---

# Debug Commands

Check I²C devices:

```
i2cdetect -y 1
```

Expected addresses:

```
0x62 → SCD40
0x68 → RTC
```

Check audio device:

```
aplay -l
```

---

# Future Hardware Expansion

| Device | Purpose |
|------|------|
| PMS5003 | PM2.5 particulate sensor |
| Light sensor | Auto brightness |
| RGB LED | Status indicator |
| LiPo UPS | Battery backup |
| Internal speaker | Case integration |

---

# Summary

AirClock hardware stack combines:

- SPI LCD display
- I²C environmental sensors
- GPIO controls
- USB audio output

This architecture keeps wiring simple while allowing future expansion.
