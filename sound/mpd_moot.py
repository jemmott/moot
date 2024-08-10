import subprocess
import time


class MPD:
    def __init__(self):
        pass

    def send_command(self, command):
        subprocess.run(["mpc"] + command.split())

    def play_files(self, file_paths):
        self.send_command("clear")
        [self.send_command(f"add {f}") for f in file_paths]
        self.send_command("play")

    def boot_active_sequence(self, active_file):
        self.send_command("single off")
        self.send_command("crossfade 0")
        self.play_files(["startup-10dB.wav", active_file, "shutdown.aif"])
        time.sleep(4)
        self.send_command("single on")

    def shutdown_sequence(self):
        self.send_command("crossfade 3")
        self.send_command("next")
        time.sleep(5)
        self.send_command("single off")

    def stop(self):
        self.send_command("stop")
        self.send_command("clear")


if __name__ == "__main__":
    try:
        mpd_manager = MPDManager()
        mpd_manager.play_active_sequence("active-03.aif")
        time.sleep(120)
    finally:
        pass
##        mpd_manager.stop()
