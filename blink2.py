import time
import keyboard
from pysmu import Session

# -----------------------------
# ADALM1000 PIO0 Clock Generator
# -----------------------------

# Create session
session = Session(ignore_dataflow=True)

if not session.devices:
    raise RuntimeError("No ADALM1000 found.")

dev = session.devices[0]

# PIO0
PIO = 28

# USB GPIO commands
GPIO_LOW = 0x50
GPIO_HIGH = 0x51

# Frequency settings
freq = 3.0
MIN_FREQ = 0.5
MAX_FREQ = 10000000000000000000000.0

STEP_FINE = 1
STEP_COARSE = 5.0

run_mode = True

print("====================================")
print(" ADALM1000 PIO0 Clock Generator")
print("====================================")
print("RUN MODE")
print("  ↑ : +0.5 Hz")
print("  ↓ : -0.5 Hz")
print("  → : +2 Hz")
print("  ← : -2 Hz")
print("  Enter : Step Mode")
print("  Esc : Quit")
print()
print("STEP MODE")
print("  Space : One clock pulse")
print("  Esc : Return to Run Mode")
print("------------------------------------")
print(f"Frequency: {freq:.1f} Hz")

try:
    while True:

        if run_mode:

            # ----- Enter Step Mode -----
            if keyboard.is_pressed("enter"):
                run_mode = False
                print("\n\n*** STEP MODE ***")
                # Make sure output starts LOW
                dev.ctrl_transfer(0x40, GPIO_LOW, PIO, 0, 0, 0, 100)
                time.sleep(0.3)
                continue

            # ----- Frequency Controls -----
            if keyboard.is_pressed("right"):
                freq = min(MAX_FREQ, freq + STEP_COARSE)
                print(f"\rFrequency: {freq:.1f} Hz      ", end="", flush=True)
                time.sleep(0.15)

            elif keyboard.is_pressed("left"):
                freq = max(MIN_FREQ, freq - STEP_COARSE)
                print(f"\rFrequency: {freq:.1f} Hz      ", end="", flush=True)
                time.sleep(0.15)

            elif keyboard.is_pressed("up"):
                freq = min(MAX_FREQ, freq + STEP_FINE)
                print(f"\rFrequency: {freq:.1f} Hz      ", end="", flush=True)
                time.sleep(0.15)

            elif keyboard.is_pressed("down"):
                freq = max(MIN_FREQ, freq - STEP_FINE)
                print(f"\rFrequency: {freq:.1f} Hz      ", end="", flush=True)
                time.sleep(0.15)

            elif keyboard.is_pressed("esc"):
                break

            # ----- Clock Output -----
            half_period = 1.0 / (2.0 * freq)

            dev.ctrl_transfer(0x40, GPIO_HIGH, PIO, 0, 0, 0, 100)
            time.sleep(half_period)

            dev.ctrl_transfer(0x40, GPIO_LOW, PIO, 0, 0, 0, 100)
            time.sleep(half_period)

        else:
            # ==========================
            # STEP MODE
            # ==========================

            if keyboard.is_pressed("esc"):
                run_mode = True
                print("\n*** RUN MODE ***")
                print(f"Frequency: {freq:.1f} Hz")
                time.sleep(0.3)
                continue

            if keyboard.is_pressed("space"):
                # One complete clock pulse
                dev.ctrl_transfer(0x40, GPIO_HIGH, PIO, 0, 0, 0, 100)
                time.sleep(0.05)
                dev.ctrl_transfer(0x40, GPIO_LOW, PIO, 0, 0, 0, 100)

                print(".", end="", flush=True)

                # Wait for key release
                while keyboard.is_pressed("space"):
                    time.sleep(0.01)

            time.sleep(0.01)

finally:
    dev.ctrl_transfer(0x40, GPIO_LOW, PIO, 0, 0, 0, 100)
    print("\nStopped.")