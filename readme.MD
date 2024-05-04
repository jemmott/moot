# MOOT
This repository has the code for the MOOT (Matter Out Of Time), a.k.a. "the time machine".

[MOOT is an interactive art installation built by Glass House Arts for Burning Man 2024](https://www.deldiosglasshouse.com/moot).

The basic steps are:

1. Read the audio input stream, which will be a theremin
2. Estimate the dominant frequency (with moving average)
3. Map that audio frequency to LED lighting effects (low tone -> red, high tone -> blue)
4. Use the audio frequency to control video playback (low tone -> backwards in time, hight tone -> fast forward in time)

Goal is to run on a Raspberry Pi.

## To Do

- Get video control to work with threading
- Better mapping of frequency to video speed, and looping with underflow
- add distance sensor as input in addition to audio
- Control LED strip

## Notes

I had trouble using pip to install pyaudio on the mac.  The solution was [here](https://stackoverflow.com/questions/31236194/installing-pyaudio-for-python-3-on-os-x), including having to install the command line tools for Xcode.

Pip also failed on the Raspberry Pi for pygame, numpy, and others that need precompiled wheels.  The solution was to build the wheel locally.

`sudo apt-get install python3-pyaudio`

Also need to install the dev version of portaudio.

`sudo apt-get install portaudio19-dev`