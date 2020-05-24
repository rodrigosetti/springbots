#! /usr/bin/python
"""
Evolves springbots for specific tasks over the network: each springbot is simulated
at a computer in a network
"""

from warnings import warn

# We need to load and store xml springbots files
from springbots.springbot import store_xml, load_xml

from springbots.networkspringbot import NetworkSpringbot
from springbots.evolvespringbot import EvolveSpringbot

# We need to generate some random names for the random ones
from springbots.latimname import latimname

# To parse command lines
import sys, optparse

# To call remote xmlrpc servers
import xmlrpc.client

# To sample from the population
from random import sample

# To strip server list names and lowercase strings
from string import strip, lower

# To create a thread for each xmlrpc server
from threading import Thread

# To handle socket error
import socket

# To do local fitness tests in case of servers error
from springbots import fitness

#                                                                              #
################################################################################
#                            Globals                                           #

WIDTH, HEIGHT = 640, 480

population = []
servers= []
servers_lock = []
fitness_function = "walk"
serverslist = "fitness-servers.txt"

#                                                                              #
################################################################################
#                                                                              #

class NetworkEvolveSpringbot(NetworkSpringbot, EvolveSpringbot):
    """
    This is a double heritage of a network and an evolvable
    springbot into a class which does both
    """

def load_servers():
    """
    Load from a file the address of the fitness-servers lists
    """
    global servers, servers_lock, serverslist

    # Reads fitness servers
    servers = [xmlrpc.client.ServerProxy(strip(l)) for l in open(serverslist, 'r')
               if len(strip(l)) > 0 and strip(l)[0] != '#']
    servers_lock = [0 for x in range(len(servers))]


#                                                                              #
################################################################################
#                                                                              #

class FitnessThread(Thread):
    """
    Tests fitness for a specific springbot
    """
    def __init__(self, index, *args, **kargs):
        self.index = index
        Thread.__init__(self, *args, **kargs)

    def run(self):
        """
        Gets the corresponding springbot and pick a server to simulate
        """
        global population, servers, servers_lock, fitness_function

        # Selects the springbot to be tested
        springbot = population[self.index]

        while True:
            try:
                # Get the less used server at the moment
                server_index = min(range(len(servers_lock)), key=servers_lock.__getitem__)

                # Get the server object
                server = servers[server_index]

                # Lock
                servers_lock[server_index] += 1

                # Calls the fitness function at the server
                marshal_springbot = server.fitness_test(
                    springbot.marshal(), fitness_function)

                # Unlock
                servers_lock[server_index] -= 1

                # Changes springbot's state
                springbot.unmarshal(marshal_springbot)

                break
            except socket.error:
                warn("Connection refused at server %s\n" % (str(server)))
            except xmlrpc.client.Error as err:
                warn("Error at server %s: %s\n" % (str(server), str(err)))

        if not servers:
            warn("There are no servers left to use. Doing local fitness test\n")
            fitness.__dict__[fitness_function](springbot, WIDTH, HEIGHT)

#                                                                              #
################################################################################
#                                                                              #

def network_evolve(save_freq=100, limit=-1,
        verbose=False, discard_fraction=0.4, random_insert=0.1,
        best=False, start_iteration = 1, prefix=''):
    """
    Given the initial population 'population', executes
    a genetic algorithm to evolve them for best fitness.
    Saves the population each 'save_freq' interval(ordered by fitness)
    """
    global population, servers, fitness_function

    # Test if parameters are correct
    if discard_fraction < 0 or random_insert < 0:
        raise ValueError("discard_fraction and random_insert must both range from 0 to 1")
    elif discard_fraction + random_insert > 1:
        raise ValueError("the sum of discard_fraction and random_insert must not be greater than 1")

    iteration = start_iteration # Initial iteration

    # Calculate amount of discarded and random population
    discarded = int(len(population)/2 * discard_fraction)
    randoms = int(len(population)/2 * random_insert)

    if verbose:
        print("# Initiating simulation with a population of %d specimens..." % (len(population)))
        print("# Evolving for %s:" % (fitness_function))
        print("# At each iteration %d will be discarded, %d of the remaining will" % (
            discarded, discarded-randoms), end=' ')
        print(" be selected cloned and mutated and %d random springbots will be inserted" % (
            randoms))

    # Turn all population into NetworkEvolveSpringbot
    population = [NetworkEvolveSpringbot(springbot) for springbot in population]

    threads = []

    try:

        while population and iteration != limit:

            # (Re)load servers from file
            load_servers()

            if verbose:
                print("Iteration %d:" % (iteration))
                fitness_sum = 0
                bloodline_len_sum = 0

            # Create threads
            threads = [FitnessThread(i) for i in range(len(population))]

            # Start all threads
            for thread in threads:
                thread.start()

            # Join(waits) all threads
            for thread in threads:
                thread.join()

                if verbose:
                    specimen = population[thread.index]
                    print("\t%d/%d: \"%s\"(%d) %.3f" % \
                    (thread.index+1, len(population), specimen['name'],
                    specimen.generations(), specimen['fitness']))
                    bloodline_len_sum +=specimen.generations()
                    fitness_sum += specimen['fitness']

            if verbose:
                print("Bloodline lenght average: %.4f" % (bloodline_len_sum/float(len(population))))
                print("Fitness average: %.4f" % (fitness_sum/float(len(population))))

            # Now Order population by its fitness
            population.sort(
                cmp=lambda A,B: cmp(A['fitness'], B['fitness']), reverse=True)

            # Discards some of the worse half
            for specimen in sample(population[len(population)//2:], discarded + randoms):
                population.remove(specimen)

            # Clones and mutates some of the remaining half
            for specimen in sample(population, discarded):
                child = NetworkEvolveSpringbot(specimen).mutate()
                child.addBloodline(specimen)
                names = child['name'].split()

                # Gives a child's name
                if len(names) == 1:
                    child['name'] = names[0] + " " + latimname(2)
                elif len(names) == 2:
                    child['name'] = " ".join([names[0], names[1], latimname(2)])
                elif len(names) == 3:
                    child['name'] = " ".join([names[0], names[2], latimname(2)])

                # Incorporate children into the population
                population.append(child)

            # Incorporate randoms
            population += [NetworkEvolveSpringbot(random=True) for x in range(randoms)]

            # Test if it is time to save population
            if iteration % save_freq == 0:
                # Saves the current population
                filename = "%s-%s-p%d-i%d.xml" % (prefix, fitness_function, len(population), iteration)
                store_xml(population, filename)

                if verbose:
                    print("# iteration %d saved into %s" % (iteration, filename))

            # Saves best if asked
            if best:
                filename = "%s-%s-p%d-best.xml" % (prefix, fitness_function, len(population))
                store_xml(population[:1], filename)

                if verbose:
                    print("# Best of iteration %d saved into %s" % (iteration, filename))

            # Increments iteration
            iteration += 1

    except KeyboardInterrupt:
        pass
    if verbose:
        print("# waiting for threads...")

    # Join(waits) all threads
    for thread in threads:
        thread.join()

    # Order population by its fitness
    population.sort(reverse=True)

    # Now, saves the current population and quit
    filename = "%s-%s-p%d-i%d.xml" % (prefix, fitness_function, len(population), iteration)
    store_xml(population, filename)
    if verbose:
        print()
        print("# iteration %d saved into %s" % (iteration, filename))
        print("# terminating...")

#
# If this module its being running as main, execute main thread
#
if __name__ == "__main__":

    # Parses command line
    parser = optparse.OptionParser(description="Starts a Springbots network distributed evolution experiment.")
    parser.add_option("-v", "--verbose", dest="verbose", default=False,
                      help="Verbose output", action="store_true")
    parser.add_option("-b", "--best", dest="best", default=False,
                      help="Save best each iteration", action="store_true")
    parser.add_option("-s", "--save-freq", dest="save_freq", default=100,
                      help="Frequency the simulation saves the current population, default is each 100 iterations",
                      metavar="NUMBER")
    parser.add_option("-l", "--limit", dest="limit", default=-1,
                      help="Evolves to a limit number of iterations, default is endless", metavar="ITERATIONS")
    parser.add_option("-f", "--fitness", dest="fitness", default="walk",
                      help="Fitness function used to evolve, default is walk", metavar="FITNESS")
    parser.add_option("-n", "--serverslist", dest="serverslist", default='fitness-servers.txt',
                      help="File which contains the url of the servers providing fitness service, defaults to fitness-servers.txt",
                      metavar="FILENAME")
    parser.add_option("-a", "--start-at", dest="start_at", default=1,
                      help="Start couting from iteration(default is one)", metavar="ITERATION")
    parser.add_option("-P", "--prefix", dest="prefix", default=None,
                      help="Append a prefix to population file names saved, default is a random name", metavar="PREFIX")
    (options, args) = parser.parse_args()

    # Read command line parameters
    serverslist = options.serverslist
    fitness_function = options.fitness

    options.save_freq = int(options.save_freq)
    options.limit = int(options.limit)
    options.start_at = int(options.start_at)

    options.prefix = options.prefix if options.prefix is not None else lower(latimname(3))
    if options.verbose: print("# %s experiment." % options.prefix)

    if len(args) == 0:
        readfile = sys.stdin
    else:
        readfile = args[0]

    # Reads the initial population
    population = load_xml(readfile)

    # Starts the simulation
    network_evolve(
        save_freq=options.save_freq, limit=options.limit,
        verbose=options.verbose, best=options.best,
        start_iteration=options.start_at, prefix=options.prefix)
