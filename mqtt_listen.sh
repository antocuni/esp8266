#!/bin/bash
mosquitto_sub -h test.mosquitto.org -v -t "/antocuni/#" | ts
