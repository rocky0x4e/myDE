#!/bin/bash
v=$(volume.sh get)
volume.sh 35
play -qn \
    synth 0.125 square 659.25   : \
    synth 0.125 square 659.25   : \
    synth 0.125 square 0        : \
    synth 0.125 square 659.25   : \
    synth 0.125 square 0        : \
    synth 0.125 square 523.25   : \
    synth 0.125 square 659.25   : \
    synth 0.125 square 0        : \
    synth 0.125 square 784.00   : \
    synth 0.125 square 0        : \
    synth 0.125 square 392.00
volume.sh $v