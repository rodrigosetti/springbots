#! /usr/bin/python
"""
Evolves springbots for specific tasks over the network: each springbot is simulated
at a computer in a network
"""

# We need to load and store xml springbots files
from springbots.springbot import store_xml, load_xml

# We need to generate some random names for the random ones
from springbots.latimname import latimname

# We need a springbot which can be marshaled, unmarshaled and evolve
from springbots.networkevolvespringbot import NetworkEvolveSpringbot

# To parse command lines
import sys, optparse

# To call remote xmlrpc servers
import xmlrpclib

# To sample from the population
from random import sample

# To strip server list names
from string import strip

# To create a thread for each xmlrpc server
from threading import Thread

# To handle socket error
import socket

#                                                                              #
################################################################################
#                            Globals                                           #

population = []
servers= []
servers_lock = []
fitness_function = "walk"

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
				i = 0
				while servers and i not in servers_lock:
					i += 1
				if not servers:
					break
				server_index = servers_lock.index(i)

				# Get the server object
				server = servers[server_index]

				# Lock
				servers_lock[server_index] += 1

				# Calls the fitness function at the server
				marshal_springbot = \
				server.fitness_test(springbot.marshal(), fitness_function)

				# Unlock
				servers_lock[server_index] -= 1

				# Changes springbot's state
				springbot.unmarshal(marshal_springbot)

				break
			except socket.error:
				sys.stderr.write("Connection refused at server %s\n" % (str(server)))				
				servers_lock = servers_lock[:server_index] + servers_lock[server_index+1:]
				servers = servers[:server_index] + servers[server_index+1:]
			except xmlrpclib.Error, err:
				sys.stderr.write("Error at server %s: %s\n" % (str(server), str(err)))

		if not servers:
			sys.stderr.write("There are no servers left to use, evolution aborted\n")
			sys.exit(1)

#                                                                              #
################################################################################
#                                                                              #

def network_evolve(save_freq=100, limit=0,
	verbose=False, discard_fraction=0.33, random_insert=0.1,
	best=False):
	"""
	Given the initial population 'population', executes
	a genetic algorithm to evolve them for best fitness.
	Saves the population each 'save_freq' interval(ordered by fitness)
	"""
	global population, servers, fitness_function

	gen = 1	# Initial generation

	# Calculate amount of discarded and random population
	discarded = int(len(population) * discard_fraction)
	randoms = int(len(population) * random_insert)

	if verbose:
		print "Initiating simulation with a population of %d specimens..." % (len(population))
		print "Evolving for %s:" % (fitness_function)
		print "At each generation %d will be discarded, %d of the remaining will" %\
		(discarded, discarded-randoms),
		print "be selected cloned and mutated and %d of random springbots will be inserted" %\
		(randoms)

	# Turn all population into NetworkEvolveSpringbot
	population = [NetworkEvolveSpringbot(springbot) for springbot in population]

	try:

		while population and servers and gen != limit:

			if verbose:
				print "Generation %d:" % (gen)
				fitness_sum = 0
				bloodline_len_sum = 0

			# Create threads
			threads = [FitnessThread(i) for i in xrange(len(population))]

			# Start all threads
			for thread in threads:
				thread.start()

			# Join(waits) all threads
			for thread in threads:
				thread.join()

				if verbose:
					specimen = population[thread.index]
					print "\t%d/%d: \"%s\"(%d) %.3f" % \
					(thread.index+1, len(population), specimen['name'], 
					specimen.generations(), specimen['fitness'])
					bloodline_len_sum +=specimen.generations()
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
				child = NetworkEvolveSpringbot(specimen).mutate()
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
			population += [NetworkEvolveSpringbot(random=True) for x in xrange(randoms)]

			# Test if it is time to save population
			if gen % save_freq == 0:
				# Saves the current population
				filename = "%s-p%d-g%d.xml" % (fitness_function, len(population), gen)
				store_xml(population, filename)

				if verbose:
					print "generation %d saved into %s" % (gen, filename)

			# Saves best if asked
			if best:
				filename = "%s-p%d-best.xml" % (fitness_function, len(population))
				store_xml(population[:1], filename)

				if verbose:
					print "Best of generation %d saved into %s" % (gen, filename)

			# Increments generation
			gen += 1

	except KeyboardInterrupt:
		pass
	if verbose:
		print "waiting for threads..."

	# Join(waits) all threads
	for thread in threads:
		thread.join()

	# Order population by its fitness
	population.sort(reverse=True)

	# Now, saves the current population and quit
	filename = "%s-p%d-g%d.xml" % (fitness_function, len(population), gen)
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
		metavar="FILENAME")
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
	parser.add_option("-n", "--serverslist", dest="serverslist", default='fitness-servers.txt',
		help="File which contains the url of the servers providing fitness service, defaults to fitness-servers.txt", 
		metavar="FILENAME")
	(options, args) = parser.parse_args()

	# Reads fitness servers
	servers = [xmlrpclib.ServerProxy(strip(l)) for l in open(options.serverslist, 'r') if len(strip(l)) > 0 and strip(l)[0] != '#']
	servers_lock = [0 for x in xrange(len(servers))]

	fitness_function = options.fitness

	options.save_freq = int(options.save_freq)
	options.limit = int(options.limit)

	# Reads the initial population
	population = load_xml(options.arquivo if options.arquivo else sys.stdin)

	# Starts the simulation
	network_evolve( 
		save_freq=options.save_freq, limit=options.limit, 
		verbose=options.verbose, best=options.best)


