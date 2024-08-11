# MOOT
This repository has the code for the MOOT (Matter Out Of Time), a.k.a. "the time machine".

[MOOT is an interactive art installation built by Glass House Arts for Burning Man 2024](https://www.deldiosglasshouse.com/moot).

## Director

The basic steps for `director` are:

1. Read the distance input stream
2. Use that data to calculate mode, audio frequency, playback speed, and lighting parameters.
3. Pass relevant data to MQTT
4. Generate audio output

## Video Server

`video_server` picks up MQTT video playback parameters and uses them to scrub through video.  It will run as one 
video per computer, on Raspberry Pi 5s.

## Screen Saver

`screen_saver` is a Rasperry Pi dedicated to running two video streams, totally independent from above. The streams are:

1. Time delay webcam
2. https://scottdraves.com/bomb


# Install Notes

This uses Python 3, and you'll need to install the libraries in requirements.txt.

To run just get into the directory in the console and run `python main.py`

To make a PR I had to use `sudo apt install gh` to auth.

Also best to make a virtual environment.  On the pi:

```
cd ~
python3 -m venv moot
nano ~/.bashrc
```
Add `source ~/moot/bin/activate` and restart.

### MQTT
Mac:
`brew install mosquitto`
Pi:
`sudo apt-get install mosquitto mosquitto-clients`

To start: `mosquito`

### pyaudio

I had trouble using pip to install pyaudio on the mac.  The solution was [here](https://stackoverflow.com/questions/31236194/installing-pyaudio-for-python-3-on-os-x), including having to install the command line tools for Xcode.

I also need to install the dev version of portaudio.

`sudo apt-get install portaudio19-dev`

I get weird errors with one USB sound card on the Pi, but the other one works.

### Raspberry Pi

<s>Pip also failed on the Raspberry Pi for pygame, numpy, and others that need precompiled wheels.  The solution was to build the wheel locally.

`sudo apt-get install python3-<packagename>`</s> This was solved with venv.

I had to enable I2C Interface on Raspberry Pi, which is disabled by default: Start > Preferences > Raspberry Pi Configuration > Interfaces tab > I2C > Enabled

### nix/nixos
When using nix, all of the required packages are defined in flake.nix.  To get the developing enable nix flakes and run `nix develop`.

If using nixos, make sure the following option is enabled. `hardware.pulseaudio.enable = true;`

## Development notes

I tried a version that put opencv in a thread, and it really doesn't like that.


# Debugging

on director `i2cdetect -y 1` will show connected i2c devices

## Wifi router not getting internet?

`sudo ip r add default via 192.168.0.1 dev wlan0`