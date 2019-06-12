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

import time


def get_hints(language_code):
    if language_code.startswith('en_'):
        return ('turn on the light',
                'turn off the light',
                'blink the light',
                'goodbye',
                'who is jamie',
                'repeat after me',
                'countdown for ... minutes')
    return None

def locale_language():
    language, _ = locale.getdefaultlocale()
    return language

def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Assistant service example.')
    parser.add_argument('--language', default=locale_language())
    args = parser.parse_args()

    logging.info('Initializing for language %s...', args.language)
    hints = get_hints(args.language)
    client = CloudSpeechClient()
    with Board() as board:
        while True:
            if hints:
                logging.info('Say something, e.g. %s.' % ', '.join(hints))
            else:
                logging.info('Say something.')
            text = client.recognize(language_code=args.language,
                                    hint_phrases=hints)
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
                break
            elif 'who is jamie' in text:
                logging.info('Jamie is hereton friend')
            elif 'repeat after me' in text:
                # Remove "repeat after me" from the text to be repeated
                to_repeat = text.replace('repeat after me','', 1)
                aiy.voice.tts.say(to_repeat)
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

if __name__ == '__main__':
    main()