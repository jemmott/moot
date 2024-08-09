import subprocess
import paho.mqtt.client as mqtt
import time
import threading
import random
import sys

class VLCMQTTController:
    def __init__(self):
        # Paths to the audio files
        self.active_audio_files = [
            "active 01.aif",
            "active 02.aif",
            "active 03.aif",
            "active 04.aif",
            "active 05.aif",
            "active 06.aif"
        ]
        self.background_audio_file = "standby.mp3"
        self.startup_audio_file = "startup.aif"
        self.shutdown_audio_file = "shutdown.aif"

        # MQTT settings
        self.mqtt_broker = "localhost"
        self.mqtt_topic = "moot/mode"

        # VLC command to start in remote control mode
        self.vlc_background_command = ["vlc", "--intf", "rc", "--loop", self.background_audio_file]

        # Initialize variables
        self.vlc_background_process = None
        self.vlc_active_process = None
        self.previous_active_file = None
        self.current_mode = "standby"
        self.volumes = {}  # Dictionary to track volumes for each VLC process

        # Start VLC for background audio
        self.start_background_audio()

        # MQTT setup
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        print(f"Connecting to MQTT broker: {self.mqtt_broker}", flush=True)
        self.client.connect(self.mqtt_broker, 1883, 60)
        print(f"Subscribing to MQTT topic: {self.mqtt_topic}", flush=True)
        self.client.subscribe(self.mqtt_topic)

        # Start the MQTT client loop
        self.client.loop_start()
        print("Started MQTT client loop", flush=True)

    def start_background_audio(self):
        print(f"Starting VLC for background audio: {self.background_audio_file}", flush=True)
        self.vlc_background_process = subprocess.Popen(
            self.vlc_background_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,  # Capture VLC output
            stderr=sys.stderr   # Redirect VLC error output to main Python stderr
        )
        self.volumes[self.vlc_background_process.pid] = 256  # Initial volume
        print(f"Started background VLC process with PID: {self.vlc_background_process.pid}", flush=True)

    def set_vlc_volume(self, vlc_process, volume):
        print(f"Setting VLC volume to {volume} for process {vlc_process.pid}", flush=True)
        vlc_process.stdin.write(f"volume {volume}\n".encode())
        vlc_process.stdin.flush()
        self.volumes[vlc_process.pid] = volume  # Update the local volume state

    def ramp_volume(self, vlc_process, target_volume, duration=1.0, steps=10, terminate=False):
        current_volume = self.volumes.get(vlc_process.pid, 256)
        print(f"Current volume for process {vlc_process.pid}: {current_volume}", flush=True)

        if current_volume == target_volume:
            print(f"Volume for process {vlc_process.pid} is already at {target_volume}, no ramping needed", flush=True)
            return

        print(f"Ramping volume to {target_volume} over {duration} seconds for process {vlc_process.pid}", flush=True)
        volume_step = (target_volume - current_volume) / steps
        step_duration = duration / steps
        for step in range(steps):
            current_volume += volume_step
            self.set_vlc_volume(vlc_process, int(current_volume))
            time.sleep(step_duration)

        if terminate:
            print(f"Terminating VLC process {vlc_process.pid} after ramping volume", flush=True)
            vlc_process.stdin.write("quit\n".encode())
            vlc_process.stdin.flush()
            vlc_process.wait()
            del self.volumes[vlc_process.pid]  # Remove the process from volume tracking

    def start_vlc_audio(self, audio_files, loop=False):
        print(f"Starting VLC for audio files: {audio_files}, loop={loop}", flush=True)
        command = ["vlc", "--intf", "rc"] + audio_files
        if loop:
            command.append("--loop")
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,  # Capture VLC output
            stderr=sys.stderr   # Redirect VLC error output to main Python stderr
        )
        self.volumes[process.pid] = 256  # Initial volume
        print(f"Started VLC process for {audio_files} with PID: {process.pid}", flush=True)
        return process

    def switch_to_random_active(self):
        selected_file = random.choice(self.active_audio_files)
        while selected_file == self.previous_active_file:
            selected_file = random.choice(self.active_audio_files)
        print(f"Switching to random active audio file: {selected_file}", flush=True)
        self.previous_active_file = selected_file
        if self.vlc_active_process:
            print(f"Terminating previous active audio process {self.vlc_active_process.pid}", flush=True)
            threading.Thread(target=self.ramp_volume, args=(self.vlc_active_process, 0, True)).start()
        self.vlc_active_process = self.start_vlc_audio([selected_file], loop=True)
        threading.Thread(target=self.ramp_volume, args=(self.vlc_active_process, 256)).start()

    def play_temporary_sound(self, audio_file, duration, ramp_delay=0, ramp_duration=5):
        print(f"Playing temporary sound: {audio_file}", flush=True)
        threading.Thread(target=self.ramp_volume, args=(self.vlc_background_process, 0)).start()  # Ramp down background audio
        temp_process = self.start_vlc_audio([audio_file])
        if ramp_delay > 0:
            time.sleep(ramp_delay)
            threading.Thread(target=self.ramp_volume, args=(self.vlc_background_process, 256, ramp_duration)).start()
        time.sleep(duration - ramp_delay)  # Wait for the rest of the duration
        temp_process.stdin.write("quit\n".encode())
        temp_process.stdin.flush()
        temp_process.wait()
        del self.volumes[temp_process.pid]

    def on_message(self, client, userdata, msg):
        mode = msg.payload.decode()

        if mode == self.current_mode:
            return  # No change in mode, do nothing

        print(f"Mode change detected: {self.current_mode} -> {mode}", flush=True)
        self.current_mode = mode

        if mode == "boot":
            self.switch_to_random_active()
        elif mode == "shutdown":
            if self.vlc_active_process:
                threading.Thread(target=self.ramp_volume, args=(self.vlc_active_process, 0, True)).start()  # Ramp down and terminate active audio
            self.play_temporary_sound(self.shutdown_audio_file, 30, ramp_delay=25, ramp_duration=10)  # 30 seconds for shutdown sound, ramp standby after 25 seconds with a 10-second ramp
        elif mode == "active":
            self.switch_to_random_active()
            threading.Thread(target=self.ramp_volume, args=(self.vlc_background_process, 0)).start()  # Ramp down background audio to mute
        else:
            if self.vlc_active_process:
                threading.Thread(target=self.ramp_volume, args=(self.vlc_active_process, 0, True)).start()  # Ramp down and terminate active audio
            threading.Thread(target=self.ramp_volume, args=(self.vlc_background_process, 256)).start()  # Ramp up background audio to full volume

if __name__ == "__main__":
    try:
        controller = VLCMQTTController()
        while True:
            time.sleep(1)  # Sleep to reduce CPU usage
    except KeyboardInterrupt:
        print("Exiting...", flush=True)
    finally:
        if controller.vlc_active_process:
            controller.vlc_active_process.stdin.write("quit\n".encode())
            controller.vlc_active_process.stdin.flush()
            controller.vlc_active_process.wait()
        if controller.vlc_background_process:
            controller.vlc_background_process.stdin.write("quit\n".encode())
            controller.vlc_background_process.stdin.flush()
            controller.vlc_background_process.wait()
        controller.client.loop_stop()
        controller.client.disconnect()

