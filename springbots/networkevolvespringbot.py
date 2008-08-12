"""
This module contains the NetworkEvolveSpringbot class, it inherits
both NetworkSpringbot and EvolveSpringbot to create a springbot which
is evolvable and network aware
"""

from networkspringbot import NetworkSpringbot
from evolvespringbot import EvolveSpringbot

class NetworkEvolveSpringbot(NetworkSpringbot, EvolveSpringbot):
	"""
	This is a double heritage of a network and an evolvable
	springbot into a class which does both
	"""

	def __init__(self, *args, **kargs):

		EvolveSpringbot.__init__(self, *args, **kargs)

