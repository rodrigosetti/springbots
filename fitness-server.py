#! /usr/bin/python
"""
Servers the fitness functions on the network using xmlrpc
"""

# Sys for stdin, and optparse for parsing command line
import sys, optparse

# Get all fitness functions we need
from springbots import fitness

# Springbot object which can be unmarshaled and evolved
from springbots.networkevolvespringbot import NetworkEvolveSpringbot

# This is used to create the xmlrpc server
import SimpleXMLRPCServer

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False

if HAS_PYGAME:
    import threading

#                                                                              #
################################################################################
#                        Globals                                               #

WIDTH, HEIGHT = 640, 480
SHOW_GRAPHICS = False
VERBOSE_MODE = False

#                                                                              #
################################################################################
#                        Functions                                             #

#
# Shut down server and pygame
#
def quit():
    """
    Tell the server to shutdown
    """
    global server

    if SHOW_GRAPHICS and HAS_PYGAME:
        pygame.quit()

    if VERBOSE_MODE:
        print "closing server..."
    server.server_close()

    return 0

#
# Listens to QUIT or ESC events fom pygame
#
def eventListener():
    """
    Keeps listening to pygame's events, if it reaches a QUIT or
    ESC it calls quit and returns.
    """

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
            (event.type == pygame.KEYDOWN and event.key == 27):
                quit()
                return

#
# Draws a message on the center of screen
#
def draw_waiting(msg):
    """
    Draws a message on the center of screen
    """
    screen = pygame.display.get_surface()
    width, height = screen.get_size()

    font = pygame.font.Font(None, 45)
    text = font.render(msg, True, (255,255,255))
    tw, th = text.get_size()
    screen.blit(text, ((width/2)-(tw/2), (height/2)-(th/2)))

    pygame.display.flip()   # Show display

#
# Tests fitness
#
def fitness_test(marshal_springbot, function="walk"):
    """
    Test fitness for marshaled springbot into a specific fitness function
    """
    global SHOW_GRAPHICS, VERBOSE_MODE

    springbot = NetworkEvolveSpringbot().unmarshal(marshal_springbot)

    # Tests fitness
    springbot['fitness'] = fitness.__dict__[function](springbot, WIDTH, HEIGHT, SHOW_GRAPHICS)

    if SHOW_GRAPHICS:
        draw_waiting("FITNESS: %.3f." % (springbot['fitness']))

    if VERBOSE_MODE:
        print '"%s": %.3f' % (springbot['name'], springbot['fitness'])

    return springbot.marshal()

#
# If this module its being running as main, execute main thread
#
if __name__ == "__main__":

    # Parses command line
    parser = optparse.OptionParser()

    if HAS_PYGAME:
        parser.add_option("-g", "--graphics", dest="graphics", default=False,
                help="Enable graphics", action="store_true")
        parser.add_option("-f", "--fullscreen", dest="fullscreen", default=False,
                action="store_true", help="Show in fullscreen")

    parser.add_option("-v", "--verbose", dest="verbose", default=False,
            help="Verbose output", action="store_true")
    parser.add_option("-p", "--port", dest="port", default=8088,
            help="Server's listening port, defaults to 8088", metavar="PORT")
    (options, args) = parser.parse_args()

    options.port = int(options.port)

    if not HAS_PYGAME:
        options.graphics = False
    else:
        SHOW_GRAPHICS = options.graphics

    VERBOSE_MODE = options.verbose

    # If graphics is enabled, starts pygame
    if options.graphics:
        pygame.init()
        pygame.display.set_mode((WIDTH,HEIGHT),
        pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE if options.fullscreen else pygame.DOUBLEBUF)
        pygame.display.set_caption("Evolving springbot")
        pygame.mouse.set_visible(not options.fullscreen)

    # Create server
    try:
        server = SimpleXMLRPCServer.SimpleXMLRPCServer(('', options.port))
    except socket.error, err:
        print err
        sys.exit(1)

    if options.verbose:
        print "Server listening on port %d" % (options.port)

    # Register functions
    server.register_function(fitness_test)
    server.register_function(quit)

    # Starts the pygame QUIT listening thread
    if SHOW_GRAPHICS:
        thread = threading.Thread(target=eventListener, name="pygame event listener")
        thread.start()
        draw_waiting("WAITING FOR CONNECTIONS")

    # Start server
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        quit()
