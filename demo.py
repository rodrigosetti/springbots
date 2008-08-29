#! /usr/bin/python

from springbots.gear import *
from springbots.springbot import load_xml
from springbots.evolvespringbot import random_springbot
import sys, pygame, optparse, os
import random

WIDTH, HEIGHT = 640,400

#
# If this module its being running as main, execute main thread
#
if __name__ == "__main__":

    # Parses command line
    parser = optparse.OptionParser()
    parser.add_option("-f", "--fullscreen", dest="fullscreen", default=False,
            action="store_true", help="Show in fullscreen")
    parser.add_option("-s", "--sound", dest="sound", default=False,
            action="store_true", help="Play sound")
    parser.add_option("-t", "--time", dest="time", default=5000, metavar="TIME",
            help="Time(in cicles) simulating each springbot")
    parser.add_option("-r", "--random", dest="randoms", default=0, metavar="RANDOMS",
            help="Adds a number of random springbots to demo")

    (options, args) = parser.parse_args()

    if len(args) == 0:
        readfile = sys.stdin
    else:
        readfile = args[0]

    options.time = int(options.time)
    options.randoms = int(options.randoms)

    # Load population from file
    population = load_xml(readfile) + [random_springbot() for x in xrange(options.randoms)]

    pygame.init()

    if options.sound:
        colide_snd = pygame.mixer.Sound(os.path.join('sound','pop.wav'))

    pygame.display.set_mode((WIDTH,HEIGHT),
            pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE if options.fullscreen else pygame.DOUBLEBUF)
    pygame.display.set_caption('Springbots viewer')
    pygame.mouse.set_visible(not options.fullscreen)
    screen = pygame.display.get_surface()

    try:
        running = True
        while running:

            random.shuffle(population)
            for springbot in population:

                try:
                    adapted = springbot["adapted"]
                except KeyError:
                    adapted = "unknown"

                if adapted == "random":
                    springbot = random_springbot()
                    extrainfo = "random generated"
                    liquid = random.choice([True,False])
                else:
                    extrainfo = "evolved for " + adapted
                    liquid = adapted in ("liquid", "water", "swim")

                # Center springbot horizontaly ant touches ground
                if not liquid:
                    springbot.centerGround(HEIGHT)
                else:
                    for node in springbot.nodes:
                        node.pos.y += (HEIGHT/2)

                # controle de fps
                clock = pygame.time.Clock()

                ticks = 0;
                while running and ticks < options.time:

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT or \
                                    (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                            running = False
                            break
                        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                            ticks = options.time
                            break

                    if liquid:
                        springbot.draw(screen, ticks=ticks, track_x=True, track_y=True,
                                        backgroundcolor=(0,50,100), extrainfo=extrainfo)
                        springbot.refresh(grav=(0,0), visc=VISCOSITY)
                    else:
                        springbot.draw(screen, ticks=ticks, track_x=True, extrainfo=extrainfo)
                        springbot.refresh()
                        col = springbot.colideWall(HEIGHT, DOWN)
                        if options.sound and col > 0.1:
                            colide_snd.set_volume((col-0.2)**2)
                            colide_snd.play(0, int(col))

                    pygame.display.flip()   # Show display

                    ticks += 1
                    clock.tick(1000)        # limita fps


                if not running:
                    break

    except KeyboardInterrupt:
        pass

    # Closes pygame
    pygame.quit()
