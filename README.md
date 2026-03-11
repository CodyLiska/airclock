# Airclock

A Raspberry Pi-powered desk clock with an alarm, Pomodoro timer, and live air quality display. Controlled entirely via a rotary encoder and three physical buttons - no touchscreen, no network required.

![Hardware: ILI9341 display, rotary encoder, SCD40 sensor]

## Features

- **Clock** - time and date on the home screen at all times
- **Alarm** - set hour/minute, enable/disable, snooze (10 min), dismiss
- **Pomodoro timer** - configurable work/break intervals, cycle counter, start/stop from home screen
- **Air quality** - CO2 (ppm), temperature (°F), and humidity (%) via SCD40 sensor

## Hardware

| Component | Part                                             |
| --------- | ------------------------------------------------ |
| SBC       | Raspberry Pi (any model with SPI, I2C, GPIO)     |
| Display   | ILI9341 2.8" SPI TFT (320×240)                   |
| Encoder   | KY-040 rotary encoder                            |
| Buttons   | 3× momentary push buttons (Select, Back, Snooze) |
| Sensor    | Sensirion SCD40 (CO2, temp, humidity) via I2C    |
| Audio     | USB audio adapter + speaker                      |

## Wiring

### ILI9341 Display (SPI0)

| Display Pin | Pi Pin       |
| ----------- | ------------ |
| VCC         | 3.3V         |
| GND         | GND          |
| CS          | GPIO 8 (CE0) |
| RESET       | GPIO 24      |
| DC          | GPIO 25      |
| MOSI        | GPIO 10      |
| SCK         | GPIO 11      |
| LED         | 3.3V         |

### Rotary Encoder

| Encoder Pin | Pi GPIO      |
| ----------- | ------------ |
| CLK (A)     | GPIO 17      |
| DT (B)      | GPIO 27      |
| SW          | - (not used) |

### Buttons (all pulled up, active low)

| Button | Pi GPIO |
| ------ | ------- |
| Select | GPIO 22 |
| Back   | GPIO 23 |
| Snooze | GPIO 5  |

### SCD40 Sensor (I2C-1)

| Sensor Pin | Pi Pin       |
| ---------- | ------------ |
| VDD        | 3.3V         |
| GND        | GND          |
| SDA        | GPIO 2 (SDA) |
| SCL        | GPIO 3 (SCL) |

## Installation

### 1. Enable SPI and I2C

```bash
sudo raspi-config
# Interface Options → SPI → Enable
# Interface Options → I2C → Enable
```

### 2. Install system dependencies

```bash
sudo apt update
sudo apt install python3-pip python3-venv fonts-dejavu alsa-utils
```

### 3. Install Python dependencies

```bash
pip3 install -r requirements.txt
```

### 4. Configure audio device

List available devices to find your USB audio adapter:

```bash
aplay -l
```

Edit `AUDIO_DEVICE` in `airclock_ui.py` if your device index differs from `plughw:2,0`.

### 5. Run manually

```bash
python3 airclock_ui.py
```

### 6. Run on boot (systemd)

```bash
cp airclock.service.example airclock.service
# Edit airclock.service and replace YOUR_USER with your username and update the path
sudo cp airclock.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable airclock
sudo systemctl start airclock
```

## Usage

| Control        | Action                                            |
| -------------- | ------------------------------------------------- |
| Rotate encoder | Navigate menu / adjust value                      |
| Select button  | Confirm / enter edit mode                         |
| Back button    | Cancel / go back / dismiss alarm                  |
| Snooze button  | Snooze alarm (10 min) / toggle Pomodoro from home |

Settings (alarm time, Pomodoro durations) are saved to `config.json` when you choose **Save & Exit** from any settings screen.

## Hardware Tests

Individual component test scripts are in `airclock-docs/`:

```bash
python3 airclock-docs/display_test.py   # SPI display
python3 airclock-docs/encoder_test.py   # Rotary encoder
python3 scd40_test.py                   # SCD40 sensor
python3 audio_test.py                   # Audio output
```

## License

MIT - see [LICENSE](LICENSE)
