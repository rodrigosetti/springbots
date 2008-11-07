#! /usr/bin/python

from springbots.springbot import store_xml
from springbots.evolvespringbot import random_springbot

import optparse

if __name__ == "__main__":

    # Parses command line
    parser = optparse.OptionParser(description="Generate a random Springbots XML genome population")
    parser.add_option("-p", "--population", dest="population", default=1,
            help="Number of random springbots to create", metavar="NUMBER")
    parser.add_option("-n", "--nodes", dest="nodes_num", default=10,
            help="Number of nodes", metavar="NUMBER")
    parser.add_option("-s", "--springs", dest="springs_num", default=30,
            help="Number of springs", metavar="NUMBER")
    parser.add_option("-r", "--noderadius", dest="node_radius", default=100,
            help="Max distance to create new nodes", metavar="NUMBER")
    (options, args) = parser.parse_args()

    # Parses integer values
    options.population = int(options.population)
    options.springs_num = int(options.springs_num)
    options.nodes_num = int(options.nodes_num)
    options.node_radius = int(options.node_radius)

    # Creates a population of random springbots with the chosen parameters and
    # writes it to XML output
    store_xml(\
            [random_springbot(options.nodes_num, options.springs_num, options.node_radius) \
            for x in xrange(options.population)])
