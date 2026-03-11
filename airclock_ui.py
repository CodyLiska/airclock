import json
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from threading import Thread, Lock

from gpiozero import RotaryEncoder, Button
from luma.core.interface.serial import spi
from luma.lcd.device import ili9341
from luma.core.render import canvas
from PIL import ImageFont

from sensirion_i2c_driver import LinuxI2cTransceiver, I2cConnection
from sensirion_i2c_scd import Scd4xI2cDevice

# ---------- Paths ----------
CONFIG_PATH = Path(__file__).parent / "config.json"

# ---------- Display ----------
serial = spi(port=0, device=0, gpio_DC=25, gpio_RST=24)
device = ili9341(serial, width=320, height=240, rotate=1)


def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

font_small = load_font(FONT_REG, 11)
font_body = load_font(FONT_REG, 14)
font_body_bold = load_font(FONT_BOLD, 14)
font_title = load_font(FONT_BOLD, 18)
font_clock = load_font(FONT_BOLD, 30)
font_big = load_font(FONT_BOLD, 24)

# ---------- Audio ----------
AUDIO_DEVICE = "plughw:2,0"
SOUND_FILE = "/usr/share/sounds/alsa/Front_Center.wav"

alarm_thread = None
alarm_stop_requested = False


def play_sound_once():
    try:
        subprocess.run(
            ["aplay", "-D", AUDIO_DEVICE, SOUND_FILE],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except Exception:
        pass


def _alarm_loop():
    global alarm_stop_requested
    while not alarm_stop_requested:
        play_sound_once()
        time.sleep(1.0)


def start_alarm_sound():
    global alarm_thread, alarm_stop_requested
    if alarm_thread is None or not alarm_thread.is_alive():
        alarm_stop_requested = False
        alarm_thread = Thread(target=_alarm_loop, daemon=True)
        alarm_thread.start()


def stop_alarm_sound():
    global alarm_stop_requested
    alarm_stop_requested = True


# ---------- Inputs ----------
enc = RotaryEncoder(a=17, b=27, max_steps=0)
btn_select = Button(22, pull_up=True, bounce_time=0.08)
btn_back = Button(23, pull_up=True, bounce_time=0.08)
btn_snooze = Button(5, pull_up=True, bounce_time=0.08)

last_steps = enc.steps
last_select = False
last_back = False
last_snooze = False

# ---------- Screens ----------
SCREEN_HOME = "home"
SCREEN_ALARM = "alarm"
SCREEN_POMODORO = "pomodoro"
SCREEN_AIR = "air"

current_screen = SCREEN_HOME

# ---------- Home menu ----------
home_menu_items = ["Pomodoro", "Alarm", "Air"]
home_menu_index = 0

# ---------- Pomodoro ----------
POMO_IDLE = "idle"
POMO_WORK = "work"
POMO_BREAK = "break"

pomodoro_mode = POMO_IDLE
pomodoro_running = False
pomodoro_work_minutes = 25
pomodoro_break_minutes = 5
pomodoro_end = None
pomodoro_cycles_completed = 0

pomodoro_menu_items = ["Work Minutes", "Break Minutes", "Start/Stop", "Save & Exit"]
pomodoro_menu_index = 0
pomodoro_edit_mode = False

# ---------- Sensor State ----------
sensor_lock = Lock()
co2_ppm = None
temp_c = None
humidity_rh = None
sensor_status = "Starting..."

# ---------- Alarm State ----------
alarm_enabled = False
alarm_hour = 7
alarm_minute = 0
alarm_ringing = False
alarm_snooze_until = None
last_alarm_trigger_minute = None

alarm_menu_items = ["Enabled", "Hour", "Minute", "Save & Exit"]
alarm_menu_index = 0
alarm_edit_mode = False

SNOOZE_MINUTES = 10


# ---------- Config ----------
def load_config():
    global alarm_enabled, alarm_hour, alarm_minute
    global pomodoro_work_minutes, pomodoro_break_minutes

    if not CONFIG_PATH.exists():
        return

    try:
        data = json.loads(CONFIG_PATH.read_text())
        alarm_enabled = bool(data.get("alarm_enabled", False))
        alarm_hour = int(data.get("alarm_hour", 7))
        alarm_minute = int(data.get("alarm_minute", 0))
        pomodoro_work_minutes = int(data.get("pomodoro_work_minutes", 25))
        pomodoro_break_minutes = int(data.get("pomodoro_break_minutes", 5))
    except Exception:
        pass


def save_config():
    data = {
        "alarm_enabled": alarm_enabled,
        "alarm_hour": alarm_hour,
        "alarm_minute": alarm_minute,
        "pomodoro_work_minutes": pomodoro_work_minutes,
        "pomodoro_break_minutes": pomodoro_break_minutes,
    }
    try:
        CONFIG_PATH.write_text(json.dumps(data, indent=2))
    except Exception:
        pass


# ---------- Sensor ----------
def sensor_loop():
    global co2_ppm, temp_c, humidity_rh, sensor_status

    try:
        with LinuxI2cTransceiver("/dev/i2c-1") as i2c_transceiver:
            scd4x = Scd4xI2cDevice(I2cConnection(i2c_transceiver))

            scd4x.stop_periodic_measurement()
            time.sleep(1)
            scd4x.start_periodic_measurement()
            sensor_status = "Measuring..."

            while True:
                time.sleep(5)
                co2, temperature, humidity = scd4x.read_measurement()

                with sensor_lock:
                    co2_ppm = co2.co2
                    temp_c = temperature.degrees_celsius
                    humidity_rh = humidity.percent_rh
                    sensor_status = "OK"

    except Exception:
        with sensor_lock:
            sensor_status = "Sensor error"


# ---------- Helpers ----------
def clamp_index(i, n):
    return i % n


def c_to_f(celsius):
    return (celsius * 9 / 5) + 32


def pomodoro_state_text():
    if pomodoro_mode == POMO_IDLE:
        return "Idle"
    if pomodoro_mode == POMO_WORK:
        return "Work"
    if pomodoro_mode == POMO_BREAK:
        return "Break"
    return "?"


def start_pomodoro_work():
    global pomodoro_running, pomodoro_mode, pomodoro_end
    pomodoro_running = True
    pomodoro_mode = POMO_WORK
    pomodoro_end = datetime.now() + timedelta(minutes=pomodoro_work_minutes)


def start_pomodoro_break():
    global pomodoro_running, pomodoro_mode, pomodoro_end, pomodoro_cycles_completed
    pomodoro_running = True
    pomodoro_mode = POMO_BREAK
    pomodoro_end = datetime.now() + timedelta(minutes=pomodoro_break_minutes)
    pomodoro_cycles_completed += 1


def stop_pomodoro():
    global pomodoro_running, pomodoro_mode, pomodoro_end
    pomodoro_running = False
    pomodoro_mode = POMO_IDLE
    pomodoro_end = None


def toggle_pomodoro():
    if pomodoro_running:
        stop_pomodoro()
    else:
        start_pomodoro_work()


def update_pomodoro_state():
    if not pomodoro_running or pomodoro_end is None:
        return

    remaining = pomodoro_end - datetime.now()
    if remaining.total_seconds() > 0:
        return

    play_sound_once()

    if pomodoro_mode == POMO_WORK:
        start_pomodoro_break()
    elif pomodoro_mode == POMO_BREAK:
        start_pomodoro_work()


def format_pomodoro_remaining():
    if not pomodoro_running or pomodoro_end is None:
        return "Idle"

    remaining = pomodoro_end - datetime.now()
    if remaining.total_seconds() < 0:
        remaining = timedelta(seconds=0)

    mins = int(remaining.total_seconds() // 60)
    secs = int(remaining.total_seconds() % 60)
    return f"{mins:02d}:{secs:02d}"


def co2_status_text(value):
    if value is None:
        return "..."
    if value < 800:
        return "Good"
    if value < 1200:
        return "Moderate"
    return "Poor"


def alarm_time_string():
    return f"{alarm_hour:02d}:{alarm_minute:02d}"


def trigger_alarm():
    global alarm_ringing
    if not alarm_ringing:
        alarm_ringing = True
        start_alarm_sound()


def dismiss_alarm():
    global alarm_ringing, alarm_snooze_until
    alarm_ringing = False
    alarm_snooze_until = None
    stop_alarm_sound()


def snooze_alarm():
    global alarm_ringing, alarm_snooze_until
    alarm_ringing = False
    alarm_snooze_until = datetime.now() + timedelta(minutes=SNOOZE_MINUTES)
    stop_alarm_sound()


def check_alarm():
    global last_alarm_trigger_minute

    now = datetime.now()
    current_minute_key = now.strftime("%Y-%m-%d %H:%M")

    if alarm_ringing:
        return

    if alarm_snooze_until is not None:
        if now >= alarm_snooze_until:
            trigger_alarm()
        return

    if not alarm_enabled:
        return

    if now.hour == alarm_hour and now.minute == alarm_minute:
        if last_alarm_trigger_minute != current_minute_key:
            trigger_alarm()
            last_alarm_trigger_minute = current_minute_key


def footer(draw, text):
    draw.rectangle((0, 222, 319, 239), outline=None, fill="black")
    draw.text((8, 225), text, fill="white", font=font_small)


# ---------- Drawing ----------
def draw_home_screen():
    now = datetime.now()
    time_str = now.strftime("%H:%M:%S")
    date_str = now.strftime("%a %b %d")

    with sensor_lock:
        current_co2 = co2_ppm
        current_temp = temp_c
        current_humidity = humidity_rh
        current_sensor_status = sensor_status

    with canvas(device) as draw:
        draw.text((10, 4), time_str, fill="white", font=font_clock)
        draw.text((12, 38), date_str, fill="white", font=font_body)

        if alarm_ringing:
            alarm_line = "Alarm: RINGING"
        elif alarm_snooze_until is not None:
            alarm_line = f"Alarm: Snoozed to {alarm_snooze_until.strftime('%H:%M')}"
        else:
            alarm_line = f"Alarm: {'On' if alarm_enabled else 'Off'} {alarm_time_string()}"

        draw.text((10, 58), alarm_line, fill="white", font=font_body)

        if pomodoro_mode == POMO_IDLE:
            pomo_line = "Pomodoro: Idle"
        else:
            pomo_line = f"Pomodoro: {pomodoro_state_text()} {format_pomodoro_remaining()}"

        draw.text((10, 76), pomo_line, fill="white", font=font_body)
        draw.text((10, 92), f"Cycles: {pomodoro_cycles_completed}", fill="white", font=font_body)

        if current_co2 is None:
            draw.text((10, 112), f"Air: {current_sensor_status}", fill="white", font=font_body)
        else:
            temp_f = c_to_f(current_temp)
            draw.text((10, 112), f"CO2: {current_co2} ppm ({co2_status_text(current_co2)})", fill="white", font=font_body)
            draw.text((10, 128), f"T: {temp_f:.1f} F   H: {current_humidity:.1f} %", fill="white", font=font_body)

        draw.text((10, 150), "Menu", fill="white", font=font_body_bold)

        y = 168
        for i, item in enumerate(home_menu_items):
            prefix = ">" if i == home_menu_index else " "
            draw.text((12, y), f"{prefix} {item}", fill="white", font=font_body)
            y += 16

        footer(draw, "Select=Open  Back=Dismiss")


def draw_alarm_screen():
    with canvas(device) as draw:
        draw.text((10, 8), "Alarm", fill="white", font=font_title)
        draw.text((10, 34), alarm_time_string(), fill="white", font=font_big)
        draw.text((120, 38), "On" if alarm_enabled else "Off", fill="white", font=font_body_bold)

        items = [
            f"Enabled: {'On' if alarm_enabled else 'Off'}",
            f"Hour: {alarm_hour:02d}",
            f"Minute: {alarm_minute:02d}",
            "Save & Exit",
        ]

        y = 78
        for i, item in enumerate(items):
            prefix = ">" if i == alarm_menu_index else " "
            suffix = " *" if alarm_edit_mode and i == alarm_menu_index else ""
            draw.text((12, y), f"{prefix} {item}{suffix}", fill="white", font=font_body)
            y += 24

        footer(draw, "Rotate/Edit  Select=Toggle")


def draw_pomodoro_screen():
    with canvas(device) as draw:
        draw.text((10, 8), "Pomodoro", fill="white", font=font_title)
        draw.text((10, 34), pomodoro_state_text(), fill="white", font=font_body_bold)
        draw.text((120, 30), format_pomodoro_remaining(), fill="white", font=font_big)

        start_stop_label = "Stop" if pomodoro_running else "Start"

        items = [
            f"Work Minutes: {pomodoro_work_minutes}",
            f"Break Minutes: {pomodoro_break_minutes}",
            f"{start_stop_label}",
            "Save & Exit",
        ]

        y = 78
        for i, item in enumerate(items):
            prefix = ">" if i == pomodoro_menu_index else " "
            suffix = " *" if pomodoro_edit_mode and i == pomodoro_menu_index else ""
            draw.text((12, y), f"{prefix} {item}{suffix}", fill="white", font=font_body)
            y += 24

        draw.text((12, 182), f"Cycles completed: {pomodoro_cycles_completed}", fill="white", font=font_body)

        footer(draw, "Rotate/Edit  Select=Start")


def draw_air_screen():
    with sensor_lock:
        current_co2 = co2_ppm
        current_temp = temp_c
        current_humidity = humidity_rh
        current_sensor_status = sensor_status

    with canvas(device) as draw:
        draw.text((10, 8), "Air Quality", fill="white", font=font_title)

        if current_co2 is None:
            draw.text((10, 40), current_sensor_status, fill="white", font=font_big)
        else:
            temp_f = c_to_f(current_temp)

            draw.text((10, 38), f"{current_co2} ppm", fill="white", font=font_big)
            draw.text((150, 46), co2_status_text(current_co2), fill="white", font=font_body_bold)

            draw.text((10, 86), "Temperature", fill="white", font=font_body_bold)
            draw.text((10, 104), f"{temp_f:.1f} F", fill="white", font=font_big)

            draw.text((150, 86), "Humidity", fill="white", font=font_body_bold)
            draw.text((150, 104), f"{current_humidity:.1f} %", fill="white", font=font_big)

        draw.text((10, 150), "CO2 Guide", fill="white", font=font_body_bold)
        draw.text((10, 168), "<800 Good", fill="white", font=font_body)
        draw.text((10, 184), "800-1200 Moderate", fill="white", font=font_body)
        draw.text((10, 200), ">1200 Poor", fill="white", font=font_body)

        footer(draw, "Back=Home")


def draw_screen():
    if current_screen == SCREEN_HOME:
        draw_home_screen()
    elif current_screen == SCREEN_ALARM:
        draw_alarm_screen()
    elif current_screen == SCREEN_POMODORO:
        draw_pomodoro_screen()
    elif current_screen == SCREEN_AIR:
        draw_air_screen()


# ---------- Input handlers ----------
def handle_encoder_home():
    global home_menu_index, last_steps

    steps = enc.steps
    if steps != last_steps:
        if steps > last_steps:
            home_menu_index = clamp_index(home_menu_index + 1, len(home_menu_items))
        else:
            home_menu_index = clamp_index(home_menu_index - 1, len(home_menu_items))
        last_steps = steps


def handle_encoder_alarm():
    global alarm_menu_index, last_steps, alarm_hour, alarm_minute

    steps = enc.steps
    if steps == last_steps:
        return

    delta = 1 if steps > last_steps else -1

    if alarm_edit_mode:
        if alarm_menu_index == 1:
            alarm_hour = (alarm_hour + delta) % 24
        elif alarm_menu_index == 2:
            alarm_minute = (alarm_minute + delta) % 60
    else:
        alarm_menu_index = clamp_index(alarm_menu_index + delta, len(alarm_menu_items))

    last_steps = steps


def handle_encoder_pomodoro():
    global pomodoro_menu_index, last_steps, pomodoro_work_minutes, pomodoro_break_minutes

    steps = enc.steps
    if steps == last_steps:
        return

    delta = 1 if steps > last_steps else -1

    if pomodoro_edit_mode:
        if pomodoro_menu_index == 0:
            pomodoro_work_minutes = max(1, min(120, pomodoro_work_minutes + delta))
        elif pomodoro_menu_index == 1:
            pomodoro_break_minutes = max(1, min(60, pomodoro_break_minutes + delta))
    else:
        pomodoro_menu_index = clamp_index(pomodoro_menu_index + delta, len(pomodoro_menu_items))

    last_steps = steps


def handle_buttons():
    global last_select, last_back, last_snooze
    global current_screen, alarm_edit_mode, alarm_enabled
    global alarm_menu_index
    global pomodoro_menu_index, pomodoro_edit_mode

    select_now = btn_select.is_pressed
    back_now = btn_back.is_pressed
    snooze_now = btn_snooze.is_pressed

    if snooze_now and not last_snooze:
        if alarm_ringing:
            snooze_alarm()
        elif current_screen == SCREEN_HOME:
            toggle_pomodoro()

    if back_now and not last_back:
        if alarm_ringing or alarm_snooze_until is not None:
            dismiss_alarm()
        elif current_screen == SCREEN_ALARM:
            if alarm_edit_mode:
                alarm_edit_mode = False
            else:
                save_config()
                current_screen = SCREEN_HOME
        elif current_screen == SCREEN_POMODORO:
            if pomodoro_edit_mode:
                pomodoro_edit_mode = False
            else:
                save_config()
                current_screen = SCREEN_HOME
        elif current_screen == SCREEN_AIR:
            current_screen = SCREEN_HOME

    if select_now and not last_select:
        if current_screen == SCREEN_HOME:
            selected_item = home_menu_items[home_menu_index]

            if selected_item == "Pomodoro":
                current_screen = SCREEN_POMODORO
                pomodoro_menu_index = 0
                pomodoro_edit_mode = False
            elif selected_item == "Alarm":
                current_screen = SCREEN_ALARM
                alarm_menu_index = 0
                alarm_edit_mode = False
            elif selected_item == "Air":
                current_screen = SCREEN_AIR

        elif current_screen == SCREEN_ALARM:
            if alarm_menu_index == 0:
                alarm_enabled = not alarm_enabled
            elif alarm_menu_index in (1, 2):
                alarm_edit_mode = not alarm_edit_mode
            elif alarm_menu_index == 3:
                save_config()
                alarm_edit_mode = False
                current_screen = SCREEN_HOME

        elif current_screen == SCREEN_POMODORO:
            if pomodoro_menu_index in (0, 1):
                pomodoro_edit_mode = not pomodoro_edit_mode
            elif pomodoro_menu_index == 2:
                toggle_pomodoro()
            elif pomodoro_menu_index == 3:
                save_config()
                pomodoro_edit_mode = False
                current_screen = SCREEN_HOME

    last_select = select_now
    last_back = back_now
    last_snooze = snooze_now


def handle_inputs():
    if current_screen == SCREEN_HOME:
        handle_encoder_home()
    elif current_screen == SCREEN_ALARM:
        handle_encoder_alarm()
    elif current_screen == SCREEN_POMODORO:
        handle_encoder_pomodoro()

    handle_buttons()


# ---------- Main ----------
def main():
    global last_steps

    load_config()
    last_steps = enc.steps

    thread = Thread(target=sensor_loop, daemon=True)
    thread.start()

    while True:
        check_alarm()
        update_pomodoro_state()
        handle_inputs()
        draw_screen()
        time.sleep(0.05)


if __name__ == "__main__":
    try:
        main()
    finally:
        stop_alarm_sound()
