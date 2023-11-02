# MOOT
This repository has the code for the MOOT (Matter Out Of Time), a.k.a. "the time machine".

[MOOT is an interactive art installation built by Glass House Arts for Burning Man 2024](https://www.deldiosglasshouse.com/moot).

The basic steps are:

- Read the audio input stream, which will be a theremin
- Estimate the dominant frequency
- Map that frequency to LED lighting effects (low tone -> red, high tone -> blue)
- Use the frequency to control VLC playback (low tone -> backwards in time, hight tone -> fast forward in time)

This will run on a Raspberry Pi.

## Notes

I had trouble using pip to install pyaudio on the mac.  The solution was [here](https://stackoverflow.com/questions/31236194/installing-pyaudio-for-python-3-on-os-x), including having to install the command line tools for Xcode.

Pip also failed on the Raspberry Pi for pygame, numpy, and others that need precompiled wheels.  The solution was to build the wheel locally.