# sumpPump
<p align="center">
	<img alt="GitHub language count" src="https://img.shields.io/github/languages/count/the-amaya/sumpPump?style=plastic">
	<img alt="GitHub top language" src="https://img.shields.io/github/languages/top/the-amaya/sumpPump?style=plastic">
	<img alt="GitHub code size in bytes" src="https://img.shields.io/github/languages/code-size/the-amaya/sumpPump?style=plastic">
	<img alt="GitHub license" src="https://img.shields.io/github/license/the-amaya/sumpPump?style=plastic">
	<img alt="GitHub contributors" src="https://img.shields.io/github/contributors/the-amaya/sumpPump?style=plastic">
	<img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/the-amaya/sumpPump?style=plastic">
</p>

A basic system to monitor my sump pump. The primary function is to alert me if my sump is going to over flow and flood my basement.

## Features!
- Alerts via webhook (specifically discord webhooks)
- Send alerts when the sump pump runs
- Track when the sump runs
- Send status updates at regular intervals with general statistics
- more to come and more already implemented that im forgetting about


## Wiring
The HC-SR04 sensor operates at 5v so we need a voltage divider to protect the GPIO on the rPi.
The procedure to calculate the R1 and R2 resistor values is beyond the scope of this readme but I have included two sets of default values.

- For the 5v and GND you can use any of the appropriate pins on the pi
- For the TRIG and ECHO you can use any available GPIO pins, you just need to update main.py accordingly.

```
┌─────────┐                    ┌─────────┐
│       ,.│ 5V                 │         │
│       .─┼────────────────────┼─VCC   H │
│       ..│                    │       C │
│rPi    ..│       ┌────────────┼─TRIG  - │
│       ..│ GPIO18│            │       S │
│GPIO   .─┼───────┘ ┌─R1───────┼─ECHO  R │
│       ..│ GPIO23  │          │       0 │
│Header .─┼─────────┴─R2────┬──┼─GND   4 │
│       ..│ GND             │  │         │
│       .─┼─────────────────┘  └─────────┘
│       ..│
│       ..│
│       ..│
│       ..│
│       ..│      R1: 1k & R2: 2k
│       ..│
│       ..│           -OR-
│       ..│
│       ..│      R1: 330 & R2: 470
│       ..│
│         │
└─────────┘
```

## Physical Setup
The sensor is placed in the end of a 2" PVC pipe that is 96cm long. The pipe is placed vertically down into my sump pit.
Water is able to enter the bottom of the pipe and the ping sensor sends a ping down from the top to measure
the disatance from the top of the pipe to the water level.

```
            ┌───┐
96cm        ├───┤ sensor
            │   │ ──────
            │   │
            │   │
            │   │
            │   │
            │   │
            │   │
63cm        │   │ top of basin
       ┌────┼───┼──────────────────┐
       │    │   │                  │
       │    │   │                  │
       │    │   │                  │
       │    │   │                  │
       │    │   │                  │
40cm   │    │   │ high water level │
       │    │   │ ──────────────── │
       │    │   │                  │
       │    │   │                  │
       │    │   │                  │
       │    │   │                  │
20cm   │    │   │ low water level  │
       │    │   │ ───────────────  │
       │    │   │                  │
       │    │   │                  │
       │    │   │                  │
       │    │   │                  │
       └────┴───┴──────────────────┘
```