import pygame
from pygame.mixer import Sound
from gpiozero import MotionSensor, LED
from time import sleep
#import RPi.GPIO as GPIO
import random
import os
from pprint import pprint



pygame.init()
pygame.mixer.init()
#load a sound file, same directory as script (no mp3s)

sounds = []


prependStr = "/home/pi/witches/"

for dirname, dirnames, filenames in os.walk('/home/pi/witches'):

    # print path to all filenames.
    for filename in filenames:
        split = os.path.splitext(filename)

        pprint(prependStr + filename)

        if split[1] == ".ogg":
            #sounds.append(prependStr + filename)
            sounds.append(pygame.mixer.Sound(prependStr + filename))


pprint(sounds)
pprint("Ready")

pir = MotionSensor(4)
cat = LED(17)
count = 0
maxCount = 3

while True:
    if pir.motion_detected:
        print("Motion detected!")
        soundToPlay = random.choice(sounds)
        soundLength = Sound.get_length(soundToPlay)
        soundToPlay.play()

        print("length = " + str(soundLength))
        if count == maxCount:
            cat.on()
            sleep(1)
            cat.off()
            count = 0
        else:
            count += 1

        # ensure playback has been fully completed before resuming motion detection, prevents "spamming" of sound
        sleep(soundLength + 1.5)
        soundToPlay.stop()
        print("Done")

   # else:
        # print ("No motion")
