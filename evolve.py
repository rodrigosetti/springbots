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

# To lowercase strings
from string import lower

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
        verbose=False, graphics=False, discard_fraction=0.4, random_insert=0.1,
        best=False, start_iteration = 0, prefix=''):

    """
    Given the initial population 'population', executes
    a genetic algorithm to evolve them for best fitness.
    Saves the population each 'save_freq' interval(ordered by fitness)
    """
    # Test if parameters are correct
    if discard_fraction < 0 or random_insert < 0:
        raise ValueError("discard_fraction and random_insert must both range from 0 to 1")
    elif discard_fraction + random_insert > 1:
        raise ValueError("the sum of discard_fraction and random_insert must not be greater than 1")

    iter = start_iteration # Initial iteration

    # Calculate amount of discarded and random population
    discarded = int(len(population)/2 * discard_fraction)
    randoms = int(len(population)/2 * random_insert)

    if verbose:
        print "# Initiating simulation with a population of %d specimens." % (len(population))
        print "# Evolving for %s:" % (fitness.__name__)
        print "# At each iteration %d will be discarded, %d of the remaining will" %\
        (discarded, discarded-randoms),
        print " be selected cloned and mutated and %d random springbots will be inserted" %\
        (randoms)

    # Transforms population into evolvespringbots
    population = [EvolveSpringbot(springbot) for springbot in population]

    try:

        while population and iter != limit:

            if verbose:
                print "Iteration %d:" % (iter)
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

            # Discards some of the worse half
            for specimen in sample(population[len(population)/2:], discarded + randoms):
                population.remove(specimen)

            # Clones and mutates some of the remaining
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
            if iter % save_freq == 0:
                # Saves the current population
                filename = "%s-%s-p%d-i%d.xml" % (prefix, fitness.__name__, len(population), iter)
                store_xml(population, filename)

                if verbose:
                    print "# iteration %d saved into %s" % (iter, filename)

            # Saves best if asked
            if best:
                filename = "%s-%s-p%d-best.xml" % (prefix, fitness.__name__, len(population))
                store_xml(population[:1], filename)

                if verbose:
                    print "# Best of iteration %d saved into %s" % (iter, filename)

            # Increments iteration
            iter += 1

    except KeyboardInterrupt:
        pass

    # Order population by its fitness
    population.sort(reverse=True)

    # Now, saves the current population and quit
    filename = "%s-%s-p%d-i%d.xml" % (prefix, fitness.__name__, len(population), iter)
    store_xml(population, filename)
    if verbose:
        print
        print "# iteration %d saved into %s" % (iter, filename)
        print "# terminating..."

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
            help="Save best each iteration", action="store_true")
    parser.add_option("-s", "--save-freq", dest="save_freq", default=100,
            help="Frequency the simulation saves the current population, default is each 100 iterations", metavar="NUMBER")
    parser.add_option("-l", "--limit", dest="limit", default=0,
            help="Evolves to a limit number of iterations, default is endless", metavar="ITERATIONS")
    parser.add_option("-a", "--start-at", dest="start_at", default=0,
            help="Start couting from iteration(default is zero)", metavar="ITERATION")
    parser.add_option("-P", "--prefix", dest="prefix", default=None,
            help="Append a prefix to population file names saved, default is a random name", metavar="PREFIX")
    parser.add_option("-f", "--fitness", dest="fitness", default="walk",
            help="Fitness function used to evolve, default is walk", metavar="FITNESS")
    (options, args) = parser.parse_args()

    if not HAS_PYGAME:
        options.graphics = False

    # Load fitness function
    fitness = fitness.__dict__[options.fitness]

    options.save_freq = int(options.save_freq)
    options.limit = int(options.limit)
    options.start_at = int(options.start_at)

    options.prefix = options.prefix if options.prefix is not None else lower(latimname(3))
    if options.verbose: print "# %s experiment." % options.prefix

    # Reads the initial population
    init_population = load_xml(options.arquivo if options.arquivo else sys.stdin)

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
            best=options.best, start_iteration=options.start_at, prefix=options.prefix)

    if options.graphics:
        pygame.quit()
