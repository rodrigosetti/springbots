"""
This module has a function to generate a latim like name, but not latim at all
"""

from random import choice

#: Latim vogals sylabes
VOG = 'a e i o u ae ia au io oi'.split()

#: Latim consonants sylabes
CONS = 'b c d e f g h j l m p q r s t v x z pr gr st fr dr ph br'.split()

#: Latim consonants sylabes no to appear first
MIDCONS = 'mm pp cc tt mn rs ll'.split()

#: Latim optional terminations for words
TERM = 'um em'.split()

def latimname(sil=5):
    """
    Creates a latim like name with N sylabes.
    """
    word = ''
    vog = choice([True, False])
    for x in range(sil-1):
        word += choice(VOG) if vog else choice(CONS+MIDCONS if x>0 else CONS)
        vog = not vog

    if not vog:
        word += choice(CONS + MIDCONS)

    word += choice(TERM) if choice([True, False]) else choice(VOG)

    return word[0].upper() + word[1:]
