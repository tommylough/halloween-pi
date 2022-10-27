import sys
import pygame
import random
import os
from pygame.mixer import Sound, Channel
from gpiozero import MotionSensor, LED
from time import sleep
from pprint import pprint

playBackground = False
witchScarePath = "/home/pi/witch_scare/"
witchSpeechPath = "/home/pi/witch_speech/"
scareSoundArr = []
speechSoundArr = []
pir = MotionSensor(4)
catGPIOOutput = LED(17)

scareSoundIndex = 0
speechSoundIndex = 0

speechTimer = 0
speechTimeDelay = 5 * 60

catPlayCount = 0
maxCatPlayCount = 3

BACKGROUND = 0
SPEECH = 1
SCARE = 2

pygame.init()
pygame.mixer.init()


try:
    sys.argv[1] and sys.argv[1] != "false"
except IndexError as e:
    playBackground = True

# Create background sound
if(playBackground != False):
    backgroundAudioPath = "/home/pi/backgroundAudio/witch_background.ogg"
    backgroundAudio = Sound(backgroundAudioPath)

def CreateList(list, path):
    for dirname, dirnames, filenames in os.walk(path):
        # print path to all filenames.
        for filename in filenames:
            split = os.path.splitext(filename)

            pprint(path + filename)

            if split[1] == ".ogg":
                list.append(Sound(path + filename))

    return list

# Populate scare and speech audio
scareSoundArr = CreateList(scareSoundArr, witchScarePath)
speechSoundArr = CreateList(speechSoundArr, witchSpeechPath)

pprint("Ready")

if(playBackground != False):
    Channel(BACKGROUND).play(backgroundAudio, -1)
    Channel(BACKGROUND).set_volume(0.75)

def StartSpeech():
    global speechSoundIndex

    print("StartSpeech speechSoundIndex " + str(speechSoundIndex))

    Channel(SPEECH).play(speechSoundArr[speechSoundIndex])

    speechSoundIndex = GetNextIndex(speechSoundIndex, speechSoundArr)

def StopSpeech():
    print("StopSpeech")
    global speechTimer

    Channel(SPEECH).stop()
    speechTimer = 0

def StartScare(index):
    soundToPlay = scareSoundArr[index]
    Channel(SCARE).play(soundToPlay)
    return soundToPlay
    
def StopScare():
    Channel(SCARE).stop()

def GetNextIndex(index, list):
    newIndex = 0

    if index < len(list) - 1:
        newIndex = index + 1
        print(" newIndex = " + str(newIndex))
    else:
        newIndex = 0

    print("GetNextIndex index = " + str(index) + " newIndex = " + str(newIndex) + " len = " + str(len(list)))

    return newIndex

def CheckForMotion():

    global scareSoundIndex
    global Sound
    global speechTimer
    global speechTimeDelay

    if pir.motion_detected:
        print("Motion detected!")

        UpdateCat(catPlayCount)
        StopSpeech()
        soundToPlay = StartScare(scareSoundIndex)
        scareSoundIndex = GetNextIndex(scareSoundIndex, scareSoundArr)

        #print("CheckForMotion scareSoundIndex = " + str(scareSoundIndex))
        
        soundLength = Sound.get_length(soundToPlay)
        #print("length = " + str(soundLength))

        sleep(soundLength + 1.5)

        StopScare()
        
        print("Scare Finished")

        #StartSpeech()
        
        #soundToPlay = random.choice(scareSoundArr)
        #Channel(1).play(soundToPlay)
        # ensure playback has been fully completed before resuming motion detection, prevents "spamming" of sound
    else:
        sleep(1)
        if speechTimer >= speechTimeDelay:
            StopSpeech()
            StartSpeech()
        else:
            speechTimer += 1

        print("No Motion speechTimer : " + str(speechTimer) )
    
def UpdateCat(catPlayCount):
    if catPlayCount >= maxCatPlayCount:
        catGPIOOutput.on()
        sleep(1)
        catGPIOOutput.off()
        catPlayCount = 0
    else:
        catPlayCount += 1

StartSpeech()

while True:
    CheckForMotion()

