from IPython.display import display, Audio, SVG
from nltk.grammar import CFG, Nonterminal
from nltk.parse.generate import generate

import os
import random
import re
import subprocess
from uuid import uuid4


# ABC music notation, header defaults
HEADER = """
X: 1
%%titleleft 1
T: {title}
L: 1/16
Q: {tempo}
K: {key}
%%printtempo false
%%MIDI program 105"""

TEMPO = 130
KEY = 'D'


# Basic rules
rules = """
     16 -> 3 3 3 3 4
     12 -> 3 3 3 3
      8 -> 3 3 2
      4 -> melody string1 string5 string1
      3 -> melody string1 string5
      2 -> melody string1
string1 -> 'd'
string5 -> 'g'
 melody -> '{pitch}'
"""


def parse_abc(abc):
    out = []
    notes = re.findall(r"[_=^]*[a-gA-G][,']*[0-9]*", abc)
    for note in notes:
        number = re.search(r'\d+', note)
        duration = number.group() if number else '1'
        pitch  = re.search(r'\D+', note).group()
        out.append((pitch, duration))
    return out


def banjoify(rules, song):
    arrangement = []
    for pitch, duration in parse_abc(song):
        grammar = CFG.fromstring(
            rules.format(pitch=pitch))
        options = list(generate(grammar, 
            start=Nonterminal(duration)))
        phrase = random.choice(options)
        arrangement.append(''.join(phrase))
    return ' '.join(arrangement)


def play(abc, title='', lyrics='', tempo=TEMPO, key=KEY, 
         soundfont_path = './GeneralUser GS v1.471.sf2'):
    
    if not os.path.exists(soundfont_path):
        raise FileNotFoundError(f'Could not find {soundfont_path}')
    
    print(abc)
    header = HEADER.format(title=title, tempo=str(tempo), key=key)
    random_string = str(uuid4())
    abc_filename = random_string + '.abc'
    with open(abc_filename, 'w') as f:
        f.write('\n'.join([header, abc, lyrics]))

    svg_filename = 'Out001.svg'
    subprocess.run(['abcm2ps', '-g', abc_filename])
    display(SVG(svg_filename))
    
    midi_filename = random_string + '.mid'
    subprocess.run(['abc2midi', abc_filename, '-o', midi_filename])
    
    wav_filename = random_string + '.wav'
    subprocess.run(['fluidsynth', '-i', '-F', wav_filename, soundfont_path, midi_filename])        
    display(Audio(wav_filename))
           
    os.remove(abc_filename)     
    os.remove(svg_filename)
    os.remove(midi_filename)
    os.remove(wav_filename)
