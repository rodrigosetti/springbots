"""
This module has a function to generate a latim like name, but not latim at all
"""

from string import upper
from random import choice

#: Latim vogals sylabes
VOG = ['a', 'e', 'i', 'o', 'u', 'ae', 'ia', 'au', 'io', 'oi']

#: Latim consonants sylabes
CONS = ['b', 'c', 'd', 'e', 'f', 'g', 'h', 'j', 'l', 'm', 'p', 'q', 'r', 's', 't',
                'v', 'x', 'z', 'pr', 'gr', 'st', 'fr', 'dr', 'ph', 'br']

#: Latim consonants sylabes no to appear first
MIDCONS = ['mm', 'pp', 'cc', 'tt', 'mn', 'rs', 'll']

#: Latim optional terminations for words
TERM = ['um', 'em']

def latimname(sil=5):
    """
    Creates a latim like name with N sylabes.
    """
    word = ''
    vog = choice([True, False])
    for x in xrange(sil-1):
        if vog:
            word += choice(VOG)
        else:
            word += choice(CONS+MIDCONS if x>0 else CONS)
        vog = not vog


    if not vog:
        word += choice(CONS + MIDCONS)

    if choice([True, False]):
        word += choice(TERM)
    else:
        word += choice(VOG)

    return upper(word[0]) + word[1:]
