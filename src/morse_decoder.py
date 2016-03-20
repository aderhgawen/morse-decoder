#!/usr/bin/env python
'''
Morse Code Decoder
Decodes morse code signals received by a coherer connected to a Beaglebone

Created by: Ashish Derhgawen
E-mail: ashish.derhgawen@gmail.com
Blog: http://ashishrd.blogspot.com
Last modified: 19 March, 2016
'''

import sys
import time
import Adafruit_BBIO.GPIO as GPIO

pin = "P9_12" # Connected to optoisolator

GPIO.setup(pin, GPIO.IN)

# Morse code parameters
dit_length = 0.05
dah_length = 3*dit_length

flag = False
pulse_processed = False
falling_edge_time = time.time()
pulse_duration = 0
rising_edge_time = 0
character_end_time = time.time()
character_start_time = time.time()

character_received = "";
sentence = ""

morse_dict = {'.-': 'A',     '-...': 'B',   '-.-.': 'C',
        '-..': 'D',    '.': 'E',      '..-.': 'F',
        '--.': 'G',    '....': 'H',   '..': 'I',
        '.---': 'J',   '-.-': 'K',    '.-..': 'L',
        '--': 'M',     '-.': 'N',     '---': 'O',
        '.--.': 'P',   '--.-': 'Q',   '.-.': 'R',
        '...': 'S',    '-': 'T',      '..-': 'U',
        '...-': 'V',   '.--': 'W',    '-..-': 'X',
        '-.--': 'Y',   '--..': 'Z',

        '-----': '0',  '.----': '1',  '..---': '2',
        '...--': '3',  '....-': '4',  '.....': '5',
        '-....': '6',  '--...': '7',  '---..': '8',
        '----.': '9'
        }

# Rising edge ISR
def edge_callback(pin):
    global flag
    global pulse_duration
    global falling_edge_time
    global rising_edge_time

    if not flag:
        rising_edge_time = time.time()
        flag = True

    GPIO.wait_for_edge(pin, GPIO.FALLING)
    falling_edge_time = time.time()
    pulse_duration = falling_edge_time - rising_edge_time


# Add rising edge interrupt
GPIO.add_event_detect(pin, GPIO.RISING, callback=edge_callback)

while True:
    if (pulse_processed and ((time.time() - falling_edge_time) >= dah_length)):
        # Character complete
        print "Received code: ", character_received
 
        char = morse_dict.get(character_received, '?')
        
        if (time.time() - character_end_time > 5):
            # End of sentence
            sentence = char
        elif (character_start_time - character_end_time >= (dit_length*20)):
            # Add a space
            sentence += " " + char
        else:
            # Add character to sentence
            sentence += char

        print sentence

        character_end_time = time.time()

        character_received = ""
        pulse_processed = False

    if (flag and ((time.time() - falling_edge_time) >= dit_length)):
        # New pulse recorded

        if not pulse_processed:
            character_start_time = time.time() # Record start time

        if (pulse_duration <= dah_length):
            character_received += "."
        else:
            character_received += "-"

        pulse_duration = 0
        pulse_processed = True
        flag = False

