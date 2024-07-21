# MOOT
This repository has the code for the MOOT (Matter Out Of Time), a.k.a. "the time machine".

[MOOT is an interactive art installation built by Glass House Arts for Burning Man 2024](https://www.deldiosglasshouse.com/moot).

The basic steps are:

1. Read the audio input stream, which will be a theremin
2. Estimate the dominant frequency (with moving average)
3. Map that audio frequency to LED lighting effects (low tone -> red, high tone -> blue)
4. Use the audio frequency to control video playback (low tone -> backwards in time, hight tone -> fast forward in time)

## To Do

- add distance sensor as input in addition to audio
- Control LED strip

## Install Notes

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
