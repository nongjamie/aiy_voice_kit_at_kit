#!/usr/bin/env python3
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A demo of the Google CloudSpeech recognizer."""
import argparse
import locale
import logging

from aiy.board import Board, Led
from aiy.cloudspeech import CloudSpeechClient
import aiy.voice.tts

# import
import time
from datetime import datetime

# multiprocess
from multiprocessing import Process

''' For playing the music '''
from pygame import mixer

''' For pi program close function '''
from subprocess import os

''' For pi shutdown function '''
from subprocess import call

# import
def get_hints(language_code):
    if language_code.startswith('en_'):
        return ('turn on the light',
                'turn off the light',
                'blink the light',
                'goodbye',
                'who is jamie',
                'repeat after me',
                'countdown for ... minutes',
                'do some programming',
                'shutdown')
    return None

def locale_language():
    language, _ = locale.getdefaultlocale()
    return language

# Greeting part of day
def greeting_part_of_day():
    currentDT = datetime.now().hour
    if 5 <= currentDT <= 11:
        return 1
    elif 12 <= currentDT <= 17:
        return 2
    elif 18 <= currentDT <= 22:
        return 3
    else: 
        return 4

# Play Music
def play_music(str):
    if (str == 'natural'):
        os.system('./music/natural.mp4')
    elif str == 'piano':
        # os.system('./music/piano-song.mp3')
        mixer.init()
        mixer.music.load('./music/piano_song.mp3')
        mixer.music.play()
    else:
        return 0

def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Assistant service example.')
    parser.add_argument('--language', default=locale_language())
    args = parser.parse_args()

    logging.info('Initializing for language %s...', args.language)
    hints = get_hints(args.language)
    client = CloudSpeechClient()

    # User name
    name_input = "jimmy"

    with Board() as board:
        while True:
            if hints:
                logging.info('Say something, e.g. %s.' % ', '.join(hints))
            else:
                logging.info('Say something.')
            
            # Greeting the user
            if name_input == '':
                greeting = greeting_part_of_day()
                if greeting == 1:
                    aiy.voice.tts.say("good morning, How may I call you")
                elif greeting == 2:
                    aiy.voice.tts.say("good afternoon, How may I call you")
                elif greeting == 3:
                    aiy.voice.tts.say("good evening, How may I call you")
                else:
                    aiy.voice.tts.say("good night, How may I call you")

            text = client.recognize(language_code=args.language,hint_phrases=hints)

            if text is None:
                logging.info('You said nothing.')
                continue

            logging.info('You said: "%s"' % text)
            text = text.lower()
            if 'turn on the light' in text:
                board.led.state = Led.ON
            elif 'turn off the light' in text:
                board.led.state = Led.OFF
            elif 'blink the light' in text:
                board.led.state = Led.BLINK
            elif 'goodbye' in text:
                # make reaction to voicekit while turn it off
                goodbye_string = 'Good bye' + name_input + ', See you again next time.'
                aiy.voice.tts.say(goodbye_string)
                goodbye_string = 'The program will close'
                aiy.voice.tts.say(goodbye_string)
                os.system('sudo service cloudspeech_demo stop')
                break
            elif 'shutdown' in text or 'shut down' in text:
                goodbye_string = 'Good bye' + name_input + ', See you again next time.'
                aiy.voice.tts.say(goodbye_string)
                shutdown_string = 'System will shutdown'
                aiy.voice.tts.say(shutdown_string)
                call('sudo poweroff', shell=True)
                break
            elif 'who is jamie' in text:
                aiy.voice.tts.say('Jamie is hereton friend.')
            elif 'repeat after me' in text:
                # Remove "repeat after me" from the text to be repeated
                to_repeat = text.replace('repeat after me','', 1)
                aiy.voice.tts.say(to_repeat)
            # Set the user name
            elif 'call me' in text:
                to_call = text.replace('call me', '')
                name_input = to_call
                to_call = 'Hello ' + to_call + ', What can I help you'
                aiy.voice.tts.say(to_call)
            elif 'countdown for' in text:
                to_do_code = text.replace('countdown for', '')
                to_do_code = to_do_code.replace('minutes', '')
                to_do_code = to_do_code.replace('minute', '')
                minute = int(to_do_code.strip())
                now = time.time()
                future = now + (minute * 60)
                while(future > now):
                    now = time.time()
                    continue
                aiy.voice.tts.say('Your countdown is over.')
            elif 'do some programming' in text:
                aiy.voice.tts.say('I will set the timer for you.')
                aiy.voice.tts.say('Which unit do you want, minute or hour')
                text = client.recognize(language_code=args.language,hint_phrases=hints)
                user_unit = ''
                user_timer = 0
                if 'minute' in text.lower():
                    user_unit = 'm'
                elif 'hour' in text.lower():
                    user_unit = 'h'
                else:
                    aiy.voice.tts.say('I do not know that units, please try again later.')
                    continue
                aiy.voice.tts.say('How long do you want to do programming in ' + text)
                text = client.recognize(language_code=args.language,hint_phrases=hints)
                try:
                    user_timer = int(text.strip())
                except:
                    aiy.voice.tts.say('The error occur, please try again')
                    continue
                aiy.voice.tts.say('Start timer')
                if user_unit == 'm':
                    time.sleep(60 * user_timer)
                else:
                    time.sleep(3600 * user_timer)
                aiy.voice.tts.say('Stop  timer, Your programming time is over. Please take a break.')
            elif 'play' or 'song' in text:
                # to_play = text.replace('play', '')
                # to_play = text.replace('song', '')
                # to_play = text.strip()
                # play_music('piano')
                p = Process(target = play_music, args = ('piano'))
                p.start()
                
if __name__ == '__main__':
    main()