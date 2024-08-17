import subprocess
import paho.mqtt.client as mqtt
import time
import threading
import random
import sys
import mpd_moot


class VLCMQTTController:
    def __init__(self):
        # Paths to the audio files
        self.active_audio_files = [
            "active-01.aif",
            "active-02.aif",
            "active-03.aif",
            "active-04.aif",
            "active-05.aif",
            "active-06.aif",
        ]
        self.standby_audio_file = "standby.mp3"
        self.startup_audio_file = "startup.aif"
        self.shutdown_audio_file = "shutdown.aif"

        # MQTT settings
        self.mqtt_broker = "192.168.0.200"
        self.mqtt_topic = "moot/mode"

        # VLC command to start in remote control mode
        self.vlc_standby_command = [
            "vlc",
            "--intf",
            "rc",
            # "--aout", "pulse",  # Use PulseAudio
            "--aout=alsa", "--alsa-audio-device=hw:3,0",  # Use ALSA
            "--loop",
            self.standby_audio_file,
        ]

        # Initialize variables
        self.vlc_standby_process = None
        self.previous_active_file = None
        self.current_mode = "standby"
        self.volumes = {}  # Dictionary to track volumes for each VLC process

        # Start VLC for standby audio
        self.start_standby_audio()

        # MPD for interactive audio
        self.mpd = mpd_moot.MPD()

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

    def start_standby_audio(self):
        print(f"Starting VLC for standby audio: {self.standby_audio_file}", flush=True)
        self.vlc_standby_process = subprocess.Popen(
            self.vlc_standby_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,  # Capture VLC output
            stderr=sys.stderr,  # Redirect VLC error output to main Python stderr
        )
        self.set_vlc_volume(self.vlc_standby_process, 256)
        print(
            f"Started standby VLC process with PID: {self.vlc_standby_process.pid}",
            flush=True,
        )

    def set_vlc_volume(self, vlc_process, volume):
        print(
            f"Setting VLC volume to {volume} for process {vlc_process.pid}", flush=True
        )
        vlc_process.stdin.write(f"volume {volume}\n".encode())
        vlc_process.stdin.flush()
        self.volumes[vlc_process.pid] = volume  # Update the local volume state

    def ramp_volume(
        self, vlc_process, target_volume, duration=1.0, steps=10, terminate=False
    ):
        current_volume = self.volumes.get(vlc_process.pid, 256)
        print(
            f"Current volume for process {vlc_process.pid}: {current_volume}",
            flush=True,
        )

        if current_volume == target_volume:
            print(
                f"Volume for process {vlc_process.pid} is already at {target_volume}, no ramping needed",
                flush=True,
            )
            return

        print(
            f"Ramping volume to {target_volume} over {duration} seconds for process {vlc_process.pid}",
            flush=True,
        )
        volume_step = (target_volume - current_volume) / steps
        step_duration = duration / steps
        for step in range(steps):
            current_volume += volume_step
            self.set_vlc_volume(vlc_process, int(current_volume))
            time.sleep(step_duration)

        if terminate:
            print(
                f"Terminating VLC process {vlc_process.pid} after ramping volume",
                flush=True,
            )
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
            stderr=sys.stderr,  # Redirect VLC error output to main Python stderr
        )
        self.volumes[process.pid] = 256  # Initial volume
        print(
            f"Started VLC process for {audio_files} with PID: {process.pid}", flush=True
        )
        return process

    def boot_random_active(self):
        selected_file = random.choice(self.active_audio_files)
        while selected_file == self.previous_active_file:
            selected_file = random.choice(self.active_audio_files)
        print(f"Starting interactivity playlist: {selected_file}", flush=True)
        self.previous_active_file = selected_file
        self.mpd.boot_active_sequence(selected_file)

    def on_message(self, client, userdata, msg):
        mode = msg.payload.decode()

        if mode == self.current_mode:
            return  # No change in mode, do nothing

        if mode not in ["boot", "shutdown", "active", "standby"]:
            print(f"ignoreing weird mode '{mode}'")
            return

        t = f"{self.current_mode} -> {mode}"
        if t not in [
            "standby -> boot",
            "boot -> standby",
            "boot -> active",
            "active -> shutdown",
            "shutdown -> active",
            "shutdown -> standby",
        ]:
            print(f"WARNING: illegal transition {t}", flush=True)
        else:
            print(f"Changing modes: {t}", flush=True)
        self.current_mode = mode

        if mode == "boot":
            threading.Thread(
                target=self.ramp_volume, args=(self.vlc_standby_process, 0)
            ).start()  # Ramp down standby audio to mute
            threading.Thread(
                target=self.boot_random_active
            ).start()  # Tell MPD to start playlist
        elif mode == "active":
            # boot -> active transition happens automatically in MPD
            pass
        elif mode == "shutdown":
            self.mpd.shutdown_sequence()
        elif mode == "standby":
            # TODO stop mpd? playlist should have terminated automatically
            threading.Thread(
                target=self.ramp_volume, args=(self.vlc_standby_process, 256, 5, 50)
            ).start()  # Ramp up standby audio to full volume

    def stop_all(self):
        self.mpd.stop()
        if self.vlc_standby_process:
            self.vlc_standby_process.stdin.write("quit\n".encode())
            self.vlc_standby_process.wait()
        self.client.loop_stop()
        self.client.disconnect()


if __name__ == "__main__":
    try:
        controller = VLCMQTTController()
        while True:
            time.sleep(1)  # Sleep to reduce CPU usage
    except KeyboardInterrupt:
        print("Exiting...", flush=True)
    finally:
        controller.stop_all()
