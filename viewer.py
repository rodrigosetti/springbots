#! /usr/bin/python

from math import *
from springbots.gear import *
from springbots.springbot import load_xml
import sys, pygame, optparse, os

WIDTH, HEIGHT = 640, 480

#
# If this module its being running as main, execute main thread
#
if __name__ == "__main__":

    # Parses command line
    parser = optparse.OptionParser()
    parser.add_option("-i", "--index", dest="index", default=0,
            help="Springbot index in population file", metavar="INDEX")
    parser.add_option("-l", "--liquid", dest="liquid", default=False,
            action="store_true",
            help="Simulates a liquid enviroment")
    parser.add_option("-f", "--fullscreen", dest="fullscreen", default=False,
            action="store_true", help="Show in fullscreen")
    parser.add_option("-s", "--sound", dest="sound", default=False,
            action="store_true", help="Play sound")

    (options, args) = parser.parse_args()

    if len(args) == 0:
        readfile = sys.stdin
    else:
        readfile = args[0]

    options.index = int(options.index)

    # Load springbot
    springbot = load_xml(readfile, limit=options.index+1)[options.index]

    pygame.init()
    pygame.display.set_mode((WIDTH,HEIGHT),
            pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE if options.fullscreen else pygame.DOUBLEBUF)
    pygame.display.set_caption('Springbots viewer')
    pygame.mouse.set_visible(not options.fullscreen)

    if options.sound:
        colide_snd = pygame.mixer.Sound(os.path.join('sound','pop.wav'))

    # Center springbot horizontaly and touches ground
    if not options.liquid:
        springbot.centerGround(HEIGHT)
    else:
        for node in springbot.nodes:
            node.pos.y += (HEIGHT/2)

    screen = pygame.display.get_surface()

    # Ticks count
    ticks = 0

    # controle de fps
    clock = pygame.time.Clock()

    try:
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or \
                (event.type == pygame.KEYDOWN and event.key == 27):
                    running = False
                    break

            if options.liquid:
                springbot.draw(screen, track_x=True, track_y=True, backgroundcolor=(0,50,100))
                springbot.refresh(grav=(0,0), visc=VISCOSITY)
            else:
                springbot.draw(screen, track_x=True)
                springbot.refresh()
                col = springbot.colideWall(HEIGHT, DOWN)
                if options.sound and col > 0.1:
                    colide_snd.set_volume((col-0.2)**2)
                    colide_snd.play(0, int(col))

            pygame.display.flip()   # Show display

            ticks += 1
            clock.tick(1000)        # limita fps


    except KeyboardInterrupt:
        pass

    # Closes pygame
    pygame.quit()
