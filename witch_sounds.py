import os
import pygame
import sys
from gpiozero import MotionSensor, LED
from pprint import pprint
from pygame.mixer import Sound, Channel
from time import sleep

playBackground = False
backgroundSoundPath = "/home/pi/witch_background_sound/witch_background.ogg"
scareSoundPath = "/home/pi/witch_scare/"
speechSoundPath = "/home/pi/witch_speech/"

scareSoundArr = []
speechSoundArr = []
pir = MotionSensor(4)
catGPIOOutput = LED(17)

checkForMotionDelay = 30
scareSoundIndex = 0

speechSoundIndex = 0
speechTimer = 0
speechTimeDelay = 2 * 60
speechVolume = 1

backgroundVolume = 0.3

catPlayCount = 0
maxCatPlayCount = 5

# Constants for sound channels
BACKGROUND = 0
SPEECH = 1
SCARE = 2

pygame.init()
pygame.mixer.init()

Channel(SPEECH).set_volume(speechVolume)

# For no background music, run this script with system arg[1] set to "false" 
try:
    sys.argv[1] and sys.argv[1] != "false"
except IndexError as e:
    playBackground = True

# If set to play background. Create background sound
if(playBackground != False):
    backgroundSound = Sound(backgroundSoundPath)

# walks through directory to get all .ogg files
def CreateList(list, path):
    for dirname, dirnames, filenames in os.walk(path):
        for filename in filenames:
            split = os.path.splitext(filename)

            if split[1] == ".ogg":
                list.append(Sound(path + filename))

    return list

# Populate scare and speech sound
scareSoundArr = CreateList(scareSoundArr, scareSoundPath)
speechSoundArr = CreateList(speechSoundArr, speechSoundPath)

if(playBackground != False):
    Channel(BACKGROUND).set_volume(backgroundVolume)
    Channel(BACKGROUND).play(backgroundSound, -1)

pprint("Ready")

def StartSpeech():
    global speechSoundIndex
    Channel(SPEECH).play(speechSoundArr[speechSoundIndex])
    speechSoundIndex = GetNextIndex(speechSoundIndex, speechSoundArr)

def StopSpeech():
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
    else:
        newIndex = 0

    return newIndex

def CheckForMotion():

    global scareSoundIndex
    global Sound
    global speechTimer
    global speechTimeDelay

    if pir.motion_detected:
        UpdateCat()
        StopSpeech()
        soundToPlay = StartScare(scareSoundIndex)
        scareSoundIndex = GetNextIndex(scareSoundIndex, scareSoundArr)
        
        soundLength = Sound.get_length(soundToPlay)

        sleep(checkForMotionDelay)

        StopScare()
    else:
        sleep(1)
        if speechTimer >= speechTimeDelay:
            StopSpeech()
            StartSpeech()
        else:
            speechTimer += 1
    
def UpdateCat():
    global catPlayCount
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
