"""
Tests springbot's fitness for specific tasks:

walk: optimizes maximum horizontal difference of mass center before and after simulation
jump: optimizes maximum mass center height achieved compared with initial height
equilibrium: optimizes maximum mass center height percentage over body's height
height: optimizes maximum aspect ratio of body favoring height
swim: optimizes maximium difference of mass center before and after in a liquid enviroment
"""

# We need vector and gear to calculate some stuff
from vector import Vector
from gear import *

try:
	import pygame
	HAS_PYGAME = True
except ImportError:
	HAS_PYGAME = False

#                                                                              #
################################################################################
#                                                                              #

def walk(springbot, width, height, enable_graphics=False, simulation_time=1000):
	"""
	Rewards maximum horizontal difference of mass center position before and after simulation
	"""

	# Center springbot horizontaly ant touches ground
	if len(springbot['bloodline'].split('.')) == 1:
		springbot.centerGround(height)
	
	# Selects its mass center
	start_x, start_y = springbot.massCenter()

	if enable_graphics and HAS_PYGAME:
		ticks = 0
		screen = pygame.display.get_surface()

	# Starts the simulation
	for i in xrange(simulation_time):
		if enable_graphics and HAS_PYGAME:		
			springbot.draw(screen, ticks, track_x=True, extrainfo="evolving for walk")
			pygame.display.flip()	# Show display
			ticks += 1

			for event in pygame.event.get():
				if event.type == pygame.QUIT or \
				(event.type == pygame.KEYDOWN and event.key == 27):	
					raise KeyboardInterrupt

		springbot.refresh()
		springbot.colideWall(height, DOWN)

	# Selects its mass center now
	end_x, end_y = springbot.massCenter()

	# Returns the horizontal distance traveled(fitness)
	return abs(end_x - start_x)

#                                                                              #
################################################################################
#                                                                              #

def jump(springbot, width, height, enable_graphics=False, simulation_time=500):
	"""
	Rewards maximum mass center height achieved compared with initial height
	"""

	# Center springbot horizontaly ant touches ground
	if len(springbot['bloodline'].split('.')) == 1:
		springbot.centerGround(height)
	
	# Selects its mass center
	start_x, start_y = springbot.massCenter()
	min_y = start_y

	if enable_graphics and HAS_PYGAME:
		ticks = 0
		screen = pygame.display.get_surface()

	# Starts the simulation
	for i in xrange(simulation_time):
		if enable_graphics and HAS_PYGAME:		
			springbot.draw(screen, ticks, extrainfo="evolving for jump")
			pygame.display.flip()	# Show display
			ticks += 1

			for event in pygame.event.get():
				if event.type == pygame.QUIT or \
				(event.type == pygame.KEYDOWN and event.key == 27):	
					raise KeyboardInterrupt

		# Calculates its mass center
		cx, cy = springbot.massCenter()
		min_y = min(min_y, cy)

		springbot.refresh()
		springbot.colideWall(height, DOWN)

	# Returns the maximal height achieved
	return abs(min_y - start_y)

#                                                                              #
################################################################################
#                                                                              #

def equilibrium(springbot, width, height, enable_graphics=False, simulation_time=600):
	"""
	Rewards maximum average mass center height percentage over body's height
	"""

	# Center springbot horizontaly ant touches ground
	if len(springbot['bloodline'].split('.')) == 1:
		springbot.centerGround(height)
	
	# Equilibrium ratio sum
	eq_ratio = 0

	# Height sum
	height_av = 0

	if enable_graphics and HAS_PYGAME:
		ticks = 0
		screen = pygame.display.get_surface()

	# Starts the simulation
	for i in xrange(simulation_time):
		if enable_graphics and HAS_PYGAME:		
			springbot.draw(screen, ticks, extrainfo="evolving for equilibrium")
			pygame.display.flip()	# Show display
			ticks += 1

			for event in pygame.event.get():
				if event.type == pygame.QUIT or \
				(event.type == pygame.KEYDOWN and event.key == 27):	
					raise KeyboardInterrupt

		# Calculates its mass center
		cx, cy = springbot.massCenter()

		# Calculates its bounding box
		x1, y1, x2, y2 = springbot.boundingBox()

		# Calculates the equilibrium ratio and sum
		eq_ratio += (y2-cy)/(y2-y1)
		height_av += y2-y1

		springbot.refresh()
		springbot.colideWall(height, DOWN)

	# Returns the equilibrium ratio average
	return 0 if height_av/simulation_time < RADIUS else eq_ratio/simulation_time

#                                                                              #
################################################################################
#                                                                              #

def height(springbot, width, height, enable_graphics=False, simulation_time=400):
	"""
	Rewards maximum average aspect ratio of body's height over width
	"""

	# Center springbot horizontaly ant touches ground
	if len(springbot['bloodline'].split('.')) == 1:
		springbot.centerGround(height)
	
	# Aspect ratio sum
	aspect_ratio = 0

	if enable_graphics and HAS_PYGAME:
		ticks = 0
		screen = pygame.display.get_surface()

	# Starts the simulation
	for i in xrange(simulation_time):
		if enable_graphics and HAS_PYGAME:		
			springbot.draw(screen, ticks, extrainfo="evolving for height")
			pygame.display.flip()	# Show display
			ticks += 1

			for event in pygame.event.get():
				if event.type == pygame.QUIT or \
				(event.type == pygame.KEYDOWN and event.key == 27):	
					raise KeyboardInterrupt

		# Calculates its bounding box
		x1, y1, x2, y2 = springbot.boundingBox()

		# Calculates the aspect ratio and sum
		if x2 - x1 != 0:
			aspect_ratio += (y2 - y1) / (x2 - x1)

		# Refresgh springbot
		springbot.refresh()
		springbot.colideWall(height, DOWN)

	# Returns the aspect ratio average
	return aspect_ratio/simulation_time

#                                                                              #
################################################################################
#                                                                              #

def swim(springbot, width, height, enable_graphics=False, simulation_time=1500):
	"""
	Rewards maximum diference between mass centers positions before and after the
	simulation in a liquid enviroment without gravity.
	"""
	
	# Selects its mass center
	start_x, start_y = springbot.massCenter()

	if enable_graphics and HAS_PYGAME:
		ticks = 0
		screen = pygame.display.get_surface()

	# Starts the simulation
	angle = 0.0
	for i in xrange(simulation_time):
		if enable_graphics and HAS_PYGAME:		
			springbot.draw(screen, ticks, track_x=True, track_y=True, 
			backgroundcolor=(0,10,20), extrainfo="evolving for swim")
			pygame.display.flip()	# Show display
			ticks += 1

			for event in pygame.event.get():
				if event.type == pygame.QUIT or \
				(event.type == pygame.KEYDOWN and event.key == 27):	
					raise KeyboardInterrupt

		springbot.refresh(grav=(0,0), visc=VISCOSITY)

	# Selects its mass center now
	end_x, end_y = springbot.massCenter()

	# Returns the horizontal distance traveled(fitness)
	return sqrt((end_x-start_x)**2 + (end_y-start_y)**2)
	

#                                                                              #
################################################################################
#                                                                              #

