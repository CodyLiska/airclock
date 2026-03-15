import subprocess

AUDIO_DEVICE = "plughw:2,0"
SOUND_FILE = "/usr/share/sounds/alsa/Front_Center.wav"

print("Playing test sound...")
subprocess.run(["aplay", "-D", AUDIO_DEVICE, SOUND_FILE], check=True)
print("Done.")
