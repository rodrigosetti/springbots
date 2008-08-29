#! /usr/bin/python
"""
Evolves springbots for specific tasks serialized: each springbot is simulated
at a time.
"""

# We need to load and store xml springbots files
from springbots.springbot import store_xml, load_xml

# We need to generate some random names for the random ones
from springbots.latimname import latimname

# We need a springbot which can evolve
from springbots.evolvespringbot import EvolveSpringbot

# To parse command lines
import sys, optparse

# Get all fitness functions we need
from springbots import fitness

# To sample from the population
from random import sample

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False

#                                                                              #
################################################################################
#                        Global Constants                                      #

WIDTH, HEIGHT = 640, 400


#                                                                              #
################################################################################
#                                                                              #

def serial_evolve(population, fitness=fitness.walk, save_freq=100,
        limit=0,
        verbose=False, graphics=False, discard_fraction=0.33, random_insert=0.1,
        best=False):

    """
    Given the initial population 'population', executes
    a genetic algorithm to evolve them for best fitness.
    Saves the population each 'save_freq' interval(ordered by fitness)
    """
    gen = 1 # Initial generation

    # Calculate amount of discarded and random population
    discarded = int(len(population) * discard_fraction)
    randoms = int(len(population) * random_insert)

    if verbose:
        print "Initiating simulation with a population of %d specimens..." % (len(population))
        print "Evolving for %s:" % (fitness.__name__)
        print fitness.__doc__
        print "At each generation %d will be discarded, %d of the remaining will" %\
        (discarded, discarded-randoms),
        print "be selected cloned and mutated and %d of random springbots will be inserted" %\
        (randoms)

    # Transforms population into evolvespringbots
    population = [EvolveSpringbot(springbot) for springbot in population]

    try:

        while population and gen != limit:

            if verbose:
                print "Generation %d:" % (gen)
                z = 1
                fitness_sum = 0
                bloodline_len_sum = 0

            # Tests fitness for each springbot
            for specimen in population:
                specimen['fitness'] = fitness(specimen, WIDTH, HEIGHT, graphics)

                if verbose:
                    print "\t%d/%d: \"%s\"(%d) %.3f" % \
                            (z, len(population), specimen['name'],
                            specimen.generations(), specimen['fitness'])
                    z += 1
                    bloodline_len_sum += specimen.generations()
                    fitness_sum += specimen['fitness']

            if verbose:
                print "Bloodline lenght average: %.4f" % (bloodline_len_sum/float(len(population)))
                print "Fitness average: %.4f" % (fitness_sum/float(len(population)))

            # Now Order population by its fitness
            population.sort(reverse=True)

            # Discards and insert randoms
            population = population[:-(discarded + randoms)]

            # Clones and mutates some of the remaining half
            for specimen in sample(population, discarded):
                child = EvolveSpringbot(specimen).mutate()
                child.addBloodline(specimen)

                names = child['name'].split()

                # Gives a child's name
                if len(names) == 1:
                    child['name'] = names[0] + " " + latimname(2)
                elif len(names) == 2:
                    child['name'] = names[0] + " " + names[1] + " " + latimname(2)
                elif len(names) == 3:
                    child['name'] = names[0] + " " + names[2] + " " + latimname(2)

                # Incorporate children into the population
                population.append(child)

            # Incorporate randoms
            population += [EvolveSpringbot(random=True) for x in xrange(randoms)]

            # Test if it is time to save population
            if gen % save_freq == 0:
                # Saves the current population
                filename = "%s-p%d-g%d.xml" % (fitness.__name__, len(population), gen)
                store_xml(population, filename)

                if verbose:
                    print "generation %d saved into %s" % (gen, filename)

            # Saves best if asked
            if best:
                filename = "%s-p%d-best.xml" % (fitness.__name__, len(population))
                store_xml(population[:1], filename)

                if verbose:
                    print "Best of generation %d saved into %s" % (gen, filename)

            # Increments generation
            gen += 1

    except KeyboardInterrupt:
        pass

    # Order population by its fitness
    population.sort(reverse=True)

    # Now, saves the current population and quit
    filename = "%s-p%d-g%d.xml" % (fitness.__name__, len(population), gen)
    store_xml(population, filename)
    if verbose:
        print
        print "generation %d saved into %s" % (gen, filename)
        print "terminating..."

#
# If this module its being running as main, execute main thread
#
if __name__ == "__main__":

    # Parses command line
    parser = optparse.OptionParser()
    parser.add_option("-p", "--population", dest="arquivo", default=None,
            help="Initial population XML file, default reads from stdin",
            metavar="FILENAME", default=None)

    if HAS_PYGAME:
        parser.add_option("-g", "--graphics", dest="graphics", default=False,
                help="Enable graphics", action="store_true")
        parser.add_option("-F", "--fullscreen", dest="fullscreen", default=False,
                action="store_true", help="Show in fullscreen")

    parser.add_option("-v", "--verbose", dest="verbose", default=False,
            help="Verbose output", action="store_true")
    parser.add_option("-b", "--best", dest="best", default=False,
            help="Save best each generation", action="store_true")
    parser.add_option("-s", "--save-freq", dest="save_freq", default=100,
            help="Frequency the simulation saves the current population, default is each 100 generations", metavar="NUMBER")
    parser.add_option("-l", "--limit", dest="limit", default=0,
            help="Evolves to a limit number of generations, default is endless", metavar="GENERATIONS")
    parser.add_option("-f", "--fitness", dest="fitness", default="walk",
            help="Fitness function used to evolve, default is walk", metavar="FITNESS")
    (options, args) = parser.parse_args()

    if not HAS_PYGAME:
        options.graphics = False

    # Load fitness function
    fitness = fitness.__dict__[options.fitness]

    options.save_freq = int(options.save_freq)
    options.limit = int(options.limit)

    # Reads the initial population
    init_population = load_xml(options.arquivo if options.arquivo else sys.stdin)

# Set "adapted" value to current fitness
    for springbot in init_population:
        springbot['adapted'] = options.fitness

    # If graphics is enabled, starts pygame
    if options.graphics:
        pygame.init()
        pygame.display.set_mode((WIDTH,HEIGHT),
        pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE if options.fullscreen else pygame.DOUBLEBUF)
        pygame.display.set_caption("Evolving springbot for %s" % (options.fitness))
        pygame.mouse.set_visible(not options.fullscreen)

    # Starts the simulation
    serial_evolve(init_population, fitness, save_freq=options.save_freq,
            limit=options.limit,
            verbose=options.verbose, graphics=options.graphics,
            best=options.best)

    if options.graphics:
        pygame.quit()
