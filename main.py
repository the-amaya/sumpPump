#!/usr/bin/python

import time
import RPi.GPIO as GPIO
import signal
import sys
from discord_webhook import DiscordWebhook

webhookurl = ''

trigger = 18
echo = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(trigger, GPIO.OUT)  # trigger
GPIO.setup(echo, GPIO.IN)  # echo
GPIO.output(trigger, False)

alarmlist = []
sentalarms = []
readsafe = [25, 30]
runtime = []
reads = [0, 0]


def signal_handler(signal, frame):
    GPIO.cleanup()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def water_level(marginsafety=0):
    reads[0] = reads[0] + 1
    time.sleep(2)
    GPIO.output(trigger, True)
    time.sleep(0.00001)
    GPIO.output(trigger, False)
    while GPIO.input(echo) == 0:
        pass
    start = time.time()
    while GPIO.input(echo) == 1:
        pass
    stop = time.time()
    elapsed = stop - start
    distance = elapsed * 34000
    distance = distance / 2
    waterdepth = 96 - round(distance, 2)
    margin = (2 * (abs(readsafe[0] - readsafe[1]) + 1) + marginsafety)
    if 39 < ((readsafe[0] + readsafe[1]) / 2) < 41 and 19 < waterdepth < 22:
        pass  # catch sudden drops from full to empty when the sump pump runs
    elif abs(waterdepth - readsafe[1]) > margin:  # otherwise we may reject reads until the margin increases enough
        reads[1] = reads[1] + 1
        ms = marginsafety + 1
        brf = open("/dev/shm/bad_read.txt", "a")
        brf.write(str(time.time()) + ' ' + str(waterdepth) + ' ' + str(readsafe) + ' ' + str(margin) + '\n')
        brf.close()
        waterdepth = water_level(marginsafety=ms)
    readsafe.append(waterdepth)
    while len(readsafe) > 2:
        readsafe.pop(0)
    if waterdepth < 15:
        alarm(waterdepth, 'low')
    elif waterdepth > 45:
        alarm(waterdepth, 'high')
    return waterdepth


def one_minute():
    start = time.time()
    seta = [water_level()]
    rt = round((reads[1] / reads[0]) * 100, 2)
    while time.time() < start + 59:
        seta.append(water_level())
    return round(sum(seta) / len(seta), 1), seta, rt


def alarm(waterdepth, alarmtype):
    alarmlist.append([time.time(), waterdepth, alarmtype])
    if len(alarmlist) > 2:
        if len(sentalarms) > 0:  # an alarm has been sent already, check how recently
            if time.time() - 600 < sentalarms[-1][0]:  # an alarm was sent within the past 10 minutes
                return
        if time.time() - 60 < alarmlist[-3][0]:  # if this function has been called 3 times in the last minute
            if alarmtype == 'low':
                msg = f"low water level alert from the sump pump. if you are receiving this alert then the water " \
                      f"level is somehow reading lower than what should be possible, the last three readings are " \
                      f"{alarmlist[-3][1]}, {alarmlist[-2][1]}, {alarmlist[-1][1]}."
            elif alarmtype == 'high':
                msg = f"high water level. the sump pump is reporting a high water level. the last 3 readings are " \
                      f"{alarmlist[-3][1]}, {alarmlist[-2][1]}, {alarmlist[-1][1]}. " \
                      f"high level alerts are triggered above 45cm. the top of the basin is 63cm."
            else:
                msg = f"how could this happen to me"
            sentalarms.append([time.time(), alarmtype])
            discord_message(msg)
    return


def discord_message(msg):
    webhook = DiscordWebhook(url=webhookurl, content=msg)
    response = webhook.execute()
    return


if __name__ == '__main__':
    state = 0
    currentlevel = one_minute()[0]
    discord_message(f'Hello! I am now monitoring your sump pump! The current depth is {currentlevel}cm')
    starttime = time.time()
    statustime = time.time()
    while True:
        currentlevel, raw, ratio = one_minute()
        if state == 0 and currentlevel > 35:
            state = 1
        if state == 1 and currentlevel < 33:
            runtime.append(time.time())
            mss = f'I believe I just detected the sump pump running. ' \
                  f'I have detected the pump running {len(runtime)} times since I started this monitoring session. ' \
                  f'This is an average of {round(len(runtime) / ((time.time() - starttime) / (60 * 60)))} runs per ' \
                  f'hour or {round(len(runtime) / ((time.time() - starttime) / (60 * 60 * 24)))} runs per hour day.'
            discord_message(mss)
            state = 0
        f = open("/dev/shm/one_minute.txt", "a")
        txt = f'current depth {str(currentlevel)}, bad reads since starting {ratio}%, ' \
              f'total number of runs since starting {len(runtime)}'
        f.write(txt + '\n')
        f.close()
        if statustime < time.time() - (60 * 60 * 24):
            updm = f'Hello! I just wanted to update and let you know that I am still monitoring the sump pump. ' \
                   f'The current water level is {currentlevel}cm.'
            updn = f'I have read the water level {reads[0]} times, of which {reads[1]} have been ' \
                   f'rejected as erroneous, a percentage of {ratio}%'
            mss = f'I have detected the pump running {len(runtime)} times since I started this monitoring session. ' \
                  f'This is an average of {round(len(runtime) / ((time.time() - starttime) / (60 * 60)))} runs per ' \
                  f'hour or {round(len(runtime) / ((time.time() - starttime) / (60 * 60 * 24)))} runs per hour day.'
            for i in (updm, updn, mss):
                discord_message(i)
            statustime = time.time()
