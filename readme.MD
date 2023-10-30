# MOOT
This repository has the code for the MOOT (Matter Out Of Time), a.k.a. "the time machine".

MOOT is an interactive art installation built by Glass House Arts for Burning Man 2024.

The basic steps are:

- Read the audio input stream, which will be a theremin
- Estimate the dominant frequency
- Map that frequency to LED lighting effects (low tone -> red, high tone -> blue)
- Use the frequency to control VLC playback (low tone -> backwards in time, hight tone -> fast forward in time)

This will run on a Raspberry Pi.