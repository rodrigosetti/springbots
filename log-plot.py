#! /usr/bin/python

import pylab
import sys, optparse
import string
import re

# Globals
AVERAGE = 1
HISTOGRAM = 2
INDIVIDUAL = 3

COLORS = "bgrcmykw"

#
# If this module its being running as main, execute main thread
#
if __name__ == "__main__":

    # Parses command line
    parser = optparse.OptionParser()
    parser.add_option("-l", "--lineages", dest="lineages", default="@",
                      help="Lineages names to plot, separated by comma. @ means to plot the average(default), and '*' plots all lineages", 
                      metavar="<lineage> | all [, (<lineage> | all)]*")
    parser.add_option("-g", "--graph", dest="graph", default="average",
            help="Specify one of three types of graph: average(default), histogram or individual", 
                      metavar="average | histogram | individual")

    (options, args) = parser.parse_args()

    # Check for argument lineages
    lineages = string.lower(options.lineages).split(',')
    if len(lineages) == 1 and lineages[0] is '':
        sys.stderr.write('You must specify a value for lineages argument(see help)\n')
        sys.exit(1)

    # Check for argument graph
    if 'average'.startswith(options.graph):
        graph = AVERAGE
    elif 'histogram'.startswith(options.graph):
        graph = HISTOGRAM
    elif 'individual'.startswith(options.graph):
        graph = INDIVIDUAL
    else:
        sys.stderr.write("Error: unrecognized graph argument %s(see help)\n" % options.graph)
        sys.exit(1)

    iter = None
    data = []

    # Read input log
    for n, line in enumerate(sys.stdin):
        # Strip leading spaces and lowercase
        line = string.lower(string.strip(line))
    
        # Ignore comments and blank lines
        if line is '' or line.startswith('#'): continue
        
        # Check for generation info
        m = re.match(r"^iteration\s(\d+):$", line)
        if m:
            new_iter = int(m.group(1))

            # Check consistency
            if iter is not None and new_iter != iter+1:
                sys.stderr.write("Error: bad log data at line %d: %s(broke iteration sequence)\n" % (d, line))
                sys.exit(1)

            iter = new_iter
            data.append({})
            data[-1]['tests'] = []
            continue


        # Check if got iteration info
        if iter is None:
            sys.stderr.write("Error: bad log data at line %d: %s(no iteration info)\n" % (n, line))
            sys.exit(1)

        # Check for bloodline info
        m = re.match(r"^bloodline\slenght\saverage:\s(\d+\.\d+)$", line)
        if m:
            data[-1]['bloodline'] = float(m.group(1))
            continue

        # Check for fitness average info
        m = re.match(r"^fitness\saverage:\s(\d+\.\d+)$", line)
        if m:
            data[-1]['fitness'] = float(m.group(1))            
            continue

        # Check for individual info
        m = re.match(r"^(\d+)/(\d+):\s\"([a-z]+)[a-z\s]*\"\((\d+)\)\s(\d+\.\d+)$", line)
        if m:
            name = m.group(3)
            if name in lineages:
                data[-1]['tests'].append({})
                data[-1]['tests'][-1]['name'] = name
                data[-1]['tests'][-1]['generation'] = int(m.group(4))
                data[-1]['tests'][-1]['fitness'] = float(m.group(5))
        else:
            sys.stderr.write("Error: bad log data at line %d: %s(finishing processing)\n" % (n, line))
            break


    if graph == AVERAGE:
         
         # Start averages data
         averages = {}        
         if 'all' in lineages:
             averages['all'] = []

         # For every iteration data
         for n, iter in enumerate(data):

             # If set 'all fitness average'
             if 'all' in lineages:
                 averages['all'].append(iter['fitness'])

             iter_averages = {}

             # For every test data in this iteration
             for test in iter['tests']:

                 # If iter_averages already have this lineage list
                 if test['name'] in iter_averages:
                     iter_averages[test['name']].append(test['fitness'])
                 else:
                     iter_averages[test['name']] = [test['fitness']]

             # Calculate the averages and save
             for name in iter_averages:

                 av_value = sum(iter_averages[name])/float(len(iter_averages[name]))

                 # If averages already have this lineage list
                 if name in averages:
                     averages[name].append(av_value)
                 else:
                     averages[name] = [None]*n + [av_value]


         # Plot
         pylab.xlabel("iterations")
         pylab.ylabel("fitness average")
         if len(averages) == 1:
             pylab.title("Fitness average for " + averages.keys()[0])
         else:
             pylab.title("Fitness average")

         for n, name in enumerate(averages):
             pylab.plot(averages[name], COLORS[n % len(COLORS)], label=name)

         pylab.legend()

    elif graph == INDIVIDUAL:

        # Start individual data
        individual = {}
        if 'all' in lineages:
             individual['all'] = ([],[])

        # For every iteration data
        for n, iter in enumerate(data):

            # If set 'all fitness average'
            if 'all' in lineages:
                individual['all'][0].append(n)
                individual['all'][1].append(iter['fitness'])

            # For every test data in this iteration
            for test in iter['tests']:

                # Check if name is already in individual data
                if test['name'] in individual:
                    individual[test['name']][0].append(n)
                    individual[test['name']][1].append(test['fitness'])
                else:
                    individual[test['name']] = ([n], [test['fitness']])

        # Plot graphs
        pylab.xlabel("iterations")
        pylab.ylabel("fitness")
        if len(individual) == 1:
            pylab.title("Fitness tests for " + individual.keys()[0])
        else:
            pylab.title("Fitness tests")

        for n, name in enumerate(individual):
            pylab.plot(individual[name][0], individual[name][1], COLORS[n % len(COLORS)] + "o", label=name)

        pylab.legend()

    elif graph == HISTOGRAM:

        # Start histogram data
        histogram = {}
        if 'all' in lineages:
             histogram['all'] = []

        # For every iteration data
        for n, iter in enumerate(data):

            # If set 'all fitness average'
            if 'all' in lineages:
                histogram['all'].append(iter['fitness'])

            # For every test data in this iteration
            for test in iter['tests']:

                # Check if name is already in histogram data
                if test['name'] in histogram:
                    histogram[test['name']].append(test['fitness'])
                else:
                    histogram[test['name']] = [test['fitness']]


        # Plot
        pylab.xlabel("fitness")
        pylab.ylabel("population")
        if len(histogram) == 1:
            pylab.title("Fitness Histogram for " + histogram.keys()[0])
        else:
            pylab.title("Fitness Histogram")

        h = []
        for n, name in enumerate(histogram):
            _, _, x = pylab.hist(histogram[name], fc=COLORS[n % len(COLORS)], ec=COLORS[n % len(COLORS)], alpha=0.5, label=name)
            h.append(x[0])
        
        pylab.legend(h,histogram.keys())

    
    # Show plot
    pylab.show()
